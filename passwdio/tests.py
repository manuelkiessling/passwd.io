import json
import re
import unittest
import transaction

from pyramid import testing
from webtest import TestApp

from .domain import DossierRepository, Dossier
from .application import WalletService

valid_owner_hash = '1111111111111111111111111111111111111111111111111111111111111111'
valid_access_hash = '2222222222222222222222222222222222222222222222222222222222222222'

def setUpUnitTests():
    from sqlalchemy import create_engine
    from .models import DBSession, Base
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession

def tearDownUnitTests():
    from passwdio.models import DBSession
    DBSession.remove()

class DomainUnitTests(unittest.TestCase):
    def setUp(self):
        setUpUnitTests()

    def tearDown(self):
        tearDownUnitTests()

    def test_cantStoreInvalidDossier(self):
        pass

    def test_dossierRepository_exists(self):
        dossier = Dossier(owner_hash=valid_owner_hash, access_hash=valid_access_hash, content='Hello World')
        repo = DossierRepository()
        repo.store(dossier)
        exists = repo.exists(valid_owner_hash, valid_access_hash)
        self.assertTrue(exists)

    def test_subsequent_storing_overwrites_existing_dossier(self):
        dossier = Dossier(owner_hash=valid_owner_hash, access_hash=valid_access_hash, content='Hello World')
        id = dossier.id
        repo = DossierRepository()
        repo.store(dossier)
        dossier = repo.find(owner_hash=valid_owner_hash, access_hash=valid_access_hash)
        self.assertTrue(dossier.id == id)
        self.assertTrue(dossier.content == 'Hello World')
        dossier = Dossier(id=id, owner_hash=valid_owner_hash, access_hash=valid_access_hash, content='foo')
        repo = DossierRepository()
        repo.store(dossier)
        dossier = repo.find(owner_hash=valid_owner_hash, access_hash=valid_access_hash)
        self.assertTrue(dossier.id == id)
        self.assertTrue(dossier.content == 'foo')

    def test_cant_store_dossier_with_existing_owner_hash_under_different_id(self):
        repo = DossierRepository()
        dossier = Dossier(owner_hash=valid_owner_hash, access_hash=valid_access_hash, content='Hello World')
        repo.store(dossier)
        dossier = Dossier(owner_hash=valid_owner_hash, access_hash=valid_access_hash, content='Hello World')
        try:
            repo.store(dossier)
        except:
            thrown = True
        self.assertTrue(thrown)

    def test_cant_store_dossier_with_invalid_hashes(self):
        repo = DossierRepository()
        dossier = Dossier(owner_hash=valid_owner_hash, access_hash=valid_access_hash, content='Hello World')
        dossier.owner_hash = 'x111111111111111111111111111111111111111111111111111111111111111'
        thrown = False
        try:
            repo.store(dossier)
        except:
            thrown = True
        self.assertTrue(thrown)
        dossier.owner_hash = valid_owner_hash
        dossier.access_hash = 'x222222222222222222222222222222222222222222222222222222222222222'
        thrown = False
        try:
            repo.store(dossier)
        except:
            thrown = True
        self.assertTrue(thrown)

    def test_can_store_dossier_with_existing_owner_hash_with_different_access_hash(self):
        repo = DossierRepository()
        dossier = Dossier(owner_hash=valid_owner_hash, access_hash='3333333333333333333333333333333333333333333333333333333333333333', content='Hello World')
        id = dossier.id
        repo.store(dossier)
        dossier.access_hash = valid_access_hash
        repo.store(dossier)
        dossier = repo.find(owner_hash=valid_owner_hash, access_hash=valid_access_hash)
        self.assertTrue(dossier.id == id)

    def test_dossierRepository_exists_not(self):
        repo = DossierRepository()
        exists = repo.exists(valid_owner_hash, valid_access_hash)
        self.assertFalse(exists)

class WalletServiceUnitTests(unittest.TestCase):
    def setUp(self):
        setUpUnitTests()

    def tearDown(self):
        tearDownUnitTests()

    def test_filing_a_dossier_with_an_existing_owner_access_hash_by_overwriting(self):
        ws = WalletService()
        ws.fileDossier(valid_owner_hash, valid_access_hash, 'Hello World')
        ws.fileDossier(valid_owner_hash, valid_access_hash, 'foo')
        dossier = ws.retrieveDossier(valid_owner_hash, valid_access_hash)
        self.assertTrue(dossier.content == 'foo')

    def test_filing_a_dossier_with_an_existing_owner_access_hash_by_overwriting(self):
        ws = WalletService()
        ws.fileDossier(valid_owner_hash, valid_access_hash, 'Hello World')
        ws.fileDossier(valid_owner_hash, valid_access_hash, 'foo')
        dossier = ws.retrieveDossier(valid_owner_hash, valid_access_hash)
        self.assertTrue(dossier.content == 'foo')

    def test_file_doesnt_change_access_hash(self):
        ws = WalletService()
        ws.fileDossier(valid_owner_hash, valid_access_hash, 'Hello World')
        thrown = False
        try:
            ws.fileDossier(valid_owner_hash, '3333333333333333333333333333333333333333333333333333333333333333', 'Hello World')
        except:
            thrown = True
        self.assertTrue(thrown)
        dossier = ws.retrieveDossier(valid_owner_hash, valid_access_hash)
        self.assertTrue(dossier.content == 'Hello World')
        dossier = ws.retrieveDossier(valid_owner_hash, '3333333333333333333333333333333333333333333333333333333333333333')
        self.assertFalse(dossier)

    def test_change_access_hash(self):
        ws = WalletService()
        ws.fileDossier(valid_owner_hash, valid_access_hash, 'Hello World')
        ws.changeAccessHash(owner_hash=valid_owner_hash, old_access_hash=valid_access_hash, new_access_hash='3333333333333333333333333333333333333333333333333333333333333333')
        dossier = ws.retrieveDossier(valid_owner_hash, '3333333333333333333333333333333333333333333333333333333333333333')
        self.assertTrue(dossier.content == 'Hello World')
        dossier = ws.retrieveDossier(valid_owner_hash, valid_access_hash)
        self.assertFalse(dossier)

    def test_change_access_hash_fails_with_wrong_old_access_hash(self):
        ws = WalletService()
        ws.fileDossier(valid_owner_hash, valid_access_hash, 'Hello World')
        thrown = False
        try:
            ws.changeAccessHash(owner_hash=valid_owner_hash, old_access_hash='4444444444444444444444444444444444444444444444444444444444444444', new_access_hash='3333333333333333333333333333333333333333333333333333333333333333')
        except:
            thrown = True
        self.assertTrue(thrown)        
        dossier = ws.retrieveDossier(valid_owner_hash, '3333333333333333333333333333333333333333333333333333333333333333')
        self.assertFalse(dossier)
        dossier = ws.retrieveDossier(valid_owner_hash, valid_access_hash)
        self.assertTrue(dossier.content == 'Hello World')

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from passwdio import main
        settings = { 'sqlalchemy.url': 'sqlite://' }
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        from sqlalchemy import create_engine
        from .models import DBSession, Base
        engine = create_engine('sqlite://')
        Base.metadata.create_all(engine)
        DBSession.configure(bind=engine)
        return DBSession

    def tearDown(self):
        del self.testapp
        from passwdio.models import DBSession
        DBSession.remove()

    def test_save_and_load(self):
        post_params = {'owner_hash': valid_owner_hash, 'access_hash': valid_access_hash, 'content': 'foo'}
        self.testapp.post('/api/dossier/save.json', post_params, status=200)
        res = self.testapp.get('/api/dossier/load.json?owner_hash=' + valid_owner_hash + '&access_hash=' + valid_access_hash, status=200) 
        self.assertTrue(res.body == b'{"content": "foo"}')
        post_params = {'owner_hash': valid_owner_hash, 'access_hash': valid_access_hash, 'content': 'bar'}
        self.testapp.post('/api/dossier/save.json', post_params, status=200)
        res = self.testapp.get('/api/dossier/load.json?owner_hash=' + valid_owner_hash + '&access_hash=' + valid_access_hash, status=200) 
        self.assertTrue(res.body == b'{"content": "bar"}')

    def test_load_wrongaccesshash(self):
        post_params = {'owner_hash': valid_owner_hash, 'access_hash': valid_access_hash, 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json', post_params, status=200)
        res = self.testapp.get('/api/dossier/load.json?owner_hash=' + valid_owner_hash + '&access_hash=3333333333333333333333333333333333333333333333333333333333333333', status=400) 
        self.assertFalse(b'fdjs9884jhf98' in res.body)
        self.assertTrue(b'Not allowed' in res.body)

    def test_change_access_hash(self):
        post_params = {'owner_hash': valid_owner_hash, 'access_hash': valid_access_hash, 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json', post_params, status=200)
        post_params = {'owner_hash': valid_owner_hash, 'old_access_hash': valid_access_hash, 'new_access_hash': '3333333333333333333333333333333333333333333333333333333333333333'}
        res = self.testapp.post('/api/dossier/change_access_hash.json', post_params, status=200) 
        self.assertTrue(res.json['success'])

    def test_change_access_hash_fails(self):
        post_params = {'owner_hash': valid_owner_hash, 'access_hash': valid_access_hash, 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json', post_params, status=200)
        post_params = {'owner_hash': valid_owner_hash, 'old_access_hash': '4444444444444444444444444444444444444444444444444444444444444444', 'new_access_hash': '3333333333333333333333333333333333333333333333333333333333333333'}
        res = self.testapp.post('/api/dossier/change_access_hash.json', post_params, status=400) 
        self.assertFalse(res.json['success'])

    def test_api_calls_fail_with_syntactically_invalid_parameters(self):
        correct_post_params = {'owner_hash': 'cb7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611', 'access_hash': '54ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json', correct_post_params, status=200)
        self.testapp.get('/api/dossier/load.json?owner_hash=cb7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611&access_hash=54ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39', status=200)
        self.testapp.get('/api/dossier/change_access_hash.json?owner_hash=cb7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611&new_access_hash=3333333333333333333333333333333333333333333333333333333333333333&old_access_hash=54ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39', status=200)
        invalid_post_params = [
            {'owner_hash': '_b7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611',  'access_hash': '54ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39',  'content': 'fdjs9884jhf98'},
            {'owner_hash': 'cb7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611',  'access_hash': '_4ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39',  'content': 'fdjs9884jhf98'},
            {'owner_hash': 'b7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611',   'access_hash': '54ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39',  'content': 'fdjs9884jhf98'},
            {'owner_hash': 'cb7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611',  'access_hash': '4ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39',   'content': 'fdjs9884jhf98'},
            {'owner_hash': 'cb7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a126136112', 'access_hash': '54ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39',  'content': 'fdjs9884jhf98'},
            {'owner_hash': 'cb7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611',  'access_hash': '54ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb392', 'content': 'fdjs9884jhf98'},
            {'owner_hash': 'cb7c862eb5400a13e01844a4*4f176072755085894bcd9b098185c5a12613611',  'access_hash': '54ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39',  'content': 'fdjs9884jhf98'},
            {'owner_hash': 'cb7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611',  'access_hash': '54ebdc364af430e55b*2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39',  'content': 'fdjs9884jhf98'},
        ]
        for params in invalid_post_params:
            res = self.testapp.post('/api/dossier/save.json', params, status=400)
            self.assertTrue(b'parameter syntax error' in res.body)
            res = self.testapp.get('/api/dossier/load.json?owner_hash=' + params['owner_hash']  + '&access_hash=' + params['access_hash'], status=400)
            self.assertTrue(b'parameter syntax error' in res.body)
            res = self.testapp.get('/api/dossier/change_access_hash.json?owner_hash=' + params['owner_hash']  + '&old_access_hash=' + params['access_hash'] + '&new_access_hash=' + valid_access_hash, status=400)
            self.assertTrue(b'parameter syntax error' in res.body)
        invalid_new_access_hashes = [
            '_b7c962eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611',
            'b7c962eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611',
            'cb7c962eb5400a13e01844a4f4f176072755085894bcd9b098185c5a126136112',
            'cb7c962eb5400a13e01844a4*4f176072755085894bcd9b098185c5a12613611',
        ]
        post_params = {'owner_hash': valid_owner_hash, 'access_hash': valid_access_hash, 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json', post_params, status=200)
        for hash in invalid_new_access_hashes:
            res = self.testapp.get('/api/dossier/change_access_hash.json?owner_hash=' + valid_owner_hash + '&new_access_hash=' + hash + '&old_access_hash=' + valid_access_hash, status=400)
            self.assertTrue(b'parameter syntax error' in res.body)


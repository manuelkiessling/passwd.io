import unittest
import transaction

from pyramid import testing
from webtest import TestApp

from .domain import DossierRepository, Dossier
from .application import WalletService

class DomainUnitTests(unittest.TestCase):
    def setUp(self):
        from sqlalchemy import create_engine
        from .models import DBSession, Base
        engine = create_engine('sqlite://')
        Base.metadata.create_all(engine)
        DBSession.configure(bind=engine)
        return DBSession

    def tearDown(self):
        from onlinepasswordsafe.models import DBSession
        DBSession.remove()

    def test_cantStoreInvalidDossier(self):
        pass

    def test_dossierRepository_exists(self):
        dossier = Dossier(owner_hash='1111111111111111', access_hash='2222222222222222', content='Hello World')
        repo = DossierRepository()
        repo.store(dossier)
        exists = repo.exists('1111111111111111', '2222222222222222')
        self.assertTrue(exists)

    def test_subsequent_storing_overwrites_existing_dossier(self):
        dossier = Dossier(owner_hash='1111111111111111', access_hash='2222222222222222', content='Hello World')
        id = dossier.id
        repo = DossierRepository()
        repo.store(dossier)
        dossier = repo.find(owner_hash='1111111111111111', access_hash='2222222222222222')
        self.assertTrue(dossier.id == id)
        self.assertTrue(dossier.content == 'Hello World')
        dossier = Dossier(id=id, owner_hash='1111111111111111', access_hash='2222222222222222', content='foo')
        repo = DossierRepository()
        repo.store(dossier)
        dossier = repo.find(owner_hash='1111111111111111', access_hash='2222222222222222')
        self.assertTrue(dossier.id == id)
        self.assertTrue(dossier.content == 'foo')

    def test_cant_store_dossier_with_existing_owner_hash_under_different_id(self):
        repo = DossierRepository()
        dossier = Dossier(owner_hash='1111111111111111', access_hash='2222222222222222', content='Hello World')
        repo.store(dossier)
        dossier = Dossier(owner_hash='1111111111111111', access_hash='2222222222222222', content='Hello World')
        try:
            repo.store(dossier)
        except:
            thrown = True
        self.assertTrue(thrown)

    def test_can_store_dossier_with_existing_owner_hash_with_different_access_hash(self):
        repo = DossierRepository()
        dossier = Dossier(owner_hash='1111111111111111', access_hash='3333333333333333', content='Hello World')
        id = dossier.id
        repo.store(dossier)
        dossier.access_hash = '2222222222222222'
        repo.store(dossier)
        dossier = repo.find(owner_hash='1111111111111111', access_hash='2222222222222222')
        self.assertTrue(dossier.id == id)

    def test_dossierRepository_exists_not(self):
        repo = DossierRepository()
        exists = repo.exists('1111111111111111', '2222222222222222')
        self.assertFalse(exists)

class ApplicationUnitTests(unittest.TestCase):
    def setUp(self):
        from sqlalchemy import create_engine
        from .models import DBSession, Base
        engine = create_engine('sqlite://')
        Base.metadata.create_all(engine)
        DBSession.configure(bind=engine)
        return DBSession

    def tearDown(self):
        from onlinepasswordsafe.models import DBSession
        DBSession.remove()

    def test_filing_a_dossier_with_an_existing_owner_access_hash_by_overwriting(self):
        ws = WalletService()
        ws.fileDossier('1111111111111111', '2222222222222222', 'Hello World')
        ws.fileDossier('1111111111111111', '2222222222222222', 'foo')
        dossier = ws.retrieveDossier('1111111111111111', '2222222222222222')
        self.assertTrue(dossier.content == 'foo')

    def test_filing_a_dossier_with_an_existing_owner_access_hash_by_overwriting(self):
        ws = WalletService()
        ws.fileDossier('1111111111111111', '2222222222222222', 'Hello World')
        ws.fileDossier('1111111111111111', '2222222222222222', 'foo')
        dossier = ws.retrieveDossier('1111111111111111', '2222222222222222')
        self.assertTrue(dossier.content == 'foo')

    def test_file_doesnt_change_access_hash(self):
        ws = WalletService()
        ws.fileDossier('1111111111111111', '2222222222222222', 'Hello World')
        thrown = False
        try:
            ws.fileDossier('1111111111111111', '3333333333333333', 'Hello World')
        except:
            thrown = True
        self.assertTrue(thrown)
        dossier = ws.retrieveDossier('1111111111111111', '2222222222222222')
        self.assertTrue(dossier.content == 'Hello World')
        dossier = ws.retrieveDossier('1111111111111111', '3333333333333333')
        self.assertFalse(dossier)

    def test_change_access_hash(self):
        ws = WalletService()
        ws.fileDossier('1111111111111111', '2222222222222222', 'Hello World')
        ws.changeAccessHash(owner_hash='1111111111111111', old_access_hash='2222222222222222', new_access_hash='3333333333333333')
        dossier = ws.retrieveDossier('1111111111111111', '3333333333333333')
        self.assertTrue(dossier.content == 'Hello World')
        dossier = ws.retrieveDossier('1111111111111111', '2222222222222222')
        self.assertFalse(dossier)

    def test_change_access_hash_fails_with_wrong_old_access_hash(self):
        ws = WalletService()
        ws.fileDossier('1111111111111111', '2222222222222222', 'Hello World')
        thrown = False
        try:
            ws.changeAccessHash(owner_hash='1111111111111111', old_access_hash='4444444444444444', new_access_hash='3333333333333333')
        except:
            thrown = True
        self.assertTrue(thrown)        
        dossier = ws.retrieveDossier('1111111111111111', '3333333333333333')
        self.assertFalse(dossier)
        dossier = ws.retrieveDossier('1111111111111111', '2222222222222222')
        self.assertTrue(dossier.content == 'Hello World')

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from onlinepasswordsafe import main
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
        from onlinepasswordsafe.models import DBSession
        DBSession.remove()

    def test_save(self):
        post_params = {'owner_hash': '1111111111111111', 'access_hash': '2222222222222222', 'content': 'fdjs9884jhf98'}
        res = self.testapp.post('/save.json', post_params, status=200)
        self.assertTrue(res.json['success'])

    def test_load(self):
        post_params = {'owner_hash': '1111111111111111', 'access_hash': '2222222222222222', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/save.json', post_params, status=200)
        res = self.testapp.get('/load.json?owner_hash=1111111111111111&access_hash=2222222222222222', status=200) 
        self.assertTrue(b'fdjs9884jhf98' in res.body)

    def test_load_wrongaccesshash(self):
        post_params = {'owner_hash': '1111111111111111', 'access_hash': '2222222222222222', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/save.json', post_params, status=200)
        res = self.testapp.get('/load.json?owner_hash=1111111111111111&access_hash=3333333333333333', status=401) 
        self.assertFalse(b'fdjs9884jhf98' in res.body)
        self.assertTrue(b'Not allowed' in res.body)

    def test_load_failsIfOwnerHashIsTooShort(self):
        res = self.testapp.get('/load.json?owner_hash=111111111111111&access_hash=3333333333333333', status=400) 
        self.assertTrue(b'Bad request' in res.body)

    def test_load_failsIfAccessHashIsTooShort(self):
        res = self.testapp.get('/load.json?owner_hash=1111111111111111&access_hash=333333333333333', status=400) 
        self.assertTrue(b'Bad request' in res.body)

    def test_change_access_hash(self):
        post_params = {'owner_hash': '1111111111111111', 'access_hash': '2222222222222222', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/save.json', post_params, status=200)
        res = self.testapp.get('/changeAccessHash.json?owner_hash=1111111111111111&old_access_hash=2222222222222222&new_access_hash=333333333333333', status=200) 
        self.assertTrue(res.json['success'])

    def test_change_access_hash_fails(self):
        post_params = {'owner_hash': '1111111111111111', 'access_hash': '2222222222222222', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/save.json', post_params, status=200)
        res = self.testapp.get('/changeAccessHash.json?owner_hash=1111111111111111&old_access_hash=4444444444444444&new_access_hash=333333333333333', status=401) 
        self.assertFalse(res.json['success'])

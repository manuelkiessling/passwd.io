import unittest
import transaction

from pyramid import testing
from webtest import TestApp

from .domain import DossierRepository, Dossier
from .application import WalletService, TokenService

def setUpUnitTests():
    from sqlalchemy import create_engine
    from .models import DBSession, Base
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession

def tearDownUnitTests():
    from onlinepasswordsafe.models import DBSession
    DBSession.remove()

class DomainUnitTests(unittest.TestCase):
    def setUp(self):
        setUpUnitTests()

    def tearDown(self):
        tearDownUnitTests()

    def test_cantStoreInvalidDossier(self):
        pass

    def test_dossierRepository_exists(self):
        dossier = Dossier(owner_hash='1111111111111111111111111111111111111111111111111111111111111111', access_hash='2222222222222222222222222222222222222222222222222222222222222222', content='Hello World')
        repo = DossierRepository()
        repo.store(dossier)
        exists = repo.exists('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222')
        self.assertTrue(exists)

    def test_subsequent_storing_overwrites_existing_dossier(self):
        dossier = Dossier(owner_hash='1111111111111111111111111111111111111111111111111111111111111111', access_hash='2222222222222222222222222222222222222222222222222222222222222222', content='Hello World')
        id = dossier.id
        repo = DossierRepository()
        repo.store(dossier)
        dossier = repo.find(owner_hash='1111111111111111111111111111111111111111111111111111111111111111', access_hash='2222222222222222222222222222222222222222222222222222222222222222')
        self.assertTrue(dossier.id == id)
        self.assertTrue(dossier.content == 'Hello World')
        dossier = Dossier(id=id, owner_hash='1111111111111111111111111111111111111111111111111111111111111111', access_hash='2222222222222222222222222222222222222222222222222222222222222222', content='foo')
        repo = DossierRepository()
        repo.store(dossier)
        dossier = repo.find(owner_hash='1111111111111111111111111111111111111111111111111111111111111111', access_hash='2222222222222222222222222222222222222222222222222222222222222222')
        self.assertTrue(dossier.id == id)
        self.assertTrue(dossier.content == 'foo')

    def test_cant_store_dossier_with_existing_owner_hash_under_different_id(self):
        repo = DossierRepository()
        dossier = Dossier(owner_hash='1111111111111111111111111111111111111111111111111111111111111111', access_hash='2222222222222222222222222222222222222222222222222222222222222222', content='Hello World')
        repo.store(dossier)
        dossier = Dossier(owner_hash='1111111111111111111111111111111111111111111111111111111111111111', access_hash='2222222222222222222222222222222222222222222222222222222222222222', content='Hello World')
        try:
            repo.store(dossier)
        except:
            thrown = True
        self.assertTrue(thrown)

    def test_cant_store_dossier_with_invalid_hashes(self):
        repo = DossierRepository()
        dossier = Dossier(owner_hash='1111111111111111111111111111111111111111111111111111111111111111', access_hash='2222222222222222222222222222222222222222222222222222222222222222', content='Hello World')
        dossier.owner_hash = 'x111111111111111111111111111111111111111111111111111111111111111'
        thrown = False
        try:
            repo.store(dossier)
        except:
            thrown = True
        self.assertTrue(thrown)
        dossier.owner_hash = '1111111111111111111111111111111111111111111111111111111111111111'
        dossier.access_hash = 'x222222222222222222222222222222222222222222222222222222222222222'
        thrown = False
        try:
            repo.store(dossier)
        except:
            thrown = True
        self.assertTrue(thrown)

    def test_can_store_dossier_with_existing_owner_hash_with_different_access_hash(self):
        repo = DossierRepository()
        dossier = Dossier(owner_hash='1111111111111111111111111111111111111111111111111111111111111111', access_hash='3333333333333333333333333333333333333333333333333333333333333333', content='Hello World')
        id = dossier.id
        repo.store(dossier)
        dossier.access_hash = '2222222222222222222222222222222222222222222222222222222222222222'
        repo.store(dossier)
        dossier = repo.find(owner_hash='1111111111111111111111111111111111111111111111111111111111111111', access_hash='2222222222222222222222222222222222222222222222222222222222222222')
        self.assertTrue(dossier.id == id)

    def test_dossierRepository_exists_not(self):
        repo = DossierRepository()
        exists = repo.exists('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222')
        self.assertFalse(exists)

class WalletServiceUnitTests(unittest.TestCase):
    def setUp(self):
        setUpUnitTests()

    def tearDown(self):
        tearDownUnitTests()

    def test_filing_a_dossier_with_an_existing_owner_access_hash_by_overwriting(self):
        ws = WalletService()
        ws.fileDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222', 'Hello World')
        ws.fileDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222', 'foo')
        dossier = ws.retrieveDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222')
        self.assertTrue(dossier.content == 'foo')

    def test_filing_a_dossier_with_an_existing_owner_access_hash_by_overwriting(self):
        ws = WalletService()
        ws.fileDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222', 'Hello World')
        ws.fileDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222', 'foo')
        dossier = ws.retrieveDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222')
        self.assertTrue(dossier.content == 'foo')

    def test_file_doesnt_change_access_hash(self):
        ws = WalletService()
        ws.fileDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222', 'Hello World')
        thrown = False
        try:
            ws.fileDossier('1111111111111111111111111111111111111111111111111111111111111111', '3333333333333333333333333333333333333333333333333333333333333333', 'Hello World')
        except:
            thrown = True
        self.assertTrue(thrown)
        dossier = ws.retrieveDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222')
        self.assertTrue(dossier.content == 'Hello World')
        dossier = ws.retrieveDossier('1111111111111111111111111111111111111111111111111111111111111111', '3333333333333333333333333333333333333333333333333333333333333333')
        self.assertFalse(dossier)

    def test_change_access_hash(self):
        ws = WalletService()
        ws.fileDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222', 'Hello World')
        ws.changeAccessHash(owner_hash='1111111111111111111111111111111111111111111111111111111111111111', old_access_hash='2222222222222222222222222222222222222222222222222222222222222222', new_access_hash='3333333333333333333333333333333333333333333333333333333333333333')
        dossier = ws.retrieveDossier('1111111111111111111111111111111111111111111111111111111111111111', '3333333333333333333333333333333333333333333333333333333333333333')
        self.assertTrue(dossier.content == 'Hello World')
        dossier = ws.retrieveDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222')
        self.assertFalse(dossier)

    def test_change_access_hash_fails_with_wrong_old_access_hash(self):
        ws = WalletService()
        ws.fileDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222', 'Hello World')
        thrown = False
        try:
            ws.changeAccessHash(owner_hash='1111111111111111111111111111111111111111111111111111111111111111', old_access_hash='4444444444444444444444444444444444444444444444444444444444444444', new_access_hash='3333333333333333333333333333333333333333333333333333333333333333')
        except:
            thrown = True
        self.assertTrue(thrown)        
        dossier = ws.retrieveDossier('1111111111111111111111111111111111111111111111111111111111111111', '3333333333333333333333333333333333333333333333333333333333333333')
        self.assertFalse(dossier)
        dossier = ws.retrieveDossier('1111111111111111111111111111111111111111111111111111111111111111', '2222222222222222222222222222222222222222222222222222222222222222')
        self.assertTrue(dossier.content == 'Hello World')

class TokenServiceUnittests(unittest.TestCase):
    def setUp(self):
        setUpUnitTests()

    def tearDown(self):
        tearDownUnitTests()

    def test_activation(self):
        ts = TokenService()
        token = ts.getToken()
        ts.activate(token)
        self.assertTrue(ts.isActivated(token))

    def test_missing_activation(self):
        ts = TokenService()
        token = ts.getToken()
        self.assertFalse(ts.isActivated(token))

    def test_update_verification_code(self):
        ts = TokenService()
        token = ts.getToken()
        verificationCode = ts.getVerificationCode(token)
        ts.updateVerificationCode(token)
        self.assertTrue(verificationCode != ts.getVerificationCode(token))

    def test_update_verification_code_fails_for_nonexistant_token(self):
        ts = TokenService()
        thrown = False
        try:
            ts.updateVerificationCode('bar')
        except:
            thrown = True
        self.assertTrue(thrown)

    def test_cant_activate_nonexisting_token(self):
        ts = TokenService()
        thrown = False
        try:
            ts.activate(token)
        except:
            thrown = True
        self.assertTrue(thrown)
    
    def test_get_verification_code(self):
        ts = TokenService()
        token = ts.getToken()
        self.assertTrue(ts.getVerificationCode(token))

    def test_get_verification_code_for_nonexistant_token(self):
        ts = TokenService()
        thrown = False
        try:
            ts.getVerificationCode('foo')
        except:
            thrown = True
        self.assertTrue(thrown)

class ThrottleServiceUnittest(unittest.TestCase):
    def setUp(self):
        setUpUnitTests()

    def tearDown(self):
        tearDownUnitTests()

    def test(self):
        return
        ts = ThrottleService(item='foo', max_events_per_second=1000000, max_events=5)
        thrown = False
        try:
          for i in range(10):
            ts.addEvent()
        except:
          thrown = True
        self.assertTrue(thrown)
        self.assertTrue(i == 4)

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
        t = getToken()
        post_params = {'owner_hash': '1111111111111111111111111111111111111111111111111111111111111111', 'access_hash': '2222222222222222222222222222222222222222222222222222222222222222', 'content': 'fdjs9884jhf98'}
        res = self.testapp.post('/api/dossier/save.json?token=' + t, post_params, status=200)
        self.assertTrue(res.json['success'])

    def test_load(self):
        t = getToken()
        post_params = {'owner_hash': '1111111111111111111111111111111111111111111111111111111111111111', 'access_hash': '2222222222222222222222222222222222222222222222222222222222222222', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json?token=' + t, post_params, status=200)
        res = self.testapp.get('/api/dossier/load.json?token=' + t +'&owner_hash=1111111111111111111111111111111111111111111111111111111111111111&access_hash=2222222222222222222222222222222222222222222222222222222222222222', status=200) 
        self.assertTrue(res.body == '{"content": "fdjs9884jhf98"}')

    def test_load_wrongaccesshash(self):
        t = getToken()
        post_params = {'owner_hash': '1111111111111111111111111111111111111111111111111111111111111111', 'access_hash': '2222222222222222222222222222222222222222222222222222222222222222', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json?token=' + t, post_params, status=200)
        res = self.testapp.get('/api/dossier/load.json?token=' + t + '&owner_hash=1111111111111111111111111111111111111111111111111111111111111111&access_hash=3333333333333333333333333333333333333333333333333333333333333333', status=400) 
        self.assertFalse(b'fdjs9884jhf98' in res.body)
        self.assertTrue(b'Not allowed' in res.body)

    def test_change_access_hash(self):
        t = getToken()
        post_params = {'owner_hash': '1111111111111111111111111111111111111111111111111111111111111111', 'access_hash': '2222222222222222222222222222222222222222222222222222222222222222', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json?token=' + t, post_params, status=200)
        post_params = {'owner_hash': '1111111111111111111111111111111111111111111111111111111111111111', 'old_access_hash': '2222222222222222222222222222222222222222222222222222222222222222', 'new_access_hash': '3333333333333333333333333333333333333333333333333333333333333333'}
        res = self.testapp.post('/api/dossier/change_access_hash.json?token=' + t, post_params, status=200) 
        self.assertTrue(res.json['success'])

    def test_change_access_hash_fails(self):
        t = getToken()
        post_params = {'owner_hash': '1111111111111111111111111111111111111111111111111111111111111111', 'access_hash': '2222222222222222222222222222222222222222222222222222222222222222', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json?token=' + t, post_params, status=200)
        post_params = {'owner_hash': '1111111111111111111111111111111111111111111111111111111111111111', 'old_access_hash': '4444444444444444444444444444444444444444444444444444444444444444', 'new_access_hash': '3333333333333333333333333333333333333333333333333333333333333333'}
        res = self.testapp.post('/api/dossier/change_access_hash.json?token=' + t, post_params, status=400) 
        self.assertFalse(res.json['success'])

    def test_get_and_activate_token(self):
        res = self.testapp.get('/api/token/get.json', status=200)
        token = res.json['token']
        ts = TokenService()
        verificationCode = ts.getVerificationCode(token)
        post_params = {'token': token, 'verification_code': verificationCode}
        res = self.testapp.post('/api/token/activate.json', post_params, status=200)
        self.assertTrue(res.json['success'])

    def test_get_token_fails_with_wrong_code(self):
        res = self.testapp.get('/api/token/get.json', status=200)
        token = res.json['token']
        post_params = {'token': token, 'verification_code': 'invalid'}
        res = self.testapp.post('/api/token/activate.json', post_params, status=400)
        self.assertFalse(res.json['success'])

    def test_get_captcha(self):
        res = self.testapp.get('/api/token/get.json', status=200)
        token = res.json['token']
        res = self.testapp.get('/getCaptcha.png?token=' + token, status=200)

    def test_subsequent_failed_activation_updates_verification_code(self):
        res = self.testapp.get('/api/token/get.json', status=200)
        token = res.json['token']
        ts = TokenService()
        verificationCode = ts.getVerificationCode(token)
        post_params = {'token': token, 'verification_code': 'foo'}
        res = self.testapp.post('/api/token/activate.json', post_params, status=400)
        self.assertTrue(verificationCode != ts.getVerificationCode(token))

    def test_get_captcha_fails(self):
        res = self.testapp.get('/getCaptcha.png?token=invalid', status=400)

    def test_api_calls_fail_with_wrong_token(self):
        t = getToken()
        post_params = {'owner_hash': '1111111111111111111111111111111111111111111111111111111111111111', 'access_hash': '2222222222222222222222222222222222222222222222222222222222222222', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json?token=' + t, post_params, status=200)
        self.testapp.post('/api/dossier/save.json?token=invalid', post_params, status=403)
        self.testapp.post('/api/dossier/save.json', post_params, status=403)
        self.testapp.get('/api/dossier/load.json?token=' + t + '&owner_hash=1111111111111111111111111111111111111111111111111111111111111111&access_hash=2222222222222222222222222222222222222222222222222222222222222222', status=200)
        self.testapp.get('/api/dossier/load.json?token=invalid&owner_hash=1111111111111111111111111111111111111111111111111111111111111111&access_hash=2222222222222222222222222222222222222222222222222222222222222222', status=403)
        self.testapp.get('/api/dossier/load.json?owner_hash=1111111111111111111111111111111111111111111111111111111111111111&access_hash=2222222222222222222222222222222222222222222222222222222222222222', status=403)
        self.testapp.get('/api/dossier/change_access_hash.json?token=' + t + '&owner_hash=1111111111111111111111111111111111111111111111111111111111111111&new_access_hash=3333333333333333333333333333333333333333333333333333333333333333&old_access_hash=2222222222222222222222222222222222222222222222222222222222222222', status=200)
        self.testapp.get('/api/dossier/change_access_hash.json?token=invalid&owner_hash=1111111111111111111111111111111111111111111111111111111111111111&new_access_hash=4444444444444444444444444444444444444444444444444444444444444444&old_access_hash=3333333333333333333333333333333333333333333333333333333333333333', status=403)
        self.testapp.get('/api/dossier/change_access_hash.json?owner_hash=1111111111111111111111111111111111111111111111111111111111111111&new_access_hash=4444444444444444444444444444444444444444444444444444444444444444&old_access_hash=3333333333333333333333333333333333333333333333333333333333333333', status=403)

    def test_api_calls_fail_with_syntactically_invalid_parameters(self):
        t = getToken()
        correct_post_params = {'owner_hash': 'cb7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611', 'access_hash': '54ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json?token=' + t, correct_post_params, status=200)
        self.testapp.get('/api/dossier/load.json?token=' + t + '&owner_hash=cb7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611&access_hash=54ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39', status=200)
        self.testapp.get('/api/dossier/change_access_hash.json?token=' + t + '&owner_hash=cb7c862eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611&new_access_hash=3333333333333333333333333333333333333333333333333333333333333333&old_access_hash=54ebdc364af430e55bf2b1cd8bbddcdf331e333bcc50d382dd590f3afd2bcb39', status=200)
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
            res = self.testapp.post('/api/dossier/save.json?token=' + t, params, status=400)
            self.assertTrue(b'parameter syntax error' in res.body)
            res = self.testapp.get('/api/dossier/load.json?token=' + t + '&owner_hash=' + params['owner_hash']  + '&access_hash=' + params['access_hash'], status=400)
            self.assertTrue(b'parameter syntax error' in res.body)
            res = self.testapp.get('/api/dossier/change_access_hash.json?token=' + t + '&owner_hash=' + params['owner_hash']  + '&old_access_hash=' + params['access_hash'] + '&new_access_hash=2222222222222222222222222222222222222222222222222222222222222222', status=400)
            self.assertTrue(b'parameter syntax error' in res.body)
        invalid_new_access_hashes = [
            '_b7c962eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611',
            'b7c962eb5400a13e01844a4f4f176072755085894bcd9b098185c5a12613611',
            'cb7c962eb5400a13e01844a4f4f176072755085894bcd9b098185c5a126136112',
            'cb7c962eb5400a13e01844a4*4f176072755085894bcd9b098185c5a12613611',
        ]
        post_params = {'owner_hash': '1111111111111111111111111111111111111111111111111111111111111111', 'access_hash': '2222222222222222222222222222222222222222222222222222222222222222', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/api/dossier/save.json?token=' + t, post_params, status=200)
        for hash in invalid_new_access_hashes:
            res = self.testapp.get('/api/dossier/change_access_hash.json?token=' + t + '&owner_hash=1111111111111111111111111111111111111111111111111111111111111111&new_access_hash=' + hash + '&old_access_hash=2222222222222222222222222222222222222222222222222222222222222222', status=400)
            self.assertTrue(b'parameter syntax error' in res.body)

def getToken():
    ts = TokenService()
    t = ts.getToken()
    ts.activate(t)
    return t


import unittest
import transaction

from pyramid import testing
from webtest import TestApp

from .domain import DossierRepository, Dossier

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
        repo = DossierRepository()
        dossier = Dossier('1111111111111111', '2222222222222222', 'Hello World')
        repo.store(dossier)
        exists = repo.exists('1111111111111111', '2222222222222222')
        self.assertTrue(exists)

    def test_dossierRepository_exists_not(self):
        from .domain import DossierRepository
        repo = DossierRepository()
        exists = repo.exists('1111111111111111', '2222222222222222')
        self.assertFalse(exists)

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
        self.testapp.post('/save', post_params, status=200)
        res = self.testapp.get('/load?owner_hash=1111111111111111&access_hash=2222222222222222', status=200) 
        self.assertTrue(b'fdjs9884jhf98' in res.body)

    def test_load_wrongaccesshash(self):
        post_params = {'owner_hash': '1111111111111111', 'access_hash': '2222222222222222', 'content': 'fdjs9884jhf98'}
        self.testapp.post('/save', post_params, status=200)
        res = self.testapp.get('/load?owner_hash=1111111111111111&access_hash=3333333333333333', status=401) 
        self.assertFalse(b'fdjs9884jhf98' in res.body)
        self.assertTrue(b'Access denied.' in res.body)

    def test_load_failsIfOwnerHashIsTooShort(self):
        res = self.testapp.get('/load?owner_hash=111111111111111&access_hash=3333333333333333', status=400) 
        self.assertTrue(b'owner_hash is too short' in res.body)

    def test_load_failsIfAccessHashIsTooShort(self):
        res = self.testapp.get('/load?owner_hash=1111111111111111&access_hash=333333333333333', status=400) 
        self.assertTrue(b'access_hash is too short' in res.body)

    def test_create(self):
        res = self.testapp.get('/editor', status=200)
        html = res.html
        print html
        #self.assertTrue(b'')

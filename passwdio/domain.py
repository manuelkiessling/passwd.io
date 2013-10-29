from .models import DBSession, File
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import exists
import transaction
import re, uuid

class Dossier(object):
    def __init__(self, owner_hash, access_hash, id=None, content=None):
        dv = DossierValidation()
        dv.validateOwnerHash(owner_hash)
        dv.validateAccessHash(access_hash)

        self.owner_hash = owner_hash
        self.access_hash = access_hash

        if id == None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id

        if content == None:
            self.content = ''
        else:
            self.content = content

class DossierRepository(object):
    def store(self, dossier):
        dv = DossierValidation()
        dv.validateOwnerHash(dossier.owner_hash)
        dv.validateAccessHash(dossier.access_hash)
        existing_dossier = self._findByOwnerHash(dossier.owner_hash)
        if existing_dossier:
            if existing_dossier.id != dossier.id:
                raise Exception('can\'t store dossier if id differs')
        file = File()
        file.id = dossier.id
        file.owner_hash = dossier.owner_hash
        file.access_hash = dossier.access_hash
        file.content = dossier.content
        DBSession.merge(file)
        transaction.commit()

    def find(self, owner_hash, access_hash):
        dv = DossierValidation()
        dv.validateOwnerHash(owner_hash)
        dv.validateAccessHash(access_hash)
        try:
            dossierData = DBSession.query(File).filter(File.owner_hash==owner_hash, File.access_hash==access_hash).first()
            if dossierData:
                dossier = Dossier(id=dossierData.id, owner_hash=dossierData.owner_hash, access_hash=dossierData.access_hash, content=dossierData.content)
                return dossier
            else:
                return False
        except DBAPIError:
            raise

    def _findByOwnerHash(self, owner_hash):
        dv = DossierValidation()
        dv.validateOwnerHash(owner_hash)
        try:
            dossierData = DBSession.query(File).filter(File.owner_hash==owner_hash).first()
            if dossierData:
                dossier = Dossier(id=dossierData.id, owner_hash=dossierData.owner_hash, access_hash=dossierData.access_hash, content=dossierData.content)
                return dossier
            else:
                return False
        except DBAPIError:
            raise

    def exists(self, owner_hash, access_hash):
        dv = DossierValidation()
        dv.validateOwnerHash(owner_hash)
        dv.validateAccessHash(access_hash)
        try:
            return bool(self.find(owner_hash, access_hash))
        except DBAPIError:
            raise

class DossierValidation(object):
    def validateOwnerHash(self, owner_hash):
        if not bool(re.findall(r'^([a-fA-F0-9]{64})$', owner_hash)):
            raise ValueError('owner_hash is too short')

    def validateAccessHash(self, access_hash):
        if not bool(re.findall(r'^([a-fA-F0-9]{64})$', access_hash)):
            raise ValueError('access_hash is too short')


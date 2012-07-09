from .models import DBSession, File
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import exists

class Dossier(object):
    id = None
    owner_hash = None
    access_hash = None 
    content = None

class DossierRepository(object):
    def store(self, dossier):
        file = File()
        file.id = dossier.id
        file.owner_hash = dossier.owner_hash
        file.access_hash = dossier.access_hash
        file.content = dossier.content
        DBSession.add(file)

    def find(self, owner_hash, access_hash):
        dv = DossierValidation()
        dv.validateOwnerHash(owner_hash)
        dv.validateAccessHash(access_hash)
        try:
            dossierData = DBSession.query(File).filter(File.owner_hash==owner_hash, File.access_hash==access_hash).first()
            if dossierData:
                dossier = Dossier()
                dossier.id = dossierData.id
                dossier.owner_hash = dossierData.owner_hash
                dossier.access_hash = dossierData.access_hash
                dossier.content = dossierData.content
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
    def hashIsLongEnough(self, hash):
        return len(hash) >= 16

    def validateOwnerHash(self, owner_hash):
        if not self.hashIsLongEnough(owner_hash):
            raise Exception("owner_hash is too short")

    def validateAccessHash(self, access_hash):
        if not self.hashIsLongEnough(access_hash):
            raise Exception("access_hash is too short")


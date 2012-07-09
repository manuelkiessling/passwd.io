from .models import DBSession, File
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import exists
import uuid

class Dossier(object):
    def __init__(self, owner_hash, access_hash, content, id=None):
        dv = DossierValidation()
        dv.validateOwnerHash(owner_hash)
        dv.validateAccessHash(access_hash)
        if not id:
            self.id = str(uuid.uuid4())
        self.owner_hash = owner_hash
        self.access_hash = access_hash
        self.content = content
   
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
                dossier = Dossier(dossierData.owner_hash, dossierData.access_hash, dossierData.content, dossierData.id)
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


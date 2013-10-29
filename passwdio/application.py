import uuid
from .domain import Dossier, DossierRepository
from .models import DBSession

class WalletService(object):
    def fileDossier(self, owner_hash, access_hash, content):
        dossier = self.retrieveDossier(owner_hash, access_hash)
        if dossier:
            dossier.content = content
        else:
            dossier = Dossier(owner_hash=owner_hash, access_hash=access_hash, content=content)        
        repo = DossierRepository()
        repo.store(dossier)
        return True

    def retrieveDossier(self, owner_hash, access_hash):
        repo = DossierRepository()
        return repo.find(owner_hash, access_hash)

    def canAccessDossier(self, owner_hash, access_hash):
        repo = DossierRepository()
        return repo.exists(owner_hash, access_hash)

    def changeAccessHash(self, owner_hash, old_access_hash, new_access_hash):
        dossier = self.retrieveDossier(owner_hash, old_access_hash)
        if not dossier:
            raise Exception('can\'t change access_hash, access denied')
        dossier.access_hash = new_access_hash
        repo = DossierRepository()
        repo.store(dossier)
        return True


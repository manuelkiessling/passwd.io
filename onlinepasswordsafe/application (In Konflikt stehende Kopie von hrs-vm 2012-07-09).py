from .domain import Dossier, DossierRepository

class WalletService(object):
    def fileDossier(self, owner_hash, access_hash, content):
        dossier = self.retrieveDossier(owner_hash, access_hash)
        if dossier:
            dossier.content = content
        else:
            dossier = Dossier(owner_hash, access_hash, content)
        repo = DossierRepository()
        repo.store(dossier)
        return True

    def retrieveDossier(self, owner_hash, access_hash):
        repo = DossierRepository()
        return repo.find(owner_hash, access_hash)

    def canAccessDossier(self, owner_hash, access_hash):
        repo = DossierRepository()
        return repo.exists(owner_hash, access_hash)

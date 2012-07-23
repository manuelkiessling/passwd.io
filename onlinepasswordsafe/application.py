import uuid, sha
from .domain import Dossier, DossierRepository
from .models import DBSession, Token

class ThrottleService(object):
    def __init__(self, item, max_events, max_events_per_second, expires=86400):
        self.identifier = sha.new(item + str(max_events) + str(max_events_per_second) + str(expires)).hexdigest()
        tw = DBSession.query(ThrottleWatch).filter(ThrottleWatch.identifier==self.identifier).first()
        if not tw:
          tw = ThrottleWatch()
          tw.identifier = self.identifier
          tw.max_events = max_events
          tw.max_events_per_second = max_events_per_second
          tw.expires = expires
          DBSession.merge(tw)

    def addEvent(self):
        pass
#        te = ThrottleEvent()
#        te.identifier = self.identifier
#        te.


class TokenService(object):
    def getVerificationCode(self, token):
        tokenData = DBSession.query(Token).filter(Token.token==token).first()
        return tokenData.verification_code

    def getToken(self):
        token = Token()
        token.token = sha.new(str(uuid.uuid4()) + '#+*dehju7/((3652fvcXXYdgzu"1238765ggxxxpP').hexdigest()
        token.verification_code = sha.new(str(uuid.uuid4()) + 'jdiUHB()&%dhehdu???opc6GGDHskj').hexdigest()[0:6]
        DBSession.merge(token)
        return token.token

    def activate(self, token):
        tokenData = DBSession.query(Token).filter(Token.token==token).first()
        token = Token()
        token.token = tokenData.token
        token.verification_code = tokenData.verification_code
        token.activated = True
        DBSession.merge(token)

    def isActivated(self, token):
        tokenData = DBSession.query(Token).filter(Token.token==token).first()
        return tokenData.activated

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

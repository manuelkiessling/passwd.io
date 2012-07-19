from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .application import WalletService, TokenService

def isInvalidToken(request):
    ts = TokenService()
    try:
        return not ts.isActivated(request.params['token'])
    except:
        return True

def respondWithAccessError(request):
    request.response.status = "403 Forbidden: Missing or invalid token"
    return {}

@view_config(route_name='save.json', renderer="json", xhr=False)
def save(request):
    if isInvalidToken(request):
        return respondWithAccessError(request)
    walletService = WalletService()
    success = walletService.fileDossier(request.params['owner_hash'], request.params['access_hash'], request.params['content'])
    if success:
        request.response.status_int = 200
    else:
        request.response.status_int = 500
    return {'success': success}

@view_config(route_name='load.json', renderer="json", xhr=False)
def load(request):
    if isInvalidToken(request):
        return respondWithAccessError(request)
    walletService = WalletService()
    try:
        allowed = walletService.canAccessDossier(request.params['owner_hash'], request.params['access_hash'])
        if not allowed:
            request.response.status_int = 400
            return {'status': 'Not allowed to request this dossier'}
    except Exception as e:
            request.response.status_int = 400
            return {'status': 'Bad request'}
    dossier = walletService.retrieveDossier(request.params['owner_hash'], request.params['access_hash'])
    if dossier:
        request.response.status_int = 200
        return { 'owner_hash': dossier.owner_hash,
                 'access_hash': dossier.access_hash,
                 'content': dossier.content }
    else:
        request.response.status_int = 500
        return {'status': 'error'}

@view_config(route_name='changeAccessHash.json', renderer="json", xhr=False)
def changeAccessHash(request):
    if isInvalidToken(request):
        return respondWithAccessError(request)
    walletService = WalletService()
    request.response.status_int = 200
    success = True
    try:
        walletService.changeAccessHash(owner_hash=request.params['owner_hash'], old_access_hash=request.params['old_access_hash'], new_access_hash=request.params['new_access_hash'])
    except Exception as e:
        request.response.status_int = 400
        success = False
    return {'success': success}

@view_config(route_name='getToken.json', renderer="json", xhr=False)
def getToken(request):
    tokenService = TokenService()
    token = tokenService.getToken()
    if token:
        request.response.status_int = 200
        return {'token': token}
    else:
        request.response.status_int = 500
        return False

@view_config(route_name='activateToken.json', renderer="json", xhr=False)
def activateToken(request):
    tokenService = TokenService()
    token = request.params['token']
    try:
        verificationCode = tokenService.getVerificationCode(token)
    except:
        request.response.status_int = 400
        return {'success': False}
    if verificationCode == request.params['verification_code']:
        try:
            tokenService.activate(token)
            return {'success': True}
        except:
            request.response.status_int = 400
            return {'success': False}
    else:
        request.response.status_int = 400
        return {'success': False}

@view_config(route_name='getCaptcha.png')
def getCaptcha(request):
    tokenService = TokenService()
    try:
        verificationCode = tokenService.getVerificationCode(request.params['token'])
        from skimpyGimpy import skimpyAPI
        import os
        imageData = skimpyAPI.Png(verificationCode,
                                  color='aaaaaa',
                                  fontpath=os.getcwd() + '/fonts/10x20.bdf',
                                  speckle=1.8,
                                  scale=2.0).data()
        return Response(body=imageData, content_type='image/png')
    except:
        request.response.status_int = 400
        return Response(body='error', content_type='text/plain', status='400')

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_OnlinePasswordSafe_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""


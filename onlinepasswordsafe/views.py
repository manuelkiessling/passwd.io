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
    request.response.status = '403 Forbidden: Missing or invalid token'
    return {}

@view_config(route_name='/api/dossier/save', renderer='json', xhr=False)
def save(request):
    if isInvalidToken(request):
        return respondWithAccessError(request)
    walletService = WalletService()
    try:
        success = walletService.fileDossier(request.params['owner_hash'], request.params['access_hash'], request.params['content'])
    except ValueError:
        request.response.status_int = 400
        return {'success': False, 'error': 'parameter syntax error'}
    if not success:
        request.response.status_int = 500
    return {'success': success}

@view_config(route_name='/api/dossier/load', renderer='json', xhr=False)
def load(request):
    if isInvalidToken(request):
        return respondWithAccessError(request)
    walletService = WalletService()
    try:
        allowed = walletService.canAccessDossier(request.params['owner_hash'], request.params['access_hash'])
        if not allowed:
            request.response.status_int = 400
            return {'status': 'Not allowed to request this dossier'}
    except ValueError:
        request.response.status_int = 400
        return {'success': False, 'error': 'parameter syntax error'}
    except Exception as e:
            request.response.status_int = 500
            return ''
    dossier = walletService.retrieveDossier(request.params['owner_hash'], request.params['access_hash'])
    if dossier:
        return { 'content': dossier.content }
    else:
        request.response.status_int = 500
        return {'status': 'error'}

@view_config(route_name='/api/dossier/change_access_hash', renderer='json', xhr=False)
def changeAccessHash(request):
    if isInvalidToken(request):
        return respondWithAccessError(request)
    walletService = WalletService()
    success = True
    try:
        walletService.changeAccessHash(owner_hash=request.params['owner_hash'], old_access_hash=request.params['old_access_hash'], new_access_hash=request.params['new_access_hash'])
    except ValueError:
        request.response.status_int = 400
        return {'success': False, 'error': 'parameter syntax error'}
    except Exception as e:
        request.response.status_int = 400
        success = False
    return {'success': success}

@view_config(route_name='/api/token/get', renderer='json', xhr=False)
def getToken(request):
    request.response.cache_expires(seconds=0)
    tokenService = TokenService()
    token = tokenService.getToken()
    if token:
        return {'token': token}
    else:
        request.response.status_int = 500
        return False

@view_config(route_name='/api/token/activate', renderer='json', xhr=False)
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
        tokenService.updateVerificationCode(token)
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
                                  color='bbbbbb',
                                  fontpath=os.getcwd() + '/fonts/10x20.bdf',
                                  speckle=1.8,
                                  scale=2.0).data()
        return Response(body=imageData, content_type='image/png')
    except:
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


import re
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .application import WalletService, TokenService

def isInvalidToken(request):
    ts = TokenService()
    try:
        return not (ts.isActivated(request.params['token']) and ts.bound(request.params['token'], request.params['owner_hash']))
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
    token = request.params['token']
    tokenService = TokenService()
    try:
      if not bool(re.findall(r'^([a-f0-9]{40})$', token)):
          request.response.status_int = 400
          return {'success': False, 'error': 'parameter syntax error'}
      if not bool(re.findall(r'^([a-fA-F0-9]{6})$', request.params['verification_code'])):
          tokenService.updateVerificationCode(token)
          request.response.status_int = 400
          return {'success': False, 'error': 'parameter syntax error'}
      if not bool(re.findall(r'^([a-f0-9]{64})$', request.params['bind_to'])):
          tokenService.updateVerificationCode(token)
          request.response.status_int = 400
          return {'success': False, 'error': 'parameter syntax error'}
    except:
          request.response.status_int = 400
          return {'success': False, 'error': 'parameter syntax error'}
    try:
        verificationCode = tokenService.getVerificationCode(token)
    except:
        request.response.status_int = 400
        return {'success': False}
    if verificationCode == request.params['verification_code'].lower():
        try:
            tokenService.bind(token, request.params['bind_to'])
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
    if not bool(re.findall(r'^([a-f0-9]{40})$', request.params['token'])):
        request.response.status_int = 400
        return Response(body='parameter syntax error', content_type='text/plain', status='400')
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


# New API

@view_config(route_name='/api/sessiontokens', renderer='json', xhr=False)
def createSessiontoken(request):
    request.response.content_type = 'application/vnd.passwd.io+json; version=1.0.0-beta.1'
    tokenService = TokenService()
    token = tokenService.getToken()
    if token:
        return {'sessiontoken': token}
    else:
        request.response.status_int = 500
        return False

@view_config(route_name='/api/sessiontokens/:sessiontoken/captcha')
def getSessiontokenCaptcha(request):
    if not bool(re.findall(r'^([a-f0-9]{40})$', request.matchdict['sessiontoken'])):
        return Response(body='parameter syntax error', content_type='text/plain', status_int=400)
    tokenService = TokenService()
    try:
        verificationCode = tokenService.getVerificationCode(request.matchdict['sessiontoken'])
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

@view_config(route_name='/api/dossiers/:id', renderer='json', xhr=False)
def updateDossier(request):
    fr = FakeRequest()
    fr.params = {'token': request.headers['x-passwdio-sessiontoken'],
                 'owner_hash': request.matchdict['id']}
    if isInvalidToken(fr):
        return respondWithAccessError(request)
    walletService = WalletService()
    try:
        success = walletService.fileDossier(request.matchdict['id'], request.headers['x-passwdio-dossiertoken'], request.params['content'])
    except ValueError:
        request.response.status_int = 400
        return {'success': False, 'error': 'parameter syntax error'}
    if not success:
        request.response.status_int = 500
    return {'success': success}

class FakeRequest(object):
    pass

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


import re
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .application import WalletService

@view_config(route_name='/api/dossier/save', renderer='json', xhr=False)
def save(request):
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

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_PasswdIO_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""


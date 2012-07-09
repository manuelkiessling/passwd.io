from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .application import WalletService

@view_config(route_name='editor', renderer="templates/editor.pt")
def editor(request):
    return {'foo': 'bar'}

@view_config(route_name='save', renderer="string")
@view_config(route_name='save.json', renderer="json", xhr=False)
def save(request):
    walletService = WalletService()
    success = walletService.fileDossier(request.params['owner_hash'], request.params['access_hash'], request.params['content'])
    if success:
        request.response.status_int = 200
    else:
        request.response.status_int = 500
    return {'success': success}

@view_config(route_name='load')
def load(request):
    walletService = WalletService()
    try:
        allowed = walletService.canAccessDossier(request.params['owner_hash'], request.params['access_hash'])
        if not allowed:
            return Response('Access denied.', status_int=401)
    except Exception as e:
            return Response(str(e), status_int=400)
    dossier = walletService.retrieveDossier(request.params['owner_hash'], request.params['access_hash'])
    if dossier:
        return Response(dossier.content)
    else:
        return Response('error', status_int=500)








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


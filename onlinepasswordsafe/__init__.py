from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('/api/dossier/save', '/api/dossier/save.json')
    config.add_route('/api/dossier/load', '/api/dossier/load.json')
    config.add_route('/api/dossier/change_access_hash', '/api/dossier/change_access_hash.json')
    config.add_route('/api/token/get', '/api/token/get.json')
    config.add_route('/api/token/activate', '/api/token/activate.json')
    config.add_route('/api/captcha', '/api/captcha')

    config.add_route('/api/sessiontokens', '/api/sessiontokens')
    config.add_route('/api/sessiontokens/:sessiontoken/captcha', '/api/sessiontokens/{sessiontoken}/captcha')
    config.add_route('/api/dossiers/:id', '/api/dossiers/{id}')

    config.scan()
    return config.make_wsgi_app()


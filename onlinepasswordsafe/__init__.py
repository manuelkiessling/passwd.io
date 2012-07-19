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
    config.add_route('changeAccessHash.json', '/changeAccessHash.json')
    config.add_route('getToken.json', '/getToken.json')
    config.add_route('activateToken.json', '/activateToken.json')
    config.add_route('getCaptcha.png', '/getCaptcha.png')
    config.scan()
    return config.make_wsgi_app()


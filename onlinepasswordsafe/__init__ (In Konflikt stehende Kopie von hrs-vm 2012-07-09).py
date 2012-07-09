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
    config.add_route('editor', '/editor')
    config.add_route('save', '/save')
    config.add_route('save.json', '/save.json')
    config.add_route('load', '/load')
    config.scan()
    return config.make_wsgi_app()


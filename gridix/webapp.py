from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from .api.utils import add_role_principals



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(
        settings=settings,
        authorization_policy=ACLAuthorizationPolicy(),
    )

    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')
    config.add_jinja2_search_path('templates', name='.html')

    config.include('.data.models')
    config.include('.routes')

    # cornice & api configs
    config.route_prefix = 'api/v0'
    config.include('cornice')

    # json web tokens
    config.include('pyramid_jwt')
    config.set_jwt_authentication_policy(callback=add_role_principals)

    config.scan()
    return config.make_wsgi_app()

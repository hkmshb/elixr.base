from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid_jwt import create_jwt_authentication_policy
from pyramid_multiauth import MultiAuthenticationPolicy

from .api.security import api_role_finder
from .security import role_finder



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(
        settings=settings,
        authorization_policy=ACLAuthorizationPolicy()
    )

    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')
    config.add_jinja2_search_path('templates', name='.html')

    config.include('.data.models')
    config.include('.routes')

    # cornice & api configs
    config.route_prefix = 'api/%s' % settings.get('api.version', 'v0')
    config.include('cornice')

    # json web tokens
    config.include('pyramid_jwt')
    set_multi_authentication_policy(config, settings)

    config.scan()
    return config.make_wsgi_app()


def set_multi_authentication_policy(config, settings):
    policy_tkt = AuthTktAuthenticationPolicy(settings['auth.secret_key'], callback=role_finder)
    policy_jwt = create_jwt_authentication_policy(config, callback=api_role_finder)
    policy = MultiAuthenticationPolicy([policy_jwt, policy_tkt])

    ## extraced from pyramid_jwt
    def request_create_token(request, principal, expiration=None, **claims):
        return policy_jwt.create_token(principal, expiration, **claims)

    def request_claims(request):
        return policy_jwt.get_claims(request)

    config.set_authentication_policy(policy)
    config.add_request_method(request_create_token, 'create_jwt_token')
    config.add_request_method(request_claims, 'jwt_claims', reify=True)

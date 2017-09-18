from cornice.resource import resource
from elixr.sax.auth import Authenticator



@resource(name='root', path='/')
class RootResource(object):
    def __init__(self, request):
        self.request = request

    def get(self):
        endpoints = {}
        app_url = self.request.application_url
        cornice_services = self.request.registry.cornice_services

        for path, service in cornice_services.items():
            name = service.name
            if name.startswith('collection'):
                name = name.replace('collection_', '')
                if name.startswith('_'):    # flag for collections to skip
                    continue
                endpoints[name] = "%s/%s" % (app_url, path)
        return endpoints


@resource(name='auth', path='/auth/')
class AuthResource(object):
    def __init__(self, request):
        self.request = request
        self.authr = Authenticator(request.db)

    def post(self):
        username = self.request.json_body.get('username', "")
        password = self.request.json_body.get('password', "")
        user = self.authr(username, password)
        if user != None:
            return {
                'result': 'ok',
                'token': self.request.create_jwt_token(
                    user.id, roles=[r.name for r in user.roles])
            }
        return {'result':'error: invalid username and/or password'}
    
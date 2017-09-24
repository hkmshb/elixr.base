from .security import ACLGridIX


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('import', '/import', factory=ACLGridIX)
    config.add_route('process', '/process/{fn}', factory=ACLGridIX)
    config.add_route('monitor', '/monitor/{fn}')

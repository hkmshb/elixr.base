from pyramid.httpexceptions import HTTPRedirection, HTTPFound
from pyramid.view import notfound_view_config, forbidden_view_config



@notfound_view_config(renderer='404.html')
def notfound_view(request):
    request.response.status = 404
    return {}


@forbidden_view_config()
def forbidden_view(request):
    request.response.status = 403
    return HTTPFound(location=request.application_url + \
                     '/login?next=' + request.url)

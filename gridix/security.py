from pyramid.security import Allow, Authenticated, Everyone


class ACLGridIX(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'edit')
    ]

    def __init__(self, request):
        self.request = request


def role_finder(userid, request):
    return 'user'

from pyramid.security import Allow, Everyone
from elixr.sax.auth import User


class ACLGridIX(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'admin', 'edit')
    ]

    def __init__(self, request):
        self.request = request


def role_finder(userid, request):
    user = request.db.query(User).filter_by(username=userid).first()
    if user is not None:
        return [r.name for r in user.roles]
    return ''

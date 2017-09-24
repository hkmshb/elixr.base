import os
import sys
import transaction

from pyramid.paster import get_appsettings, setup_logging
from pyramid.scripts.common import parse_vars

from elixr.sax.auth import User, Role

from ..data.models import get_engine, get_session_factory, get_tm_session
from ..data.models.base import BASE
from ..data.models.network import Voltage


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    # create tables
    engine = get_engine(settings)
    BASE.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        db = get_tm_session(session_factory, transaction.manager)

        ## make database entries
        # add default user
        user = User(username='manager', is_active=True)
        user.roles.append(Role(name='admin'))
        user.set_password('gridix')
        db.add(user)

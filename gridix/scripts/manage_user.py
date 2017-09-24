import os
import sys
import transaction

from pyramid.paster import get_appsettings, setup_logging
from pyramid.scripts.common import parse_vars

from elixr.sax.auth import Authenticator, User, Role

from ..data.models import get_engine, get_session_factory, get_tm_session


## options
# task=(add|del|change_passwd)
# add task fields: username, role, password, password2
# del task fields: username
# change_passwd fields: username, old_password, password, password2
def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [task=(add|del|change_passwd|list)] '
          '[username=] [role=] [password=] [password2=] [oldpassword=]\n'
          '(example: "%s development.ini task=add username=... role=...'
          ' password=*** password2=***")' % (cmd, cmd))
    sys.exit(1)


def _error(message, args=None):
    message = message if not args else message % args
    print(message)
    sys.exit(1)


def _check_required_options(options, *fields):
    for field in fields:
        if field not in options:
            _error("error: option '%s' is required", field)
        value = options[field]
        if not value or value.strip() == '':
            _error("error: Invalid '%s' provided", field)


def _add_user(db, options):
    _check_required_options(options, 'username', 'password', 'password2')
    username = options['username']
    password = options['password']
    password2 = options['password2']
    if password != password2:
        _error('error: passwords mismatch')

    user = User(username=username, is_active=True)
    user.set_password(password)
    if 'role' in options:
        role = options['role']
        if role and role.strip() != '':
            user.roles.append(Role(name=role))

    # ensure username is not taken
    exists = db.query(User).filter_by(username=username).first()
    if exists is not None:
        _error("error: username '%s' is already taken.", username)
    db.add(user)


def _del_user(db, options):
    _check_required_options(options, 'username')
    username = options['username']
    user = db.query(User).filter_by(username=username).first()
    if user is None:
        _error("error: user '%s' not found" % username)
    db.delete(user)


def _change_passwd(db, options):
    _check_required_options(options, 'username', 'oldpassword', 'password', 'password2')
    username = options['username']
    password = options['oldpassword']
    user = db.query(User).filter_by(username=username).first()
    if user is None or not user.check_password(password):
        _error('error: Invalid username and/or password')

    password = options['password']
    password2 = options['password2']
    if password != password2:
        _error('error: passwords mismatch')

    user.set_password(password)
    db.add(user)


def _list_users(db, options):
    print('\nRegistered Users')
    for user in db.query(User):
        print('username=%s roles=%s is_active=%s last_login=%s' % (
            user.username, [r.name for r in user.roles], user.is_active, 
            user.last_login
        ))


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)

    settings = get_appsettings(config_uri, options=options)
    session_factory = get_session_factory(get_engine(settings))

    with transaction.manager:
        db = get_tm_session(session_factory, transaction.manager)
        _check_required_options(options, 'task')

        task = options['task'].strip()
        known_tasks = ('add', 'del', 'change_passwd', 'list')
        if task not in known_tasks:
            text = ", ".join(known_tasks)
            _error('error: Invalid task provided. Expected: %s', text)

        func = _add_user
        if task != 'add':
            func = _del_user if task == 'del' \
                else _list_users if task == 'list' \
                else _change_passwd

        # call func
        func(db, options)

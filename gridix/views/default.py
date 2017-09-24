import os
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.view import view_config, forbidden_view_config

from elixr.sax.auth import Authenticator
from ..scripts.importdt import main as import_task
from ..utils import handle_file_upload, get_upload_filepath, \
     ticks, TaskThread


_THREADS_ = {}



@view_config(route_name='home', renderer='index.html')
def home(request):
    return {
        'project': 'GridIX.Web'
    }


@view_config(route_name='login', renderer='login.html')
def login(request):
    login_url = request.route_url('login')
    username, password, message = ('', '', '')
    referrer = request.url

    if referrer == login_url:
        referrer = '/'  # referrer should not be login form

    next_url = request.params.get('next', referrer)
    if 'form.submitted' in request.params:
        username = request.params['username']
        password = request.params['password']
        authr = Authenticator(request.db)
        user = authr(username, password)
        if user is not None:
            headers = remember(request, username)
            return HTTPFound(location=next_url, headers=headers)

        message = 'Invalid username and/or password'
    return dict(
        show_auth_bar=False,
        message=message, next=next_url,
        username=username, password=password,
        url=request.application_url + '/login'
    )


@view_config(route_name='logout')
def logout(request):
    home_url = request.route_url('home')
    headers = forget(request)
    return HTTPFound(location=home_url, headers=headers)


@view_config(route_name='import', renderer='import-data.html', permission='edit')
def import_data(request):
    message = ''
    if 'form.submitted' in request.params:
        # validate uploaded file
        target_ext = ('.xls', '.xlsx')
        fileobj = request.POST.get('uplfile')
        if os.path.splitext(fileobj.filename)[1] not in target_ext:
            message = 'Invalid file uploaded. Expected .xls, .xlsx'
        else:
            filepath = handle_file_upload(fileobj)
            if filepath is None:
                message = 'Upload failed: %s' % fileobj.name
            else:
                url = request.application_url + '/process/' \
                    + os.path.basename(filepath)
                return HTTPFound(location=url)
    return {'message': message}


@view_config(route_name='process', renderer='process-data.html', permission='edit')
def process_data(request):
    fn = request.matchdict.get('fn')
    if fn in ('', None):
        return HTTPFound(location=request.application_url)

    # locate file for processing
    filepath = get_upload_filepath(fn)
    if not os.path.exists(filepath):
        return HTTPFound(location=request.application_url)

    # init return dict and start thread
    rdict = dict(done=False, error='', key='-1', percent=0, task='')
    try:
        task = TaskThread(import_task, ( # task args
            '', request.registry.settings.get('config.filename', 'development.ini'),
            'file=%s' % filepath
        ))
        task.set_progress('1:1:1', target=0)
        task.start()

        # store thread in a request, session independent manager
        key = str(ticks())
        _THREADS_[key] = task
        rdict.update({'key':key, 'filename':fn, 'percent':1})
        return rdict
    except Exception as ex:
        rdict.update({'error': str(ex) if ex else 'Uknown error occured.' , 'percent':1})
        return rdict


@view_config(route_name='monitor', renderer='json')
def process_monitor(request):
    # init dict to be returned by ajax call to default values
    rdict = dict(done=False, error='', key='-1', percent=1, task='')
    key = request.params.get('key')
    if not key in _THREADS_:
        rdict.update({'error': 'Unable to monitor import task progress.'})
        return rdict

    try:
        task = _THREADS_[key]
        done, percent = False, task.percent_done()
        if not task.is_alive() or percent == 100:
            del _THREADS_[key]
            done, percent = (True, 100)

        rdict.update({'done':done, 'key':key, 'percent':percent})
        return rdict
    except Exception as ex:
        rdict.update({'error':str(ex) if ex else 'Unknown error occured.', 'percent':1})
        return rdict

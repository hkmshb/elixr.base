import os
import pytest
from urllib.parse import urljoin, urlencode
from collections import namedtuple
from webtest.app import AppError
from webtest import TestApp



Args = namedtuple('Args', 'app db')


@pytest.fixture(scope='module')
def args():
    ## setup
    from utils import _get_settings, _init_db
    from gridix.webapp import main

    settings = _get_settings()
    db_path = settings.pop('db')
    if os.path.exists(db_path):
        os.remove(db_path)

    session = _init_db(settings)
    _app = TestApp(main({}, **settings))
    yield Args(app=_app, db=session)
    ## teardown


class TestResourceBase(object):
    API_ROOT = '/api/v0/'
    API_TOKEN = None

    def _get_api_url(self, path):
        return urljoin(self.API_ROOT, path)

    def _get_auth_token(self, app):
        url = self._get_api_url('auth/')
        creds = {'username':'usr', 'password':'open'}
        resp = app.post_json(url, creds)
        assert resp.json_body['result'] == 'ok'
        return resp.json_body['token']

    def _get_auth_header(self, app):
        if self.API_TOKEN == None:
            self.API_TOKEN = token = self._get_auth_token(app)
        return ('Authorization', 'JWT %s' % self.API_TOKEN)

    def _test_unauthn_collection_get_access_fails(self, args, endpoint):
        url = self._get_api_url(endpoint)
        with pytest.raises(AppError):
            resp = args.app.get(url, status=200)

    def _get_resource(self, args, endpoint=None, hdr=None, **filters):
        endpoint = endpoint or self.endpoint
        qs = '&'.join(['{}={}'.format(k, v) for k,v in filters.items()])
        url = self._get_api_url('{}?{}'.format(endpoint, urlencode(qs)))
        hdr = hdr or self._get_auth_header(args.app)
        return args.app.get(url, headers=[hdr])

    def _test_authn_collection_get_access_passes(self, args, endpoint):
        url = self._get_api_url(endpoint)
        hdr = self._get_auth_header(args.app)
        resp = args.app.get(url, headers=[hdr])
        assert resp.status_code == 200 \
           and resp.json_body == []

    def _test_collection_post_passes(self, args, **entries):
        assert hasattr(self, '_get_post_args')
        jargs = self._get_post_args(**entries)
        url = self._get_api_url(self.endpoint)
        hdr = self._get_auth_header(args.app)
        resp = args.app.post_json(url, jargs, headers=[hdr])
        assert resp.status_code == 200
        assert resp.json_body.get('id', 0) != 0
        return resp

    def _test_get_via_id_fails_for_missing_resource(self, args, id, hdr=None):
        endpoint = '{}{}'.format(self.endpoint, id)
        with pytest.raises(AppError):
            resp = self._get_resource(args, self._get_api_url(endpoint))
            assert resp and resp.status_code == 400
            assert resp.json_body \
            and resp.json_body['status'] == 'error'

    def _test_get_via_id_passes_for_found_resource(self, args, id, hdr=None):
        endpoint = '{}{}'.format(self.endpoint, id)
        resp = self._get_resource(args, self._get_api_url(endpoint))
        assert resp and resp.status_code == 200
        assert resp.json_body['id'] == id
        return resp
import pytest
from webtest.app import AppError
from elixr.sax.orgz import PartyType
from utils import _clear_db

from .api_test_base import args     # pytest.fixture
from .api_test_base import TestResourceBase



class TestOrganisationResource(TestResourceBase):
    endpoint = 'orgs/'

    def test_unauthn_collection_get_access_fails(self, args):
        self._test_unauthn_collection_get_access_fails(args, self.endpoint)

    def test_authn_collection_get_access_passes(self, args):
        self._test_authn_collection_get_access_passes(args, self.endpoint)

    def test_authn_collection_post_passes(self, args):
        url = self._get_api_url(self.endpoint)
        hdr = self._get_auth_header(args.app)
        resp = args.app.post_json(url, {
            'subtype': PartyType.organisation.value, 
            'name': 'Org', 'identifier': '01'
        }, headers=[hdr])
        assert resp.status_code == 200
        assert resp.json_body.get('id', 0) != 0 \
           and resp.json_body.get('name', '') == 'Org'

    def test_fails_when_creating_multiple_root_orgs(self, args):
        _clear_db(args.db, 'parties', 'organisations', 'people')
        url = self._get_api_url(self.endpoint)
        hdr = self._get_auth_header(args.app)
        resp = args.app.post_json(url, {
            'subtype': PartyType.organisation.value,
            'name': 'Org', 'identifier': '01'
        }, headers=[hdr])
        assert resp.status_code == 200
        assert resp.json_body.get('id', 0) != 0
        with pytest.raises(Exception):
            resp = args.app.post_json(url, {
                'subtype': PartyType.organisation.value,
                'name': 'Branch', 'identifier': '02'
            }, headers=[hdr])

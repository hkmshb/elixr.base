import pytest
from webtest.app import AppError
from .api_test_base import args     # pytest.fixture
from .api_test_base import TestResourceBase
from utils import _clear_db

from gridix.data.models.network import LineType, Owner, StationType



class TestVoltageResource(TestResourceBase):
    endpoint = 'voltages/'

    def _get_post_args(self, **entries):
        kw = {'value': 415}
        return {'value': entries.get('value', kw.get('value'))}

    def test_unauthn_collection_get_access_fails(self, args):
        self._test_unauthn_collection_get_access_fails(args, self.endpoint)
    
    def test_collection_get_access_passes(self, args):
        self._test_authn_collection_get_access_passes(args, self.endpoint)
    
    def test_collection_post_passes(self, args):
        resp = self._test_collection_post_passes(args)
        assert resp.json_body.get('value', 0) == 415
    
    def test_get_fails_for_no_existing_resource_gotten_by_id(self, args):
        resp = self._test_get_via_id_fails_for_missing_resource(args, 0)
    
    def test_get_passes_for_existing_resource_gotten_by_id(self, args):
        _clear_db(args.db, self.endpoint.replace("/", ""))
        url = self._get_api_url(self.endpoint)
        hdr = self._get_auth_header(args.app)
        resp = args.app.post_json(url, {'value':415}, headers=[hdr])
        assert resp.status_code == 200
        resp = self._test_get_via_id_passes_for_found_resource(
                    args, resp.json_body.get('id', 0))


class TestElectricStationResource(TestResourceBase):
    endpoint = 'electric_stations/'

    def _get_post_args(self, **entries):
        kw = {
            'facility_code': '01', 'register_code': 'r01',
            'owner': Owner.company.value, 'name': 'T.Station', 
            'subtype': StationType.transmission.value
        }
        get = lambda k: entries.get(k, kw.get(k, ''))
        return {k:get(k) for k in ['facility_code', 'registry_code', 'owner',
            'name', 'subtype']}

    def test_unauthn_collection_get_access_fails(self, args):
        self._test_unauthn_collection_get_access_fails(args, self.endpoint)
    
    def test_authn_collection_get_access_passes(self, args):
        self._test_authn_collection_get_access_passes(args, self.endpoint)
    
    def test_collection_post_passes(self, args):
        resp = self._test_collection_post_passes(args)
        assert resp.json_body.get('name', '') == 'T.Station'

    def test_get_fails_for_no_existing_resource_gotten_by_id(self, args):
        resp = self._test_get_via_id_fails_for_missing_resource(args, 0)
    
    def test_get_passes_for_existing_resource_gotten_by_id(self, args):
        _clear_db(args.db, self.endpoint.replace("/", ""))
        url = self._get_api_url(self.endpoint)
        hdr = self._get_auth_header(args.app)
        resp = args.app.post_json(url, self._get_post_args(), headers=[hdr])
        assert resp.status_code == 200
        resp = self._test_get_via_id_passes_for_found_resource(
                    args, resp.json_body.get('id', 0))


class TestElectricLineResource(TestResourceBase):
    endpoint = 'electric_lines/'

    def _get_post_args(self, **entries):
        kw = {
            'line_code': 'L01', 'register_code': 'rL01', 
            'name': 'Feeder', 'owner': Owner.company.value,
            'subtype': LineType.feeder.value,
        }
        get = lambda k: entries.get(k, kw.get(k, ''))
        return {k:get(k) for k in ['line_code', 'facility_code', 'owner',
            'name', 'subtype', 'voltage', 'source_station']}
    
    def _prep_for_post(self, args, hdr):
        ## create voltage
        url = self._get_api_url(TestVoltageResource.endpoint)
        jargs = TestVoltageResource()._get_post_args()
        resp = args.app.post_json(url, jargs, headers=[hdr])
        assert resp.status_code == 200
        entries = {'voltage': resp.json_body.get('id')}

        ## create station
        url = self._get_api_url(TestElectricStationResource.endpoint)
        jargs = TestElectricStationResource()._get_post_args()
        resp = args.app.post_json(url, jargs, headers=[hdr])
        assert resp.status_code == 200
        entries['source_station'] = resp.json_body.get('id')
        return entries

    def test_unauthn_collection_get_access_fails(self, args):
        self._test_unauthn_collection_get_access_fails(args, self.endpoint)
    
    def test_authn_collection_get_access_passes(self, args):
        self._test_authn_collection_get_access_passes(args, self.endpoint)

    def test_collection_get_access_passes(self, args):
        # need to add voltage and station
        _clear_db(args.db, 'electric_lines', 'electric_stations', 'voltages')
        entries = self._prep_for_post(args, self._get_auth_header(args.app))
        resp = self._test_collection_post_passes(args, **entries)
        assert resp.json_body.get('', '') == ''
    
    def test_get_fails_for_no_existing_resource_gotten_by_id(self, args):
        resp = self._test_get_via_id_fails_for_missing_resource(args, 0)
    
    def test_get_passes_for_existing_resource_gotten_by_id(self, args):
        _clear_db(args.db, 'electric_lines', 'electric_stations', 'voltages')
        url = self._get_api_url(self.endpoint)
        hdr = self._get_auth_header(args.app)
        entries = self._prep_for_post(args, hdr)
        jargs = self._get_post_args(**entries)
        resp = args.app.post_json(url, jargs, headers=[hdr])
        assert resp.status_code == 200
        resp = self._test_get_via_id_passes_for_found_resource(args, 1)
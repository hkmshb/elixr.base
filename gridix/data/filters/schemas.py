"""Contains schema definitions which define fields expected for a collection
api endpoint for filtering, sorting and paging within a url querystring. These
schemas are not really required for validation of values provided on the query-
string, rather they ease accessing certain `expected` values within the query-
string as opposed the schema defined at `pylons.data.schema` which are solely
meant for input validation.
"""
from marshmallow import Schema, fields, post_load
from .objects import (
    VoltageFilter, ElectricStationFilter, ElectricLineFilter,
    OrganisationFilter
)


class PagingMixin(object):
    page_index = fields.Int(load_from='page')
    page_size  = fields.Int(load_from='pageSize')


class SyncMixin(object):
    uuid = fields.Str()
    date_updated = fields.DateTime(load_from='dateUpdated')


class VoltageFilterSchema(Schema, PagingMixin, SyncMixin):
    """Defines fields which can be used to page and filter a collection of 
    Voltage objects.
    """
    value = fields.Int()

    @post_load
    def make_filter(self, data):
        return VoltageFilter(**data)


class ElectricStationFilterSchema(Schema, PagingMixin, SyncMixin):
    """Defines fields which can be used to page and filter a collection of
    ElectricStation objects.
    """
    name    = fields.Str()
    owner   = fields.Int()
    subtype = fields.Int(load_from='subType')
    is_public = fields.Boolean(load_from='isPublic')
    is_manned = fields.Boolean(load_from='isManned')
    is_automated = fields.Boolean(load_from='isAutomated')
    facility_code = fields.Str(load_from='facilityCode')
    register_code = fields.Str(load_from='registerCode')
    organisation_id = fields.Int(load_from='organisationId')
    date_installed = fields.DateTime(load_from='dateInstalled')
    source_line_id = fields.Int(load_from='sourceLineId')

    @post_load
    def make_filter(self, data):
        return ElectricStationFilter(**data)


class ElectricLineFilterSchema(Schema, PagingMixin, SyncMixin):
    """Defines fields which can be used to page and filter a collection of
    ElectricLine objects.
    """
    name    = fields.Str()
    owner   = fields.Int()
    subtype = fields.Int(load_from='subType')
    line_code = fields.Str(load_from='lineCode')
    register_code = fields.Str(load_from='registerCode')
    voltage_id = fields.Int(load_from='voltageId')
    source_station_id = fields.Int(load_from='sourceStationId')
    date_commissioned = fields.DateTime(load_from='dateCommissioned')

    @post_load
    def make_filter(self, data):
        return ElectricLineFilter(**data)


class OrganisationFilterSchema(Schema, PagingMixin, SyncMixin):
    """Defines fields which can be used to page and filter a colleciton of
    Organisation objects.
    """
    name   = fields.Str()
    fncode = fields.Int()
    parent_id = fields.Int(load_from='parentId')
    identifier = fields.Str()
    description = fields.Str()
    date_established = fields.DateTime(load_form='dateEstablished')

    @post_load
    def make_filter(self, data):
        return OrganisationFilter(**data)

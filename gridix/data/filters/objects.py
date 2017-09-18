"""Defines filter models.
"""


class FilterBase(object):
    def __init__(self, **kwargs):
        # initialize fields via introspection
        kwargs = (kwargs or {})
        for field in self._fields:
            setattr(self, field, kwargs.get(field, None))
    
    @property
    def _fields(self):
        skip = lambda x: x.startswith('_') or x.startswith('__')
        return [key for key in dir(self.__class__) if not skip(key)]

    def _as_dict(self):
        result = {}
        for field in self._fields:
            value = getattr(self, field)
            if value != None:
                result[field] = value
        return result


class PagingFilter(FilterBase):
    """Defines filtering attributes for paging a collection of items.
    """
    page_index = None
    page_size  = None


class SyncFilter(FilterBase):
    """Defines attributes to help identify unique and altered objects.
    """
    uuid = None
    date_updated = None


class VoltageFilter(SyncFilter):
    """Defines filtering attributes unique for the Voltage model.
    """
    value = None


class ElectricStationFilter(PagingFilter, SyncFilter):
    """Defines filtering attributes unique for the ElectricStation model.
    """
    name    = None
    owner   = None
    subtype = None
    is_public = None
    is_manned = None
    is_automated = None
    facility_code = None
    register_code = None
    organisation_id = None
    date_installed = None
    source_line_id = None


class ElectricLineFilter(PagingFilter, SyncFilter):
    """Defines filtering attributes unique for the ElectricLine model.
    """
    name    = None
    owner   = None
    subtype = None
    line_code = None
    register_code = None
    voltage_id    = None
    source_station_id = None
    date_commissioned = None


class OrganisationFilter(PagingFilter, SyncFilter):
    """Defines filtering attributes unique for the Organisation model.
    """
    name   = None
    fncode = None
    parent_id = None
    identifier = None
    description = None
    date_established = None

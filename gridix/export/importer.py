from elixr.base import AttrDict
from elixr.sax.address import State
from elixr.sax.orgz import Organisation
from elixr.sax.export.importer import (
    ImporterBase, MegaImporterBase, 
    AdminBoundaryImporter, OrganisationImporter
)
from ..data.models.base import OrgFnType
from ..data.models.network import (
    Owner, LineType, StationType,
    Voltage, ElectricStation, ElectricLine
)


class VoltageImporter(ImporterBase):
    """An importer to process and import Voltage data from an excel sheet.
    """
    sheet_name = 'voltages'

    def create_voltage(self, row, data):
        try:
            voltage = Voltage(**data)
            self.context.db.add(voltage)
        except Exception as ex:
            message_fmt = 'Voltage could not be created. Err: %s'
            self.error(row, 0, message_fmt % str(ex))
    
    def process(self):
        sh, nrows = (self.sheet, self.sheet.max_row)
        for row in range(2, nrows + 1):
            data = AttrDict()
            num_errors = len(self.errors)
            data['value'] = self.get_required_int_from_cell(sh, row, 1)
            if num_errors == len(self.errors):
                self.create_voltage(row, data)
            self.progress(row, nrows)


class StationLineImporter(ImporterBase):
    """An importer able to process and import ElectricStation and ElectricLine
    data from an excel file.
    """
    sheet_name = 'stations-lines'

    def _handle_relationships(self, row, data):
        self.resolve_xref(data,
            ('voltage_id', 'value', Voltage),
            ('addr_state_id', 'code', State),
            ('organisation', 'short_name', Organisation),
            ('organisation_id', 'short_name', Organisation),
            ('source_line_id', 'line_code', ElectricLine),
            ('source_station_id', 'facility_code', ElectricStation))
        
    def create_line(self, row, data):
        self._handle_relationships(row, data)
        organisations = data.pop('organisation')
        try:
            line = ElectricLine(**data)
            if organisations:
                line.organisations.extend(organisations)
            self.context.db.add(line)
        except Exception as ex:
            print(organisations)
            message_fmt = 'ElectricLine could not be created. Err: %s'
            self.error(row, 0, message_fmt % str(ex))
    
    def create_station(self, row, data):
        self._handle_relationships(row, data)
        try:
            station = ElectricStation(**data)
            self.context.db.add(station)
        except Exception as ex:
            message_fmt = 'ElectricStation could not be created. Err: %s'
            self.error(row, 0, message_fmt % str(ex))
    
    def import_line(self, sh, row):
        num_errors = len(self.errors)
        subtype = self.get_required_enum_from_cell(sh, row, 2, LineType)
        if num_errors < len(self.errors):
            return (row + 1)

        voltage = self.get_required_id_from_cell(sh, row+1, 2)
        if num_errors < len(self.errors):
            return
        
        row += 3
        while row <= sh.max_row:
            if self.is_empty_row(sh, row):
                break
            
            num_errors = len(self.errors)
            data = AttrDict({'subtype': subtype, 'voltage_id': voltage})
            data['source_station_id'] = self.get_required_id_from_cell(sh, row, 1)
            data['line_code'] = self.get_required_id_from_cell(sh, row, 2)
            data['register_code'] = self.get_required_id_from_cell(sh, row, 3)
            data['organisation'] = self.get_ids_from_cell(sh, row, 4)
            data['name'] = self.get_required_text_from_cell(sh, row, 5)
            data['is_public'] = self.get_required_bool_from_cell(sh, row, 6)
            data['owner'] = self.get_required_enum_from_cell(sh, row, 7, Owner)
            data['date_commissioned'] = self.get_date_from_cell(sh, row, 8)
            data['comments'] = self.get_text_from_cell(sh, row, 9, None)
            if num_errors < len(self.errors):
                break
            
            self.create_line(row, data)
            row += 1
        return (row + 1)

    def import_station(self, sh, row):
        num_errors = len(self.errors)
        subtype = self.get_required_enum_from_cell(sh, row, 2, StationType)
        if num_errors < len(self.errors):
            return (row + 1)
        
        row += 2
        while row <= sh.max_row:
            if self.is_empty_row(sh, row):
                break
            
            data, num_errors = (AttrDict({'subtype': subtype}), len(self.errors))
            if subtype != StationType.transmission:
                data['source_line_id'] = self.get_required_id_from_cell(sh, row, 1)
            data['facility_code'] = self.get_required_id_from_cell(sh, row, 2)
            data['register_code'] = self.get_required_id_from_cell(sh, row, 3)
            data['organisation_id'] = self.get_id_from_cell(sh, row, 4)
            data['name'] = self.get_required_text_from_cell(sh, row, 5)
            data['is_public'] = self.get_required_bool_from_cell(sh, row, 6)
            data['is_manned'] = self.get_required_bool_from_cell(sh, row, 7)
            data['owner'] = self.get_required_enum_from_cell(sh, row, 8, Owner)
            data['addr_state_id'] = self.get_required_text_from_cell(sh, row, 9)
            data['addr_street'] = self.get_text_from_cell(sh, row, 10, None)
            data['addr_town'] = self.get_text_from_cell(sh, row, 11, None)
            data['addr_landmark'] = self.get_text_from_cell(sh, row, 12, None)
            data['longitude'] = self.get_float_from_cell(sh, row, 13, None)
            data['latitude'] = self.get_float_from_cell(sh, row, 14, None)
            data['altitude'] = self.get_float_from_cell(sh, row, 15, None)
            data['gps_error'] = self.get_int_from_cell(sh, row, 16, None)
            data['date_installed'] = self.get_date_from_cell(sh, row, 17)
            data['comments'] = self.get_text_from_cell(sh, row, 18, None)
            if num_errors < len(self.errors):
                break
            
            self.create_station(row, data)
            row += 1
        return (row + 1)
    
    def process(self):
        sh, row, nrows = (self.sheet, 1, self.sheet.max_row)
        ## flags are provided in reverse order as `list.pop` operates
        ## on items from the bottom NOT the top
        flags = ['lines', 'stations']
        while row <= nrows:
            if not flags: break
            if self.is_empty_row(sh, row):
                row += 1; continue
            
            value = sh.cell(row=row, column=1).value
            if value not in flags:
                row += 1; continue
            
            while value != flags.pop():
                pass    # keep popping ;-)
            
            if value == 'stations':
                row = self.import_station(sh, row)
            elif value == 'lines':
                row = self.import_line(sh, row)
        self.progress(row, nrows)


class MegaImporter(MegaImporterBase):
    """Manages a collection of `importers` to pull in data from an excel file
    into the database.
    """

    @property
    def importers(self):
        AdminBoundaryImporter.sheet_name = 'coverage'
        OrganisationImporter.fncode_type = OrgFnType
        return [
            AdminBoundaryImporter,
            VoltageImporter,
            OrganisationImporter,
            StationLineImporter
        ]

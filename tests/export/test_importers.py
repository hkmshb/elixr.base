import os
import pytest
import openpyxl
from datetime import datetime
from collections import namedtuple
from elixr.base import AttrDict
from elixr.sax import utils
from elixr.sax.orgz import Organisation
from elixr.sax.address import Country, State
from elixr.sax.export.importer import XRefResolver
from gridix.data.models.network import Voltage, ElectricStation, ElectricLine
from gridix.export.importer import ImporterBase, StationLineImporter



FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture(scope='module')
def wb():
    fp = os.path.join(FIXTURES_DIR, 'sample-assets.xlsx')
    return openpyxl.load_workbook(fp, read_only=True)


@pytest.fixture(scope='module')
def imp_sl():
    def initdb(session):
        cn = Country(code='CN', name='Country')
        org = Organisation(identifier="Org0", name="Org.Main", short_name="Org0")
        session.add_all([
            ## voltages
            Voltage(value=415), Voltage(value=11000),
            Voltage(value=33000),
            ## states
            State(code='S1', name='State 1', country=cn),
            State(code='S2', name='State 2', country=cn),
            ## organisations
            Organisation(identifier="Org1", name="Child1", short_name="Org1", parent=org),
            Organisation(identifier="Org2", name="Child2", short_name="Org2", parent=org),
        ])
        session.commit()
    
    ## setup
    resx = utils.make_session(initdb_callback=initdb)
    cache = XRefResolver(resx.session)
    return StationLineImporter(AttrDict(db=resx.session, cache=cache))
    ## teardown
    utils.drop_tables(resx.engine)


class TestStationsLinesImporter(object):

    def test_fails_for_missing_station_type(self, wb, imp_sl):
        imp_sl.errors.clear()
        imp_sl.sheet_name = 'stations-missing-type'
        imp_sl.import_data(wb)
        assert len(imp_sl.errors) == 1

    def test_fails_for_invalid_station_type(self, wb, imp_sl):
        imp_sl.errors.clear()
        imp_sl.sheet_name = 'stations-invalid-type'
        imp_sl.import_data(wb)
        assert len(imp_sl.errors) == 1

    def test_save_listed_stations(self, wb, imp_sl):
        imp_sl.errors.clear()
        imp_sl.sheet_name = 'stations'
        imp_sl.import_data(wb)
        assert len(imp_sl.errors) == 0
        db = imp_sl.context['db']
        assert db.query(ElectricStation).count() == 2

    def test_save_listed_stations_lines(self, wb, imp_sl):
        imp_sl.errors.clear()
        imp_sl.sheet_name = 'stations-lines-1'
        imp_sl.import_data(wb)
        assert len(imp_sl.errors) == 0
        db = imp_sl.context['db']
        assert db.query(ElectricStation).count() == 4
        lines = db.query(ElectricLine).all()
        assert len(lines) == 2
    
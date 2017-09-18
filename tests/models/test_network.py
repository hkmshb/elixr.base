import pytest
from pyramid import testing
from gridix.data.models.network import (
    Voltage, LineType, StationType, Owner,
    ElectricLine, ElectricStation 
)
from .common import db



class TestVoltage(object):
    def test_uuid_is_auto_created(self, db):
        db.add(Voltage(value=1))
        db.commit()

        volt = db.query(Voltage).filter_by(deleted=False, value=1).one()
        assert volt and volt.uuid != None

    def test_unique_uuid_create_for_each_record(self, db):
        db.add_all([Voltage(value=2), Voltage(value=3)])
        db.commit()

        volts = db.query(Voltage).filter(Voltage.value.in_([2,3]))\
                  .order_by(Voltage.value).all()
        assert volts and len(volts) == 2 \
           and volts[0].uuid != volts[1].uuid \
           and volts[0].uuid != None \
           and volts[1].uuid != None \


class TestElectricLine(object):
    def test_can_save_when_required_fields_provided(self, db):
        voltage = Voltage(value=11001)
        station = ElectricStation(name='Briscoe', facility_code='fcode#1',
                    register_code='rcode#1', owner=Owner.company,
                    subtype=StationType.injection)
        db.add_all([voltage, station])
        db.commit()

        line = ElectricLine(name='Gezawa', line_code='code#1', owner=Owner.company,
                register_code='rcode#1', subtype=LineType.feeder,
                voltage=voltage, source_station=station)
        db.add(line)
        db.commit()

        assert line and line.id != None \
           and line.name == 'Gezawa' \
           and line.line_code == 'code#1' \
           and line.register_code == 'rcode#1' \
           and line.subtype == LineType.feeder \
        
        assert line.voltage and line.voltage.id != None \
           and line.voltage.value == 11001 \
        
        assert line.source_station and line.source_station.id != None \
           and line.source_station.name == 'Briscoe' \
           and line.source_station.facility_code == 'fcode#1' \
           and line.source_station.register_code == 'rcode#1' \
           and line.source_station.owner == Owner.company \
           and line.source_station.subtype == StationType.injection
        
    def test_commit_fails_for_missing_source_station(self, db):
        voltage = Voltage(value=11002)
        db.add(voltage)
        db.commit()
        
        with pytest.raises(Exception):
            line = ElectricLine(name='Gezawa', line_code='code#1', 
                register_code='rcode#1', subtype=LineType.feeder,
                voltage=voltage, owner=Owner.company
            )
            db.add(line)
            db.commit()
        db.rollback()
    
    def test_commit_fails_for_missing_voltage(self, db):
        station = ElectricStation(name='Briscoe#2', facility_code='fcode#2',
                    register_code='rcode#2', owner=Owner.company,
                    subtype=StationType.injection)
        db.add(station)
        db.commit()

        with pytest.raises(Exception):
            line = ElectricLine(name='Gezawa', line_code='code#1',
                    register_code='rcode#1', subtype=LineType.feeder,
                    source_station=station)
            db.add(line)
            db.commit()
        db.rollback()


class TestElectricStation(object):
    def test_can_save_for_all_required_fields_excluding_source_line(self, db):
        station = ElectricStation(name='Briscoe#3', facility_code='fcode#3',
                    register_code='rcode#3', owner=Owner.company,
                    subtype=StationType.injection)
        db.add(station)
        db.commit()

        assert station and station.id != None \
           and station.name == 'Briscoe#3' \
           and station.facility_code == 'fcode#3' \
           and station.register_code == 'rcode#3' \
           and station.owner == Owner.company \
           and station.subtype == StationType.injection
    
    def test_can_save_multi_records_with_null_register_code(self, db):
        station1 = ElectricStation(name='Briscoe#4', facility_code='fcode#4',
                     owner=Owner.company, subtype=StationType.injection)
        station2 = ElectricStation(name='Briscoe#5', facility_code='fcode#5',
                     owner=Owner.company, subtype=StationType.injection)
        db.add_all([station1, station2])
        db.commit()

        assert station1 and station2 \
           and station1.id != None and station2.id != None \
           and station1.id != station2.id \
           and station1.register_code == None \
           and station2.register_code == None
    
    def test_commit_fails_for_duplicate_register_code(self, db):
        station1 = ElectricStation(name='Briscoe#6', facility_code='fcode#6',
                    register_code='rcode#6', owner=Owner.company, 
                    subtype=StationType.injection)
        db.add(station1)
        db.commit()

        with pytest.raises(Exception):
            station2 = ElectricStation(
                name='Briscoe#7', facility_code='fcode#7',
                regiter_code='rcode#6', owner=Owner.company, 
                subtype=StationType.injection)
            db.add(station2)
            db.commit()
        db.rollback()
    
    def test_can_save_with_source_line_provided(self, db):
        voltage = Voltage(value=33000)
        tstation = ElectricStation(name='Kumbotso', facility_code='tfcode#1',
                    register_code='trcode#1', owner=Owner.company,
                    subtype=StationType.transmission)
        feedr33 = ElectricLine(name='IDH', line_code='fdr#1',
                    register_code='rfdr#1', subtype=LineType.feeder,
                    source_station=tstation, voltage=voltage,
                    owner=Owner.company)
        db.add_all([voltage, tstation, feedr33])
        db.commit()

        istation = ElectricStation(name='Race Cource', facility_code='rc_fdr#1',
                    register_code='rc_fdr#1', subtype=StationType.injection,
                    owner=Owner.company, source_line=feedr33)
        db.add(istation)
        db.commit()

        assert istation and istation.id != None \
           and istation.source_line \
           and istation.source_line.id != None \
           and istation.source_line_id == istation.source_line.id
    
    def test_electric_lines_does_reverse_listing(self, db):
        voltage = Voltage(value=33001)
        station = ElectricStation(name='Kumbotso#1', facility_code='tfcode#2',
                    register_code='trcode#2', owner=Owner.company,
                    subtype=StationType.transmission)
        db.add_all([voltage, station])
        db.commit()

        db.add_all([
            ElectricLine(name='IDH#1', line_code='idh#f1', register_code='idh#rc1',
                subtype=LineType.feeder, source_station=station, voltage=voltage,
                owner=Owner.company),
            ElectricLine(name='IDH#2', line_code='idh#f2', register_code='idh#rc2',
                subtype=LineType.feeder, source_station=station, voltage=voltage,
                owner=Owner.company)])
        db.commit()

        assert station and station.electric_lines \
           and len(station.electric_lines) == 2 \
           and station.electric_lines[0].id != None \
           and station.electric_lines[1].id != None

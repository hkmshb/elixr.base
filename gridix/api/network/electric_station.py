from cornice.resource import resource, view
from elixr.sax.address import State
from ...data.filters import ElectricStationFilterSchema
from ...data.models.schemas import ElectricStationSchema
from ...data.models.network import ElectricStation
from ..utils import use_args_with, ACLResource



@resource(name='electric_stations',
          factory=ACLResource, permission='api',
          collection_path='/electric_stations/', path='/electric_stations/{id}')
class ElectricStationResource(object):
    def __init__(self, request, context=None):
        self.request = request
        self.user = context
    
    @use_args_with(ElectricStationFilterSchema)
    def collection_get(self, args):
        try:
            qry = self.request.db.query(ElectricStation) \
                      .filter_by(deleted=False)
            if args != None:
                qry = qry.filter_by(**args._as_dict())
            
            qry.order_by(ElectricStation.id)
            schema = ElectricStationSchema(many=True)
            jwrap = schema.dump(qry.all())
            return jwrap.data
        except Exception as ex:
            self.request.errors.add('body', None, str(ex))
    
    def collection_post(self):
        db, schema = (self.request.db, ElectricStationSchema())
        result = schema.load(self.request.json, db)
        if result.errors:
            self.request.errors.add('body', None, result.errors)
            return
        
        # save collected object
        db.add(result.data)
        db.flush()

        jresult = schema.dump(result.data)
        return jresult.data

    def get(self):
        try:
            id = self.request.matchdict['id']
            qry = self.request.db.query(ElectricStation).filter_by(
                deleted=False, id=id)
            schema = ElectricStationSchema()
            jresult = schema.dump(qry.one())
            return jresult.data
        except Exception as ex:
            self.request.errors.add('body', None, str(ex))
    
    def put(self):
        db, schema = (self.request.db, ElectricStationSchema())
        result = schema.load(self.request.json)
        if result.errors:
            self.request.errors.add('body', 'electric_station', result.errors)
            return
        
        # ensure resource exists
        upd_estation = result.data
        try:
            estation = db.query(ElectricStation) \
                         .filter_by(id == upd_estation.id).one()
            self._update(estation, upd_station)
            db.flush()
            
            jresult = schema.dump(estation)
            return jresult.data
        except Exception as ex:
            self.request.errors.add('body', 'electric_station', str(ex))
    
    def _update(self, target, source):
        assert target != None and source != None
        if str(target.uuid) != str(source.uuid):
            raise Exception('Operation aborted as uuids miss-match')
        
        target_fields = ['name', 'facitlity_code', 'register_code', 'owner',
            'subtype', 'source_line_id', 'date_installed', 'date_created',
            'date_updated', 'comments']
        for f in target_fields:
            target[f] = source[f]
        
        # clear date_updated on target so that it's auto-created on database
        target.date_updated = None


@resource(name='_electric_line_stations',
          factory=ACLResource, permission='api',
          collection_path='/electric_lines/{line_id}/electric_stations/',
          path='/electric_lines/{line_id}/electric_stations/{id}')
class ElectricLineStationsResource(object):
    def __init__(self, request, context=None):
        self.request = request
        self.context = context
    
    @use_args_with(ElectricStationFilterSchema)
    def collection_get(self, filters):
        try:
            line_id = self.request.matchdict['line_id']
            query = self.request.db.query(ElectricStation).filter_by(
                deleted=False, source_line_id=line_id
            )
            if filters != None:
                query = query.filter_by(**filters._as_dict())
            
            query.order_by(ElectricStation.id)
            schema = ElectricStationSchema(many=True)
            jresult = schema.dump(query.all())
            return jresult.data
        except Exception as ex:
            self.request.errors.add('body', None, str(ex))
    
    def get(self):
        try:
            line_id = self.request.matchdict['line_id']
            id = self.request.matchdict['id']
            query = self.request.db.query(ElectricStation).filter_by(
                deleted=False, source_line_id=line_id, id=id
            )
            schema = ElectricStationSchema()
            jresult = schema.dump(query.one())
            return jresult.data
        except Exception as ex:
            self.request.errors.add('body', None, str(ex))
    
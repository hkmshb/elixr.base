from cornice.resource import resource
from ...data.filters import ElectricLineFilterSchema
from ...data.models.schemas import ElectricLineSchema
from ...data.models.network import ElectricLine
from ..utils import use_args_with, ACLResource



@resource(name='electric_lines',
          factory=ACLResource, permission='api',
          collection_path='/electric_lines/', path='/electric_lines/{id}')
class ElectricLineResource(object):
    def __init__(self, request, context=None):
        self.request = request
        self.user = context
    
    @use_args_with(ElectricLineFilterSchema)
    def collection_get(self, filters):
        try:
            qry = self.request.db.query(ElectricLine).filter_by(deleted=False)
            if filters != None:
                qry = qry.filter_by(**filters._as_dict())
            qry.order_by(ElectricLine.id)
            schema = ElectricLineSchema(many=True)
            result = schema.dump(qry.all())
            return result.data
        except Exception as ex:
            self.request.errors.add('body', None, str(ex))
    
    def collection_post(self):
        db, schema = (self.request.db, ElectricLineSchema())
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
            qry = self.request.db.query(ElectricLine).filter_by(
                deleted=False, id=id
            )
            schema = ElectricLineSchema()
            jresult = schema.dump(qry.one())
            return jresult.data
        except Exception as ex:
            self.request.errors.add('body', None, str(ex))


@resource(name='_electric_station_lines',
          factory=ACLResource, permission='api',
          collection_path='/electric_stations/{station_id}/electric_lines/',
          path='/electric_stations/{station_id}/electric_lines/{id}')
class ElectricStationLinesResource(object):
    def __init__(self, request, context=None):
        self.request = request
        self.context = context
    
    @use_args_with(ElectricLineFilterSchema)
    def collection_get(self, filters):
        try:
            station_id = self.request.matchdict['station_id']
            qry = self.request.db.query(ElectricLine).filter_by(
                deleted=False, source_station_id=station_id
            )
            if filters != None:
                qry = qry.filter_by(**filters._as_dict())
            
            qry.order_by(ElectricLine.id)
            schema = ElectricLineSchema(many=True)
            jresult = schema.dump(qry.all())
            return jresult.data
        except Exception as ex:
            self.request.errors.add('body', None, str(ex))
    
    def collection_post(self):
        db, schema = (self.request.db, ElectricLineSchema())
        result = schema.load(self.request.json, db)
        if result.errors:
            self.request.errors.add('body', None, result.errors)
            return
        # save collected object
        db.add(result.data)
        db.flush()

    def get(self):
        try:
            station_id = self.request.matchdict['station_id']
            id = self.request.matchdict['id']
            query = self.request.db.query(ElectricLine).filter_by(
                deleted=False, source_station_id=station_id, id=id
            )
            schema = ElectricLineSchema()
            jresult = schema.dump(query.one())
            return jresult.data
        except Exception as ex:
            self.request.errors.add('body', None, str(ex))
    
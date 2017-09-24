from sqlalchemy.orm import exc
from cornice.resource import resource, view
from ...data.models.schemas import VoltageSchema
from ...data.models.network import Voltage
from ...data.filters import VoltageFilterSchema
from ..security import use_args_with, ACLResource



@resource(name='voltages',
          factory=ACLResource, permission='api', 
          collection_path='/voltages/', path='/voltages/{id}')
class VoltageResource(object):
    def __init__(self, request, context=None):
        self.request = request
        self.user = context

    @use_args_with(VoltageFilterSchema)
    def collection_get(self, args):
        try:
            qry = self.request.db.query(Voltage).filter_by(deleted=False)
            # apply filters
            if args != None:
                qry = qry.filter_by(**args._as_dict())
            
            qry = qry.order_by(Voltage.id)
            schema = VoltageSchema(many=True)
            jresult = schema.dump(qry.all())
            return jresult.data
        except exc.NoResultFound as ex:
            self.request.errors.add('body', None, str(ex))

    def collection_post(self):
        db, schema = (self.request.db, VoltageSchema())
        result = schema.load(self.request.json, db)
        if result.errors:
            self.request.errors.add('body', 'voltage', result.errors)
            return

        # save collected object
        db.add(result.data)
        db.flush()

        jresult = schema.dump(result.data)
        return jresult.data

    def get(self):
        try:
            id = self.request.matchdict['id']
            qry = self.request.db.query(Voltage).filter_by(deleted=False, id=id)
            schema = VoltageSchema()
            jresult = schema.dump(qry.one())
            return jresult.data
        except exc.NoResultFound as ex:
            self.request.errors.add('body', None, str(ex))

    def put(self):
        db, schema = (self.request.db, VoltageSchema())
        result = schema.load(self.request.json, db)
        if result.errors:
            self.request.errors.add('body', 'voltage', result.errors)
            return

        # ensure resource exists
        upd_voltage = result.data
        try:
            voltage = db.query(Voltage).filter(Voltage.id == upd_voltage.id).one()
            voltage.value = upd_voltage.value
            db.flush()

            jresult = schema.dump(voltage)
            return jresult.data
        except exc.NoResultFound as ex:
            self.request.errors.add('body', 'voltage', str(ex))

    def delete(self):
        try:
            id = self.request.matchdict['id']
            qry = self.request.db.query(Voltage).filter(Voltage.id == id)
            voltage = qry.one()
            voltage.deleted = True
        except exc.NoResultFound as ex:
            self.request.errors.add('body', None, str(ex))

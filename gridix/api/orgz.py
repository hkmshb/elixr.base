from sqlalchemy.orm import exc
from cornice.resource import resource
from elixr.sax.orgz import Organisation, PartyType
from ..data.models.schemas import OrganisationSchema
from ..data.filters import OrganisationFilterSchema
from .utils import use_args_with, ACLResource



@resource(name='orgs',
          factory=ACLResource, permission='api',
          collection_path='/orgs/', path='/orgs/{id}')
class OrgResource(object):
    def __init__(self, request, context=None):
        self.request = request
        self.user = context
    
    @use_args_with(OrganisationFilterSchema)
    def collection_get(self, filters):
        try:
            kw = {'deleted':False, 'subtype': PartyType.organisation}
            qry = self.request.db.query(Organisation).filter_by(**kw)
            if filters != None:
                qry = qry.filter_by(**filters._as_dict())
            
            qry = qry.order_by(Organisation.id)
            schema = OrganisationSchema(many=True)
            result = schema.dump(qry.all())
            return result.data
        except exc.NoResultFound as ex:
            self.request.errors.add('body', None, str(ex))
    
    def collection_post(self):
        # note with ref to loads `partial` arg. `id` field is both primary_key 
        # foreign_key to Party. its being foreign_key makes it required during
        # deserialization... but 1-to-1 between Party & Organisation means it
        # gets value when Party is created thus with partial it gets ignored for
        # deserialization...
        db, schema = (self.request.db, OrganisationSchema())
        result = schema.load(self.request.json, db, partial=['id'])
        if result.errors:
            self.request.errors.add('body', 'organisation', result.errors)
            return
        # todo: use a service to verify and save object
        # save collected object
        db.add(result.data)
        db.flush()

        jresult = schema.dump(result.data)
        return jresult.data
    
    def get(self):
        db = self.request.db
        kw = {'deleted': False, 'subtype': PartyType.organisation}
        try:
            kw.update({'id': self.request.matchdict['id']})
            qry = db.query(Organisation).filter_by(**kw)
            schema = OrganisationSchema()
            jresult = schema.dump(qry.one())
            return jresult.data
        except exc.NoResultFound as ex:
            self.request.errors.add('body', None, str(ex))


@resource(name='_orgs_children',
          factory=ACLResource, permission='api',
          collection_path='/orgs/{parent_id}/subs/',
          path='/orgs/{parent_id}/subs/1')
class OrgChildrenResource(object):
    def __init__(self, request, context=None):
        self.request = request
        self.context = context
    
    @use_args_with(OrganisationFilterSchema)
    def collection_get(self, filters):
        db = self.request.db
        kw = {'deleted': False, 'subtype': PartyType.organisation}
        try:
            kw.update({'parent_id': self.request.matchdict['parent_id']})
            query = db.query(Organisation).filter_by(**kw)
            if filters != None:
                query = query.filter_by(**filters._as_dict())
            
            query = query.order_by(Organisation.id)
            schema = OrganisationSchema(many=True)
            jresult = schema.dump(query.all())
            return jresult.data
        except exc.NoResultFound as ex:
            self.request.errors.add('body', None, str(ex))
    
    def collection_post(self):
        db, schema = (self.request.db, OrganisationSchema())
        result = schema.load(self.request.json, db, partial=['id'])
        if result.errors:
            self.request.errors.add('body', None, result.errors)
            return
        # todo: further verification
        db.add(result.data)
        db.flush()

        jresult = schema.dump(result.data)
        return jresult.data
    
    def get(self):
        db = self.request.db
        kw = {'deleted': False, 'subtype': PartyType.organisation}
        try:
            kw.update({
                'id': self.request.matchdict['id'],
                'parent_id': self.request.matchdict['parent_id'],
            })
            query = db.query(Organisation).filter_by(**kw)
            schena = OrganisationSchema()
            jresult = schema.dump(query.one())
            return jresult.data
        except exc.NoResultFound as ex:
            self.request.errors.add('body', None, str(ex))

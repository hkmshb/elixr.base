"""Contains schema definitions used to validate form inputs provided to create
corresponding model objects. Thus validation enforcement during deserialization
is critically important for these schemas.
"""
from enum import Enum
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema
from elixr.sax.orgz import PhoneContact, Organisation
from .network import (
    Voltage, ElectricStation, ElectricLine, Owner, StationType,
    LineType )



class ChoiceField(fields.Field):
    """Represents a schema field for serializing Choice model fields which works
    with :mod:`enum` in the standard library of Python 3.4+
    """
    def __init__(self, enum_class, *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)
        self.enum_class = enum_class
    
    def _deserialize(self, value, attr, data):
        if value is None:
            return value
        return self.enum_class(value)

    def _serialize(self, value, attr, obj):
        if value:
            if isinstance(value, Enum):
                return value.value
        return value


class VoltageSchema(ModelSchema):
    """A serializer for the Voltage model.
    """
    value = fields.Int(required=True)
    class Meta:
        model = Voltage


class ElectricStationSchema(ModelSchema):
    """A serializer for the ElectricStation model.
    """
    owner   = ChoiceField(Owner, required=True)
    subtype = ChoiceField(StationType, required=True)
    class Meta:
        model = ElectricStation


class ElectricLineSchema(ModelSchema):
    """A serializer for the ElectricLine model.
    """
    owner   = ChoiceField(Owner, required=True)
    subtype = ChoiceField(LineType, required=True)
    class Meta:
        model = ElectricLine


class ContactDetailSchema(ModelSchema):
    """A serializer for the PhoneContact model extended with fields for 
    EmailContact model as both model data gets store in a single table.
    """
    address = fields.Str()
    subtype = fields.Int()
    class Meta:
        model = PhoneContact


class OrganisationSchema(ModelSchema):
    """A serializer for the Organisation model.
    """
    contacts = fields.Nested(ContactDetailSchema, many=True)
    class Meta:
        model = Organisation
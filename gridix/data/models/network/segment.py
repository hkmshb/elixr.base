import enum
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, Boolean, DateTime, ForeignKey, Integer, 
    String, Text, Table, UniqueConstraint
)
from elixr.sax.types import Choice
from elixr.sax.orgz import Organisation
from ..base import Model, IdTimestampMixin, UUIDMixin
from .common import Owner, Voltage



class LineType(enum.Enum):
    """Indicates the categorization for an electric line.
    """
    feeder  = 1
    upriser = 2


# many-to-many relation between lines and orgs
electric_lines_orgs = Table(
    'electric_lines_orgs',
    Model.metadata,
    Column('electric_line_id', Integer, ForeignKey('electric_lines.id')),
    Column('organisation_id', Integer, ForeignKey('organisations.id'))
)


class ElectricLine(Model, IdTimestampMixin, UUIDMixin):
    """A model to represent electric lines of varying voltage levels within the
    electric network.
    """
    __tablename__ = 'electric_lines'
    
    name = Column(String(30), nullable=False, unique=True)
    line_code = Column(String(32), nullable=False, unique=True)
    register_code = Column(String(32), nullable=True, unique=True)
    owner   = Column(Choice(Owner), nullable=False)
    is_public = Column(Boolean(create_constraint=False), nullable=False, 
                        default=True)
    subtype = Column(Choice(LineType), nullable=False)
    voltage_id = Column(Integer, ForeignKey('voltages.id'), nullable=False)
    voltage    = relationship("Voltage")
    source_station_id = Column(Integer, ForeignKey('electric_stations.id'), nullable=False)
    source_station = relationship("ElectricStation", foreign_keys=[source_station_id],
                        backref="electric_lines")
    date_commissioned = Column(DateTime)
    deleted = Column(Boolean(create_constraint=False), default=False)
    comments = Column(Text)
    organisations = relationship("Organisation", secondary="electric_lines_orgs",
                        lazy="joined")
    
    def __str__(self):
        return self.name
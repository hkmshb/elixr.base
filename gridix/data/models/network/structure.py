import enum
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, Boolean, DateTime, ForeignKey, Integer, 
    String, Text, UniqueConstraint
)
from elixr.sax.address import AddressMixin, CoordinatesMixin
from elixr.sax.orgz import Organisation
from elixr.sax.types import Choice
from ..base import Model, IdTimestampMixin, UUIDMixin
from .common import Owner



## ENUMS
class StationType(enum.Enum):
    """Indicates the position/role of and ElectricStation within an electric
    power network.
    """
    transmission = 1
    injection    = 2
    distribution = 3


## MODELS
class StructureMixin(IdTimestampMixin, UUIDMixin, CoordinatesMixin):
    """A base model mixin for features that support electrical transmission and 
    distribution equipment.

    :facility_code: internal, company assigned unique identifier.
    :register_code: a standardized unique identifier used by regulatory body for
                    the power sector.
    """
    facility_code = Column(String(32), nullable=False, unique=True)
    register_code = Column(String(32), nullable=True, unique=True)
    owner = Column(Choice(Owner), nullable=False)
    date_installed = Column(DateTime)
    deleted = Column(Boolean(create_constraint=False), default=False)
    comments = Column(Text)


class ElectricStation(Model, StructureMixin, AddressMixin):
    """A model which represents a building or fenced-in enclosure that houses
    the equipment that switches and modifieds the characteristics of energy
    from a generation source.
    """
    __tablename__ = 'electric_stations'
    __table_args__ = (
        UniqueConstraint('subtype', 'name', name='uq_station_subtype_name'),
    )

    name  = Column(String(50), nullable=False)
    subtype = Column(Choice(StationType), nullable=False)
    is_public = Column(Boolean(create_constraint=False), nullable=False, default=True)
    is_manned = Column(Boolean(create_constraint=False), nullable=False, default=True)
    is_automated = Column(Boolean(create_constraint=False), nullable=False, default=False)
    source_line_id = Column(Integer, ForeignKey("electric_lines.id"))
    source_line    = relationship("ElectricLine", foreign_keys=[source_line_id])
    organisation_id = Column(Integer, ForeignKey("organisations.id"))
    organisation    = relationship("Organisation", foreign_keys=[organisation_id])
    
    @property
    def date_commissioned(self):
        return self.date_installed
    
    def __str__(self):
        return self.name

import enum
from sqlalchemy import Column, Boolean, Integer
from ..base import Model, IdTimestampMixin, UUIDMixin



## ENUMS
class Owner(enum.Enum):
    """Indicates the ownership of a particular 'entity' within the electric
    distribution network.
    """
    company  = 1
    customer = 2
    other_utility = 3


## MODELS
class Voltage(Model, IdTimestampMixin, UUIDMixin):
    """Represents an electrical voltage level for electric lines and power
    devices/equipment within an electric distribution network.
    """
    __tablename__ = 'voltages'
    value = Column(Integer, nullable=False, unique=True)
    deleted = Column(Boolean(create_constraint=False), default=False)

    def __str__(self):
        if self.value in (0, 1):
            return "%s Volt" % self.value
        return "%s Volts" % self.value

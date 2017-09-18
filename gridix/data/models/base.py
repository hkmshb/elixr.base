import enum
from elixr.sax import ( 
    BASE, 
    Model, 
    IdMixin, 
    TimestampMixin, 
    IdTimestampMixin, 
    UUIDMixin 
)


# general enum type
class OrgFnType(enum.Enum):
    hq      = 1
    region  = 2
    tech_sp = 3
    cust_sp = 4

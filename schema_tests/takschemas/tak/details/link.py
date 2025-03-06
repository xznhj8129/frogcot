from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata.models.datatype import XmlDateTime
from xsdata_pydantic.fields import field


class Link(BaseModel):
    """
    :ivar point: concise version described as lat,lon,altHAE or lat,lon
        without an altitude
    :ivar parent_callsign:
    :ivar production_time:
    :ivar relation:
    :ivar type_value:
    :ivar uid:
    :ivar callsign:
    :ivar remarks:
    """

    class Meta:
        name = "link"

    model_config = ConfigDict(defer_build=True)
    point: str = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    parent_callsign: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    production_time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    relation: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    uid: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    callsign: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    remarks: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )

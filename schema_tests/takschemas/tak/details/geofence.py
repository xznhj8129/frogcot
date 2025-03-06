from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Geofence(BaseModel):
    class Meta:
        name = "__geofence"

    model_config = ConfigDict(defer_build=True)
    elevation_monitored: bool = field(
        metadata={
            "name": "elevationMonitored",
            "type": "Attribute",
            "required": True,
        }
    )
    min_elevation: Decimal = field(
        metadata={
            "name": "minElevation",
            "type": "Attribute",
            "required": True,
        }
    )
    monitor: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    trigger: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    tracking: bool = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    max_elevation: Decimal = field(
        metadata={
            "name": "maxElevation",
            "type": "Attribute",
            "required": True,
        }
    )
    bounding_sphere: Decimal = field(
        metadata={
            "name": "boundingSphere",
            "type": "Attribute",
            "required": True,
        }
    )

from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Environment(BaseModel):
    class Meta:
        name = "environment"

    model_config = ConfigDict(defer_build=True)
    temperature: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    wind_direction: Decimal = field(
        metadata={
            "name": "windDirection",
            "type": "Attribute",
            "required": True,
        }
    )
    wind_speed: Decimal = field(
        metadata={
            "name": "windSpeed",
            "type": "Attribute",
            "required": True,
        }
    )

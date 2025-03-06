from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class StrokeWeight(BaseModel):
    class Meta:
        name = "strokeWeight"

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

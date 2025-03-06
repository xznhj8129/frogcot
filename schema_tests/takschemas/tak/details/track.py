from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Track(BaseModel):
    class Meta:
        name = "track"

    model_config = ConfigDict(defer_build=True)
    course: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    slope: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    speed: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

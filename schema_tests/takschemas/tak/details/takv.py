from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Takv(BaseModel):
    class Meta:
        name = "takv"

    model_config = ConfigDict(defer_build=True)
    device: Optional[object] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    os: Optional[object] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    platform: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    version: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

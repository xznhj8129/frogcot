from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Emergency(BaseModel):
    class Meta:
        name = "emergency"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    cancel: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    type_value: Optional[object] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )

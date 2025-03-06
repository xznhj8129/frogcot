from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Status(BaseModel):
    class Meta:
        name = "status"

    model_config = ConfigDict(defer_build=True)
    battery: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    readiness: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )

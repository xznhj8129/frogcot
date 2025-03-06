from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Uid(BaseModel):
    class Meta:
        name = "uid"

    model_config = ConfigDict(defer_build=True)
    droid: str = field(
        metadata={
            "name": "Droid",
            "type": "Attribute",
            "required": True,
        }
    )
    nett: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )

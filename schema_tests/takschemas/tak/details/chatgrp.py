from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Chatgrp(BaseModel):
    class Meta:
        name = "chatgrp"

    model_config = ConfigDict(defer_build=True)
    id: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    uid0: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    uid1: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    uid2: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )

from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Contact(BaseModel):
    class Meta:
        name = "contact"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    uid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Group(BaseModel):
    class Meta:
        name = "group"

    model_config = ConfigDict(defer_build=True)
    contact: list[Contact] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    group: Optional["Group"] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    uid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Hierarchy(BaseModel):
    class Meta:
        name = "hierarchy"

    model_config = ConfigDict(defer_build=True)
    group: Group = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )

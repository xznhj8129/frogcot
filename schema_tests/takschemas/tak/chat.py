from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata.models.datatype import XmlDateTime
from xsdata_pydantic.fields import field

from takschemas.tak.details.chat import Chat
from takschemas.tak.details.chatreceipt import Chatreceipt
from takschemas.tak.event.point import EventPoint


class LinkType(BaseModel):
    class Meta:
        name = "linkType"

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
    type_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    relation: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class RemarksType(BaseModel):
    class Meta:
        name = "remarksType"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    source: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    source_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "sourceID",
            "type": "Attribute",
        },
    )
    to: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class DetailType(BaseModel):
    class Meta:
        name = "detailType"

    model_config = ConfigDict(defer_build=True)
    chat: Chat = field(
        metadata={
            "name": "__chat",
            "type": "Element",
            "required": True,
        }
    )
    link: list[LinkType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 2,
        },
    )
    remarks: Optional[RemarksType] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    chatreceipt: Optional[Chatreceipt] = field(
        default=None,
        metadata={
            "name": "__chatreceipt",
            "type": "Element",
        },
    )


class EventType(BaseModel):
    class Meta:
        name = "eventType"

    model_config = ConfigDict(defer_build=True)
    point: EventPoint = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    detail: DetailType = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    version: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    uid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    type_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    start: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    stale: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    how: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Event(EventType):
    class Meta:
        name = "event"

    model_config = ConfigDict(defer_build=True)

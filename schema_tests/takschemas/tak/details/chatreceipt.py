from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

from takschemas.tak.details.chatgrp import Chatgrp


class Chatreceipt(BaseModel):
    class Meta:
        name = "__chatreceipt"

    model_config = ConfigDict(defer_build=True)
    chatgrp: Chatgrp = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    chatroom: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    group_owner: bool = field(
        metadata={
            "name": "groupOwner",
            "type": "Attribute",
            "required": True,
        }
    )
    id: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    parent: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    sender_callsign: str = field(
        metadata={
            "name": "senderCallsign",
            "type": "Attribute",
            "required": True,
        }
    )
    message_id: Optional[object] = field(
        default=None,
        metadata={
            "name": "messageId",
            "type": "Attribute",
        },
    )

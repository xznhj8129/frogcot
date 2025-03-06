from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Contact(BaseModel):
    class Meta:
        name = "contact"

    model_config = ConfigDict(defer_build=True)
    callsign: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    email_address: Optional[object] = field(
        default=None,
        metadata={
            "name": "emailAddress",
            "type": "Attribute",
        },
    )
    endpoint: Optional[object] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    phone: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    xmpp_username: Optional[object] = field(
        default=None,
        metadata={
            "name": "xmppUsername",
            "type": "Attribute",
        },
    )

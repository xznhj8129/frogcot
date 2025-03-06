from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Fileshare(BaseModel):
    class Meta:
        name = "fileshare"

    model_config = ConfigDict(defer_build=True)
    filename: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    name: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    sender_callsign: str = field(
        metadata={
            "name": "senderCallsign",
            "type": "Attribute",
            "required": True,
        }
    )
    sender_uid: str = field(
        metadata={
            "name": "senderUid",
            "type": "Attribute",
            "required": True,
        }
    )
    sender_url: str = field(
        metadata={
            "name": "senderUrl",
            "type": "Attribute",
            "required": True,
        }
    )
    sha256: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    size_in_bytes: int = field(
        metadata={
            "name": "sizeInBytes",
            "type": "Attribute",
            "required": True,
        }
    )

from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from xsdata.models.datatype import XmlDateTime
from xsdata_pydantic.fields import field

from takschemas.tak.details.color import DetailColor
from takschemas.tak.details.contact import Contact
from takschemas.tak.details.link import Link
from takschemas.tak.details.precisionlocation import Precisionlocation
from takschemas.tak.details.remarks import Remarks
from takschemas.tak.details.status import Status
from takschemas.tak.details.usericon import Usericon


class Event(BaseModel):
    class Meta:
        name = "event"

    model_config = ConfigDict(defer_build=True)
    point: str = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    detail: "Event.Detail" = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    version: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    uid: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    time: XmlDateTime = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    start: XmlDateTime = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    stale: XmlDateTime = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    how: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

    class Detail(BaseModel):
        """
        :ivar status:
        :ivar archive:
        :ivar precisionlocation:
        :ivar usericon: 2525 icons use the following template for
            iconsetpath:
            "COT_MAPPING_2525B/a-AFFILIATION/a-AFFILIATION-..." where
            AFFILIATION is one of: "u" - Unknown "f" - Friend "n" -
            Neutral "h" - Hostile and ... is the remaining CoT type that
            defines the 2525 icon (See CoT Base-Event Schema  (PUBLIC
            RELEASE).xsd for more details)
        :ivar link: Link should reference the TAK instance's SA event
            that produces it. For instance, for a TAK instance with uid,
            'ANDROID-589520ccfcd20f01', callsign, 'HOPE', and type 'a-f-
            G-U-C', the following link attributes values apply:
            uid='ANDROID-589520ccfcd20f01'
            production_time='2020-12-16T19:50:57.629Z' type='a-f-G-U-C'
            parent_callsign='HOPE' relation='p-p'
        :ivar contact:
        :ivar color:
        :ivar remarks:
        """

        model_config = ConfigDict(defer_build=True)
        status: list[Status] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )
        archive: list[object] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )
        precisionlocation: list[Precisionlocation] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )
        usericon: list[Usericon] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )
        link: list[Link] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )
        contact: list[Contact] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )
        color: list[DetailColor] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )
        remarks: list[Remarks] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )

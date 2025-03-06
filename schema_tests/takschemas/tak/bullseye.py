from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict
from xsdata.models.datatype import XmlDateTime
from xsdata_pydantic.fields import field

from takschemas.tak.details.contact import Contact
from takschemas.tak.details.precisionlocation import Precisionlocation
from takschemas.tak.details.remarks import Remarks
from takschemas.tak.event.point import EventPoint


class BullseyeBearingRef(Enum):
    T = "T"
    M = "M"
    G = "G"


class Event(BaseModel):
    class Meta:
        name = "event"

    model_config = ConfigDict(defer_build=True)
    point: EventPoint = field(
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
        model_config = ConfigDict(defer_build=True)
        archive: list[object] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )
        bullseye: list["Event.Detail.Bullseye"] = field(
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
        remarks: list[Remarks] = field(
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

        class Bullseye(BaseModel):
            """
            :ivar mils:
            :ivar distance:
            :ivar bearing_ref: "M" magnetic north "T" true north "G"
                grid north
            :ivar bullseye_uid:
            :ivar distance_units:
            :ivar edge_to_center:
            :ivar range_ring_visible:
            :ivar title:
            :ivar has_range_rings:
            """

            model_config = ConfigDict(defer_build=True)
            mils: bool = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            distance: Decimal = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            bearing_ref: BullseyeBearingRef = field(
                metadata={
                    "name": "bearingRef",
                    "type": "Attribute",
                    "required": True,
                }
            )
            bullseye_uid: str = field(
                metadata={
                    "name": "bullseyeUID",
                    "type": "Attribute",
                    "required": True,
                }
            )
            distance_units: str = field(
                const=True,
                default="u-r-b-bullseye",
                metadata={
                    "name": "distanceUnits",
                    "type": "Attribute",
                    "required": True,
                },
            )
            edge_to_center: bool = field(
                metadata={
                    "name": "edgeToCenter",
                    "type": "Attribute",
                    "required": True,
                }
            )
            range_ring_visible: bool = field(
                metadata={
                    "name": "rangeRingVisible",
                    "type": "Attribute",
                    "required": True,
                }
            )
            title: str = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            has_range_rings: bool = field(
                metadata={
                    "name": "hasRangeRings",
                    "type": "Attribute",
                    "required": True,
                }
            )

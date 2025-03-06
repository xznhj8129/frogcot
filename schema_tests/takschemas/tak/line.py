from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata.models.datatype import XmlDateTime
from xsdata_pydantic.fields import field

from takschemas.tak.details.contact import Contact
from takschemas.tak.details.labels_on import LabelsOn
from takschemas.tak.details.remarks import Remarks
from takschemas.tak.details.stroke_color import StrokeColor
from takschemas.tak.details.stroke_weight import StrokeWeight
from takschemas.tak.event.point import EventPoint


class BearingUnits(Enum):
    VALUE_0 = 0
    VALUE_1 = 1
    VALUE_2 = 2


class NorthRef(Enum):
    VALUE_0 = 0
    VALUE_1 = 1
    VALUE_2 = 2


class RangeUnits(Enum):
    VALUE_0 = 0
    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_3 = 3
    VALUE_4 = 4
    VALUE_5 = 5


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
        const=True,
        default="u-rb-a",
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
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
        range: "Event.Detail.Range" = field(
            metadata={
                "type": "Element",
                "required": True,
            }
        )
        bearing: "Event.Detail.Bearing" = field(
            metadata={
                "type": "Element",
                "required": True,
            }
        )
        inclination: "Event.Detail.Inclination" = field(
            metadata={
                "type": "Element",
                "required": True,
            }
        )
        range_units: "Event.Detail.RangeUnits" = field(
            metadata={
                "name": "rangeUnits",
                "type": "Element",
                "required": True,
            }
        )
        bearing_units: "Event.Detail.BearingUnits" = field(
            metadata={
                "name": "bearingUnits",
                "type": "Element",
                "required": True,
            }
        )
        north_ref: "Event.Detail.NorthRef" = field(
            metadata={
                "name": "northRef",
                "type": "Element",
                "required": True,
            }
        )
        stroke_color: StrokeColor = field(
            metadata={
                "name": "strokeColor",
                "type": "Element",
                "required": True,
            }
        )
        stroke_weight: StrokeWeight = field(
            metadata={
                "name": "strokeWeight",
                "type": "Element",
                "required": True,
            }
        )
        contact: Contact = field(
            metadata={
                "type": "Element",
                "required": True,
            }
        )
        remarks: Remarks = field(
            metadata={
                "type": "Element",
                "required": True,
            }
        )
        archive: Optional[object] = field(
            default=None,
            metadata={
                "type": "Element",
            },
        )
        labels_on: LabelsOn = field(
            metadata={
                "type": "Element",
                "required": True,
            }
        )
        color: "Event.Detail.Color" = field(
            metadata={
                "type": "Element",
                "required": True,
            }
        )

        class Range(BaseModel):
            """
            :ivar value: The range distance
            """

            model_config = ConfigDict(defer_build=True)
            value: Decimal = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )

        class Bearing(BaseModel):
            """
            :ivar value: The bearing angle
            """

            model_config = ConfigDict(defer_build=True)
            value: Decimal = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )

        class Inclination(BaseModel):
            """
            :ivar value: The slope angle
            """

            model_config = ConfigDict(defer_build=True)
            value: Decimal = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )

        class RangeUnits(BaseModel):
            """
            :ivar value: 0 - kilometers 1 - meters 2 - miles 3 - yards 4
                - feet 5 - nautical miles
            """

            model_config = ConfigDict(defer_build=True)
            value: RangeUnits = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )

        class BearingUnits(BaseModel):
            """
            :ivar value: 0 - degrees 1 - mils 2 - radians
            """

            model_config = ConfigDict(defer_build=True)
            value: BearingUnits = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )

        class NorthRef(BaseModel):
            """
            :ivar value: 0 - true north 1 - magnetic north 2 - grid
                north
            """

            model_config = ConfigDict(defer_build=True)
            value: NorthRef = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )

        class Color(BaseModel):
            model_config = ConfigDict(defer_build=True)
            value: int = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )

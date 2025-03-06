from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata.models.datatype import XmlDateTime
from xsdata_pydantic.fields import field

from takschemas.tak.details.contact import Contact
from takschemas.tak.details.remarks import Remarks
from takschemas.tak.details.stroke_color import StrokeColor
from takschemas.tak.details.stroke_weight import StrokeWeight
from takschemas.tak.event.point import EventPoint


class RouteFil(Enum):
    INFIL = "Infil"
    EXFIL = "Exfil"


class RouteMethod(Enum):
    DRIVING = "Driving"
    WALKING = "Walking"
    FLYING = "Flying"
    SWIMMING = "Swimming"
    WATERCRAFT = "Watercraft"


class RouteOrder(Enum):
    ASCENDING_CHECK_POINTS = "Ascending Check Points"
    DESCENDING_CHECK_POINTS = "Descending Check Points"


class RouteRoutetype(Enum):
    PRIMARY = "Primary"
    SECONDARY = "Secondary"


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
        default="b-m-r",
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
        link: list["Event.Detail.Link"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            },
        )
        link_attr: "Event.Detail.LinkAttr" = field(
            metadata={
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
        routeinfo: "Event.Detail.Routeinfo" = field(
            metadata={
                "name": "__routeinfo",
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
        labels_on: str = field(
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

        class Link(BaseModel):
            """
            :ivar uid:
            :ivar callsign:
            :ivar type_value: Common types: "b-m-p-c" Control Point
                "b-m-p-w" Waypoint
            :ivar point: Format: "Lat,Lng" decimal values
            :ivar remarks:
            :ivar relation: Common values: "c"
            """

            model_config = ConfigDict(defer_build=True)
            uid: str = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            callsign: str = field(
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
            point: str = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            remarks: str = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            relation: str = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )

        class LinkAttr(BaseModel):
            model_config = ConfigDict(defer_build=True)
            planningmethod: RouteFil = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            color: int = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            method: RouteMethod = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            prefix: str = field(
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
            stroke: int = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            direction: RouteFil = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            routetype: RouteRoutetype = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            order: RouteOrder = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )

        class Routeinfo(BaseModel):
            model_config = ConfigDict(defer_build=True)
            navcues: Optional[object] = field(
                default=None,
                metadata={
                    "name": "__navcues",
                    "type": "Element",
                },
            )

        class Color(BaseModel):
            model_config = ConfigDict(defer_build=True)
            value: int = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )

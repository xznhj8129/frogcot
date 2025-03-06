from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata.models.datatype import XmlDateTime
from xsdata_pydantic.fields import field

from takschemas.tak.details.contact import Contact
from takschemas.tak.details.fill_color import FillColor
from takschemas.tak.details.labels_on import LabelsOn
from takschemas.tak.details.precisionlocation import Precisionlocation
from takschemas.tak.details.remarks import Remarks
from takschemas.tak.details.shape import ShapeEllipse
from takschemas.tak.details.stroke_color import StrokeColor
from takschemas.tak.details.stroke_weight import StrokeWeight
from takschemas.tak.event.point import EventPoint


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
        default="u-r-b-c-c",
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
        shape: "Event.Detail.Shape" = field(
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
        fill_color: FillColor = field(
            metadata={
                "name": "fillColor",
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
        precisionlocation: Precisionlocation = field(
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

        class Shape(BaseModel):
            model_config = ConfigDict(defer_build=True)
            ellipse: ShapeEllipse = field(
                metadata={
                    "type": "Element",
                    "required": True,
                }
            )
            link: ShapeEllipse = field(
                metadata={
                    "type": "Element",
                    "required": True,
                }
            )

        class Color(BaseModel):
            model_config = ConfigDict(defer_build=True)
            argb: int = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )

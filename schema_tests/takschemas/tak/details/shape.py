from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

from takschemas.tak.details.color import Color


class Alpha(BaseModel):
    class Meta:
        name = "alpha"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
        }
    )


class ShapeEllipse(BaseModel):
    class Meta:
        name = "shape_ellipse"

    model_config = ConfigDict(defer_build=True)
    angle: int = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    major: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    minor: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class Vertex(BaseModel):
    class Meta:
        name = "vertex"

    model_config = ConfigDict(defer_build=True)
    hae: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    lat: float = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    lon: float = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class Width(BaseModel):
    class Meta:
        name = "width"

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "required": True,
        }
    )


class Color1(BaseModel):
    class Meta:
        name = "color"

    model_config = ConfigDict(defer_build=True)
    color: Color = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )


class Ellipse(ShapeEllipse):
    class Meta:
        name = "ellipse"

    model_config = ConfigDict(defer_build=True)


class ShapePolyline(BaseModel):
    class Meta:
        name = "shape_polyline"

    model_config = ConfigDict(defer_build=True)
    vertex: list[Vertex] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    closed: bool = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class LineStyle(Color1):
    model_config = ConfigDict(defer_build=True)
    width: Width = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    alpha: Optional[Alpha] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class PolyStyle(Color1):
    pass
    model_config = ConfigDict(defer_build=True)


class Polyline(ShapePolyline):
    class Meta:
        name = "polyline"

    model_config = ConfigDict(defer_build=True)


class Style(BaseModel):
    model_config = ConfigDict(defer_build=True)
    line_style: LineStyle = field(
        metadata={
            "name": "LineStyle",
            "type": "Element",
            "required": True,
        }
    )
    poly_style: PolyStyle = field(
        metadata={
            "name": "PolyStyle",
            "type": "Element",
            "required": True,
        }
    )


class ShapeLink(BaseModel):
    class Meta:
        name = "shape_link"

    model_config = ConfigDict(defer_build=True)
    style: Optional[Style] = field(
        default=None,
        metadata={
            "name": "Style",
            "type": "Element",
        },
    )
    relation: str = field(
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
    uid: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class Link(ShapeLink):
    class Meta:
        name = "link"

    model_config = ConfigDict(defer_build=True)


class Shape(BaseModel):
    class Meta:
        name = "shape"

    model_config = ConfigDict(defer_build=True)
    polyline: Optional[Polyline] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    ellipse: Optional[Ellipse] = field(
        default=None,
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

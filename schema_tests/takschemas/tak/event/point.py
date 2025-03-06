from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class EventPoint(BaseModel):
    """
    :ivar lat: Latitude based on WGS-84 ellipsoid in signed degree-
        decimal format (e.g. -33.350000). Range -90 -&gt; +90.
    :ivar lon: Longitude based on WGS-84 ellipsoid in signed degree-
        decimal format (e.g. 44.383333). Range -180 -&gt; +180.
    :ivar hae: HAE acronym for Height above Ellipsoid based on WGS-84
        ellipsoid (measured in meters).
    :ivar ce: Circular Error around point defined by lat and lon fields
        in meters. Although named ce, this field is intended to define a
        circular area around the event point, not necessarily an error
        (e.g. Describing a reservation area is not an "error").  If it
        is appropriate for the "ce" field to represent an error value
        (e.g. event describes laser designated target), the value will
        represent the one sigma point for a zero mean normal (Guassian)
        distribution.
    :ivar le: Linear Error in meters associated with the HAE field.
        Although named le, this field is intended to define a height
        range about the event point, not necessarily an error. This
        field, along with the ce field allow for the definition of a
        cylindrical volume about the point. If it is appropriate for the
        "le" field to represent an error (e.g. event describes laser
        designated target), the value will represent the one sigma point
        for a zero mean normal (Guassian) distribution.
    """

    class Meta:
        name = "event_point"

    model_config = ConfigDict(defer_build=True)
    lat: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("-90"),
            "max_inclusive": Decimal("90"),
        }
    )
    lon: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        }
    )
    hae: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    ce: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    le: Decimal = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

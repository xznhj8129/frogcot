from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Precisionlocation(BaseModel):
    """
    :ivar geopointsrc:
    :ivar altsrc: Common values: ??? - Unknown DTED0 DTED1 DTED2 DTED3
        LIDAR USER GPS SRTM1 COT CALC ESTIMATED RTK DGPS GPS_PPS
    :ivar precise_image_file:
    :ivar precise_image_file_x:
    :ivar precise_image_file_y:
    """

    class Meta:
        name = "precisionlocation"

    model_config = ConfigDict(defer_build=True)
    geopointsrc: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    altsrc: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    precise_image_file: Optional[str] = field(
        default=None,
        metadata={
            "name": "PRECISE_IMAGE_FILE",
            "type": "Attribute",
        },
    )
    precise_image_file_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "PRECISE_IMAGE_FILE_X",
            "type": "Attribute",
        },
    )
    precise_image_file_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "PRECISE_IMAGE_FILE_Y",
            "type": "Attribute",
        },
    )

from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata.models.datatype import XmlDateTime
from xsdata_pydantic.fields import field


class Remarks(BaseModel):
    class Meta:
        name = "remarks"

    model_config = ConfigDict(defer_build=True)
    source: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    source_id: Optional[object] = field(
        default=None,
        metadata={
            "name": "sourceID",
            "type": "Attribute",
        },
    )
    time: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    to: Optional[object] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    content: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
        },
    )

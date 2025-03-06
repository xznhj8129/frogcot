from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class DetailColor(BaseModel):
    class Meta:
        name = "detail_color"

    model_config = ConfigDict(defer_build=True)
    argb: int = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class Color(DetailColor):
    class Meta:
        name = "color"

    model_config = ConfigDict(defer_build=True)

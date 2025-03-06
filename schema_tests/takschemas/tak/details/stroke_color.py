from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class StrokeColor(BaseModel):
    class Meta:
        name = "strokeColor"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

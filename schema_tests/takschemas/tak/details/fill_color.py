from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class FillColor(BaseModel):
    class Meta:
        name = "fillColor"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

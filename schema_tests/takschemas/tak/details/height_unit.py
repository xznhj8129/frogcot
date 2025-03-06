from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class HeightUnit(BaseModel):
    class Meta:
        name = "height_unit"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
        }
    )

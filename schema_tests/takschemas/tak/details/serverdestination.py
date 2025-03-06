from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Serverdestination(BaseModel):
    class Meta:
        name = "__serverdestination"

    model_config = ConfigDict(defer_build=True)
    destinations: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

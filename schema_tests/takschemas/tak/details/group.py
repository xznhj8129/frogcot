from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Group(BaseModel):
    class Meta:
        name = "__group"

    model_config = ConfigDict(defer_build=True)
    name: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    role: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

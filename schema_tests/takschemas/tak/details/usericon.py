from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Usericon(BaseModel):
    class Meta:
        name = "usericon"

    model_config = ConfigDict(defer_build=True)
    iconsetpath: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Video(BaseModel):
    class Meta:
        name = "__video"

    model_config = ConfigDict(defer_build=True)
    url: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

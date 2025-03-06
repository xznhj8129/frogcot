from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class LabelsOn(BaseModel):
    class Meta:
        name = "labels_on"

    model_config = ConfigDict(defer_build=True)
    value: bool = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

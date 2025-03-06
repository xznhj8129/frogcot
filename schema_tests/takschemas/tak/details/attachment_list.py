from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class AttachmentList(BaseModel):
    class Meta:
        name = "attachment_list"

    model_config = ConfigDict(defer_build=True)
    hashes: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

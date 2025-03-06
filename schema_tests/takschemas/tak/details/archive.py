from pydantic import BaseModel, ConfigDict


class Archive(BaseModel):
    class Meta:
        name = "archive"

    model_config = ConfigDict(defer_build=True)

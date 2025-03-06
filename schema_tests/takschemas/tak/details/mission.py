from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata.models.datatype import XmlDateTime
from xsdata_pydantic.fields import field

from takschemas.tak.details.uid import Uid


class ContentUid(BaseModel):
    class Meta:
        name = "contentUid"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class CreatorUid(BaseModel):
    class Meta:
        name = "creatorUid"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class Details(BaseModel):
    class Meta:
        name = "details"

    model_config = ConfigDict(defer_build=True)
    callsign: Optional[object] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    iconset_path: Optional[object] = field(
        default=None,
        metadata={
            "name": "iconsetPath",
            "type": "Attribute",
        },
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )


class Filename(BaseModel):
    class Meta:
        name = "filename"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class Hash(BaseModel):
    class Meta:
        name = "hash"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class Keywords(BaseModel):
    class Meta:
        name = "keywords"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class MimeType(BaseModel):
    class Meta:
        name = "mimeType"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class MissionName(BaseModel):
    class Meta:
        name = "missionName"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class Name(BaseModel):
    class Meta:
        name = "name"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class Size(BaseModel):
    class Meta:
        name = "size"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
        }
    )


class SubmissionTime(BaseModel):
    class Meta:
        name = "submissionTime"

    model_config = ConfigDict(defer_build=True)
    value: XmlDateTime = field(
        metadata={
            "required": True,
        }
    )


class Submitter(BaseModel):
    class Meta:
        name = "submitter"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class Timestamp(BaseModel):
    class Meta:
        name = "timestamp"

    model_config = ConfigDict(defer_build=True)
    value: XmlDateTime = field(
        metadata={
            "required": True,
        }
    )


class Tool(BaseModel):
    class Meta:
        name = "tool"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class Type(BaseModel):
    class Meta:
        name = "type"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class UrlData(BaseModel):
    class Meta:
        name = "urlData"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class UrlView(BaseModel):
    class Meta:
        name = "urlView"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class ContentResource(BaseModel):
    class Meta:
        name = "contentResource"

    model_config = ConfigDict(defer_build=True)
    creator_uid: Optional[CreatorUid] = field(
        default=None,
        metadata={
            "name": "creatorUid",
            "type": "Element",
        },
    )
    filename: Optional[Filename] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    hash: Hash = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    keywords: list[Keywords] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    mime_type: MimeType = field(
        metadata={
            "name": "mimeType",
            "type": "Element",
            "required": True,
        }
    )
    name: Name = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    size: Size = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    submission_time: SubmissionTime = field(
        metadata={
            "name": "submissionTime",
            "type": "Element",
            "required": True,
        }
    )
    submitter: Submitter = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    tool: Optional[Tool] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    uid: Uid = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )


class ExternalData(BaseModel):
    class Meta:
        name = "externalData"

    model_config = ConfigDict(defer_build=True)
    uid: Uid = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    name: Name = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    tool: Tool = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    url_data: UrlData = field(
        metadata={
            "name": "urlData",
            "type": "Element",
            "required": True,
        }
    )
    url_view: UrlView = field(
        metadata={
            "name": "urlView",
            "type": "Element",
            "required": True,
        }
    )


class MissionChange(BaseModel):
    model_config = ConfigDict(defer_build=True)
    content_resource: Optional[ContentResource] = field(
        default=None,
        metadata={
            "name": "contentResource",
            "type": "Element",
        },
    )
    content_uid: Optional[ContentUid] = field(
        default=None,
        metadata={
            "name": "contentUid",
            "type": "Element",
        },
    )
    creator_uid: CreatorUid = field(
        metadata={
            "name": "creatorUid",
            "type": "Element",
            "required": True,
        }
    )
    external_data: Optional[ExternalData] = field(
        default=None,
        metadata={
            "name": "externalData",
            "type": "Element",
        },
    )
    mission_name: MissionName = field(
        metadata={
            "name": "missionName",
            "type": "Element",
            "required": True,
        }
    )
    timestamp: Timestamp = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    type_value: Type = field(
        metadata={
            "name": "type",
            "type": "Element",
            "required": True,
        }
    )
    details: Optional[Details] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class MissionChanges(BaseModel):
    model_config = ConfigDict(defer_build=True)
    mission_change: MissionChange = field(
        metadata={
            "name": "MissionChange",
            "type": "Element",
            "required": True,
        }
    )


class Mission(BaseModel):
    class Meta:
        name = "mission"

    model_config = ConfigDict(defer_build=True)
    mission_changes: Optional[MissionChanges] = field(
        default=None,
        metadata={
            "name": "MissionChanges",
            "type": "Element",
        },
    )
    author_uid: Optional[str] = field(
        default=None,
        metadata={
            "name": "authorUid",
            "type": "Attribute",
        },
    )
    name: object = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    tool: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )

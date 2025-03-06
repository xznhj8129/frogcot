import uuid
from datetime import datetime, timedelta

import importlib
import pkgutil
import json
from datetime import datetime as dt, timedelta
from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.models.datatype import XmlDateTime
from frogcot import *


import inspect
from pydantic import BaseModel
import typing
from decimal import Decimal
from pydantic import BaseModel

def simplify_type(annotation) -> str:
    """
    Convert a type annotation into a human-friendly string.
    For common types, returns a simplified name.
    For generics (like list, dict, or Optional), recursively simplifies.
    """
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)
    if origin is None:
        if annotation == str:
            return "string"
        elif annotation == int:
            return "int"
        elif annotation == float:
            return "float"
        elif annotation == bool:
            return "bool"
        elif annotation == Decimal:
            return "decimal"
        else:
            if hasattr(annotation, '__name__'):
                return annotation.__name__
            return str(annotation)
    else:
        if origin is list:
            if args:
                return f"list of {simplify_type(args[0])}"
            else:
                return "list"
        elif origin is dict:
            if len(args) == 2:
                return f"dict of {simplify_type(args[0])} to {simplify_type(args[1])}"
            else:
                return "dict"
        elif origin is typing.Union:
            # Optional[T] is represented as Union[T, NoneType]
            non_none = [arg for arg in args if arg is not type(None)]
            if len(non_none) == 1:
                return f"optional {simplify_type(non_none[0])}"
            else:
                return " or ".join(simplify_type(arg) for arg in args)
        else:
            return str(annotation)

def iter_top_level_models(package):
    """
    Recursively iterate over all top-level classes in the package that are:
      - Defined in the module (not imported from elsewhere)
      - Subclasses of BaseModel (but not BaseModel itself)
      - Top-level (ignores nested classes, which have a dot in their __qualname__)
    """
    for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        try:
            module = importlib.import_module(modname)
        except Exception as e:
            print(f"Skipping module {modname} due to import error: {e}")
            continue
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip nested classes (their __qualname__ contains a dot)
            if "." in obj.__qualname__:
                continue
            if obj.__module__ == modname and issubclass(obj, BaseModel) and obj is not BaseModel:
                yield modname, name, obj

def print_model_summary(package_name):
    """
    Imports the given package and prints a summary for every top-level Pydantic model found.
    For each field in the model (pulled from __fields__ or model_fields), only fields that carry
    xsdata metadata or extra metadata (i.e. those derived from the XSD) are shown.
    The summary includes:
      - Field name
      - Simplified type (e.g. "int", "string", "optional int", etc.)
      - Whether the field is required
      - Its default (if any)
      - Any xsdata or extra metadata attached to the field
    """
    try:
        package = importlib.import_module(package_name)
    except ImportError as e:
        print(f"Error importing package {package_name}: {e}")
        return
    x = ""
    bigdict = {}
    for modname, clsname, cls in iter_top_level_models(package):
        x+=f"Model: {clsname} (Module: {modname})\n"
        print(f"Model: {clsname} (Module: {modname})")
        # Rebuild the model if deferred build is enabled
        if hasattr(cls, "model_rebuild"):
            cls.model_rebuild()

        # Get fields from Pydantic v2 ("model_fields") or v1 ("__fields__")
        fields = getattr(cls, "model_fields", None) or getattr(cls, "__fields__", None) or {}
        if not fields:
            x+="  No fields found.\n"
            print("  No fields found.")
        else:
            for field_name, field_info in fields.items():
                # Only consider fields that have xsdata metadata (or extra metadata)
                xsdata_meta = getattr(field_info, "xsdata_metadata", None)
                extra_meta = field_info.field_info.extra if hasattr(field_info, "field_info") else {}
                if not xsdata_meta and not extra_meta:
                    continue

                field_type = simplify_type(field_info.annotation)
                required = field_info.is_required()
                # Only show a default if the field is not required and a default is defined.
                default = field_info.default if (not required and field_info.default is not None) else None

                x+=f"  Field: {field_name}\n    Type: {field_type}\n    Required: {required}\n"
                print(f"  Field: {field_name}")
                print(f"    Type: {field_type}")
                print(f"    Required: {required}")
                if default is not None:
                    print(f"    Default: {default}")
                    x+=f"    Default: {default}\n"
                if xsdata_meta:
                    print(f"    Default: {default}")
                    x+=f"    Default: {default}\n"
                if extra_meta:
                    print(f"    Extra metadata: {extra_meta}")
                    x+=f"    Extra metadata: {extra_meta}\n"
        print("-" * 40)
    with open("dump.txt","w+") as file:
        file.write(x)

import importlib
import json
import importlib
import json

def dump_models_json(package_name, json_file="dump.json"):
    """
    Imports the given package and finds every top-level Pydantic model.
    For each model, it extracts only the fields that have xsdata metadata or extra metadata.
    The models are grouped into a nested dictionary using the third part of the module name
    as the top key. Each field is represented as a dictionary with keys: "type",
    "required", and "default". The result is written to a JSON file.
    
    Example output structure:
    
    {
      "route": {
         "point": {"type": "EventPoint", "required": True, "default": None},
         "detail": {"type": "Detail", "required": True, "default": None},
         ...
      },
      ...
    }
    """
    try:
        package = importlib.import_module(package_name)
    except ImportError as e:
        print(f"Error importing package {package_name}: {e}")
        return

    schemas = {}

    for modname, clsname, cls in iter_top_level_models(package):
        # Rebuild the model if deferred build is enabled
        if hasattr(cls, "model_rebuild"):
            cls.model_rebuild()

        # Use the third part of the module name (e.g. "takschemas.tak.route") as the top key
        mod_parts = modname.split('.')
        top_key = mod_parts[2] if len(mod_parts) >= 3 else modname

        if top_key not in schemas:
            schemas[top_key] = {}

        # Get fields from Pydantic v2 ("model_fields") or v1 ("__fields__")
        fields = getattr(cls, "model_fields", None) or getattr(cls, "__fields__", None) or {}
        for field_name, field_info in fields.items():
            # Only include fields that have xsdata metadata or extra metadata.
            xsdata_meta = getattr(field_info, "xsdata_metadata", None)
            extra_meta = field_info.field_info.extra if hasattr(field_info, "field_info") else {}
            if not xsdata_meta and not extra_meta:
                continue

            field_type = simplify_type(field_info.annotation)
            required = field_info.is_required()
            if field_type.startswith("optional "):
                field_type = field_type[9:]
                if field_type == "object": field_type = "string"
                required = False
            # Get the default if available, but only if it's not required.
            default = field_info.default if (not required and field_info.default is not None) else None
            # If the default value is of type "PydanticUndefinedType", set it to None.
            if default is not None and default.__class__.__name__ == "PydanticUndefinedType":
                default = None

            schemas[top_key][field_name] = {
                "type": field_type,
                "required": required,
                "default": default,
            }

    with open(json_file, "w") as file:
        json.dump(schemas, file, indent=2)


dump_models_json("takschemas")

exit()
#print_all_functions("takschemas")


from takschemas.tak import Event
from takschemas.tak.event.point import EventPoint
from takschemas.tak.chat import Chat
from takschemas.tak.details.chatgrp import Chatgrp
from takschemas.tak.details import Link
from takschemas.tak.details import Remarks
from takschemas.tak.details import Takv
from takschemas.tak.details import Usericon
from takschemas.tak.details import Contact
from takschemas.tak.details import Color
from takschemas.tak.details.precisionlocation import Precisionlocation
print(Event.model_dump(mode='json'))

debug_model_schema(Takv)
debug_model_schema(EventPoint)
print(EventPoint.model_dump(self=EventPoint,mode='json'))

def generate_cot_time(offset: int = 0) -> XmlDateTime:
    return XmlDateTime.from_datetime(dt.utcnow() + timedelta(seconds=offset))

def geochat(self, msg, dest=None, to_team=None, pos=None) -> str:
    if to_team and not dest:
        to_callsign = to_team
        to_uid = to_team
    elif dest and not to_team:
        to_callsign = dest.callsign
        to_uid = dest.uid
    else:
        return ""
    my_callsign = self.callsign
    my_uid = self.uid
    msg_cottype = "b-t-f"
    msguid = str(uuid.uuid4())
    chat_parent = "TeamGroups" if to_team else "RootContactGroup"
    if pos is None:
        pos = {}
    lat = str(pos.get("lat", 0))
    lon = str(pos.get("lon", 0))
    hae = str(pos.get("alt", 0))
    ce = str(pos.get("ce", 0))
    le = str(pos.get("le", 0))
    event_obj = Event(
        version="2.0",
        unique_id=f"GeoChat.{my_uid}.{to_uid}.{msguid}",  # use unique_id instead of uid
        type_value=msg_cottype,                           # use type_value instead of type
        time=generate_cot_time(),
        start=generate_cot_time(),
        stale=generate_cot_time(60),
        how="m-g",
        point=EventPoint(
            lat=lat,
            lon=lon,
            hae=hae,
            ce=ce,
            le=le,
        ),
        detail=Event.Detail(
            type_value=self.cottype,  # required field in Detail
            takv=Takv(**self.takv),
            chat=Chat(
                parent=chat_parent,
                group_owner=False,
                message_id=str(uuid.uuid4()),
                chatroom=to_callsign,
                id=to_uid,
                sender_callsign=my_callsign,
                chatgrp=Chatgrp(uid0=my_uid, uid1=to_uid, id=to_uid),
            ),
            link=[Link(uid=my_uid, type_value=self.cottype, relation="p-p")],
            remarks=Remarks(
                source=f"BAO.F.ATAK.{my_uid}",
                to=to_uid,
                time=generate_cot_time(),
                __value=msg,
            ),
        ),
    )
    context = XmlContext()
    serializer = XmlSerializer(context=context)
    return serializer.render(event_obj)


client = ATAKClient("ABC123")
client.pos["lat"] = 0
client.pos["lon"] = 0
client.pos["alt"] = 0
client.pos["ce"] = 0
client.pos["le"] = 0
some_other_client = ATAKClient("DEST123")
print(client.geochat("test message", dest=some_other_client))
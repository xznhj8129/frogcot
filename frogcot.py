# Library for interacting with Cursor-on-Target (CoT) and MIL-STD-2525 data
import datetime
import pytz
import uuid
import xml.etree.ElementTree as ET
import xmltodict
import re
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, Union
import json

# Utility Functions
def generate_cot_time(offset_seconds: float = 0) -> str:
    # Generate ISO8601 timestamp offset from UTC now
    return (datetime.datetime.utcnow() + datetime.timedelta(seconds=offset_seconds)).replace(tzinfo=pytz.utc).isoformat()

# CoT and MIL-STD-2525 Conversion Functions (Standalone)
def convert_cot_to_2525b(cot_type: str) -> str:
    if not re.match(r"^a-([puafnshjkox\.])-([PAGSUFXZ])(-\w+)*$", cot_type):
        raise ValueError("Invalid CoT type for conversion to MIL-STD-2525B")
    
    chars = re.sub(r"[^A-Z0-9]+", "", cot_type[4:])
    if not chars:
        raise ValueError("Invalid CoT type: missing battle dimension and function code")
    battle_dimension = chars[0]
    
    aff_char = cot_type[2:3]
    if aff_char == '.':
        sidc_aff = '-'
    else:
        sidc_aff = aff_char.upper() if aff_char not in ['o', 'x'] else 'U'
    
    function_id = (chars[1:] if len(chars) > 1 else "").ljust(6, '-')[:6]
    modifiers = "-----"
    
    sidc = f"S{sidc_aff}{battle_dimension}P{function_id}{modifiers}"
    return sidc

def convert_2525b_to_cot(sidccode: str) -> str:
    sidc = sidccode
    if len(sidc) < 15:
        sidc = sidc.ljust(15, '-')
    sidc = sidc.replace("*","-")
    
    pattern = r"^S[PUAFNSHGWMDLJK\-][PAGSUFXZ\-][AP\-]([A-Z0-9\-]{10})([AECGNS\-]{0,5})$"
    if not re.match(pattern, sidc):
        raise ValueError("Invalid SIDC for conversion to CoT")
    
    aff_char = sidc[1]
    cot_aff = '.' if aff_char == '-' else aff_char.lower()
    
    battle_dimension = sidc[2]
    
    func_section = sidc[4:10]
    function_id = re.sub(r"[^A-Z0-9]+", "", func_section)
    function_str = f"-{'-'.join(function_id)}" if function_id else ""
    
    cot_type = f"a-{cot_aff}-{battle_dimension}{function_str}"
    return cot_type

def get_tasking(cot_type: str) -> Optional[str]:
    if re.match("^t-x-f", cot_type): return "remarks"
    if re.match("^t-x-s", cot_type): return "state/sync"
    if re.match("^t-s", cot_type): return "required"
    if re.match("^t-z", cot_type): return "cancel"
    if re.match("^t-x-c-c", cot_type): return "commcheck"
    if re.match("^t-x-c-g-d", cot_type): return "dgps"
    if re.match("^t-k-d", cot_type): return "destroy"
    if re.match("^t-k-i", cot_type): return "investigate"
    if re.match("^t-k-t", cot_type): return "target"
    if re.match("^t-k", cot_type): return "strike"
    if re.match("^t-", cot_type): return "tasking"
    return None

def get_affiliation(cot_type: str) -> Optional[str]:
    # Extract affiliation from CoT type
    if re.match("^t-", cot_type): return get_tasking(cot_type)
    affiliation_map = {
        "^a-f-": "friendly", 
        "^a-h-": "hostile", 
        "^a-u-": "unknown", 
        "^a-p-": "pending",
        "^a-a-": "assumed", 
        "^a-n-": "neutral", 
        "^a-s-": "suspect", 
        "^a-j-": "joker",
        "^a-k-": "faker"
    }
    for pattern, aff in affiliation_map.items():
        if re.match(pattern, cot_type): return aff
    return None

def get_battle_dimension(cot_type: str) -> Optional[str]:
    # Extract battle dimension from CoT type
    dimension_map = {
        "^a-.-A": "airborne", 
        "^a-.-G": "ground", 
        "^a-.-G-I": "installation",
        "^a-.-S": "surface/sea", 
        "^a-.-U": "subsurface"
    }
    for pattern, dim in dimension_map.items():
        if re.match(pattern, cot_type): return dim
    return None

def parse_type(cot_type: str) -> Optional[str]:
    # Parse specific CoT type details
    type_map = {
        "^a-.-G-I": "installation", 
        "^a-.-G-E-V": "vehicle", 
        "^a-.-G-E": "equipment",
        "^a-.-A-W-M-S": "sam", 
        "^a-.-A-M-F-Q-r": "uav"
    }
    for pattern, typ in type_map.items():
        if re.match(pattern, cot_type): return typ
    return None


# Data Classes
@dataclass
class Point:
    latitude: float
    longitude: float
    height_above_ellipsoid: float
    circular_error: float
    linear_error: float

    def __post_init__(self):
        # Validate geographical coordinates
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError("Longitude must be between -180 and 180")

    def to_dict(self) -> Dict[str, float]:
        # Convert to dictionary for serialization
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Point':
        # Create from dictionary
        return cls(**data)

@dataclass
class Event:
    point: Point
    detail: Optional[Dict[str, Any]] = None
    version: int = 2
    event_type: str = field(default_factory=str)
    access: Optional[str] = None
    quality_of_service: Optional[str] = None
    unique_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    time: datetime = field(default_factory=lambda: datetime.datetime.now(pytz.utc))
    start: datetime = field(default_factory=lambda: datetime.datetime.now(pytz.utc))
    stale: datetime = field(default_factory=lambda: datetime.datetime.now(pytz.utc))
    how: str = field(default_factory=str)

    def __post_init__(self):
        # Validate attributes based on CoT standards
        if self.version < 2: raise ValueError("Version must be >= 2")
        if not re.match(r"^\w+(-\w+)*(;[^;]*)?$", self.event_type):
            raise ValueError("Invalid event_type format")
        if self.quality_of_service and not re.match(r"^\d-[rfi]-[gcd]$", self.quality_of_service):
            raise ValueError("Invalid QoS format")
        if not re.match(r"^\w(-\w+)*$", self.how):
            raise ValueError("Invalid how format")

    def to_dict(self) -> Dict[str, Any]:
        # Convert to dictionary with ISO8601 timestamps
        data = asdict(self)
        for key in ['time', 'start', 'stale']:
            data[key] = data[key].isoformat() if data[key] else None
        data['point'] = self.point.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        # Create from dictionary, parsing timestamps
        for key in ['time', 'start', 'stale']:
            if data.get(key): data[key] = datetime.fromisoformat(data[key])
        data['point'] = Point.from_dict(data['point'])
        return cls(**data)

    def to_json(self) -> str:
        # Serialize to JSON string
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> 'Event':
        # Create from JSON string
        return cls.from_dict(json.loads(json_str))

    def get_detail_value(self, property_path: str) -> str:
        # Retrieve value from detail dictionary using dot notation
        if not isinstance(self.detail, dict):
            raise TypeError("Detail is not a dictionary")
        current = self.detail
        for part in property_path.split("."):
            if not isinstance(current, dict) or part not in current:
                raise ValueError(f"Invalid property path: {property_path}")
            current = current[part]
        return str(current)

# CoT Parsing and Writing Functions (Replaces CoTHandler)
def xml_to_cot(xml_input: str) -> Event:
    # Parse CoT XML from string into an Event object
    data = xmltodict.parse(xml_input).get('event', {})
    point_data = data.get('point', {})
    if not isinstance(point_data, dict):
        raise ValueError("Missing 'point' in XML")

    def safe_float(value: Any, default: float = 0.0) -> float:
        try: return float(value)
        except (ValueError, TypeError): return default

    def safe_datetime(value: Any) -> datetime:
        if not value: return datetime.datetime.now(pytz.utc)
        try:
            from dateutil.parser import parse
            return parse(value)
        except: return datetime.datetime.now(pytz.utc)

    point = Point(
        latitude=safe_float(point_data.get('@lat')),
        longitude=safe_float(point_data.get('@lon')),
        height_above_ellipsoid=safe_float(point_data.get('@hae')),
        circular_error=safe_float(point_data.get('@ce')),
        linear_error=safe_float(point_data.get('@le'))
    )
    detail = data.get('detail')
    if isinstance(detail, dict): detail = dict(detail)

    return Event(
        point=point,
        detail=detail,
        version=int(data.get('@version', 2)),
        event_type=data.get('@type', ''),
        access=data.get('@access'),
        quality_of_service=data.get('@qos'),
        unique_id=data.get('@uid', str(uuid.uuid4())),
        time=safe_datetime(data.get('@time')),
        start=safe_datetime(data.get('@start')),
        stale=safe_datetime(data.get('@stale')),
        how=data.get('@how', '')
    )

def cot_to_xml(event: Event) -> str:
    # Convert Event object to XML string
    event_dict = {
        'event': {
            '@version': str(event.version),
            '@type': event.event_type,
            '@access': event.access,
            '@qos': event.quality_of_service,
            '@uid': event.unique_id,
            '@time': event.time.isoformat() if event.time else None,
            '@start': event.start.isoformat() if event.start else None,
            '@stale': event.stale.isoformat() if event.stale else None,
            '@how': event.how,
            'point': {
                '@lat': str(event.point.latitude),
                '@lon': str(event.point.longitude),
                '@hae': str(event.point.height_above_ellipsoid),
                '@ce': str(event.point.circular_error),
                '@le': str(event.point.linear_error)
            }
        }
    }
    if event.detail: event_dict['event']['detail'] = event.detail
    return xmltodict.unparse(event_dict, pretty=True)

# Category Management Classes
class CoTCatManager:
    def __init__(self, tag: str):
        # Initialize category with tag and mappings
        self.tag = tag
        self.code_to_info: Dict[str, Dict[str, str]] = {}
        self.description_to_code: Dict[str, str] = {}
        self.hierarchy = defaultdict(dict)
        self.base_categories = {
            'a': 'Atoms', 'b': 'Bits', 't': 'Tasking', 'y': 'Reply',
            'c': 'Capability', 'r': 'Reservation'
        }
        for code, desc in self.base_categories.items():
            self.code_to_info[code] = {'desc': desc, 'full': desc}
            self.description_to_code[desc] = code

    def add_entry(self, element: ET.Element) -> None:
        cot = element.attrib.get('cot', '')  # Remove .lower() to preserve case
        desc = element.attrib.get('desc')
        full = element.attrib.get('full', desc)
        if not cot or not desc:
            return
        clean_cot = re.sub(r'[\^$|]', '', cot)
        self.code_to_info[clean_cot] = {'desc': desc, 'full': full}
        self.description_to_code[desc] = clean_cot
        self.description_to_code[full] = clean_cot
        current = self.hierarchy
        for part in clean_cot.split('-'):
            if part and not any(c in part for c in '*'):
                current = current.setdefault(part, defaultdict(dict))

    def get_subcategories(self, parent_code: str) -> list[Dict[str, str]]:
        # Retrieve subcategories for a parent code
        code = "a-." if parent_code == "a" else parent_code
        parts = code.split('-')
        current = self.hierarchy
        for part in parts:
            if part not in current: return []
            current = current[part]
        result = []
        for key in current:
            if any(c in key for c in ('.', '*', '^', '$')): continue
            child_code = f"{code}-{key}" if code else key
            desc = self.code_to_info.get(child_code, {}).get('desc') or self.code_to_info.get(key, {}).get('desc')
            if desc:
                result.append({"cottype": child_code, "desc": desc})
        return result

    def find_code(self, description: str) -> Optional[str]:
        # Find CoT code by description
        return self.description_to_code.get(description)

    def get_full_name(self, code: str) -> Optional[str]:
        # Get full hierarchical name for a code
        if code not in self.code_to_info: return None
        entry = self.code_to_info[code]
        if '/' in entry['full']: return entry['full']
        parts = code.split('-')
        path = []
        current_code = []
        for part in parts:
            current_code.append(part)
            key = '-'.join(current_code)
            if key in self.code_to_info:
                path.append(self.code_to_info[key]['desc'])
        return '/'.join(path)

class CoTTypes:
    def __init__(self, xml_path: str):
        # Manage multiple CoT categories from an XML file
        self.categories = {
            'cot': CoTCatManager('cot'),
            'weapon': CoTCatManager('weapon'),
            'relation': CoTCatManager('relation'),
            'is': CoTCatManager('is'),
            'how': CoTCatManager('how')
        }
        tree = ET.parse(xml_path)
        for elem in tree.getroot():
            if elem.tag in self.categories:
                self.categories[elem.tag].add_entry(elem)

    def __getattr__(self, name: str) -> CoTCatManager:
        # Access categories as attributes
        if name in self.categories: return self.categories[name]
        raise AttributeError(f"No category '{name}'")

class ATAKClient:
    def __init__(self, callsign: str, cottype: str = "a-f-U", is_self: bool = False):
        self.self = is_self
        self.callsign = callsign
        self.cottype = cottype
        xuid = str(uuid.uuid4()).split("-")
        self.uid = f"PYTAK-{str(xuid[3]) + str(xuid[4])}"
        self.takv = {"version": "5.2.0.8", 'platform': "ATAK-CIV", 'device': "PC", 'os': '33'}
        self.groups = {}
        self.pos = {}
        self.xmppusername = None

    # Well-defined functions
    def geochat(self, msg, dest=None, to_team=None, pos=None):
        if to_team is not None and not dest:
            to_callsign = to_team
            to_uid = to_team
        elif not to_team and dest is not None:
            to_callsign = dest.callsign
            to_uid = dest.uid
        else:
            return
        my_callsign = self.callsign
        my_uid = self.uid
        my_cottype = self.cottype
        msg_cottype = 'b-t-f'
        msguid = str(uuid.uuid4())
        chat_parent = "TeamGroups" if to_team is not None else 'RootContactGroup'
        cot = ET.Element('event')
        cot.set('version', '2.0')
        cot.set('uid', f"GeoChat.{my_uid}.{to_uid}.{msguid}")
        cot.set('type', msg_cottype)
        cot.set('time', generate_cot_time())
        cot.set('start', generate_cot_time())
        cot.set('stale', generate_cot_time(60))
        cot.set('how', 'm-g')
        if pos:
            point = ET.SubElement(cot, 'point')
            point.set('lat', str(pos["lat"]))
            point.set('lon', str(pos["lon"]))
            point.set('hae', str(pos["alt"]))
            point.set('ce', str(pos["ce"]))
            point.set('le', str(pos["le"]))
        detail = ET.SubElement(cot, 'detail')
        takv = ET.SubElement(detail, 'takv')
        for i in self.takv: takv.set(i, self.takv[i])
        chat = ET.SubElement(detail, '__chat')
        chat.set('parent', chat_parent)
        chat.set('groupOwner', 'false')
        chat.set('messageId', str(uuid.uuid4()))
        chat.set('chatroom', to_callsign)
        chat.set('id', to_uid)
        chat.set('senderCallsign', my_callsign)
        chatgrp = ET.SubElement(chat, 'chatgrp')
        chatgrp.set('uid0', my_uid)
        chatgrp.set('uid1', to_uid)
        chatgrp.set('id', to_uid)
        link = ET.SubElement(detail, 'link')
        link.set('uid', my_uid)
        link.set('type', my_cottype)
        link.set('relation', 'p-p')
        remarks = ET.SubElement(detail, 'remarks')
        remarks.set('source', f'BAO.F.ATAK.{my_uid}')
        remarks.set('to', to_uid)
        remarks.set('time', generate_cot_time())
        remarks.text = msg
        marti = ET.SubElement(detail, 'marti')
        dest = ET.SubElement(marti, 'dest')
        dest.set('callsign', to_callsign)
        return ET.tostring(cot)

    def cot_marker(self, callsign, uid, cottype, pos, iconpath=None):
        cot = ET.Element('event')
        cot.set('version', '2.0')
        cot.set('uid', uid)
        cot.set('type', cottype)
        cot.set('time', generate_cot_time())
        cot.set('start', generate_cot_time())
        cot.set('stale', generate_cot_time(60))
        cot.set('how', "h-g-i-g-o")
        point = ET.SubElement(cot, 'point')
        point.set('lat', str(pos["lat"]))
        point.set('lon', str(pos["lon"]))
        point.set('hae', str(pos["alt"]))
        point.set('ce', str(pos["ce"]))
        point.set('le', str(pos["le"]))
        detail = ET.SubElement(cot, 'detail')
        takv = ET.SubElement(detail, 'takv')
        for i in self.takv: takv.set(i, self.takv[i])
        if iconpath:
            usericon = ET.SubElement(detail, "usericon")
            usericon.set('iconsetpath', iconpath)
        contact = ET.SubElement(detail, 'contact')
        contact.set('callsign', callsign)
        color = ET.SubElement(detail, 'color')
        color.set('argb', "-1")
        precisionlocation = ET.SubElement(detail, 'precisionlocation')
        precisionlocation.set('altsrc', "SRTM1")
        link = ET.SubElement(detail, 'link')
        link.set('uid', self.uid)
        link.set('type', self.cottype)
        link.set('parent_callsign', self.callsign)
        link.set('production_time', generate_cot_time())
        link.set('relation', 'p-p')
        return ET.tostring(cot)

# Incomplete, inflexible Parse Function
def parse_cot_xml(cot_xml):
    tree = ET.ElementTree(ET.fromstring(cot_xml))
    root = tree.getroot()
    event_info = {
        'uid': root.get('uid'),
        'type': root.get('type'),
        'time': root.get('time'),
        'start': root.get('start'),
        'stale': root.get('stale')
    }
    point = root.find('point')
    point_info = {
        'latitude': float(point.get('lat')),
        'longitude': float(point.get('lon')),
        'hae': float(point.get('hae')),
        'ce': float(point.get('ce')),
        'le': float(point.get('le'))
    }
    detail = root.find('detail')
    contact = detail.find('contact')
    group = detail.find('__group')
    status = detail.find('status')
    detail_info = {
        'callsign': contact.get('callsign'),
        'group_role': group.get('role'),
        'group_name': group.get('name'),
        'battery': int(status.get('battery'))
    }
    return event_info, point_info, detail_info

# Usage Example
if __name__ == "__main__":
    # Category management
    cot_manager = CoTTypes("CoTtypes.xml")
    for i, level in enumerate(["a", "a-.", "a-.-G", "a-.-G-U", "a-.-G-U-C"]):
        print(f"{i}: {cot_manager.cot.get_subcategories(level)}")

    # Name and code lookups
    print(cot_manager.cot.get_full_name("b-w-A-P-F-C-U"))
    print(cot_manager.cot.find_code("HIGH PRESSURE CENTER"))

    # Event creation and serialization
    event = Event(
        point=Point(latitude=32.0, longitude=-117.0, height_above_ellipsoid=0.0, circular_error=10.0, linear_error=10.0),
        event_type="a-f-G",
        how="m-g",
        unique_id="test123"
    )

    print(cot_to_xml(event))
    print(event.to_json())

    # Conversion examples
    print(convert_2525b_to_cot("SHGPUCIZ----"))
    print(convert_2525b_to_cot("S-GPUCIZ----"))
    print(convert_cot_to_2525b("a-h-G-U-C-I-Z"))
    print(convert_cot_to_2525b("a-.-G-U-C-I-Z"))

    # ATAK client usage
    client = ATAKClient("TestUser")
    pos = {"lat": 32.0, "lon": -117.0, "alt": 0.0, "ce": 10.0, "le": 10.0}
    print(client.geochat("Hello", to_team="Team1", pos=pos).decode())

    uava = "S*APMHR-----"
    uav1 = convert_2525b_to_cot(uava)
    print(uav1)
    print(cot_manager.cot.get_full_name(uav1))
    uav2 = convert_cot_to_2525b(uav1)
    print(uav2)
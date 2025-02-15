#!/usr/bin/env python3
import asyncio
import pytak
import datetime
import pytz
import uuid
import time
import multiprocessing
import xml.etree.ElementTree as ET
from collections import defaultdict
from multiprocessing import Manager

def cot_time(offset_seconds=0):
    """
    Generates a COT formatted timestamp offset by a given number of seconds from now.
    """
    return (datetime.datetime.utcnow() + datetime.timedelta(seconds=offset_seconds)).replace(tzinfo=pytz.utc).isoformat()


class ATAKClient():
    def __init__(self, callsign: str, cottype: str = "a-f-U", is_self: bool = False):
        self.self = is_self
        self.callsign = callsign
        self.cottype = cottype
        xuid = str(uuid.uuid4()).split("-")
        self.uid = f"PYTAK-{str(xuid[3]) + str(xuid[4])}"
        self.takv = {
            "version": "5.2.0.8",
            'platform': "ATAK-CIV",
            'device': "PC",
            'os': '33'
        }
        self.groups = {}
        self.pos = {}
        self.xmppusername = None



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
        cot.set('time', pytak.cot_time())
        cot.set('start', pytak.cot_time())
        cot.set('stale', cot_time(60))
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
        for i in self.takv:
            takv.set(i, self.takv[i])

        # Create __chat element with attributes
        chat = ET.SubElement(detail, '__chat')
        chat.set('parent', chat_parent)
        chat.set('groupOwner', 'false')
        chat.set('messageId', str(uuid.uuid4()))
        chat.set('chatroom', to_callsign)
        chat.set('id', to_uid)
        chat.set('senderCallsign', my_callsign)

        # Add chatgrp under __chat
        chatgrp = ET.SubElement(chat, 'chatgrp')
        chatgrp.set('uid0', my_uid)
        chatgrp.set('uid1', to_uid)
        chatgrp.set('id', to_uid)

        # Create link element
        link = ET.SubElement(detail, 'link')
        link.set('uid', my_uid)
        link.set('type', my_cottype)
        link.set('relation', 'p-p')

        # Create remarks element with text content
        remarks = ET.SubElement(detail, 'remarks')
        remarks.set('source', f'BAO.F.ATAK.{my_uid}')
        remarks.set('to', to_uid)
        remarks.set('time', pytak.cot_time())
        remarks.text = msg

        # Create marti and dest elements
        marti = ET.SubElement(detail, 'marti')
        dest = ET.SubElement(marti, 'dest')
        dest.set('callsign', to_callsign)

        return ET.tostring(cot)


    def cot_marker(self, callsign, uid, cottype, pos, iconpath=None):

        cot = ET.Element('event')
        cot.set('version', '2.0')
        cot.set('uid', uid)
        cot.set('type', cottype)
        cot.set('time', pytak.cot_time())
        cot.set('start', pytak.cot_time())
        cot.set('stale', cot_time(60))
        cot.set('how', "h-g-i-g-o")

        point = ET.SubElement(cot, 'point')
        point.set('lat', str(pos["lat"]))  # Set latitude
        point.set('lon', str(pos["lon"]))  # Set longitude
        point.set('hae', str(pos["alt"]))  # Altitude
        point.set('ce', str(pos["ce"]))
        point.set('le', str(pos["le"]))

        detail = ET.SubElement(cot, 'detail')
        takv = ET.SubElement(detail, 'takv')
        for i in self.takv:
            takv.set(i, self.takv[i])

        if iconpath:
            usericon = ET.SubElement("usericon")
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
        link.set('production_time', pytak.cot_time())
        link.set('relation', 'p-p')

        #precisionlocation = ET.SubElement(detail, 'precisionlocation')
        #precisionlocation.set('altsrc', "GPS") 
        #precisionlocation.set('geopointsrc', "GPS")

        #status = ET.SubElement(detail, 'status')
        #status.set('battery', '90')  # Example battery level

        return ET.tostring(cot)

def parse_cot_xml(cot_xml):
    # Parse the XML string into an ElementTree object
    tree = ET.ElementTree(ET.fromstring(cot_xml))
    root = tree.getroot()
    
    # Extract event attributes
    event_info = {
        'uid': root.get('uid'),
        'type': root.get('type'),
        'time': root.get('time'),
        'start': root.get('start'),
        'stale': root.get('stale')
    }
    
    # Extract point information
    point = root.find('point')
    point_info = {
        'latitude': float(point.get('lat')),
        'longitude': float(point.get('lon')),
        'hae': float(point.get('hae')),
        'ce': float(point.get('ce')),
        'le': float(point.get('le'))
    }
    
    # Extract detail information
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


# Shared data
class MySender(pytak.QueueWorker):

    def __init__(self, tx_queue, config, shared_data):
        super().__init__(tx_queue, config)
        self.shared_data = shared_data

    async def run(self):
        while True:
            print(self.shared_data)

            if len(self.shared_data["cot_send_queue"])>0:
                pos = self.shared_data['pos']

                data = gen_cot()

                if data:
                    self._logger.info("Sending:\n%s\n", data.decode())
                    await self.handle_data(data)

            await asyncio.sleep(5)

    async def handle_data(self, data):
        await self.put_queue(data)



class MyReceiver(pytak.QueueWorker):
    """Defines how you will handle events from RX Queue."""

    async def handle_data(self, data):
        """Handle data from the receive queue."""
        self._logger.info("Received:\n%s\n", data.decode())

    async def run(self):  # pylint: disable=arguments-differ
        """Read from the receive queue, put data onto handler."""
        while 1:
            data = (
                await self.queue.get()
            )  # this is how we get the received CoT from rx_queue
            await self.handle_data(data)


async def main_async():
    """Main definition of your program, sets config params and
    adds your serializer to the asyncio task list.
    """
    config = ConfigParser()
    config["mycottool"] = {
        "DEBUG": 1,
        "COT_URL": "tcp://127.0.0.1:8087"
        }
    config = config["mycottool"]

    # Initializes worker queues and tasks.
    clitool = pytak.CLITool(config)
    await clitool.setup()

    # Add your serializer to the asyncio task list.
    clitool.add_tasks(
        set([MySender(clitool.tx_queue, config), 
        MyReceiver(clitool.rx_queue, config)])
    )

    # Start all tasks.
    await clitool.run()



class CategoryManager:
    def __init__(self, category_tag):
        self.category_tag = category_tag
        self.code_map = {}          # {code: {'desc': str, 'full': str}}
        self.desc_map = {}          # {description: code}
        self.faction_map = {
            "null": ".",
            "friendly": "f",
            "hostile": "h",
            "unknown": "u",
            "pending": "p",
            "assumed": "a",
            "neutral": "n",
            "suspect": "s",
            "joker": "j",
            "faker": "k"
        }
        self.hierarchy = defaultdict(dict)
        self.base_categories = {
            'a': 'Atoms',
            'b': 'Bits',
            't': 'Tasking',
            'y': 'Reply',
            'c': 'Capability',
            'r': 'Reservation'
        }
        for code, desc in self.base_categories.items():
            self.code_map[code] = {'desc': desc, 'full': desc}
            self.desc_map[desc] = code

    def find_code(self, description):
        """Find code by description or path"""
        return self.desc_map.get(description)

    def get_sub(self, parent_code):
        """Get direct child categories for a parent code"""
        if parent_code == "a":
            pc = "a-."
        else:
            pc = parent_code
        parts = pc.split('-') if pc else []
        current = self.hierarchy
        
        # Traverse to parent node
        for part in parts:
            if part not in current:
                return []
            current = current[part]
        
        # Collect valid children with proper descriptions
        children = []
        for child_key in current.keys():
            # Skip placeholder and regex components
            if any(c in child_key for c in ('.', '*', '^', '$')):
                continue
                
            child_code = f"{pc}-{child_key}" if pc else child_key
            
            # Get description from code_map or base categories
            desc = None
            if child_code in self.code_map:
                desc = self.code_map[child_code]['desc']
            elif child_key in self.code_map:  # Check for base category
                desc = self.code_map[child_key]['desc']
            
            # Only include if we have a valid description
            if desc:
                children.append({
                    "cottype": child_code,
                    "desc": desc
                })
        
        return children

    def add_entry(self, elem):
        """Add an entry from XML element"""
        cot = elem.attrib.get('cot')
        if cot:
            cot = cot.lower()
        desc = elem.attrib.get('desc')
        full = elem.attrib.get('full', desc)

        if not cot or not desc:
            return

        # Clean COT code from regex patterns
        clean_cot = cot.replace('^', '').replace('$', '').split('|')[0]
        
        # Store mappings
        self.code_map[clean_cot] = {'desc': desc, 'full': full}
        self.desc_map[full] = clean_cot
        self.desc_map[desc] = clean_cot

        # Build hierarchy with clean components
        parts = clean_cot.split('-')
        current = self.hierarchy
        for part in parts:
            # Skip empty parts and regex characters
            if part and not any(c in part for c in ('*', '^', '$', '|')):
                current = current.setdefault(part, defaultdict(dict))

    def get_name(self, code):
        """Get hierarchical path for a code"""
        if code not in self.code_map:
            return None
            
        # Check if we have explicit full path
        entry = self.code_map[code]
        if entry['full'] and '/' in entry['full']:
            return entry['full']
        
        # Build path from hierarchy components
        parts = code.split('-')
        path = []
        current_code = []
        
        for part in parts:
            current_code.append(part)
            lookup_code = '-'.join(current_code)
            if lookup_code in self.code_map:
                path.append(self.code_map[lookup_code]['desc'])
        
        return '/'.join(path)

class CoTManager:
    """Main manager for all CoT types"""
    def __init__(self, xml_path):
        self.categories = {
            'cot': CategoryManager('cot'),
            'weapon': CategoryManager('weapon'),
            'relation': CategoryManager('relation'),
            'is': CategoryManager('is'),
            'how': CategoryManager('how')
        }
        self._parse_xml(xml_path)
        
    def _parse_xml(self, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        for elem in root:
            category = elem.tag
            if category in self.categories:
                self.categories[category].add_entry(elem)
                
    def __getattr__(self, name):
        """Provide direct access to categories"""
        if name in self.categories:
            return self.categories[name]
        raise AttributeError(f"No category named '{name}'")


# Usage examples
if __name__ == "__main__":
    cot_system = CoTManager("CoTtypes.xml")
    i = 0
    print(i, cot_system.cot.get_sub("a"))
    i+=1
    print(i, cot_system.cot.get_sub("a-."))
    i+=1
    print(i, cot_system.cot.get_sub("a-.-G"))
    i+=1
    print(i, cot_system.cot.get_sub("a-.-G-U"))
    i+=1
    print(i, cot_system.cot.get_sub("a-.-G-U-C"))
    i+=1
    # Output:
    # 0 [{'cottype': 'a-.-A', 'desc': 'Air Track'}, {'cottype': 'a-.-G', 'desc': 'GROUND TRACK'}, {'cottype': 'a-.-S', 'desc': 'SEA SURFACE TRACK'}, {'cottype': 'a-.-U', 'desc': 'SUBSURFACE TRACK'}, {'cottype': 'a-.-X', 'desc': 'Other'}]
    # 1 [{'cottype': 'a-.-A', 'desc': 'Air Track'}, {'cottype': 'a-.-G', 'desc': 'GROUND TRACK'}, {'cottype': 'a-.-S', 'desc': 'SEA SURFACE TRACK'}, {'cottype': 'a-.-U', 'desc': 'SUBSURFACE TRACK'}, {'cottype': 'a-.-X', 'desc': 'Other'}]
    # 2 [{'cottype': 'a-.-G-E', 'desc': 'EQUIPMENT'}, {'cottype': 'a-.-G-I', 'desc': 'Building'}, {'cottype': 'a-.-G-U', 'desc': 'UNIT'}]
    # 3 [{'cottype': 'a-.-G-U-C', 'desc': 'COMBAT'}, {'cottype': 'a-.-G-U-H', 'desc': 'SPECIAL C2 HEADQUARTERS COMPONENT'}, {'cottype': 'a-.-G-U-S', 'desc': 'COMBAT SERVICE SUPPORT'}, {'cottype': 'a-.-G-U-U', 'desc': 'COMBAT SUPPORT'}, {'cottype': 'a-.-G-U-i', 'desc': 'Incident Management Resources'}]
    # 4 [{'cottype': 'a-.-G-U-C-A', 'desc': 'ARMOR'}, {'cottype': 'a-.-G-U-C-D', 'desc': 'AIR DEFENSE'}, {'cottype': 'a-.-G-U-C-E', 'desc': 'ENGINEER'}, {'cottype': 'a-.-G-U-C-F', 'desc': 'Artillery (Fixed)'}, {'cottype': 'a-.-G-U-C-I', 'desc': 'Troops (Open)'}, {'cottype': 'a-.-G-U-C-M', 'desc': 'MISSILE (SURF SURF)'}, {'cottype': 'a-.-G-U-C-R', 'desc': 'RECONNAISSANCE'}, {'cottype': 'a-.-G-U-C-S', 'desc': 'INTERNAL SECURITY FORCES'}, {'cottype': 'a-.-G-U-C-V', 'desc': 'AVIATION'}]


    # Usage
    # Now properly separated access
    # Example 1: Full path lookup
    print(cot_system.cot.get_name("b-w-A-P-F-C-U")) 
    print(cot_system.weapon.get_name("m-a-s-AGM158")) 
    print(cot_system.cot.get_name("b-r-.-O-O-R-C"))
    print(cot_system.cot.get_name("a-.-G-U-C-D-M-M"))

    # Example 2: Reverse lookup
    print(cot_system.cot.find_code("HIGH PRESSURE CENTER"))  
    # Output: b-w-A-P-H

    # Example 3: Direct full path lookup
    print(cot_system.cot.find_code("Alarm/Security/Law Enforcement/Burglary/Audible/Day/Night Zone"))
    print(cot_system.cot.find_code("Gnd/Combat/Defense/THEATER MISSILE DEFENSE UNIT"))
    # Output: b-l-l-l-bur-a-d"""
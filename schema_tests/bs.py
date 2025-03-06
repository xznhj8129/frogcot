#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET
import xmlschema

def create_combined_schema(main_schema_path, include_paths, output_path):
    xs_ns = "http://www.w3.org/2001/XMLSchema"
    ET.register_namespace("xs", xs_ns)
    tree = ET.parse(main_schema_path)
    root = tree.getroot()
    # For every include path that we require but isn’t already present, add it.
    for include_path in include_paths:
        found = False
        for child in root.findall(f"{{{xs_ns}}}include"):
            if child.get("schemaLocation") == include_path:
                found = True
                break
        if not found:
            # Create and insert the missing include element at the beginning of the schema.
            include_elem = ET.Element(f"{{{xs_ns}}}include", schemaLocation=include_path)
            root.insert(0, include_elem)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

def main():
    # Change these paths if needed.
    # This is the main schema that references "event_point" (defined in event/point.xsd)
    main_schema = "Marker - 2525.xsd"
    # The missing type is defined in event/point.xsd, so we add an include for that.
    include_paths = ["event/point.xsd"]
    # Name of the combined schema file to be written.
    combined_schema = "combined_marker2525.xsd"
    # Base URL to help xmlschema resolve relative includes.
    base_url = "file:///media/anon/WD2TB/DataVault/TechProjects/GitRepos/frogcot/xsd_schema/xsd/"

    print("Creating combined schema...")
    create_combined_schema(main_schema, include_paths, combined_schema)
    
    print("Loading combined schema with xmlschema...")
    schema = xmlschema.XMLSchema(combined_schema, base_url=base_url)
    print("Combined schema loaded successfully!")
    
    print("\nGlobal elements in the combined schema:")
    for name in schema.elements:
        print(f" - {name}")

if __name__ == "__main__":
    main()

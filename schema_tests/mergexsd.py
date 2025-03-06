import os
from lxml import etree

# Define the XML Schema namespace.
XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
NSMAP = {"xs": XSD_NAMESPACE}

def merge_includes(xsd_tree, base_path):
    """
    Recursively merge all xs:include elements in the given XSD tree.

    :param xsd_tree: An lxml.etree.ElementTree object representing the XSD.
    :param base_path: The directory path used to resolve relative schema locations.
    :return: The modified XSD tree with all includes inlined.
    """
    root = xsd_tree.getroot()
    # Find all xs:include elements in the tree
    includes = root.xpath(".//xs:include", namespaces=NSMAP)
    for include in includes:
        schema_location = include.get("schemaLocation")
        if not schema_location:
            continue
        # Resolve the full path to the included schema file.
        included_path = os.path.join(base_path, schema_location)
        print(f"Merging included schema: {included_path}")
        # Parse the included schema.
        try:
            included_tree = etree.parse(included_path)
        except Exception as e:
            print(f"Error parsing {included_path}: {e}")
            continue
        # Recursively merge any includes in the included file.
        included_tree = merge_includes(included_tree, os.path.dirname(included_path))
        included_root = included_tree.getroot()
        # Append each child from the included schema into the main schema.
        for child in included_root:
            # You can choose to skip certain elements (like annotations) if needed.
            root.append(child)
        # Remove the xs:include element from the main tree.
        parent = include.getparent()
        parent.remove(include)
    return xsd_tree

def merge_xsd(main_xsd_path, output_path):
    """
    Parse the main XSD, merge all includes, and write out the merged XSD.

    :param main_xsd_path: Path to the main XSD file.
    :param output_path: Path to write the merged XSD file.
    """
    base_path = os.path.dirname(main_xsd_path)
    try:
        tree = etree.parse(main_xsd_path)
    except Exception as e:
        print(f"Error parsing main XSD file: {e}")
        return
    merged_tree = merge_includes(tree, base_path)
    merged_tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"Merged XSD saved to {output_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Merge XSD includes into a single unitary XSD file.")
    parser.add_argument("main_xsd", help="Path to the main XSD file (e.g., chat.xsd)")
    parser.add_argument("output", help="Path to save the merged XSD file")
    args = parser.parse_args()

    merge_xsd(args.main_xsd, args.output)

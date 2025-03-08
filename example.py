import frogcot

# Usage Example
if __name__ == "__main__":
    # Category management
    cot_manager = frogcot.CoTTypes()
    for i, level in enumerate(["a", "a-.", "a-.-G", "a-.-G-U", "a-.-G-U-C"]):
        print(f"{i}: {cot_manager.cot.get_subcategories(level)}")

    # Name and code lookups
    print(cot_manager.cot.get_full_name("b-w-A-P-F-C-U"))
    print(cot_manager.cot.find_code("HIGH PRESSURE CENTER"))
    # Event creation and serialization
    event = frogcot.Event(
        point=frogcot.Point(latitude=32.0, longitude=-117.0, height_above_ellipsoid=0.0, circular_error=10.0, linear_error=10.0),
        event_type="a-f-G",
        how="m-g",
        unique_id="test123"
    )

    print(frogcot.cot_to_xml(event))
    print(event.to_json())

    # Conversion examples
    print(frogcot.convert_2525b_to_cot("SHGPUCIZ----"))
    print(frogcot.convert_2525b_to_cot("S-GPUCIZ----"))
    print(frogcot.convert_cot_to_2525b("a-h-G-U-C-I-Z"))
    print(frogcot.convert_cot_to_2525b("a-.-G-U-C-I-Z"))

    # ATAK client usage
    client = frogcot.ATAKClient("TestUser")
    pos = {"lat": 32.0, "lon": -117.0, "alt": 0.0, "ce": 10.0, "le": 10.0}
    print(client.geochat("Hello", to_team="Team1", pos=pos).decode())

    uava = "S*APMHR-----"
    uav1 = frogcot.convert_2525b_to_cot(uava)
    print(uav1)
    print(cot_manager.cot.get_full_name(uav1))
    uav2 = frogcot.convert_cot_to_2525b(uav1)
    print(uav2)
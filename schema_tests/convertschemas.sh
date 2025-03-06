#!/bin/bash

rm -rf takschemas/
#xsdata generate xsd_schema/xsd/ --recursive --package takschemas.tak --output pydantic  --structure-style=filenames
xsdata generate xsd_schema/mitre/ --recursive --package takschemas.mitre --output pydantic --structure-style=namespaces


cd xsd_schema/xsd

cp "Drawing Shapes - Circle.xsd" circle.xsd
cp "Drawing Shapes - Free Form.xsd" freeform.xsd
cp "Drawing Shapes - Rectangle.xsd" rectangle.xsd
cp "Drawing Shapes - Telestration.xsd" telestration.xsd
cp "Geo Fence.xsd" geofence.xsd
cp "Marker - 2525.xsd" marker2525.xsd
cp "Marker - Icon Set.xsd" markerset.xsd
cp "Marker - Spot.xsd" spot.xsd
cp "Range & Bearing - Bullseye.xsd" bullseye.xsd
cp "Range & Bearing - Circle.xsd" rbcircle.xsd
cp "Range & Bearing - Line.xsd" line.xsd
cp "Chat.xsd" chat.xsd
cp "Route.xsd" route.xsd

cd ../..
rm -rf takschemas/

xsdata generate xsd_schema/xsd/event/ --recursive --package takschemas.tak.event --output pydantic
xsdata generate xsd_schema/xsd/details/ --recursive --package takschemas.tak.details --output pydantic 
xsdata generate xsd_schema/xsd/circle.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/freeform.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/rectangle.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/telestration.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/spot.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/markerset.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/geofence.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/bullseye.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/rbcircle.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/line.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/route.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/chat.xsd --recursive --package takschemas.tak --output pydantic
xsdata generate xsd_schema/xsd/marker2525.xsd --recursive --package takschemas.tak --output pydantic
"""Small, dependency-free situational-awareness state for CoT event streams."""

import datetime
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Union


@dataclass(frozen=True)
class GeoPoint:
    """A CoT point, in WGS-84 degrees and metres."""

    latitude: float
    longitude: float
    hae: Optional[float] = None
    ce: Optional[float] = None
    le: Optional[float] = None


@dataclass(frozen=True)
class Contact:
    """The latest PLI state for one CoT UID."""

    uid: str
    cot_type: str
    callsign: Optional[str]
    point: GeoPoint
    time: datetime.datetime


@dataclass(frozen=True)
class Marker:
    """The latest state for one point-bearing, non-PLI CoT UID."""

    uid: str
    cot_type: str
    callsign: Optional[str]
    point: GeoPoint
    time: datetime.datetime


@dataclass(frozen=True)
class GeoChat:
    """A GeoChat message received from a CoT event."""

    uid: str
    cot_type: str
    sender: Optional[str]
    room: Optional[str]
    text: str
    time: datetime.datetime
    point: Optional[GeoPoint] = None


@dataclass(frozen=True)
class RangeBearing:
    """Distance and initial bearing from one WGS-84 point to another."""

    range_m: float
    bearing_deg: float


SituationalEvent = Union[Contact, Marker, GeoChat]
Location = Union[
    GeoPoint,
    Contact,
    Marker,
    Sequence[float],
    str,
]


class CoTParseError(ValueError):
    """Raised when one input is not a usable CoT event."""


class SituationalAwareness:
    """Accumulate queryable PLI, marker, and GeoChat state one event at a time."""

    def __init__(self) -> None:
        self._contacts: Dict[str, Contact] = {}
        self._markers: Dict[str, Marker] = {}
        self._chats: List[GeoChat] = []

    @property
    def contacts(self) -> List[Contact]:
        return list(self._contacts.values())

    @property
    def chats(self) -> List[GeoChat]:
        return list(self._chats)

    def ingest(self, xml: Union[str, bytes]) -> Optional[SituationalEvent]:
        """Parse and apply exactly one CoT ``event`` XML document.

        PLI and marker records are replaced only by an event with an equal or
        later CoT time. GeoChat messages are retained in arrival order. Other
        events without a point are valid but are not retained.
        """

        try:
            root = ET.fromstring(xml)
        except (ET.ParseError, TypeError) as exc:
            raise CoTParseError("invalid CoT XML") from exc
        if _local_name(root.tag) != "event":
            raise CoTParseError("CoT XML root must be an event")

        uid = _required_attribute(root, "uid")
        cot_type = _required_attribute(root, "type")
        event_time = _parse_time(_required_attribute(root, "time"))
        point_element = _child(root, "point")
        point = _parse_point(point_element) if point_element is not None else None
        detail = _child(root, "detail")

        if cot_type == "b-t-f":
            chat_element = _child(detail, "__chat")
            remarks = _child(detail, "remarks")
            message = GeoChat(
                uid=uid,
                cot_type=cot_type,
                sender=(
                    chat_element.get("senderCallsign")
                    if chat_element is not None
                    else None
                ),
                room=(
                    chat_element.get("chatroom")
                    if chat_element is not None
                    else None
                ),
                text="".join(remarks.itertext()) if remarks is not None else "",
                time=event_time,
                point=point,
            )
            self._chats.append(message)
            return message

        if point is None:
            return None

        contact_element = _child(detail, "contact")
        callsign = (
            contact_element.get("callsign")
            if contact_element is not None
            else None
        )
        if _type_is(cot_type, "a-f-G"):
            contact = Contact(uid, cot_type, callsign, point, event_time)
            return self._store_latest(self._contacts, contact)

        marker = Marker(uid, cot_type, callsign, point, event_time)
        return self._store_latest(self._markers, marker)

    def get_contact(self, uid_or_callsign: str) -> Optional[Contact]:
        """Find a contact by exact UID, then callsign (case-insensitive)."""

        return _lookup(self._contacts, uid_or_callsign)

    def get_marker(self, uid_or_callsign: str) -> Optional[Marker]:
        """Find a marker by exact UID, then callsign (case-insensitive)."""

        return _lookup(self._markers, uid_or_callsign)

    def list_markers(self) -> List[Marker]:
        """Return a snapshot of the current marker records."""

        return list(self._markers.values())

    def nearest_marker(self, origin: Location) -> Optional[Marker]:
        """Return the marker nearest to ``origin``, or ``None`` if empty."""

        origin_point = self._resolve_point(origin)
        if not self._markers:
            return None
        return min(
            self._markers.values(),
            key=lambda marker: _wgs84_inverse(origin_point, marker.point).range_m,
        )

    def range_bearing(self, origin: Location, target: Location) -> RangeBearing:
        """Calculate WGS-84 surface range and initial true bearing."""

        return _wgs84_inverse(
            self._resolve_point(origin),
            self._resolve_point(target),
        )

    @staticmethod
    def _store_latest(store, event):
        current = store.get(event.uid)
        if current is None or event.time >= current.time:
            store[event.uid] = event
        return event

    def _resolve_point(self, location: Location) -> GeoPoint:
        if isinstance(location, GeoPoint):
            return location
        if isinstance(location, (Contact, Marker)):
            return location.point
        if isinstance(location, str):
            contact = self.get_contact(location)
            if contact is not None:
                return contact.point
            marker = self.get_marker(location)
            if marker is not None:
                return marker.point
            raise KeyError("unknown contact or marker: {!r}".format(location))
        if (
            isinstance(location, Sequence)
            and not isinstance(location, (str, bytes))
            and len(location) >= 2
        ):
            return GeoPoint(float(location[0]), float(location[1]))
        raise TypeError(
            "location must be a GeoPoint, contact, marker, name, or (lat, lon)"
        )


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(parent: Optional[ET.Element], name: str) -> Optional[ET.Element]:
    if parent is None:
        return None
    for element in parent:
        if _local_name(element.tag) == name:
            return element
    return None


def _required_attribute(element: ET.Element, name: str) -> str:
    value = element.get(name)
    if not value:
        raise CoTParseError("CoT event is missing {!r}".format(name))
    return value


def _parse_time(value: str) -> datetime.datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise CoTParseError("invalid CoT time: {!r}".format(value)) from exc
    if parsed.tzinfo is None:
        raise CoTParseError("CoT time must include a timezone")
    return parsed.astimezone(datetime.timezone.utc)


def _optional_float(element: ET.Element, name: str) -> Optional[float]:
    value = element.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise CoTParseError("invalid point {}: {!r}".format(name, value)) from exc


def _parse_point(element: ET.Element) -> GeoPoint:
    latitude = _optional_float(element, "lat")
    longitude = _optional_float(element, "lon")
    if latitude is None or longitude is None:
        raise CoTParseError("CoT point requires lat and lon")
    if not -90.0 <= latitude <= 90.0:
        raise CoTParseError("point latitude is outside WGS-84 bounds")
    if not -180.0 <= longitude <= 180.0:
        raise CoTParseError("point longitude is outside WGS-84 bounds")
    return GeoPoint(
        latitude=latitude,
        longitude=longitude,
        hae=_optional_float(element, "hae"),
        ce=_optional_float(element, "ce"),
        le=_optional_float(element, "le"),
    )


def _type_is(cot_type: str, prefix: str) -> bool:
    return cot_type == prefix or cot_type.startswith(prefix + "-")


def _lookup(records, uid_or_callsign):
    by_uid = records.get(uid_or_callsign)
    if by_uid is not None:
        return by_uid
    values = list(records.values())
    for record in reversed(values):
        if record.callsign == uid_or_callsign:
            return record
    folded = uid_or_callsign.casefold()
    for record in reversed(values):
        if record.callsign is not None and record.callsign.casefold() == folded:
            return record
    return None


def _wgs84_inverse(origin: GeoPoint, target: GeoPoint) -> RangeBearing:
    """Vincenty's inverse solution, with a spherical fallback at antipodes."""

    semi_major = 6378137.0
    flattening = 1.0 / 298.257223563
    semi_minor = (1.0 - flattening) * semi_major
    phi1 = math.radians(origin.latitude)
    phi2 = math.radians(target.latitude)
    longitude_delta = math.radians(target.longitude - origin.longitude)

    if (
        origin.latitude == target.latitude
        and origin.longitude == target.longitude
    ):
        return RangeBearing(0.0, 0.0)

    reduced1 = math.atan((1.0 - flattening) * math.tan(phi1))
    reduced2 = math.atan((1.0 - flattening) * math.tan(phi2))
    sin1, cos1 = math.sin(reduced1), math.cos(reduced1)
    sin2, cos2 = math.sin(reduced2), math.cos(reduced2)
    lam = longitude_delta

    for _ in range(100):
        sin_lam, cos_lam = math.sin(lam), math.cos(lam)
        sin_sigma = math.sqrt(
            (cos2 * sin_lam) ** 2
            + (cos1 * sin2 - sin1 * cos2 * cos_lam) ** 2
        )
        if sin_sigma == 0.0:
            return RangeBearing(0.0, 0.0)
        cos_sigma = sin1 * sin2 + cos1 * cos2 * cos_lam
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = cos1 * cos2 * sin_lam / sin_sigma
        cos_sq_alpha = 1.0 - sin_alpha**2
        cos_two_sigma_m = (
            cos_sigma - 2.0 * sin1 * sin2 / cos_sq_alpha
            if cos_sq_alpha
            else 0.0
        )
        coefficient = (
            flattening
            / 16.0
            * cos_sq_alpha
            * (4.0 + flattening * (4.0 - 3.0 * cos_sq_alpha))
        )
        previous = lam
        lam = longitude_delta + (1.0 - coefficient) * flattening * sin_alpha * (
            sigma
            + coefficient
            * sin_sigma
            * (
                cos_two_sigma_m
                + coefficient
                * cos_sigma
                * (-1.0 + 2.0 * cos_two_sigma_m**2)
            )
        )
        if abs(lam - previous) <= 1e-12:
            break
    else:
        return _spherical_inverse(origin, target)

    u_sq = cos_sq_alpha * (
        (semi_major**2 - semi_minor**2) / semi_minor**2
    )
    series_a = 1.0 + u_sq / 16384.0 * (
        4096.0 + u_sq * (-768.0 + u_sq * (320.0 - 175.0 * u_sq))
    )
    series_b = u_sq / 1024.0 * (
        256.0 + u_sq * (-128.0 + u_sq * (74.0 - 47.0 * u_sq))
    )
    delta_sigma = series_b * sin_sigma * (
        cos_two_sigma_m
        + series_b
        / 4.0
        * (
            cos_sigma * (-1.0 + 2.0 * cos_two_sigma_m**2)
            - series_b
            / 6.0
            * cos_two_sigma_m
            * (-3.0 + 4.0 * sin_sigma**2)
            * (-3.0 + 4.0 * cos_two_sigma_m**2)
        )
    )
    distance = semi_minor * series_a * (sigma - delta_sigma)
    bearing = math.degrees(
        math.atan2(
            cos2 * math.sin(lam),
            cos1 * sin2 - sin1 * cos2 * math.cos(lam),
        )
    )
    return RangeBearing(distance, bearing % 360.0)


def _spherical_inverse(origin: GeoPoint, target: GeoPoint) -> RangeBearing:
    phi1, phi2 = map(math.radians, (origin.latitude, target.latitude))
    delta_phi = phi2 - phi1
    delta_lam = math.radians(target.longitude - origin.longitude)
    haversine = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lam / 2.0) ** 2
    )
    distance = 6371008.8 * 2.0 * math.atan2(
        math.sqrt(haversine), math.sqrt(max(0.0, 1.0 - haversine))
    )
    bearing = math.degrees(
        math.atan2(
            math.sin(delta_lam) * math.cos(phi2),
            math.cos(phi1) * math.sin(phi2)
            - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lam),
        )
    )
    return RangeBearing(distance, bearing % 360.0)


__all__ = [
    "CoTParseError",
    "Contact",
    "GeoChat",
    "GeoPoint",
    "Marker",
    "RangeBearing",
    "SituationalAwareness",
]

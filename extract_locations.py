import datetime
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

XML_PATH = Path("data.xml")
OUTPUT_PATH = Path("data.js")

DATE_PATTERNS = [
    re.compile(r"(\d{4})-(\d{2})-(\d{2})"),
    re.compile(r"(\d{4})(\d{2})(\d{2})"),
]

MANUAL_DATE_OVERRIDES = {
    "slimegardbarnehange": datetime.date.fromisoformat("2023-12-11"),
    "reg-loren": datetime.date.fromisoformat("2024-03-07"),
    "reg-bygdoy": datetime.date.fromisoformat("2024-03-07"),
    "reg-fredensborg": datetime.date.fromisoformat("2024-03-07"),
    "reg-grefsen": datetime.date.fromisoformat("2024-03-07"),
    "reg-gronmo": datetime.date.fromisoformat("2024-03-07"),
    "reg-haraldrud": datetime.date.fromisoformat("2024-03-07"),
    "reg-lilleaker": datetime.date.fromisoformat("2024-03-07"),
    "reg-lindeberg": datetime.date.fromisoformat("2024-03-07"),
    "reg-ryen": datetime.date.fromisoformat("2024-03-07"),
    "reg-smestad": datetime.date.fromisoformat("2024-03-07"),
    "reg-sorenga": datetime.date.fromisoformat("2024-03-07"),
    "reg-trosterud": datetime.date.fromisoformat("2024-03-07"),
    "reg-ulven": datetime.date.fromisoformat("2024-03-07"),
    "haugerudseniorsenter": datetime.date.fromisoformat("2024-03-08"),
    "deichmanholmlia": datetime.date.fromisoformat("2024-05-21"),
    "holmlianaermijolokale": datetime.date.fromisoformat("2024-06-21"),
    "reg-bentsehjornet": datetime.date.fromisoformat("2024-09-09"),
    "reg-vollebekk": datetime.date.fromisoformat("2024-11-27"),
    "reg-sogn": datetime.date.fromisoformat("2024-11-27"),
    "reg-oppsal": datetime.date.fromisoformat("2024-12-20"),
    "bjerke-linderud-senter": datetime.date.fromisoformat("2025-02-21"),
    "kiosken": datetime.date.fromisoformat("2025-02-25"),
    "piloten-arena": datetime.date.fromisoformat("2025-02-25"),
    "frivillighetssentral-boler": datetime.date.fromisoformat("2025-02-25"),
    "admin_vestreaker_frivilligsent": datetime.date.fromisoformat("2025-04-25"),
    "trosterudgard": datetime.date.fromisoformat("2025-09-08"),
    "reg-smedstua": datetime.date.fromisoformat("2025-09-12"),
    "reg-myrer": datetime.date.fromisoformat("2025-09-17"),
    "reg-nedre-haugen": datetime.date.fromisoformat("2025-09-25"),
    "reg-sio-kringsja": datetime.date.fromisoformat("2025-09-25"),
    "reg-skjonhaug": datetime.date.fromisoformat("2025-10-10"),
    "reg-skoyenasen": datetime.date.fromisoformat("2025-10-10"),
    "reg-kalbakken": datetime.date.fromisoformat("2025-10-10"),
    "reg-lindebergskogen": datetime.date.fromisoformat("2025-10-10"),
    "ude_bentsebrua": datetime.date.fromisoformat("2025-10-15"),
    "reg-hoybraten": datetime.date.fromisoformat("2025-10-29"),
}

RANDOMIZED_SUBJECT_IDS = {
    "deichman-fubiak",
    "deichman-toyen",
    "deichman-oppsal",
    "voldslokkaskole",
    "frognerbydelshusd60",
    "frognerseniorsenter",
    "grorudveien-3",
    "vestlitoppenbarnehage",
    "frivillighetenshus",
    "slurpen",
    "sondrenordstrandbydelshus",
    "veslestua",
    "verdenshusethaugenstua",
    "happyroad",
    "haugen-skole",
    "deichman-torshov",
    "hjelpemiddelformidlingen",
    "holmenkollennasjonalanlegg",
    "deichman-stovner",
    "homansbyennaermiljohus",
    "deichmanlambertseter",
    "lindeberg",
    "loftsrudnaermiljohus",
    "majorstuenseniorarena",
    "nedrefossumgard",
    "nordstrandbydelshus",
    "origo",
    "ovrefossumgard",
    "deichman-majorstuen",
    "rachel-grepp--nordre-aker",
    "deichmanroa",
    "deichman-bler",
    "deichman-bjerke",
    "deichman-nydalen",
    "deichman-nordtvet",
    "alnabydelshus",
    "deichman-bjrvika",
    "bydel-nordre-aker",
    "deichman-grnerlkka",
}

RANDOM_DATE_START = datetime.date(2020, 1, 1)
RANDOM_DATE_END = datetime.date(2024, 12, 31)


def pseudo_random_date(subject_id: str) -> datetime.date:
    """Return a deterministic pseudo-random date within the configured range."""
    if not subject_id:
        return RANDOM_DATE_START

    span_days = (RANDOM_DATE_END - RANDOM_DATE_START).days
    digest = hashlib.sha256(subject_id.encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big")
    offset = value % (span_days + 1)
    return RANDOM_DATE_START + datetime.timedelta(days=offset)


def parse_date_from_text(text: str) -> datetime.date | None:
    if not text:
        return None

    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if match:
            year, month, day = match.groups()
            try:
                return datetime.date(int(year), int(month), int(day))
            except ValueError:
                continue
    return None


def build_category_map(root: ET.Element) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for category in root.findall(".//categories/category"):
        category_id = category.get("id")
        name = (category.findtext("name") or "").strip()
        if category_id and name:
            mapping[category_id] = name
    return mapping


def extract_date(subject: ET.Element, fallback: datetime.date) -> datetime.date:
    for tag_name in ("date", "startDate", "start", "published", "publishedAt"):
        node = subject.find(f".//{tag_name}")
        if node is not None and node.text:
            parsed = parse_date_from_text(node.text)
            if parsed:
                return parsed

    for node in subject.iter():
        if node.text:
            parsed = parse_date_from_text(node.text)
            if parsed:
                return parsed

    for node in subject.iter():
        for value in node.attrib.values():
            parsed = parse_date_from_text(value)
            if parsed:
                return parsed

    return fallback


def extract_locations_from_xml(xml_file: Path) -> list[dict]:
    tree = ET.parse(xml_file)
    root = tree.getroot()

    category_map = build_category_map(root)
    fallback_start = datetime.date(2018, 1, 1)

    locations: list[dict] = []
    for index, subject in enumerate(root.findall(".//subjects/subject")):
        name = (subject.findtext("name") or "").strip()
        if not name:
            continue

        coordinates = subject.find("coordinates")
        if coordinates is None:
            continue

        lat_text = coordinates.findtext("lat")
        lon_text = coordinates.findtext("lon") or coordinates.findtext("lng")
        if not lat_text or not lon_text:
            continue

        try:
            lat = float(lat_text)
            lon = float(lon_text)
        except ValueError:
            continue

        subject_id = subject.get("id") or ""
        subject_category_id = subject.get("category")
        category_name = category_map.get(subject_category_id, "Ukjent kategori")

        fallback_date = fallback_start + datetime.timedelta(days=index * 14)
        if subject_id in RANDOMIZED_SUBJECT_IDS:
            date_value = pseudo_random_date(subject_id)
        else:
            manual_override = MANUAL_DATE_OVERRIDES.get(subject_id)
            date_value = manual_override or extract_date(subject, fallback_date)

        locations.append(
            {
                "name": name,
                "lat": round(lat, 6),
                "lng": round(lon, 6),
                "date": date_value.isoformat(),
                "category": category_name,
            }
        )

    return locations


def write_data_js(locations: list[dict], output_path: Path) -> None:
    payload = json.dumps(locations, ensure_ascii=False, indent=2)
    output_lines = [
        "// Auto-generated from data.xml. Contains only name, coordinates, date and category.",
        "const LOCATIONS_DATA = " + payload + ";",
        "if (typeof window !== 'undefined') {",
        "  window.LOCATIONS_DATA = LOCATIONS_DATA;",
        "}",
        "",
    ]
    output = "\n".join(output_lines)
    output_path.write_text(output, encoding="utf-8")


def main() -> None:
    if not XML_PATH.exists():
        raise FileNotFoundError("data.xml is missing in the project root.")

    locations = extract_locations_from_xml(XML_PATH)
    if not locations:
        raise RuntimeError("No valid locations were extracted from data.xml")

    write_data_js(locations, OUTPUT_PATH)
    print(f"Wrote {len(locations)} locations to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

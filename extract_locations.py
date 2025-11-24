import datetime
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

        subject_category_id = subject.get("category")
        category_name = category_map.get(subject_category_id, "Ukjent kategori")

        fallback_date = fallback_start + datetime.timedelta(days=index * 14)
        date_value = extract_date(subject, fallback_date)

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
    output = (
        "// Auto-generated from data.xml. Contains only name, coordinates, date and "
        "category.\n"
        "const LOCATIONS_DATA = "
        f"{payload};\n"
    )
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

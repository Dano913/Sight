from __future__ import annotations

import csv
import zipfile
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path


XLSX_PATH = Path(
    "/tmp/government_bonds_csv/"
    "International Monthly Government Bond Returns.xlsx"
)

OUTPUT_PATH = (
    Path(__file__).resolve().parent
    / "government_bonds.csv"
)

SHEET_PATH = "xl/worksheets/sheet3.xml"

NAMESPACE = (
    "{http://schemas.openxmlformats.org/"
    "spreadsheetml/2006/main}"
)


def excel_date(serial: str) -> date:
    """
    Convert an Excel serial date to a calendar date.
    """

    return date(1899, 12, 30) + timedelta(
        days=int(float(serial))
    )


def cell_value(
    cell: ET.Element,
) -> str | None:
    """
    Return the raw value from an XLSX cell.
    """

    value = cell.find(f"{NAMESPACE}v")

    if value is None:
        return None

    return value.text


def parse_sheet(
    xml_data: bytes,
) -> list[dict[str, object]]:
    """
    Extract observation_date and Cum Ret from
    Improved_US_1947.

    Column A = observation_date
    Column F = Cum Ret
    """

    root = ET.fromstring(xml_data)

    rows: list[dict[str, object]] = []

    for row in root.findall(f".//{NAMESPACE}row"):
        cells = {
            cell.attrib["r"][0]: cell_value(cell)
            for cell in row.findall(f"{NAMESPACE}c")
        }

        observation_date = cells.get("A")
        cumulative_return = cells.get("F")

        if observation_date is None:
            continue

        if cumulative_return is None:
            continue

        # Row 1 contains the column headers as shared-string IDs.
        if row.attrib.get("r") == "1":
            continue

        try:
            parsed_date = excel_date(observation_date)
            value = float(cumulative_return)
        except (TypeError, ValueError):
            continue

        rows.append(
            {
                "date": parsed_date.isoformat(),
                "asset": "GOVERNMENT_BONDS",
                "value": value,
                "source": "SWINKELS_INTERNATIONAL_GOVERNMENT_BOND_RETURNS",
                "value_type": "total_return_index",
            }
        )

    return rows


def main() -> None:
    if not XLSX_PATH.exists():
        raise FileNotFoundError(
            f"Government bond dataset not found: {XLSX_PATH}"
        )

    with zipfile.ZipFile(XLSX_PATH) as archive:
        if SHEET_PATH not in archive.namelist():
            raise ValueError(
                f"{SHEET_PATH} not found in XLSX"
            )

        xml_data = archive.read(SHEET_PATH)

    rows = parse_sheet(xml_data)

    if not rows:
        raise ValueError(
            "No government bond observations found"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "date",
                "asset",
                "value",
                "source",
                "value_type",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"Created: {OUTPUT_PATH}")
    print(f"Rows: {len(rows)}")
    print(f"First: {rows[0]}")
    print(f"Last: {rows[-1]}")


if __name__ == "__main__":
    main()
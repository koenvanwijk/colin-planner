#!/usr/bin/env python3
"""Normalize Heerbeeck vakanties to ISO start/end dates."""
from __future__ import annotations

import json
import re
from datetime import datetime, date
from pathlib import Path

from lineage_utils import write_lineage, build_base_record, sha256_file

SRC = Path("data/heerbeeck_vakanties_2025_2026.json")
OUT = Path("data/heerbeeck_vakanties_2025_2026_normalized.json")
DATASET_ID = "heerbeeck_vakanties_2025_2026_normalized"
PARSER_VERSION = "1.0"

MONTHS = {
    "januari": 1,
    "februari": 2,
    "maart": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "augustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}


def parse_single(d: str) -> date | None:
    # e.g. "maandag 6 april 2026"
    m = re.search(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", d, re.I)
    if not m:
        return None
    day, mon, year = m.groups()
    mon = mon.lower()
    month = MONTHS.get(mon)
    if not month:
        return None
    return date(int(year), month, int(day))


def parse_range(text: str):
    # e.g. "maandag 13 oktober tot en met vrijdag 17 oktober 2025"
    # sometimes year appears once at end
    m = re.search(r"(\d{1,2})\s+([a-z]+).*?(\d{1,2})\s+([a-z]+)\s+(\d{4})", text, re.I)
    if not m:
        return None, None
    d1, mon1, d2, mon2, year = m.groups()
    mon1 = mon1.lower()
    mon2 = mon2.lower()
    m1 = MONTHS.get(mon1)
    m2 = MONTHS.get(mon2)
    if not m1 or not m2:
        return None, None
    return date(int(year), m1, int(d1)), date(int(year), m2, int(d2))


def main():
    src = json.loads(SRC.read_text())
    out_items = []
    for item in src.get("items", []):
        name = item["name"]
        raw = item["date"]
        raw = raw.replace("\xa0", " ")
        # special case: Hemelvaart includes extra friday
        if name.lower().startswith("hemelvaart"):
            # pick first date as start and include next day if mentioned
            start = parse_single(raw)
            end = None
            m = re.search(r"vrijdag\s+(\d{1,2})\s+([a-z]+)\s+(\d{4})", raw, re.I)
            if m:
                d, mon, year = m.groups()
                end = date(int(year), MONTHS[mon.lower()], int(d))
            out_items.append({"name": name, "start": start.isoformat() if start else None, "end": end.isoformat() if end else None, "raw": raw})
            continue

        # range with tot en met
        if "tot en met" in raw:
            start, end = parse_range(raw)
            out_items.append({"name": name, "start": start.isoformat() if start else None, "end": end.isoformat() if end else None, "raw": raw})
            continue

        # single date
        single = parse_single(raw)
        out_items.append({"name": name, "start": single.isoformat() if single else None, "end": single.isoformat() if single else None, "raw": raw})

    OUT.write_text(json.dumps({"source": src.get("source"), "school_year": src.get("school_year"), "items": out_items}, ensure_ascii=False, indent=2))

    record = build_base_record(
        dataset_id=DATASET_ID,
        source_url=src.get("source"),
        fetch_method="transform",
        output_files=[str(OUT)],
        raw_file=str(SRC),
        raw_checksum=sha256_file(SRC),
        parser_version=PARSER_VERSION,
    )
    write_lineage(record)

    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()

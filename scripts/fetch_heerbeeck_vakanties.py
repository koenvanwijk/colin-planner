#!/usr/bin/env python3
"""Fetch Heerbeeck vakanties (schooljaar 2025-2026) and export JSON.

Source: https://heerbeeck.nl/onze-school/vakantierooster/
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

from lineage_utils import write_raw, write_lineage, build_base_record, sha256_file

URL = "https://heerbeeck.nl/onze-school/vakantierooster/"
OUT_PATH = Path("data/heerbeeck_vakanties_2025_2026.json")
DATASET_ID = "heerbeeck_vakanties_2025_2026"
PARSER_VERSION = "1.0"


def strip_tags(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def main():
    raw_bytes = urlopen(URL, timeout=20).read()
    html = raw_bytes.decode("utf-8", errors="ignore")
    text = strip_tags(html)

    # Define labels in order
    labels = [
        "Herfstvakantie",
        "Kerstvakantie",
        "Carnavalsvakantie",
        "Tweede paasdag",
        "Meivakantie",
        "Bevrijdingsdag",
        "Hemelvaart",
        "Tweede pinksterdag",
        "Zomervakantie",
    ]

    items = []
    for label in labels:
        # find the label and capture following date phrase
        m = re.search(rf"{re.escape(label)}\s+([^\n]+?)\s+(?=Herfstvakantie|Kerstvakantie|Carnavalsvakantie|Tweede paasdag|Meivakantie|Bevrijdingsdag|Hemelvaart|Tweede pinksterdag|Zomervakantie|$)", text)
        if m:
            items.append({"name": label, "date": m.group(1).strip()})

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": URL,
        "school_year": "2025-2026",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    raw_path = write_raw(DATASET_ID, "html", raw_bytes)
    record = build_base_record(
        dataset_id=DATASET_ID,
        source_url=URL,
        fetch_method="web_fetch",
        output_files=[str(OUT_PATH)],
        raw_file=str(raw_path),
        raw_checksum=sha256_file(raw_path),
        parser_version=PARSER_VERSION,
    )
    write_lineage(record)

    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()

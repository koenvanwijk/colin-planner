#!/usr/bin/env python3
"""Fetch KNVB speeldagenkalender (Zuid) PDF and extract date ranges.

Best-effort: downloads PDF, runs pdftotext if available, then extracts lines
like "16 / 17 aug. 2025" into JSON.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from urllib.request import urlretrieve

from lineage_utils import write_lineage, build_base_record, sha256_file

PDF_URL = "https://www.knvb.nl/downloads/sites/bestand/knvb/29145/speeldagenkalender-veld-zuid-2025-2026"
OUT_DIR = Path(os.getenv("OUT_DIR", "."))
PDF_PATH = OUT_DIR / "knvb_speeldagenkalender_zuid_2025_2026.pdf"
TXT_PATH = OUT_DIR / "knvb_speeldagenkalender_zuid_2025_2026.txt"
JSON_PATH = OUT_DIR / "knvb_speeldagenkalender_zuid_2025_2026.json"
DATASET_ID = "knvb_speeldagenkalender_zuid_2025_2026"
PARSER_VERSION = "1.0"

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mrt": 3,
    "apr": 4,
    "mei": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sept": 9,
    "okt": 10,
    "nov": 11,
    "dec": 12,
}


def run_pdftotext(pdf_path: Path, txt_path: Path) -> bool:
    try:
        subprocess.run(["pdftotext", str(pdf_path), str(txt_path)], check=True)
        return True
    except Exception:
        return False


def parse_dates(text: str):
    # Matches: 16 / 17 aug. 2025
    pattern = re.compile(r"(\d{1,2})\s*/\s*(\d{1,2})\s+([a-z]{3,4})\.\s+(\d{4})", re.I)
    out = []
    for m in pattern.finditer(text):
        d1, d2, mon, year = m.groups()
        mon_key = mon.lower()[:4]
        mon_key = "sept" if mon_key.startswith("sep") else mon_key[:3]
        month = MONTHS.get(mon_key[:3], None)
        if not month:
            continue
        out.append(
            {
                "start_day": int(d1),
                "end_day": int(d2),
                "month": month,
                "year": int(year),
                "raw": m.group(0),
            }
        )
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    urlretrieve(PDF_URL, PDF_PATH)

    text = ""
    if run_pdftotext(PDF_PATH, TXT_PATH):
        text = TXT_PATH.read_text(errors="ignore")
    else:
        # keep pdf only
        TXT_PATH.write_text("pdftotext not available")

    dates = parse_dates(text)
    JSON_PATH.write_text(json.dumps(dates, ensure_ascii=False, indent=2))

    record = build_base_record(
        dataset_id=DATASET_ID,
        source_url=PDF_URL,
        fetch_method="pdf_download+pdftotext",
        output_files=[str(PDF_PATH), str(TXT_PATH), str(JSON_PATH)],
        raw_file=str(PDF_PATH),
        raw_checksum=sha256_file(PDF_PATH),
        parser_version=PARSER_VERSION,
    )
    write_lineage(record)

    print(f"Saved PDF: {PDF_PATH}")
    print(f"Saved TXT: {TXT_PATH}")
    print(f"Saved JSON: {JSON_PATH} ({len(dates)} date ranges)")


if __name__ == "__main__":
    main()

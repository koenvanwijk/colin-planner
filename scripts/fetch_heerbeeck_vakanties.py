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

URL = "https://heerbeeck.nl/onze-school/vakantierooster/"
OUT_PATH = Path("data/heerbeeck_vakanties_2025_2026.json")


def strip_tags(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def main():
    html = urlopen(URL, timeout=20).read().decode("utf-8", errors="ignore")
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
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()

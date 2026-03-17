#!/usr/bin/env python3
"""Best-effort fetch of vvdbs.nl program, filtered for a team (DBS JO16-2).

Uses WordPress REST endpoints. If the MEC plugin doesn't expose event dates,
we return title/link + published date as a fallback.
"""
from __future__ import annotations

import json
import os
import re
from html import unescape
from urllib.parse import urlencode
from urllib.request import urlopen

from lineage_utils import write_lineage, build_base_record

BASE = os.getenv("VVDBS_BASE", "https://vvdbs.nl")
TEAM = os.getenv("TEAM_QUERY", "DBS JO16-2")
DATASET_ID = "vvdbs_programma_filtered"
PARSER_VERSION = "1.0"


def strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()


def fetch_json(url: str):
    with urlopen(url, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def iter_mec_events():
    page = 1
    while True:
        params = {"per_page": 100, "page": page, "search": TEAM}
        url = f"{BASE}/wp-json/wp/v2/mec-events?{urlencode(params)}"
        data = fetch_json(url)
        if not data:
            break
        for item in data:
            yield item
        page += 1


def main():
    results = []
    for item in iter_mec_events():
        title = item.get("title", {}).get("rendered", "")
        content = item.get("content", {}).get("rendered", "")
        hay = f"{title} {content}".lower()
        if TEAM.lower() not in hay:
            continue
        results.append(
            {
                "title": strip_html(title),
                "published": item.get("date"),
                "link": item.get("link"),
                "snippet": strip_html(content)[:200],
            }
        )

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
}",
        fetch_method="wp-json/mec-events search",
        output_files=[],
        raw_file=None,
        raw_checksum=None,
        parser_version=PARSER_VERSION,
    )
    write_lineage(record)


if __name__ == "__main__":
    main()

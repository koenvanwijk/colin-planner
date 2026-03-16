"""Magister adapter (token-based)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional
import requests


@dataclass
class MagisterConfig:
    tenant: str  # e.g. "vobo"
    token: str
    person_id: int


class MagisterClient:
    def __init__(self, config: MagisterConfig):
        self.config = config
        self.base = f"https://{config.tenant}.magister.net:443"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {config.token}",
            "User-Agent": "Mozilla/5.0",
            "Referer": f"https://{config.tenant}.magister.net/magister/",
            "Connection": "close",
        }

    def roster(self, date_from: date, date_till: date) -> Dict[str, Any]:
        url = f"{self.base}/api/personen/{self.config.person_id}/afspraken"
        params = {"status": 1, "tot": date_till.isoformat(), "van": date_from.isoformat()}
        r = requests.get(url, headers=self.headers, params=params, timeout=20)
        r.raise_for_status()
        return r.json()

    def homework(self, date_from: date, date_till: date) -> List[Dict[str, Any]]:
        raw = self.roster(date_from, date_till)
        items = raw.get("Items") or raw.get("items") or []
        out: List[Dict[str, Any]] = []
        for it in items:
            inhoud = (it.get("Inhoud") or "").strip()
            opm = (it.get("Opmerking") or "").strip()
            if not inhoud and not opm:
                continue
            out.append(
                {
                    "Start": it.get("Start"),
                    "Einde": it.get("Einde"),
                    "Omschrijving": it.get("Omschrijving"),
                    "Locatie": it.get("Lokatie"),
                    "Tekst": inhoud or opm,
                }
            )
        return out

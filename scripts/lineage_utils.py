from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Iterable

LINEAGE_DIR = Path("data/lineage")
RAW_DIR = Path("data/raw")


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def write_raw(dataset_id: str, ext: str, data: bytes) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{dataset_id}.{ext}"
    path.write_bytes(data)
    return path


def write_lineage(record: Dict[str, Any]) -> Path:
    LINEAGE_DIR.mkdir(parents=True, exist_ok=True)
    dataset_id = record["dataset_id"]
    path = LINEAGE_DIR / f"{dataset_id}.json"
    record = {
        **record,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2))
    return path


def build_base_record(dataset_id: str, source_url: str, fetch_method: str, output_files: Iterable[str], raw_file: str | None, raw_checksum: str | None, parser_version: str) -> Dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "source_url": source_url,
        "fetch_method": fetch_method,
        "raw_artifact": raw_file,
        "raw_checksum": raw_checksum,
        "output_files": list(output_files),
        "parser_version": parser_version,
    }

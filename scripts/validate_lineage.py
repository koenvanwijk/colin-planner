from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    print("Missing dependency: jsonschema. Install with `pip install jsonschema`." , file=sys.stderr)
    raise


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    lineage_dir = repo_root / "data" / "lineage"
    schema_path = lineage_dir / "schema.json"

    if not schema_path.exists():
        print(f"Schema not found: {schema_path}", file=sys.stderr)
        return 1

    schema = json.loads(schema_path.read_text())
    validator = Draft202012Validator(schema)

    errors: list[str] = []
    for record_path in sorted(lineage_dir.glob("*.json")):
        if record_path.name == "schema.json":
            continue
        record = json.loads(record_path.read_text())

        for err in validator.iter_errors(record):
            errors.append(f"{record_path}: schema validation error: {err.message}")

        raw_artifact = record.get("raw_artifact")
        if raw_artifact:
            raw_path = repo_root / raw_artifact
            if not raw_path.exists():
                errors.append(f"{record_path}: raw_artifact missing: {raw_artifact}")

        output_files = record.get("output_files") or []
        for output in output_files:
            output_path = repo_root / output
            if not output_path.exists():
                errors.append(f"{record_path}: output_file missing: {output}")

    if errors:
        print("Lineage validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Lineage validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

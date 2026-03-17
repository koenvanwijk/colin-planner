#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required (sudo apt install jq)" >&2
  exit 1
fi

BASE_URL="${MAGISTER_BASE_URL:-http://127.0.0.1:5000}"
USERNAME="${MAGISTER_USERNAME:-}"
PASSWORD="${MAGISTER_PASSWORD:-}"
SCHOOL="${MAGISTER_SCHOOL:-}"
PERSON_ID="${MAGISTER_PERSON_ID:-}"

if [[ -z "$USERNAME" || -z "$PASSWORD" || -z "$SCHOOL" ]]; then
  cat >&2 <<'EOF'
Missing required env vars.
Required:
  MAGISTER_USERNAME
  MAGISTER_PASSWORD
  MAGISTER_SCHOOL
Optional:
  MAGISTER_PERSON_ID (auto-detected from /api/auth if empty)
  MAGISTER_BASE_URL (default: http://127.0.0.1:5000)
EOF
  exit 1
fi

DATE_FROM="$(date +%F)"
DATE_TILL="$(date -d '+7 days' +%F)"

echo "[1/3] Fetching access token..."
AUTH_JSON="$(curl -fsS -G "$BASE_URL/api/auth" \
  --data-urlencode "username=$USERNAME" \
  --data-urlencode "password=$PASSWORD" \
  --data-urlencode "school=$SCHOOL")"

TOKEN="$(echo "$AUTH_JSON" | jq -r '.accessToken // .apitoken // empty')"
if [[ -z "$TOKEN" ]]; then
  echo "Auth failed. Response:" >&2
  echo "$AUTH_JSON" >&2
  exit 1
fi

if [[ -z "$PERSON_ID" ]]; then
  PERSON_ID="$(echo "$AUTH_JSON" | jq -r '.personID // .personId // empty')"
fi
if [[ -z "$PERSON_ID" ]]; then
  echo "Missing personId. Response did not include personID." >&2
  echo "$AUTH_JSON" >&2
  exit 1
fi

echo "[2/3] Fetching roster from $DATE_FROM to $DATE_TILL..."
ROSTER_JSON="$(curl -fsS -G "$BASE_URL/api/rooster" \
  --data-urlencode "apitoken=$TOKEN" \
  --data-urlencode "school=$SCHOOL" \
  --data-urlencode "personId=$PERSON_ID" \
  --data-urlencode "dateFrom=$DATE_FROM" \
  --data-urlencode "dateTill=$DATE_TILL")"

ROSTER_FILE="/tmp/magister_roster_${DATE_FROM}_${DATE_TILL}.json"
printf '%s' "$ROSTER_JSON" > "$ROSTER_FILE"

OUT_FILE="huiswerk_${DATE_FROM}_to_${DATE_TILL}.json"
python - <<PY
import json, re
from pathlib import Path

raw = json.loads(Path("$ROSTER_FILE").read_text())
items = raw.get('Items') or raw.get('items') or []

out = []
for it in items:
    inhoud = (it.get('Inhoud') or '').strip()
    opm = (it.get('Opmerking') or '').strip()
    if not inhoud and not opm:
        continue
    text = inhoud or opm
    text = re.sub('<[^<]+?>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    out.append({
        'Start': it.get('Start') or it.get('start'),
        'Einde': it.get('Einde') or it.get('end') or it.get('End'),
        'Omschrijving': it.get('Omschrijving') or it.get('description') or it.get('Description'),
        'Locatie': it.get('Lokatie') or it.get('location') or it.get('Location'),
        'Tekst': text,
    })

Path("$OUT_FILE").write_text(json.dumps(out, ensure_ascii=False, indent=2))
PY

# lineage (sanitized raw roster)
PYTHONPATH="$SCRIPT_DIR" python - <<PY
import json, hashlib, os, re
from pathlib import Path
from lineage_utils import write_lineage, write_raw

raw_path = Path("$ROSTER_FILE")
obj = json.loads(raw_path.read_text())

PII_KEYS = {
    "docenten",
    "docent",
    "docentid",
    "docentids",
    "docentnaam",
    "docentnaamvolledig",
    "docentafkorting",
    "docentinitialen",
    "leerling",
    "leerlingen",
    "leerlingid",
    "leerlingids",
    "student",
    "students",
    "studentid",
    "personid",
    "persoonid",
    "email",
    "e-mail",
    "telefoon",
    "mobiel",
    "adres",
    "postcode",
    "geboortedatum",
    "geboortedate",
    "geboortedat",
    "geboorte",
    "links",
    "groepen",
    "vakken",
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def scrub(value):
    if isinstance(value, dict):
        cleaned = {}
        for k, v in value.items():
            if k.lower() in PII_KEYS:
                cleaned[k] = None
            else:
                cleaned[k] = scrub(v)
        return cleaned
    if isinstance(value, list):
        return [scrub(v) for v in value]
    if isinstance(value, str):
        if EMAIL_RE.search(value):
            return "[redacted]"
        return value
    return value

obj = scrub(obj)

sanitized = json.dumps(obj, ensure_ascii=False).encode('utf-8')
raw_file = write_raw(Path("$OUT_FILE").stem + "_sanitized", "json", sanitized)

base = os.environ.get("MAGISTER_BASE_URL", "http://127.0.0.1:5000")
record = {
    "dataset_id": Path("$OUT_FILE").stem,
    "source_url": f"{base}/api/rooster",
    "fetch_method": "magister-api",
    "raw_artifact": str(raw_file),
    "raw_checksum": hashlib.sha256(sanitized).hexdigest(),
    "output_files": [str(Path("$OUT_FILE"))],
    "parser_version": "1.0",
}
write_lineage(record)
PY


echo "[3/3] Done. Saved homework to: $OUT_FILE"

echo

echo "Compact preview:"
python - <<PY
import json
from pathlib import Path
p = Path("$OUT_FILE")
items = json.loads(p.read_text())
for it in items[:10]:
    print(f"{it['Start']} | {it['Omschrijving']} | {it['Tekst'][:80]}")
PY

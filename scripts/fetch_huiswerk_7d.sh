#!/usr/bin/env bash
set -euo pipefail

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

OUT_FILE="huiswerk_${DATE_FROM}_to_${DATE_TILL}.json"
python - <<'PY'
import json, re, sys
from datetime import datetime

raw = json.loads(sys.stdin.read())
items = raw.get('Items') or raw.get('items') or []

out = []
for it in items:
    inhoud = (it.get('Inhoud') or '').strip()
    opm = (it.get('Opmerking') or '').strip()
    if not inhoud and not opm:
        continue
    text = inhoud or opm
    # strip html
    text = re.sub('<[^<]+?>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    out.append({
        'Start': it.get('Start') or it.get('start'),
        'Einde': it.get('Einde') or it.get('end') or it.get('End'),
        'Omschrijving': it.get('Omschrijving') or it.get('description') or it.get('Description'),
        'Locatie': it.get('Lokatie') or it.get('location') or it.get('Location'),
        'Tekst': text,
    })

print(json.dumps(out, ensure_ascii=False, indent=2))
PY

# shellcheck disable=SC2005
echo "$(python - <<'PY'
import json, re, sys
from datetime import datetime

raw = json.loads(sys.stdin.read())
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

print(json.dumps(out, ensure_ascii=False, indent=2))
PY
" > "$OUT_FILE"

echo "[3/3] Done. Saved homework to: $OUT_FILE"

echo

echo "Compact preview:"
python - <<'PY'
import json
from pathlib import Path
p = Path('$OUT_FILE')
items = json.loads(p.read_text())
for it in items[:10]:
    print(f"{it['Start']} | {it['Omschrijving']} | {it['Tekst'][:80]}")
PY

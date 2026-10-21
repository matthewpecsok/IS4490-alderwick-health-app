#!/usr/bin/env bash
# Creates the database and loads demo data. Safe to re-run: on a rebuild the
# workspace (and db.sqlite3) survives, so existing data is left alone.
set -euo pipefail

cd "$(dirname "$0")/.."

python manage.py migrate --noinput

if python manage.py shell --no-imports -c "import sys; from clinic.models import Patient; sys.exit(0 if Patient.objects.exists() else 1)"; then
    echo "Demo data already loaded. To reload with fresh dates: python manage.py seed_demo_data --reset"
else
    python manage.py seed_demo_data
fi

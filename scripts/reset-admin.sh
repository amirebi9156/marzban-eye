#!/usr/bin/env bash
set -euo pipefail
cd /opt/marzban-eye
source venv/bin/activate
read -rp "New admin username: " ADMIN_USERNAME
read -rsp "New admin password: " PW; echo
read -rsp "Repeat password: " PW2; echo
[ "$PW" = "$PW2" ] || { echo "Passwords do not match."; exit 1; }
HASH=$(python - <<PY
from passlib.hash import bcrypt
import os
print(bcrypt.hash(os.environ["PW"]))
PY
PW="$PW")
# Update lines in .env (create if missing)
grep -q '^ADMIN_USERNAME=' .env && sed -i "s|^ADMIN_USERNAME=.*|ADMIN_USERNAME=${ADMIN_USERNAME}|" .env || echo "ADMIN_USERNAME=${ADMIN_USERNAME}" >> .env
grep -q '^ADMIN_PASSWORD_HASH=' .env && sed -i "s|^ADMIN_PASSWORD_HASH=.*|ADMIN_PASSWORD_HASH=${HASH}|" .env || echo "ADMIN_PASSWORD_HASH=${HASH}" >> .env
sudo systemctl restart marzban-eye
echo "✅ Updated. Try login again."

#!/usr/bin/env bash
set -euo pipefail

echo "==> Checking Python & venv..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install Python 3.10+ and retry."; exit 1
fi

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

echo "==> Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
# نیازهای Auth و هش:
pip install "passlib[bcrypt]" "python-jose[cryptography]" uvicorn

# Gather Marzban credentials (URL + admin user/pass)
echo
read -rp "Marzban API URL (مثلا https://YOUR_MARZBAN_IP:443): " MARZBAN_API_URL
read -rp "Marzban admin username: " MARZBAN_ADMIN_USERNAME
read -rsp "Marzban admin password: " MARZBAN_ADMIN_PASSWORD; echo

echo
read -rp "Admin username for panel: " ADMIN_USERNAME
# ورودی پسورد بدون نمایش
read -rsp "Admin password: " ADMIN_PASSWORD; echo
read -rsp "Repeat password: " ADMIN_PASSWORD2; echo
if [ "$ADMIN_PASSWORD" != "$ADMIN_PASSWORD2" ]; then
  echo "Passwords do not match."; exit 1
fi

echo "==> Generating bcrypt hash for admin password..."
ADMIN_PASSWORD_HASH=$(python - <<PY
from passlib.hash import bcrypt
import os
pw = os.environ["PW"]
print(bcrypt.hash(pw))
PY
PW="$ADMIN_PASSWORD")

echo "==> Generating JWT secret..."
JWT_SECRET=$(python - <<PY
import secrets; print(secrets.token_hex(48))
PY
)

# تأیید TLS؛ اگر مرزبان گواهی معتبر ندارد، بذار False (برای تست فقط)
read -rp "Verify TLS for Marzban API? (True/False) [True]: " VERIFY_SSL
VERIFY_SSL=${VERIFY_SSL:-True}

# پورت پنل
read -rp "Panel port [9000]: " PANEL_PORT
PANEL_PORT=${PANEL_PORT:-9000}

ENV_FILE="/opt/marzban-eye/.env"
mkdir -p "$(dirname "${ENV_FILE}")"
echo "==> Writing ${ENV_FILE} ..."
cat > "${ENV_FILE}" <<ENV
# --- Admin login (dashboard & JWT) ---
ADMIN_USERNAME=${ADMIN_USERNAME}
ADMIN_PASSWORD_HASH=${ADMIN_PASSWORD_HASH}

# --- JWT ---
JWT_SECRET=${JWT_SECRET}
JWT_EXPIRE_MINUTES=720

# --- Marzban API ---
MARZBAN_API_URL=${MARZBAN_API_URL}
MARZBAN_ADMIN_USERNAME=${MARZBAN_ADMIN_USERNAME}
MARZBAN_ADMIN_PASSWORD=${MARZBAN_ADMIN_PASSWORD}
VERIFY_SSL=${VERIFY_SSL}
MARZBAN_TIMEOUT=15
TOKEN_SKEW_SECONDS=30
TOKEN_FALLBACK_TTL=3300

# --- Server ---
HOST=0.0.0.0
PORT=${PANEL_PORT}
ENV

sed -i '/^MARZBAN_API_TOKEN/d;/^MARZBAN_API_KEY/d' "${ENV_FILE}" 2>/dev/null || true

echo "==> Creating systemd service..."
sudo bash -c "cat > /etc/systemd/system/marzban-eye.service <<SERVICE
[Unit]
Description=Marzban Eye API
After=network.target

[Service]
WorkingDirectory=/opt/marzban-eye
EnvironmentFile=/opt/marzban-eye/.env
ExecStart=/opt/marzban-eye/venv/bin/uvicorn app.main:app --host \${HOST} --port \${PORT}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
SERVICE"

echo "==> Applying service changes..."
if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files | grep -q '^marzban-eye.service'; then
  sudo systemctl daemon-reload
  sudo systemctl restart marzban-eye
  sleep 1
  sudo systemctl status marzban-eye --no-pager || true
elif command -v docker >/dev/null 2>&1 && [ -f docker-compose.yml ]; then
  echo "Docker environment detected. Rebuild/start with:"
  echo "  docker compose up -d --build"
else
  echo "Please restart the marzban-eye service manually."
fi

echo
echo "==> Done."
echo "Open:  http://<YOUR_SERVER_IP>:${PANEL_PORT}/dashboard"
echo "Login with the admin username/password you just set."
echo
echo "NOTE: If using Azure, allow inbound TCP port ${PANEL_PORT} in the VM's NSG (source: your IP only)."

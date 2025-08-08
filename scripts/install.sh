#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/marzban-eye"
PORT="${APP_PORT:-9000}"

sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

if [ ! -d "$APP_DIR" ]; then
  sudo mkdir -p "$APP_DIR"
  sudo chown "$USER":"$USER" "$APP_DIR"
fi

cd "$APP_DIR"

# اگر سورس اینجا نیست، فرض می‌کنیم کلون شده
if [ ! -d "app" ]; then
  echo "Please clone the repository to $APP_DIR before running this installer."
  exit 1
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Fill your .env file at $APP_DIR/.env and rerun: sudo systemctl restart marzban-eye"
fi

sudo tee /etc/systemd/system/marzban-eye.service > /dev/null << EOS
[Unit]
Description=Marzban Eye API
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment="PYTHONUNBUFFERED=1"
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOS

sudo systemctl daemon-reload
sudo systemctl enable --now marzban-eye

echo ">>> Installed. Check: curl http://SERVER_IP:$PORT/health"

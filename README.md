# Marzban-Eye

Marzban-Eye is a lightweight FastAPI dashboard for [Marzban](https://github.com/razordeveloper/marzban) servers. It proxies the Marzban admin API and offers a simple web UI and REST interface secured with JWT authentication.

## Features

- Auto-manages Marzban admin token using username/password
- User listing and basic stats proxying the Marzban API
- Optional dashboard with local admin credentials
- Systemd or Docker deployment

## Requirements

- Python 3.10+
- Access to a running Marzban instance

## Environment Variables

| Variable | Description | Default |
| --- | --- | --- |
| `MARZBAN_API_URL` | Base URL of Marzban API (e.g. `https://host:8000`) | — |
| `MARZBAN_ADMIN_USERNAME` | Marzban admin username used to fetch tokens | — |
| `MARZBAN_ADMIN_PASSWORD` | Marzban admin password | — |
| `VERIFY_SSL` | Verify Marzban TLS certificate | `True` |
| `MARZBAN_TIMEOUT` | HTTP timeout for Marzban requests (seconds) | `15` |
| `TOKEN_SKEW_SECONDS` | Clock skew allowance when refreshing tokens | `30` |
| `TOKEN_FALLBACK_TTL` | Fallback token TTL used before first refresh | `3300` |

## Installation

Clone the repository to `/opt/marzban-eye` and run the installer:

```bash
git clone https://github.com/marzban-eye/marzban-eye.git /opt/marzban-eye
cd /opt/marzban-eye
bash scripts/install.sh
```

The script prompts for:

1. `MARZBAN_API_URL`
2. `MARZBAN_ADMIN_USERNAME`
3. `MARZBAN_ADMIN_PASSWORD`
4. Dashboard admin username & password

Configuration is stored in `/opt/marzban-eye/.env`.

### Easy Install

Run as root or with sudo:

```bash
curl -fsSL https://raw.githubusercontent.com/marzban-eye/marzban-eye/main/scripts/install.sh | sudo bash
```

## Health Check

Verify the service is running:

```bash
curl -f http://localhost:9000/health
```

List users through Marzban using a freshly obtained dashboard token:

```bash
TOKEN=$(curl -s -X POST http://localhost:9000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ADMIN_USER&password=ADMIN_PASS" | jq -r '.access_token')
curl -H "Authorization: Bearer $TOKEN" http://localhost:9000/users
```

Replace `ADMIN_USER`/`ADMIN_PASS` with the dashboard credentials you configured.

## License

MIT


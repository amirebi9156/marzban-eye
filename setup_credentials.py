# setup_credentials.py
import os
from passlib.context import CryptContext

ENV_PATH = ".env"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def read_env(path):
    data = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()
    return data

def write_env(path, data):
    # Keep order: write existing keys first, then new ones
    lines = []
    existing = set()
    if os.path.exists(path):
        with open(path, "r") as f:
            for raw in f:
                line = raw.rstrip("\n")
                if not line or line.startswith("#") or "=" not in line:
                    lines.append(line)
                    continue
                k, _ = line.split("=", 1)
                k = k.strip()
                if k in data:
                    lines.append(f"{k}={data[k]}")
                    existing.add(k)
                else:
                    lines.append(line)
    # Append new keys
    for k, v in data.items():
        if k not in existing:
            lines.append(f"{k}={v}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

def main():
    print("=== Admin credential setup ===")
    username = input("Enter admin username: ").strip()
    password = input("Enter admin password: ").strip()
    if not username or not password:
        print("Username and password cannot be empty.")
        return
    hashed = pwd_context.hash(password)

    env_data = read_env(ENV_PATH)
    env_data["ADMIN_USERNAME"] = username
    env_data["ADMIN_PASSWORD_HASH"] = hashed

    # Make sure JWT secret exists
    if not env_data.get("JWT_SECRET"):
        from secrets import token_hex
        env_data["JWT_SECRET"] = token_hex(48)  # random 96 hex chars

    # Keep default expire if not set
    env_data.setdefault("JWT_EXPIRE_MINUTES", "60")

    write_env(ENV_PATH, env_data)
    print("✅ Admin credentials saved/updated in .env. You can restart the service now.")

if __name__ == "__main__":
    main()

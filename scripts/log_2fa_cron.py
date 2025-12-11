#!/usr/bin/env python3

import os
from datetime import datetime, timezone
import base64
import pyotp

SEED_FILE = "/data/seed.txt"

def read_seed():
    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
            return hex_seed
    except FileNotFoundError:
        print("ERROR: seed.txt not found!")
        return None

def hex_to_base32(hex_seed):
    raw_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(raw_bytes).decode("utf-8")

def generate_totp(hex_seed):
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed)
    return totp.now()

def log_code():
    hex_seed = read_seed()
    if not hex_seed:
        return

    code = generate_totp(hex_seed)

    # UTC timestamp (required!)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Output format
    print(f"{timestamp} 2FA Code: {code}")

if __name__ == "__main__":
    log_code()

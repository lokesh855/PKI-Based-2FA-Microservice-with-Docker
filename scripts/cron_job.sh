#!/usr/bin/env bash
# Ensure UTC timestamps
export TZ=UTC

LOGFILE=/cron/last_code.txt
SEED_FILE=/data/seed.txt

timestamp() {
  date -u +"%Y-%m-%d %H:%M:%S"
}

# Make sure /cron exists
mkdir -p /cron

if [ ! -f "${SEED_FILE}" ]; then
  echo "$(timestamp) ERROR: seed file not found" >&2
  exit 1
fi

# Run python snippet to generate totp code (uses pyotp)
CODE=$(python - <<'PY'
import sys, pyotp, binascii
try:
    with open('/data/seed.txt', 'r') as f:
        hexseed = f.read().strip()
    # validate length
    if len(hexseed) != 64:
        raise SystemExit(1)
    b = binascii.unhexlify(hexseed)
    import base64
    # base32 encode (pyotp expects base32 str w/out padding)
    base32 = base64.b32encode(b).decode('utf-8').strip('=')
    t = pyotp.TOTP(base32)
    print(t.now())
except Exception as e:
    sys.exit(1)
PY
)

if [ $? -ne 0 ] || [ -z "$CODE" ]; then
  echo "$(timestamp) ERROR generating code" >&2
  exit 1
fi

echo "$(timestamp) 2FA Code: ${CODE}" >> "${LOGFILE}"

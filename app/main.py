from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import base64
import time

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# --- Import your functions ---
from app.totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()

# -------------------------------------------------------------
# UPDATED PATHS (correct for Docker)
# -------------------------------------------------------------
SEED_PATH = "/data/seed.txt"                      # seed mount
PRIVATE_KEY_PATH = "/app/student_private.pem"     # private key mount


# -------------------------------------------------------------
# MODELS
# -------------------------------------------------------------
class DecryptRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str


# -------------------------------------------------------------
# ENDPOINT 1: POST /decrypt-seed
# -------------------------------------------------------------
@app.post("/decrypt-seed")
def decrypt_seed(req: DecryptRequest):

    # 1. Load student private key
    try:
        with open(PRIVATE_KEY_PATH, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )
    except Exception:
        raise HTTPException(status_code=500, detail="Private key load failed")

    # 2. Base64 decode encrypted seed
    try:
        encrypted_bytes = base64.b64decode(req.encrypted_seed)
    except:
        raise HTTPException(status_code=400, detail="Invalid base64 string")

    # 3. RSA/OAEP-SHA256 decrypt
    try:
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        hex_seed = decrypted_bytes.decode().strip()
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")

    # 4. Validate hex seed
    if len(hex_seed) != 64 or any(c not in "0123456789abcdef" for c in hex_seed):
        raise HTTPException(status_code=400, detail="Invalid decrypted seed format")

    # 5. Save to /data/seed.txt
    try:
        os.makedirs("/data", exist_ok=True)
        with open(SEED_PATH, "w") as f:
            f.write(hex_seed)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save seed")

    return {"status": "ok"}


# -------------------------------------------------------------
# ENDPOINT 2: GET /generate-2fa
# -------------------------------------------------------------
@app.get("/generate-2fa")
def generate_2fa():

    # 1. Check seed exists
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    # 2. Read seed
    with open(SEED_PATH, "r") as f:
        hex_seed = f.read().strip()

    # 3. Generate TOTP
    try:
        code = generate_totp_code(hex_seed)
    except Exception:
        raise HTTPException(status_code=500, detail="TOTP generation failed")

    # 4. Remaining time
    remaining = 30 - (int(time.time()) % 30)

    return {
        "code": code,
        "valid_for": remaining
    }


# -------------------------------------------------------------
# ENDPOINT 3: POST /verify-2fa
# -------------------------------------------------------------
@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):

    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")

    # Seed check
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    # Read seed
    with open(SEED_PATH, "r") as f:
        hex_seed = f.read().strip()

    # Verify ±1 time step
    try:
        result = verify_totp_code(hex_seed, req.code, valid_window=1)
    except Exception:
        raise HTTPException(status_code=500, detail="Verification error")

    return {"valid": result}

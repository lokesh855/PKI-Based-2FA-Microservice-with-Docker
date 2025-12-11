import pyotp
import base64

def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code from a 64-character hex seed.
    """
    # 1. Convert hex seed to bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # 2. Convert bytes → Base32 (required by TOTP)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    # 3. Initialize TOTP object
    totp = pyotp.TOTP(base32_seed)  # SHA-1, 30s, 6 digits (defaults)

    # 4. Generate current TOTP code
    return totp.now()



def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify a TOTP code using the same hex seed.
    Accepts ±1 time window for clock drift.
    """
    # 1. Convert hex seed to bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # 2. Convert bytes → Base32
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    # 3. Create TOTP object
    totp = pyotp.TOTP(base32_seed)

    # 4. Verify using ± valid_window (default: 1 = 30 seconds)
    return totp.verify(code, valid_window=valid_window)




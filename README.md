# PKI-Based-2FA-Microservice-with-Docker

# Overview

This project implements a complete PKI-secured TOTP-based 2FA verification backend.
It includes:

-RSA key handling

-Seed decryption

-TOTP generation

-2FA verification API

-Cron-based logging of TOTP codes

-Docker + Docker Compose deployment

-Commit-signing proof using RSA-PSS and RSA-OAEP

The system is fully containerized and evaluated based on reproducibility and correct cryptographic implementation.

# Docker Container Build and Run Commands

docker-compose build

docker-compose up -d


# Test Endpoints

# 1. Decrypt seed
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d "{\"encrypted_seed\": \"$(cat encrypted_seed.txt)\"}"

# 2. Generate 2FA code
curl http://localhost:8080/generate-2fa

# 3. Verify valid code
CODE=$(curl -s http://localhost:8080/generate-2fa | jq -r '.code')
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d "{\"code\": \"$CODE\"}"

# 4. Verify invalid code
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "000000"}'

# 5. Check cron output (wait 70+ seconds)
sleep 70
docker exec <container-name> cat /cron/last_code.txt

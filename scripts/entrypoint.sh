#!/usr/bin/env bash
set -e

# Ensure directories exist
mkdir -p /data /cron

# Give proper permissions (cron must write to /cron)
chmod 755 /data
chmod 777 /cron

# Start cron
service cron start || /etc/init.d/cron start || cron

# Start the API
exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level info

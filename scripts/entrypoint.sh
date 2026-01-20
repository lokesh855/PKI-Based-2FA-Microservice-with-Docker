set -e

mkdir -p /data /cron

chmod 755 /data
chmod 777 /cron

service cron start || /etc/init.d/cron start || cron

exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level info

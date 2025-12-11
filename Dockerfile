# ---------- Stage 1: Builder ----------
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

ENV VENV_PATH=/opt/venv
RUN python -m venv ${VENV_PATH} \
    && . ${VENV_PATH}/bin/activate \
    && pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt


# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim

ENV TZ=UTC
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    ca-certificates \
    && ln -fs /usr/share/zoneinfo/UTC /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*


# Create virtual env
ENV VENV_PATH=/opt/venv
RUN python -m venv ${VENV_PATH}
ENV PATH="${VENV_PATH}/bin:${PATH}"


# Install dependencies
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*


# ------------------------------------------------------------
# Copy Project Files
# ------------------------------------------------------------

COPY app/ /app/app/
COPY data/ /data/
COPY encrypted_seed.txt /encrypted_seed.txt
COPY scripts/ /app/scripts/
RUN chmod +x /app/scripts/*.sh

# --- FIXED KEYS COPY  ---
COPY student_private.pem /keys/student_private.pem
COPY student_public.pem /keys/student_public.pem
COPY instructor_public.pem /keys/instructor_public.pem


# ------------------------------------------------------------
# Cron Job Setup
# ------------------------------------------------------------
COPY cron/2fa-cron /etc/cron.d/2fa-cron

RUN chmod 0644 /etc/cron.d/2fa-cron \
    && crontab /etc/cron.d/2fa-cron


# ------------------------------------------------------------
# Create mount points WITH PROPER PERMISSIONS
# ------------------------------------------------------------
RUN mkdir -p /data /cron /var/log/cron \
    && chmod 755 /data \
    && chmod 777 /cron

EXPOSE 8080

ENTRYPOINT ["/app/scripts/entrypoint.sh"]

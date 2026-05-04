#!/bin/sh
set -eu

if [ "${DATA_DIR:-}" = "/data" ]; then
  mkdir -p /data
  if [ ! -f /data/orders.csv ]; then
    cp /app/data/*.csv /data/
  fi
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"

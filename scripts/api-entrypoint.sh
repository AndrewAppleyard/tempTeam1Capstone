#!/bin/sh
set -e

until pg_isready -h db -p 5432 -U postgres; do
  echo "Waiting for Postgres..."
  sleep 1
done

echo "Running Advising-path..."
Advising-path || true

echo "Running Advising-encrypt..."
Advising-encrypt || true

echo "Starting server..."
exec python Advising/app.py
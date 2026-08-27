#!/usr/bin/env bash
set -euo pipefail
BASE=${1:-http://localhost:8080}
curl -fsS "$BASE/api/health"
curl -fsS "$BASE/auth/health"

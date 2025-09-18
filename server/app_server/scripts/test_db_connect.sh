#!/usr/bin/env bash

set -euo pipefail

# Simple Postgres connectivity checker for AWS/production environments.
# - Loads env from --env <file> (e.g., ../secret/.env.prod) if provided
# - Uses ML_DB_URL if set, otherwise DB_APP_URL
# - Tries DNS resolution, TCP connectivity, then optional SQL query via psql

usage() {
  echo "Usage: $0 [--env <path_to_env_file>] [--url <db_url_override>]" >&2
  echo "  Example: $0 --env ../secret/.env.prod" >&2
}

ENV_FILE=""
URL_OVERRIDE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_FILE="$2"; shift 2 ;;
    --url)
      URL_OVERRIDE="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"

if [[ -n "$ENV_FILE" ]]; then
  if [[ -f "$ENV_FILE" ]]; then
    echo "[INFO] Loading env from $ENV_FILE"
    # Robust .env loader: only accept KEY=VALUE lines; ignore others (e.g., INI headers, comments, YAML)
    while IFS= read -r line || [[ -n "$line" ]]; do
      # Trim leading/trailing spaces
      line="${line%%[[:space:]]*}$([[ ${line##*[![:space:]]} ]] && printf '')"
      # Skip blanks or comments
      [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
      # Accept only KEY=VALUE format (allow spaces around '=')
      if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=[[:space:]]*.+$ ]]; then
        key="${line%%=*}"
        val="${line#*=}"
        # Trim spaces around key and value
        key="${key//[[:space:]]/}"
        val="${val##[[:space:]]}"
        val="${val%%[[:space:]]}"
        # Strip surrounding single/double quotes
        [[ "$val" =~ ^\".*\"$ ]] && val="${val:1:${#val}-2}"
        [[ "$val" =~ ^\'.*\'$ ]] && val="${val:1:${#val}-2}"
        export "$key"="$val"
      else
        # Ignore lines like "Section:", "Server:", INI headers, etc.
        continue
      fi
    done < "$ENV_FILE"
  else
    echo "[WARN] Env file not found: $ENV_FILE" >&2
  fi
fi

DB_URL="${URL_OVERRIDE:-${ML_DB_URL:-${DB_APP_URL:-}}}"
if [[ -z "${DB_URL}" ]]; then
  echo "[ERROR] Neither ML_DB_URL nor DB_APP_URL is set. Use --env or --url." >&2
  exit 2
fi

echo "[INFO] Using DB URL: ${DB_URL}"

# Normalize scheme for general parsing/psql compatibility
NORM_URL="${DB_URL//postgresql+asyncpg:\/\//postgresql://}"

# Extract components using bash/awk
# Supports: postgresql://user:pass@host:port/dbname?params
proto_removed="${NORM_URL#*://}"
creds_and_host="${proto_removed%%/*}"   # user:pass@host:port
DB_NAME_AND_PARAMS="${proto_removed#*/}" # dbname?params
DB_NAME="${DB_NAME_AND_PARAMS%%\?*}"    # dbname
hostpart="${creds_and_host#*@}"         # host:port
userpass="${creds_and_host%@*}"         # user:pass

DB_HOST="${hostpart%%:*}"
DB_PORT="${hostpart##*:}"
[[ "$DB_PORT" == "$hostpart" ]] && DB_PORT="5432"

DB_USER="${userpass%%:*}"
DB_PASS_ENC="${userpass#*:}"
[[ "$DB_PASS_ENC" == "$DB_USER" ]] && DB_PASS_ENC=""

echo "[INFO] Parsed host=$DB_HOST port=$DB_PORT db=$DB_NAME user=$DB_USER"

echo "[STEP] DNS resolution"
if command -v getent >/dev/null 2>&1; then
  if ! getent hosts "$DB_HOST" >/dev/null 2>&1; then
    echo "[WARN] getent failed to resolve $DB_HOST" >&2
  else
    echo "[OK] getent resolved $DB_HOST"
  fi
elif command -v nslookup >/dev/null 2>&1; then
  if ! nslookup "$DB_HOST" >/dev/null 2>&1; then
    echo "[WARN] nslookup failed to resolve $DB_HOST" >&2
  else
    echo "[OK] nslookup resolved $DB_HOST"
  fi
else
  echo "[INFO] getent/nslookup not available; skipping DNS check"
fi

echo "[STEP] TCP connectivity"
if command -v nc >/dev/null 2>&1; then
  if nc -z -w 3 "$DB_HOST" "$DB_PORT"; then
    echo "[OK] TCP connectivity to $DB_HOST:$DB_PORT"
  else
    echo "[ERROR] Cannot reach $DB_HOST:$DB_PORT via TCP" >&2
    exit 3
  fi
else
  # Fallback to bash /dev/tcp
  if timeout 3 bash -c "</dev/tcp/$DB_HOST/$DB_PORT" 2>/dev/null; then
    echo "[OK] TCP connectivity to $DB_HOST:$DB_PORT"
  else
    echo "[ERROR] Cannot reach $DB_HOST:$DB_PORT via TCP (no nc)" >&2
    exit 3
  fi
fi

echo "[STEP] SQL query via psql (if available)"
if command -v psql >/dev/null 2>&1; then
  # Use URL directly so psql handles percent-encoded password
  # Add sslmode from URL params if present; otherwise rely on default
  set +e
  PSQL_OUT=$(psql "$NORM_URL" -c "SELECT version();" -tAo 2>&1)
  PSQL_CODE=$?
  set -e
  if [[ $PSQL_CODE -ne 0 ]]; then
    echo "[WARN] psql query failed: $PSQL_OUT" >&2
    echo "[INFO] Network OK; verify credentials/SSL parameters"
  else
    echo "[OK] psql succeeded. Version: $PSQL_OUT"
  fi
else
  echo "[INFO] psql is not installed; skipped SQL query. Network looks OK."
fi

echo "[DONE] DB connectivity checks completed."


#!/usr/bin/env bash
# ==============================================================================
# Sprints LEARMS - Active Process Telemetry & Resource Monitoring
# Sprint 3 - Advanced Operations (ps, grep, CPU/Memory telemetry)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================================="
echo "       SPRINTS LEARMS - ACTIVE PROCESS TELEMETRY MONITOR         "
echo "================================================================="
echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "Operator : $(whoami)"
echo "-----------------------------------------------------------------"

cd "$APP_ROOT"

echo "[1/4] Launching LEARMS ingestion in background with simulated load..."
python3 "$APP_ROOT/code/main.py" --simulate-load &
PID=$!
echo "Application process launched with PID: $PID"

echo "-----------------------------------------------------------------"
echo "[2/4] Monitoring active process using 'ps' and 'grep'..."
sleep 0.2

# Monitor active process table
echo "Filtering process table: ps aux | grep python3"
ps aux | head -n 1
ps aux | grep -E "[p]ython3.*code/main\.py" || true

echo "-----------------------------------------------------------------"
echo "[3/4] Detailed Memory and CPU State Verification for PID $PID:"
if ps -p "$PID" > /dev/null 2>&1; then
    ps -p "$PID" -o pid,ppid,user,group,%cpu,%mem,vsz,rss,stat,start,time,comm
    
    echo ""
    echo "Process telemetry breakdown:"
    CPU_MEM=$(ps -p "$PID" -o %cpu,%mem,vsz,rss --no-headers || echo "0.0 0.0 0 0")
    echo "  -> %CPU Utilization: $(echo "$CPU_MEM" | awk '{print $1}')%"
    echo "  -> %MEM Utilization: $(echo "$CPU_MEM" | awk '{print $2}')%"
    echo "  -> Virtual Size (VSZ): $(echo "$CPU_MEM" | awk '{print $3}') KB"
    echo "  -> Resident Set Size (RSS): $(echo "$CPU_MEM" | awk '{print $4}') KB"
fi

echo "-----------------------------------------------------------------"
echo "[4/4] Awaiting background process completion..."
if wait "$PID"; then
    EXIT_STATUS=0
    echo "[SUCCESS] Process $PID terminated normally with exit status 0."
else
    EXIT_STATUS=$?
    echo "[FATAL ERROR] Process $PID terminated abnormally with exit status $EXIT_STATUS." >&2
    exit "$EXIT_STATUS"
fi
echo "================================================================="

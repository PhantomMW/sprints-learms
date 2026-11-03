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
if MATCHED_PROC=$(ps aux | grep -E "[p]ython3.*code/main\.py"); then
    echo "$MATCHED_PROC"
else
    echo "[WARNING] Target process $PID not detected in process table snapshot (may have already completed)." >&2
fi

echo "-----------------------------------------------------------------"
echo "[3/4] Detailed Memory and CPU State Verification for PID $PID:"
if ps -p "$PID" > /dev/null 2>&1; then
    ps -p "$PID" -o pid,ppid,user,group,%cpu,%mem,vsz,rss,stat,start,time,comm
    
    echo ""
    echo "Process telemetry breakdown:"
    if CPU_MEM=$(ps -p "$PID" -o %cpu,%mem,vsz,rss --no-headers 2>/dev/null) && [ -n "$CPU_MEM" ]; then
        echo "  -> %CPU Utilization: $(echo "$CPU_MEM" | awk '{print $1}')%"
        echo "  -> %MEM Utilization: $(echo "$CPU_MEM" | awk '{print $2}')%"
        echo "  -> Virtual Size (VSZ): $(echo "$CPU_MEM" | awk '{print $3}') KB"
        echo "  -> Resident Set Size (RSS): $(echo "$CPU_MEM" | awk '{print $4}') KB"
    else
        echo "[ERROR] Failed to query telemetry metrics for PID $PID (process terminated prematurely)." >&2
    fi
else
    echo "[WARNING] Process $PID is not running; telemetry metrics could not be retrieved." >&2
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

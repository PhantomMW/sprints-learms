#!/usr/bin/env bash
# ==============================================================================
# Sprints LEARMS - Linux Environment Setup & Security Hardening Script
# Sprint 3 - Basic & Advanced Linux Operations
# Author: Mohammed Wael (Junior Solutions Consultant)
# ==============================================================================

set -euo pipefail

echo "================================================================="
echo "   SPRINTS LEARMS - LINUX ENVIRONMENT PROVISIONING & SECURITY    "
echo "================================================================="
echo "Execution Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "Host Machine       : $(hostname)"
echo "Kernel Release     : $(uname -r)"
echo "Current User       : $(whoami)"
echo "-----------------------------------------------------------------"

# Step 1: Package Management (Sprint 3 - Basic Operations)
echo "[STEP 1/4] Updating package repositories and installing SQLite3..."
apt-get update -qq
apt-get install -y sqlite3 libsqlite3-dev

echo "[VERIFICATION] Installed SQLite3 binary:"
which sqlite3
sqlite3 --version

# Step 2: User & Group Access Management (Sprint 3 - Advanced Operations)
echo "-----------------------------------------------------------------"
echo "[STEP 2/4] Provisioning primary administrative group 'sprints_ops'..."
if ! getent group sprints_ops > /dev/null 2>&1; then
    groupadd -f sprints_ops
    echo "Created user group: sprints_ops"
else
    echo "Group sprints_ops already exists."
fi

# Ensure default WSL user belongs to sprints_ops
TARGET_USER="$(awk -F: '$3 == 1000 {print $1}' /etc/passwd)"
if [ -z "$TARGET_USER" ]; then
    TARGET_USER="mw851"
fi
usermod -a -G sprints_ops "$TARGET_USER"
echo "Assigned user '$TARGET_USER' to group 'sprints_ops'."

# Step 3: Permissions Hardening (chmod / chown)
echo "-----------------------------------------------------------------"
echo "[STEP 3/4] Configuring directory group ownership and least-privilege permissions..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Application Root: $APP_ROOT"

# Set group ownership to sprints_ops
chown -R "$TARGET_USER:sprints_ops" "$APP_ROOT" || true

# Apply hardened octal permissions:
# - Directories: 750 (rwxr-x---)
# - Python code & Bash scripts: 750 (rwxr-x---)
# - Relational Database: 640 (rw-r-----)
# - Operational Logs: 660 (rw-rw----)
find "$APP_ROOT" -type d -exec chmod 750 {} + || true
chmod 750 "$APP_ROOT"/code/*.py || true
chmod 750 "$APP_ROOT"/scripts/*.sh || true
chmod 640 "$APP_ROOT"/data/*.db 2>/dev/null || true
chmod 660 "$APP_ROOT"/logs/*.log 2>/dev/null || true

echo "[VERIFICATION] Validated directory permissions and group ownership:"
ls -ld "$APP_ROOT"
ls -la "$APP_ROOT/code"
ls -la "$APP_ROOT/data"
ls -la "$APP_ROOT/logs"

echo "-----------------------------------------------------------------"
echo "[STEP 4/4] Environment setup completed successfully."
echo "================================================================="

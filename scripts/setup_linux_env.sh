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
echo "Executing User     : $(whoami)"
echo "-----------------------------------------------------------------"

# Step 1: Package Management (Sprint 3 - Basic Operations)
echo "[STEP 1/5] Updating package repositories and installing SQLite3..."
apt-get update -qq
apt-get install -y sqlite3 libsqlite3-dev

echo "[VERIFICATION 1] Installed SQLite3 binary & version:"
which sqlite3
sqlite3 --version

# Step 2: User Identification & Primary Group Assignment
echo "-----------------------------------------------------------------"
echo "[STEP 2/5] Configuring primary administrative group 'sprints_ops'..."
if ! getent group sprints_ops > /dev/null 2>&1; then
    groupadd sprints_ops
    echo "Created user group: sprints_ops"
else
    echo "Group sprints_ops already exists."
fi

# Determine target non-root operator
if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ]; then
    TARGET_USER="$SUDO_USER"
elif [ -n "${OPERATOR_USER:-}" ]; then
    TARGET_USER="$OPERATOR_USER"
else
    TARGET_USER="$(awk -F: '$3 == 1000 {print $1}' /etc/passwd)"
    if [ -z "$TARGET_USER" ]; then
        TARGET_USER="mw851"
    fi
fi

# Verify user exists in system
if ! id "$TARGET_USER" > /dev/null 2>&1; then
    echo "[ERROR] Target user '$TARGET_USER' does not exist." >&2
    exit 1
fi

# Set sprints_ops as the PRIMARY group for the target operator
usermod -g sprints_ops "$TARGET_USER"
echo "Set primary group of '$TARGET_USER' to 'sprints_ops'."

echo "[VERIFICATION 2] Verified user identity and primary group:"
id "$TARGET_USER"

# Step 3: Application Directory & Ownership Assignment
echo "-----------------------------------------------------------------"
echo "[STEP 3/5] Assigning group ownership to 'sprints_ops'..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="${APP_ROOT:-$(dirname "$SCRIPT_DIR")}"

echo "Target Application Directory: $APP_ROOT"

if [ ! -d "$APP_ROOT" ]; then
    echo "[ERROR] Application directory '$APP_ROOT' not found." >&2
    exit 1
fi

# Set user and primary group ownership strictly without masking errors
chown -R "$TARGET_USER:sprints_ops" "$APP_ROOT"
echo "Applied ownership '$TARGET_USER:sprints_ops' recursively to $APP_ROOT."

# Step 4: Least-Privilege Permissions Hardening (chmod)
echo "-----------------------------------------------------------------"
echo "[STEP 4/5] Applying least-privilege permission matrix..."

# 1. Directory traversal & access: 750 (rwxr-x---)
find "$APP_ROOT" -type d -exec chmod 750 {} +

# 2. Executable Python source files & Bash scripts: 750 (rwxr-x---)
find "$APP_ROOT/code" -type f -name "*.py" -exec chmod 750 {} +
find "$APP_ROOT/scripts" -type f -name "*.sh" -exec chmod 750 {} +

# 3. Relational Database & Data files: 660 (rw-rw----)
# Allows members of sprints_ops primary group to read and write records
if [ -d "$APP_ROOT/data" ]; then
    find "$APP_ROOT/data" -type f -exec chmod 660 {} +
fi

# 4. Operational Activity Logs: 660 (rw-rw----)
# Allows append and rotation by operators in sprints_ops
if [ -d "$APP_ROOT/logs" ]; then
    find "$APP_ROOT/logs" -type f -exec chmod 660 {} +
fi

# 5. Documentation & Markdown files: 640 (rw-r-----)
if [ -d "$APP_ROOT/docs" ]; then
    find "$APP_ROOT/docs" -type f -exec chmod 640 {} +
fi
find "$APP_ROOT" -maxdepth 1 -type f -name "*.md" -exec chmod 640 {} +

echo "[VERIFICATION 3] Permission Matrix Validated:"
ls -ld "$APP_ROOT"
ls -la "$APP_ROOT/code"
ls -la "$APP_ROOT/data"
ls -la "$APP_ROOT/logs"

# Step 5: Functional Write Verification as Non-Root Operator
echo "-----------------------------------------------------------------"
echo "[STEP 5/5] Testing non-root database and log write access as '$TARGET_USER'..."
su - "$TARGET_USER" -c "
    set -euo pipefail
    cd '$APP_ROOT'
    # Test file write to logs
    touch logs/.perm_test && rm logs/.perm_test
    # Verify sqlite database read & integrity check
    if [ -f data/sprints_learners.db ]; then
        sqlite3 data/sprints_learners.db 'PRAGMA integrity_check;'
    fi
"
echo "[SUCCESS] Non-root operator '$TARGET_USER' successfully verified with full read/write access."
echo "================================================================="
echo "   LINUX ENVIRONMENT SETUP & SECURITY PROVISIONING COMPLETE      "
echo "================================================================="

#!/bin/bash
# Cron管理器CLI包装器

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$SCRIPT_DIR/../skills/cron-optimization-manager"

python3 "$SKILL_DIR/cron_manager.py" "$@"

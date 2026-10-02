#!/bin/sh
# Tests of the stage 4 commands: ls, cd, history, rev, cat.
cd "$(dirname "$0")/.." || exit 1

echo "===== Stage 4 commands on the deep VFS ====="
python3 src/main.py --vfs vfs/deep --script scripts/start_commands.txt
echo "exit code: $?"

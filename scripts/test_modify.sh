#!/bin/sh
# Tests of the stage 5 commands: chown, rm.
cd "$(dirname "$0")/.." || exit 1
rm -rf out

echo "===== Stage 5 commands on the deep VFS ====="
python3 src/main.py --vfs vfs/deep --script scripts/start_modify.txt
echo "exit code: $?"
echo "----- source VFS on disk is unchanged:"
git status --short vfs/deep && echo "no changes in vfs/deep"
echo "----- differences between the source and the saved VFS:"
diff -r vfs/deep out/modified

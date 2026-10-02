#!/bin/sh
# Tests with a VFS of several files in one directory.
cd "$(dirname "$0")/.." || exit 1
rm -rf out

echo "===== VFS with several files ====="
python3 src/main.py --vfs vfs/files --script scripts/start_vfs.txt
echo "exit code: $?"
diff -r vfs/files out/vfs_copy && echo "saved copy is identical"

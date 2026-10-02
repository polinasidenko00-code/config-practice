#!/bin/sh
# Tests with a VFS of 3+ levels of files and directories.
cd "$(dirname "$0")/.." || exit 1
rm -rf out

echo "===== VFS with several levels of directories ====="
python3 src/main.py --vfs vfs/deep --script scripts/start_vfs.txt
echo "exit code: $?"
echo "----- source VFS:"
find vfs/deep | sort
diff -r vfs/deep out/vfs_copy && echo "saved copy is identical"

rm -rf out/vfs_copy
echo "===== Same VFS, path with a trailing separator ====="
python3 src/main.py --vfs vfs/deep/ --script scripts/start_vfs.txt
echo "exit code: $?"

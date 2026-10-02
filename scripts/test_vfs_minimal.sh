#!/bin/sh
# Tests with minimal VFS variants: an empty directory and a
# directory with a single file.
cd "$(dirname "$0")/.." || exit 1
rm -rf out
mkdir -p out/empty_vfs

echo "===== 1. Empty VFS directory ====="
python3 src/main.py --vfs out/empty_vfs --script scripts/start_vfs.txt
echo "exit code: $?"
diff -r out/empty_vfs out/vfs_copy && echo "saved copy is identical"

rm -rf out/vfs_copy
echo "===== 2. Minimal VFS: a single file ====="
python3 src/main.py --vfs vfs/minimal --script scripts/start_vfs.txt
echo "exit code: $?"
diff -r vfs/minimal out/vfs_copy && echo "saved copy is identical"

#!/bin/sh
# Tests of VFS loading errors.
cd "$(dirname "$0")/.." || exit 1

echo "===== 1. VFS path does not exist ====="
python3 src/main.py --vfs vfs/no_such_vfs --script scripts/start_vfs.txt
echo "exit code: $?"

echo "===== 2. Invalid format: a file instead of a directory ====="
python3 src/main.py --vfs vfs/not_a_directory.txt
echo "exit code: $?"

echo "===== 3. Invalid format: a symbolic link inside the VFS ====="
rm -rf out/link_vfs
mkdir -p out/link_vfs
ln -s ../../vfs/minimal/readme.txt out/link_vfs/link.txt
python3 src/main.py --vfs out/link_vfs
echo "exit code: $?"

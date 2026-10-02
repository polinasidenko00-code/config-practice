#!/bin/sh
# Tests of the --vfs parameter.
DIR="$(cd "$(dirname "$0")" && pwd)"
EMU="$DIR/../src/main.py"
START="$DIR/start_basic.txt"

echo "===== 1. No parameters (default VFS name) ====="
echo exit | python3 "$EMU"
echo "exit code: $?"

echo "===== 2. Relative VFS path ====="
python3 "$EMU" --vfs vfs/demo --script "$START"
echo "exit code: $?"

echo "===== 3. Absolute VFS path with trailing separator ====="
python3 "$EMU" --vfs /home/user/my_vfs/ --script "$START"
echo "exit code: $?"

echo "===== 4. Root directory (default VFS name) ====="
python3 "$EMU" --vfs / --script "$START"
echo "exit code: $?"

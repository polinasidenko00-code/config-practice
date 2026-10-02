#!/bin/sh
# Tests of combined and invalid command line parameters.
DIR="$(cd "$(dirname "$0")" && pwd)"
EMU="$DIR/../src/main.py"

echo "===== 1. Both parameters ====="
python3 "$EMU" --vfs "$DIR/../vfs/deep" --script "$DIR/start_basic.txt"
echo "exit code: $?"

echo "===== 2. Both parameters in reverse order ====="
python3 "$EMU" --script "$DIR/start_errors.txt" --vfs "$DIR/../vfs/deep"
echo "exit code: $?"

echo "===== 3. Help ====="
python3 "$EMU" --help
echo "exit code: $?"

echo "===== 4. Unknown parameter ====="
python3 "$EMU" --unknown
echo "exit code: $?"

echo "===== 5. Parameter without value ====="
python3 "$EMU" --vfs
echo "exit code: $?"

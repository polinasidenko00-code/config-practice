#!/bin/sh
# Tests of the --script parameter.
DIR="$(cd "$(dirname "$0")" && pwd)"
EMU="$DIR/../src/main.py"

echo "===== 1. Script with all commands ====="
python3 "$EMU" --script "$DIR/start_basic.txt" --vfs "$DIR/../vfs/deep"
echo "exit code: $?"

echo "===== 2. Script with errors and exit code 3 ====="
python3 "$EMU" --script "$DIR/start_errors.txt" --vfs "$DIR/../vfs/deep"
echo "exit code: $?"

echo "===== 3. Script without exit, then interactive input ====="
printf 'ls user\nexit 0\n' \
    | python3 "$EMU" --script "$DIR/start_interactive.txt" --vfs "$DIR/../vfs/deep"
echo "exit code: $?"

echo "===== 4. Missing script file ====="
python3 "$EMU" --script "$DIR/no_such_script.txt"
echo "exit code: $?"

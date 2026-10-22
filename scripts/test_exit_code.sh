#!/bin/sh
# Test 3: exit codes of the emulator process.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAIN="$ROOT/src/main.py"
EXAMPLES="$ROOT/examples"
VFS="$EXAMPLES/vfs/deep.xml"
PYTHON="${PYTHON:-python3}"

echo "=== 1. --vfs and --script ending with 'exit 3' (window closes itself) ==="
"$PYTHON" "$MAIN" --vfs "$VFS" --script "$EXAMPLES/startup_exit.emu"
echo "exit code: $? (expected 3)"

echo "=== 2. Only --script ending with 'exit 3' ==="
"$PYTHON" "$MAIN" --script "$EXAMPLES/startup_exit.emu"
echo "exit code: $? (expected 3)"

echo "=== 3. Only --vfs: type 'exit 5' in the window ==="
"$PYTHON" "$MAIN" --vfs "$VFS"
echo "exit code: $? (expected 5)"

echo "=== 4. Both parameters, script without exit: close the window ==="
"$PYTHON" "$MAIN" --vfs "$VFS" --script "$EXAMPLES/startup_ok.emu"
echo "exit code: $? (expected 0)"

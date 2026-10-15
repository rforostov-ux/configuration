#!/bin/sh
# Test 1: all combinations of command-line parameters.
# Each call opens a window; close it (or type exit) to run the next call.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAIN="$ROOT/src/main.py"
EXAMPLES="$ROOT/examples"
VFS="$EXAMPLES/demo_vfs.xml"
PYTHON="${PYTHON:-python3}"

echo "=== 1. No parameters (defaults) ==="
"$PYTHON" "$MAIN"

echo "=== 2. Only --vfs (path is shown in the debug output) ==="
"$PYTHON" "$MAIN" --vfs "$VFS"

echo "=== 3. Only --script ==="
"$PYTHON" "$MAIN" --script "$EXAMPLES/startup_ok.emu"

echo "=== 4. Both --vfs and --script ==="
"$PYTHON" "$MAIN" --vfs "$VFS" --script "$EXAMPLES/startup_ok.emu"

echo "=== 5. Both parameters, other order, --name=value form ==="
"$PYTHON" "$MAIN" --script="$EXAMPLES/startup_ok.emu" --vfs="$VFS"

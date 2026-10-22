#!/bin/sh
# Test: deep VFS, more than 3 levels of directories and files.
# Close the window (or type exit) to run the next call.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAIN="$ROOT/src/main.py"
EXAMPLES="$ROOT/examples"
VFS_DIR="$EXAMPLES/vfs"
SCRIPT="$EXAMPLES/startup_vfs.emu"
PYTHON="${PYTHON:-python3}"

echo "=== 1. Deep VFS with the stage 3 startup script ==="
"$PYTHON" "$MAIN" --vfs "$VFS_DIR/deep.xml" --script "$SCRIPT"

echo "=== 2. Deep VFS, --name=value form of the parameter ==="
"$PYTHON" "$MAIN" --vfs="$VFS_DIR/deep.xml" --script "$SCRIPT"

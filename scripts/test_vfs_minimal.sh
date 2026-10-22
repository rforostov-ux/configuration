#!/bin/sh
# Test: minimal VFS (only the root directory).
# Close the window (or type exit) to run the next call.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAIN="$ROOT/src/main.py"
EXAMPLES="$ROOT/examples"
VFS_DIR="$EXAMPLES/vfs"
SCRIPT="$EXAMPLES/startup_vfs.emu"
PYTHON="${PYTHON:-python3}"

echo "=== 1. Minimal VFS with the stage 3 startup script ==="
"$PYTHON" "$MAIN" --vfs "$VFS_DIR/minimal.xml" --script "$SCRIPT"

echo "=== 2. Minimal VFS, type vfs-info by hand ==="
"$PYTHON" "$MAIN" --vfs "$VFS_DIR/minimal.xml"

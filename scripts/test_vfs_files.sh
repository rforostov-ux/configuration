#!/bin/sh
# Test: VFS with several files, including a binary (base64) one.
# Close the window (or type exit) to run the next call.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAIN="$ROOT/src/main.py"
EXAMPLES="$ROOT/examples"
VFS_DIR="$EXAMPLES/vfs"
SCRIPT="$EXAMPLES/startup_vfs.emu"
PYTHON="${PYTHON:-python3}"

echo "=== 1. Several files with the stage 3 startup script ==="
"$PYTHON" "$MAIN" --vfs "$VFS_DIR/files.xml" --script "$SCRIPT"

echo "=== 2. Several files, type vfs-info by hand ==="
"$PYTHON" "$MAIN" --vfs "$VFS_DIR/files.xml"

#!/bin/sh
# Test: VFS loading errors. The window opens with an empty VFS.
# Close the window (or type exit) to run the next call.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAIN="$ROOT/src/main.py"
EXAMPLES="$ROOT/examples"
VFS_DIR="$EXAMPLES/vfs"
SCRIPT="$EXAMPLES/startup_vfs.emu"
PYTHON="${PYTHON:-python3}"

echo "=== 1. VFS file does not exist ==="
"$PYTHON" "$MAIN" --vfs "$VFS_DIR/no_such_vfs.xml" --script "$SCRIPT"

echo "=== 2. Broken XML ==="
"$PYTHON" "$MAIN" --vfs "$VFS_DIR/broken.xml" --script "$SCRIPT"

echo "=== 3. Not an XML file at all ==="
"$PYTHON" "$MAIN" --vfs "$ROOT/README.md" --script "$SCRIPT"

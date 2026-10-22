#!/bin/sh
# Test: stage 4 commands (ls, cd, tail, tac) on examples/vfs/deep.xml.
# First the full stage 4 startup script, then one script per error case.
# Close the window (or type exit) to run the next call.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAIN="$ROOT/src/main.py"
EXAMPLES="$ROOT/examples"
VFS="$EXAMPLES/vfs/deep.xml"
PYTHON="${PYTHON:-python3}"

echo "=== 1. All modes of ls, cd, tail, tac ==="
"$PYTHON" "$MAIN" --vfs "$VFS" --script "$EXAMPLES/startup_commands.emu"

for SCRIPT in "$EXAMPLES"/errors/*.emu; do
    echo "=== Error case: $(basename "$SCRIPT") ==="
    "$PYTHON" "$MAIN" --vfs "$VFS" --script "$SCRIPT"
done

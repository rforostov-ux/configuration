#!/bin/sh
# Test 2: startup script errors and invalid parameters.
# The script stops at the first error, the window stays open.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAIN="$ROOT/src/main.py"
EXAMPLES="$ROOT/examples"
VFS="$EXAMPLES/demo_vfs.xml"
PYTHON="${PYTHON:-python3}"

echo "=== 1. --script with an unknown command (stops at line 4) ==="
"$PYTHON" "$MAIN" --script "$EXAMPLES/startup_error.emu"

echo "=== 2. --vfs and --script with a syntax error (stops at line 4) ==="
"$PYTHON" "$MAIN" --vfs "$VFS" --script "$EXAMPLES/startup_syntax_error.emu"

echo "=== 3. --vfs and --script pointing to a missing file ==="
"$PYTHON" "$MAIN" --vfs "$VFS" --script "$EXAMPLES/no_such_script.emu"

echo "=== 4. Only --vfs, then type a wrong command by hand ==="
"$PYTHON" "$MAIN" --vfs "$VFS"

echo "=== 5. Unknown option (argparse error, exit code 2, no window) ==="
"$PYTHON" "$MAIN" --vfs "$VFS" --bogus
echo "exit code: $?"

echo "=== 6. Option without a value (exit code 2, no window) ==="
"$PYTHON" "$MAIN" --script
echo "exit code: $?"

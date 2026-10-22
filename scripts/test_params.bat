@echo off
setlocal
rem Test 1: all combinations of command-line parameters.
rem Each call opens a window; close it (or type exit) to run the next call.

set "ROOT=%~dp0.."
set "MAIN=%ROOT%\src\main.py"
set "EXAMPLES=%ROOT%\examples"
set "VFS=%EXAMPLES%\vfs\deep.xml"
if not defined PYTHON set "PYTHON=python"

echo === 1. No parameters (defaults) ===
"%PYTHON%" "%MAIN%"

echo === 2. Only --vfs (path is shown in the debug output) ===
"%PYTHON%" "%MAIN%" --vfs "%VFS%"

echo === 3. Only --script ===
"%PYTHON%" "%MAIN%" --script "%EXAMPLES%\startup_ok.emu"

echo === 4. Both --vfs and --script ===
"%PYTHON%" "%MAIN%" --vfs "%VFS%" --script "%EXAMPLES%\startup_ok.emu"

echo === 5. Both parameters, other order, --name=value form ===
"%PYTHON%" "%MAIN%" --script="%EXAMPLES%\startup_ok.emu" --vfs="%VFS%"
endlocal

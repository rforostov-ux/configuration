@echo off
setlocal
rem Test 3: exit codes of the emulator process.

set "ROOT=%~dp0.."
set "MAIN=%ROOT%\src\main.py"
set "EXAMPLES=%ROOT%\examples"
set "VFS=%EXAMPLES%\vfs\deep.xml"
if not defined PYTHON set "PYTHON=python"

echo === 1. --vfs and --script ending with 'exit 3' (window closes itself) ===
"%PYTHON%" "%MAIN%" --vfs "%VFS%" --script "%EXAMPLES%\startup_exit.emu"
echo exit code: %errorlevel% (expected 3)

echo === 2. Only --script ending with 'exit 3' ===
"%PYTHON%" "%MAIN%" --script "%EXAMPLES%\startup_exit.emu"
echo exit code: %errorlevel% (expected 3)

echo === 3. Only --vfs: type 'exit 5' in the window ===
"%PYTHON%" "%MAIN%" --vfs "%VFS%"
echo exit code: %errorlevel% (expected 5)

echo === 4. Both parameters, script without exit: close the window ===
"%PYTHON%" "%MAIN%" --vfs "%VFS%" --script "%EXAMPLES%\startup_ok.emu"
echo exit code: %errorlevel% (expected 0)
endlocal

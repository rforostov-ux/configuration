@echo off
setlocal
rem Test: minimal VFS (only the root directory).
rem Close the window (or type exit) to run the next call.

set "ROOT=%~dp0.."
set "MAIN=%ROOT%\src\main.py"
set "EXAMPLES=%ROOT%\examples"
set "VFS_DIR=%EXAMPLES%\vfs"
set "SCRIPT=%EXAMPLES%\startup_vfs.emu"
if not defined PYTHON set "PYTHON=python"

echo === 1. Minimal VFS with the stage 3 startup script ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\minimal.xml" --script "%SCRIPT%"

echo === 2. Minimal VFS, type vfs-info by hand ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\minimal.xml"
endlocal

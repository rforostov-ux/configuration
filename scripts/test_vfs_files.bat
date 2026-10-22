@echo off
setlocal
rem Test: VFS with several files, including a binary (base64) one.
rem Close the window (or type exit) to run the next call.

set "ROOT=%~dp0.."
set "MAIN=%ROOT%\src\main.py"
set "EXAMPLES=%ROOT%\examples"
set "VFS_DIR=%EXAMPLES%\vfs"
set "SCRIPT=%EXAMPLES%\startup_vfs.emu"
if not defined PYTHON set "PYTHON=python"

echo === 1. Several files with the stage 3 startup script ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\files.xml" --script "%SCRIPT%"

echo === 2. Several files, type vfs-info by hand ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\files.xml"
endlocal

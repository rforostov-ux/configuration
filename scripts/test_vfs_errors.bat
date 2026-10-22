@echo off
setlocal
rem Test: VFS loading errors. The window opens with an empty VFS.
rem Close the window (or type exit) to run the next call.

set "ROOT=%~dp0.."
set "MAIN=%ROOT%\src\main.py"
set "EXAMPLES=%ROOT%\examples"
set "VFS_DIR=%EXAMPLES%\vfs"
set "SCRIPT=%EXAMPLES%\startup_vfs.emu"
if not defined PYTHON set "PYTHON=python"

echo === 1. VFS file does not exist ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\no_such_vfs.xml" --script "%SCRIPT%"

echo === 2. Broken XML ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\broken.xml" --script "%SCRIPT%"

echo === 3. Not an XML file at all ===
"%PYTHON%" "%MAIN%" --vfs "%ROOT%\README.md" --script "%SCRIPT%"
endlocal

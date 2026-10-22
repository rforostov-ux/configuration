@echo off
setlocal
rem Test: deep VFS, more than 3 levels of directories and files.
rem Close the window (or type exit) to run the next call.

set "ROOT=%~dp0.."
set "MAIN=%ROOT%\src\main.py"
set "EXAMPLES=%ROOT%\examples"
set "VFS_DIR=%EXAMPLES%\vfs"
set "SCRIPT=%EXAMPLES%\startup_vfs.emu"
if not defined PYTHON set "PYTHON=python"

echo === 1. Deep VFS with the stage 3 startup script ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\deep.xml" --script "%SCRIPT%"

echo === 2. Deep VFS, --name=value form of the parameter ===
"%PYTHON%" "%MAIN%" --vfs="%VFS_DIR%\deep.xml" --script "%SCRIPT%"
endlocal

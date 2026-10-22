@echo off
setlocal
rem Test: stage 4 commands (ls, cd, tail, tac) on examples/vfs/deep.xml.
rem First the full stage 4 startup script, then one script per error case.
rem Close the window (or type exit) to run the next call.

set "ROOT=%~dp0.."
set "MAIN=%ROOT%\src\main.py"
set "EXAMPLES=%ROOT%\examples"
set "VFS=%EXAMPLES%\vfs\deep.xml"
if not defined PYTHON set "PYTHON=python"

echo === 1. All modes of ls, cd, tail, tac ===
"%PYTHON%" "%MAIN%" --vfs "%VFS%" --script "%EXAMPLES%\startup_commands.emu"

for %%S in ("%EXAMPLES%\errors\*.emu") do (
    echo === Error case: %%~nxS ===
    "%PYTHON%" "%MAIN%" --vfs "%VFS%" --script "%%~S"
)
endlocal

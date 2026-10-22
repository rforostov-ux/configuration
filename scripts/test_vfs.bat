@echo off
setlocal
rem Test 4: loading different VFS variants (stage 3).
rem Every call runs examples/startup_vfs.emu, so vfs-info shows what was loaded.
rem Close the window to run the next call.

set "ROOT=%~dp0.."
set "MAIN=%ROOT%\src\main.py"
set "EXAMPLES=%ROOT%\examples"
set "VFS_DIR=%EXAMPLES%\vfs"
set "SCRIPT=%EXAMPLES%\startup_vfs.emu"
if not defined PYTHON set "PYTHON=python"

echo === 1. Minimal VFS: only the root directory ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\minimal.xml" --script "%SCRIPT%"

echo === 2. Several files in the root, including a binary (base64) one ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\files.xml" --script "%SCRIPT%"

echo === 3. Deep VFS: more than 3 levels of directories and files ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\deep.xml" --script "%SCRIPT%"

echo === 4. No --vfs: empty VFS ===
"%PYTHON%" "%MAIN%" --script "%SCRIPT%"

echo === 5. Error: VFS file does not exist ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\no_such_vfs.xml" --script "%SCRIPT%"

echo === 6. Error: broken XML ===
"%PYTHON%" "%MAIN%" --vfs "%VFS_DIR%\broken.xml" --script "%SCRIPT%"

echo === 7. Error: not an XML file at all ===
"%PYTHON%" "%MAIN%" --vfs "%ROOT%\README.md" --script "%SCRIPT%"
endlocal

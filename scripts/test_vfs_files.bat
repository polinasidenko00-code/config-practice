@echo off
rem Tests with a VFS of several files in one directory.
pushd "%~dp0.."
if exist out rmdir /s /q out

echo ===== VFS with several files =====
python src\main.py --vfs vfs\files --script scripts\start_vfs.txt
echo exit code: %ERRORLEVEL%
echo ----- saved copy:
tree /f /a out\vfs_copy
popd

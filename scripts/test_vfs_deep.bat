@echo off
rem Tests with a VFS of 3+ levels of files and directories.
pushd "%~dp0.."
if exist out rmdir /s /q out

echo ===== VFS with several levels of directories =====
python src\main.py --vfs vfs\deep --script scripts\start_vfs.txt
echo exit code: %ERRORLEVEL%
echo ----- source VFS:
tree /f /a vfs\deep
echo ----- saved copy:
tree /f /a out\vfs_copy

rmdir /s /q out\vfs_copy
echo ===== Same VFS, path with a trailing separator =====
python src\main.py --vfs vfs\deep\ --script scripts\start_vfs.txt
echo exit code: %ERRORLEVEL%
popd

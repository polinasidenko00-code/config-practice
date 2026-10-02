@echo off
rem Tests with minimal VFS variants: an empty directory and a
rem directory with a single file.
pushd "%~dp0.."
if exist out rmdir /s /q out
mkdir out\empty_vfs

echo ===== 1. Empty VFS directory =====
python src\main.py --vfs out\empty_vfs --script scripts\start_vfs.txt
echo exit code: %ERRORLEVEL%
echo ----- saved copy:
tree /f /a out\vfs_copy

rmdir /s /q out\vfs_copy
echo ===== 2. Minimal VFS: a single file =====
python src\main.py --vfs vfs\minimal --script scripts\start_vfs.txt
echo exit code: %ERRORLEVEL%
echo ----- saved copy:
tree /f /a out\vfs_copy
popd

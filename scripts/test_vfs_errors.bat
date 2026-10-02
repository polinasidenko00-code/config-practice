@echo off
rem Tests of VFS loading errors.
pushd "%~dp0.."

echo ===== 1. VFS path does not exist =====
python src\main.py --vfs vfs\no_such_vfs --script scripts\start_vfs.txt
echo exit code: %ERRORLEVEL%

echo ===== 2. Invalid format: a file instead of a directory =====
python src\main.py --vfs vfs\not_a_directory.txt
echo exit code: %ERRORLEVEL%
popd

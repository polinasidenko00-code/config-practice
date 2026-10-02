@echo off
rem Tests of the --vfs parameter.
set EMU=python "%~dp0..\src\main.py"
set START=%~dp0start_basic.txt

echo ===== 1. No parameters (default VFS name) =====
echo exit | %EMU%
echo exit code: %ERRORLEVEL%

echo ===== 2. Relative VFS path =====
%EMU% --vfs vfs\demo --script "%START%"
echo exit code: %ERRORLEVEL%

echo ===== 3. Absolute VFS path with trailing separator =====
%EMU% --vfs C:\data\my_vfs\ --script "%START%"
echo exit code: %ERRORLEVEL%

echo ===== 4. Root of a drive (default VFS name) =====
%EMU% --vfs C:\ --script "%START%"
echo exit code: %ERRORLEVEL%

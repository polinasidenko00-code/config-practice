@echo off
rem Tests of combined and invalid command line parameters.
set EMU=python "%~dp0..\src\main.py"

echo ===== 1. Both parameters =====
%EMU% --vfs "%~dp0..\vfs\deep" --script "%~dp0start_basic.txt"
echo exit code: %ERRORLEVEL%

echo ===== 2. Both parameters in reverse order =====
%EMU% --script "%~dp0start_errors.txt" --vfs "%~dp0..\vfs\deep"
echo exit code: %ERRORLEVEL%

echo ===== 3. Help =====
%EMU% --help
echo exit code: %ERRORLEVEL%

echo ===== 4. Unknown parameter =====
%EMU% --unknown
echo exit code: %ERRORLEVEL%

echo ===== 5. Parameter without value =====
%EMU% --vfs
echo exit code: %ERRORLEVEL%

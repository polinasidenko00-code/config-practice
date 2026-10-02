@echo off
rem Tests of the --script parameter.
set EMU=python "%~dp0..\src\main.py"

echo ===== 1. Script with all commands =====
%EMU% --script "%~dp0start_basic.txt"
echo exit code: %ERRORLEVEL%

echo ===== 2. Script with errors and exit code 3 =====
%EMU% --script "%~dp0start_errors.txt"
echo exit code: %ERRORLEVEL%

echo ===== 3. Script without exit, then interactive input =====
(echo ls typed by user&echo exit 0) | %EMU% --script "%~dp0start_interactive.txt"
echo exit code: %ERRORLEVEL%

echo ===== 4. Missing script file =====
%EMU% --script "%~dp0no_such_script.txt"
echo exit code: %ERRORLEVEL%

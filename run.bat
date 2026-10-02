@echo off
rem Run emulator: run.bat
rem Run tests:    run.bat test
if "%1"=="test" (
    python -m unittest discover -s "%~dp0tests" -v
) else (
    python "%~dp0src\main.py" %*
)

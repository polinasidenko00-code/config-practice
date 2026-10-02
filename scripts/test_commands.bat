@echo off
rem Tests of the stage 4 commands: ls, cd, history, rev, cat.
pushd "%~dp0.."

echo ===== Stage 4 commands on the deep VFS =====
python src\main.py --vfs vfs\deep --script scripts\start_commands.txt
echo exit code: %ERRORLEVEL%
popd

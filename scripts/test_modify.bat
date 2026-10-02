@echo off
rem Tests of the stage 5 commands: chown, rm.
pushd "%~dp0.."
if exist out rmdir /s /q out

echo ===== Stage 5 commands on the deep VFS =====
python src\main.py --vfs vfs\deep --script scripts\start_modify.txt
echo exit code: %ERRORLEVEL%
echo ----- source VFS on disk (unchanged):
tree /f /a vfs\deep
echo ----- modified VFS saved by vfs-save:
tree /f /a out\modified
popd

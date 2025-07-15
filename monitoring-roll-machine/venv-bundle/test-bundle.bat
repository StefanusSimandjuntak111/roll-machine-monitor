@echo off
echo Testing Roll Machine Monitor Bundle...
"D:\Apps\monitoring-roll-machine\monitoring-roll-machine\venv-bundle\venv\Scripts\python.exe" --version
"D:\Apps\monitoring-roll-machine\monitoring-roll-machine\venv-bundle\venv\Scripts\python.exe" -c "import sys; print("Python path:", sys.executable)"
echo Bundle test completed.
pause

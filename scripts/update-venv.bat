@echo "Updating ecorcon using venv module with system python"
@echo "If you change your system python version, remove the venv folder"
python -m venv venv & ".\venv\Scripts\python.exe" -m pip install --upgrade pip & ".\venv\Scripts\python.exe" -m pip install -r requirements.txt

@echo off
setlocal

if not exist figures mkdir figures

echo Running Main.py...
python Main.py
if errorlevel 1 (
	echo Main.py failed. Stopping.
	pause
	exit /b 1
)

echo Running notebook to auto-generate figures, tables, and PDF...
python -m nbconvert --to notebook --execute Ransomware_Paper_Enhancements.ipynb --inplace --ExecutePreprocessor.timeout=-1
if errorlevel 1 (
	echo nbconvert not available or notebook execution failed.
	echo Attempting to install required notebook packages...
	python -m pip install --upgrade nbconvert nbclient ipykernel
	if errorlevel 1 (
		echo Auto-install failed. Please install manually:
		echo   pip install nbconvert nbclient ipykernel
		pause
		exit /b 1
	)

	echo Retrying notebook execution...
	python -m nbconvert --to notebook --execute Ransomware_Paper_Enhancements.ipynb --inplace --ExecutePreprocessor.timeout=-1
	if errorlevel 1 (
		echo Notebook execution still failed after install.
		pause
		exit /b 1
	)
)

echo Done. Check the figures folder for all outputs.
pause
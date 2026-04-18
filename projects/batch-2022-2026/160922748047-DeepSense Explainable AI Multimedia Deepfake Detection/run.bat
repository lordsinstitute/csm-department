@echo off
cd /d "%~dp0"

call myvenv\Scripts\activate

streamlit run app.py

pause
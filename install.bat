@echo off
REM Installing the Metal Slug Tactics translator from source on Windows.
REM
REM This is a thin wrapper: it sets up a Python environment and calls tools\install.py.
REM If you do not need Python — grab the ready-made installer from the Releases section
REM (mst-ru-setup.exe, it requires nothing to be installed).
REM
REM Run again after every Steam update of the game.
setlocal
cd /d "%~dp0"

set "PYEXE=.venv\Scripts\python.exe"

if not exist "%PYEXE%" (
    echo -^> creating environment and installing deps ^(UnityPy, numpy, Pillow^)
    where py >nul 2>nul && ( py -3 -m venv .venv ) || ( python -m venv .venv )
    if not exist "%PYEXE%" (
        echo.
        echo [X] Python not found. Install Python 3 from https://python.org
        echo     ^(tick "Add python.exe to PATH" during setup^), then run install.bat again.
        echo     Or use the ready-made mst-ru-setup.exe from Releases - no Python needed.
        pause
        exit /b 1
    )
    "%PYEXE%" -m pip install -q --disable-pip-version-check UnityPy numpy Pillow
)

"%PYEXE%" tools\install.py %*
echo.
pause

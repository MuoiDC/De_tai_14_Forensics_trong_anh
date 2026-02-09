@echo off
echo ================================================
echo Building Payload.exe
echo ================================================


REM Compile payload
pyinstaller ^
    --onefile ^
    --noconsole ^
    --name payload ^
    --distpath . ^
    --workpath build ^
    --specpath build ^
    payload.py

echo.
echo ================================================
echo Build complete: payload.exe
echo ================================================
pause
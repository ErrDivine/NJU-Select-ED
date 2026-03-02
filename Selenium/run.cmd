@echo off
REM 一键安装依赖并运行脚本（Windows）
setlocal
cd /d "%~dp0"

REM 选择 Python 启动器
where py >nul 2>&1 && (set "PY=py") || (set "PY=python")

if not exist .venv (
  %PY% -m venv .venv
  if errorlevel 1 (
    echo 创建虚拟环境失败，改为安裝到用戶目錄 (--user)。
    %PY% -m pip install --upgrade pip
    %PY% -m pip install --user -r requirements.txt
    %PY% sel.py
    echo.
    echo 程序已退出。如需重新运行，請再次雙擊本文件。
    pause
    exit /b
  )
)

call .\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python sel.py
echo.
echo 程序已退出。如需重新运行，请再次双击本文件。
pause


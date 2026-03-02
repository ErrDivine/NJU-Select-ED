#!/usr/bin/env bash
# 一键安装依赖并运行脚本（macOS/Linux）

set -u

# 切到脚本所在目录（即 Selenium/）
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || exit 1

# 选择可用的 Python 可执行程序
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "未找到 Python，请先安装 Python 3。"
  exit 1
fi

# 创建并使用虚拟环境；失败时回退为用户目录安装
if [ ! -d .venv ]; then
  "$PY" -m venv .venv || {
    echo "创建虚拟环境失败，改为安装到用户目录 (--user)。"
    "$PY" -m pip install --upgrade pip || true
    "$PY" -m pip install --user -r requirements.txt || exit 1
    "$PY" sel.py
    exit $?
  }
fi

# 激活虚拟环境
if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  . .venv/bin/activate
else
  echo "未找到虚拟环境激活脚本，直接运行。"
fi

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python sel.py


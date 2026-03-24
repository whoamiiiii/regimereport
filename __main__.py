"""
包入口点，允许通过 `python -m regimereport` 运行
"""
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from main import run

if __name__ == "__main__":
    raise SystemExit(run())

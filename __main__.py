"""
包入口点，允许通过 `python -m regimereport` 运行
"""
from .main import run

if __name__ == "__main__":
    raise SystemExit(run())

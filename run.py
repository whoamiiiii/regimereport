#!/usr/bin/env python
"""
应用启动器 - 直接运行此文件执行 Regime 报告任务
"""
import sys
from pathlib import Path

# 添加项目目录到 Python 路径，允许导入当前目录的模块
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    from main import run
    sys.exit(run())

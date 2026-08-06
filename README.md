# 五子棋（Gomoku）

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-19%20passed-brightgreen)]()
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

一个可直接运行的终端五子棋游戏，支持**双人对战**、**人机对战**和 **AI 对战**三种模式，纯 Python 标准库实现，无第三方运行依赖。

## 环境要求

- Python >= 3.11（开发环境为 3.12.3）

## 快速开始

```bash
# 进入项目目录
cd /root/CodeBuddy/Demo

# 使用已有虚拟环境
source .venv/bin/activate
python -m gomoku          # 默认人机对战（你执黑先手，终端界面）
python -m gomoku gui      # 图形界面（tkinter）
```

如果虚拟环境尚未创建：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .          # 安装 gomoku 包
python -m gomoku          # 启动游戏
```

> **图形界面依赖**：GUI 基于 Python 标准库 `tkinter`。Ubuntu 若缺少需先安装：
> ```bash
> sudo apt-get install python3-tk
> ```

## 游戏模式

```bash
# 终端界面
python -m gomoku           # 人机对战（默认，你执黑先手）
python -m gomoku pvp       # 双人对战
python -m gomoku ai2       # AI 对 AI（观战）
python -m gomoku ai hard   # 人机对战，困难难度

# 图形界面（tkinter）
python -m gomoku gui           # 人机对战
python -m gomoku gui pvp       # 双人对战
python -m gomoku gui ai hard   # 困难难度
python -m gomoku.gui           # 等同 python -m gomoku gui
```

难度可选：`easy` / `medium` / `hard`

## 操作说明

### 图形界面（GUI）
- **落子**：鼠标点击棋盘交叉点
- **悔棋**：点击「悔棋」按钮（AI 回合时会自动撤销到人类回合）
- **重新开始**：点击「重新开始」按钮
- 黑棋 `●` 先行，五子连成一线（横、竖、斜）即获胜；最后一手用红点标记

### 终端界面（TUI）
- **落子**：输入 `行 列`，例如 `7 7`（坐标为 0~14）
- **悔棋**：输入 `undo`
- **退出**：输入 `quit` 或 `q`

## 项目结构

```
.
├── gomoku/
│   ├── __init__.py     # 包入口
│   ├── core.py         # 核心逻辑：棋盘、棋子、规则判定、游戏状态
│   ├── ai.py           # AI：棋型评分启发式算法（含 easy/medium/hard 难度）
│   ├── ui.py           # 终端交互界面（棋盘绘制、命令行入口）
│   └── gui.py          # 图形界面（tkinter Canvas 绘制、鼠标落子）
├── tests/
│   └── test_gomoku.py  # 单元测试
├── pyproject.toml      # 项目配置与依赖管理
├── .pre-commit-config.yaml
└── .venv/              # 虚拟环境（不入库）
```

## 运行测试与代码质量检查

```bash
pytest                     # 单元测试
black gomoku tests         # 代码格式化
ruff check gomoku tests    # 静态检查
mypy gomoku                # 类型检查
```

## 核心模块 API

```python
from gomoku import Game, Player, Point
from gomoku.ai import AIPlayer

game = Game()
game.play(Point(7, 7))            # 黑棋落子
ai = AIPlayer(Player.WHITE)       # 白棋 AI
move = ai.choose_move(game.board) # AI 选点
game.play(move)
if game.winner is not None:
    print(f"{game.winner.value} 方获胜！")
```

## License

[MIT License](LICENSE) © 2026 ZhaoWeir

本项目采用 MIT 许可证开源，允许自由使用、修改和分发，详见 [LICENSE](LICENSE) 文件。

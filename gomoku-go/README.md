# 五子棋（Gomoku）· Go 版

一个用 **Go 语言**实现的可直接运行的终端五子棋游戏，支持**双人对战**、**人机对战**和 **AI 对战**三种模式，纯标准库实现，无第三方依赖。

> 本分支为 Go 语言实现版本。Python 版本请切换到 `main` 分支。

## 环境要求

- Go >= 1.22

## 快速开始

```bash
cd gomoku-go
go run .           # 人机对战（你执黑先手，默认）
```

## 游戏模式

```bash
go run .           # 人机对战（默认，你执黑先手）
go run . pvp       # 双人对战
go run . ai2       # AI 对 AI（观战）
go run . ai hard   # 人机对战，困难难度
```

难度可选：`easy` / `medium` / `hard`

## 操作说明

- **落子**：输入 `行 列`，例如 `7 7`（坐标为 0~14）
- **悔棋**：输入 `undo`
- **退出**：输入 `quit` 或 `q`
- 黑棋 `●` 先行，五子连成一线（横、竖、斜）即获胜

## 项目结构

```
.
├── go.mod           # Go 模块定义
├── main.go          # 终端界面与命令行入口
├── core/            # 核心逻辑：棋盘、规则、游戏状态
│   ├── gomoku.go
│   └── gomoku_test.go
└── ai/              # AI：启发式评分算法
    ├── ai.go
    └── ai_test.go
```

## 运行测试

```bash
cd gomoku-go
go test ./...
```

## 核心模块 API

```go
import "github.com/ZhaoWeir/gomoku-go/core"

g := core.NewGame()
g.Play(core.Point{7, 7})        // 黑棋落子
ai := ai.NewAIPlayer(core.PlayerWhite, ai.Medium)
move := ai.ChooseMove(g.Board)  // AI 选点
g.Play(move)
if g.Winner != core.PlayerEmpty {
    fmt.Printf("%s 方获胜！\n", g.Winner.Symbol())
}
```

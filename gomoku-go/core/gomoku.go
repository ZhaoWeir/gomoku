// Package core 实现五子棋的核心逻辑：棋盘、棋子、规则判定与游戏状态。
// 不依赖任何 UI，可在任何 Go 1.22+ 环境运行。
package core

import "fmt"

const (
	// BoardSize 棋盘尺寸
	BoardSize = 15
	// WinCount 获胜所需连子数
	WinCount = 5
)

// Player 表示棋盘上的棋子/玩家。
type Player int

const (
	// PlayerEmpty 空位
	PlayerEmpty Player = iota
	// PlayerBlack 黑棋
	PlayerBlack
	// PlayerWhite 白棋
	PlayerWhite
)

// Opponent 返回对方的玩家。
func (p Player) Opponent() Player {
	switch p {
	case PlayerBlack:
		return PlayerWhite
	case PlayerWhite:
		return PlayerBlack
	default:
		panic("空位没有对手")
	}
}

// Symbol 返回棋子的显示符号。
func (p Player) Symbol() string {
	switch p {
	case PlayerBlack:
		return "●"
	case PlayerWhite:
		return "○"
	default:
		return "."
	}
}

// Point 表示棋盘上的一个坐标点。
type Point struct {
	Row int
	Col int
}

// String 实现 fmt.Stringer。
func (p Point) String() string {
	return fmt.Sprintf("(%d,%d)", p.Row, p.Col)
}

// Board 管理棋盘状态与落子/胜负判定。
type Board struct {
	Size  int
	grid  [][]Player
	moves []Point // 落子历史
}

// NewBoard 创建一个 size x size 的空棋盘。
func NewBoard(size int) *Board {
	grid := make([][]Player, size)
	for i := range grid {
		grid[i] = make([]Player, size)
	}
	return &Board{Size: size, grid: grid}
}

// IsValid 判断坐标是否在棋盘内。
func (b *Board) IsValid(p Point) bool {
	return p.Row >= 0 && p.Row < b.Size && p.Col >= 0 && p.Col < b.Size
}

// Get 获取某个坐标的棋子。
func (b *Board) Get(p Point) Player {
	return b.grid[p.Row][p.Col]
}

// Grid 返回底层棋盘网格（只读访问，供 AI 等使用）。
func (b *Board) Grid() [][]Player {
	return b.grid
}

// IsEmpty 判断坐标是否为空。
func (b *Board) IsEmpty(p Point) bool {
	return b.Get(p) == PlayerEmpty
}

// Place 落子。成功返回 true，位置非法或已占用返回 false。
func (b *Board) Place(p Point, player Player) bool {
	if !b.IsValid(p) || !b.IsEmpty(p) {
		return false
	}
	b.grid[p.Row][p.Col] = player
	b.moves = append(b.moves, p)
	return true
}

// Undo 悔棋：撤销最后一步，返回被撤销的点。棋盘为空时返回 false。
func (b *Board) Undo() (Point, bool) {
	if len(b.moves) == 0 {
		return Point{}, false
	}
	p := b.moves[len(b.moves)-1]
	b.moves = b.moves[:len(b.moves)-1]
	b.grid[p.Row][p.Col] = PlayerEmpty
	return p, true
}

// IsFull 判断棋盘是否下满。
func (b *Board) IsFull() bool {
	return len(b.moves) >= b.Size*b.Size
}

// LastMove 返回最后一步落子。
func (b *Board) LastMove() (Point, bool) {
	if len(b.moves) == 0 {
		return Point{}, false
	}
	return b.moves[len(b.moves)-1], true
}

// countInDirection 沿方向 (dr, dc) 统计从 p 出发两侧的连续同色棋子数。
func (b *Board) countInDirection(p Point, player Player, dr, dc int) int {
	count := 1
	r, c := p.Row+dr, p.Col+dc
	for b.IsValid(Point{r, c}) && b.grid[r][c] == player {
		count++
		r += dr
		c += dc
	}
	r, c = p.Row-dr, p.Col-dc
	for b.IsValid(Point{r, c}) && b.grid[r][c] == player {
		count++
		r -= dr
		c -= dc
	}
	return count
}

// Winner 检查从 p 出发是否有玩家连成五子。返回获胜玩家及是否获胜。
func (b *Board) Winner(p Point) (Player, bool) {
	player := b.Get(p)
	if player == PlayerEmpty {
		return PlayerEmpty, false
	}
	directions := [][2]int{{0, 1}, {1, 0}, {1, 1}, {1, -1}}
	for _, d := range directions {
		if b.countInDirection(p, player, d[0], d[1]) >= WinCount {
			return player, true
		}
	}
	return PlayerEmpty, false
}

// EmptyPoints 返回棋盘上所有空点。
func (b *Board) EmptyPoints() []Point {
	var result []Point
	for r := 0; r < b.Size; r++ {
		for c := 0; c < b.Size; c++ {
			if b.grid[r][c] == PlayerEmpty {
				result = append(result, Point{r, c})
			}
		}
	}
	return result
}

// Game 表示一局五子棋的状态机。
type Game struct {
	Board         *Board
	CurrentPlayer Player
	Winner        Player
	hasWinner     bool
}

// NewGame 创建一个新游戏，黑棋先行。
func NewGame() *Game {
	return &Game{
		Board:         NewBoard(BoardSize),
		CurrentPlayer: PlayerBlack,
		Winner:        PlayerEmpty,
		hasWinner:     false,
	}
}

// Play 由当前玩家在 p 落子。成功返回 true。
func (g *Game) Play(p Point) bool {
	if g.hasWinner {
		return false
	}
	if !g.Board.Place(p, g.CurrentPlayer) {
		return false
	}
	if w, won := g.Board.Winner(p); won {
		g.Winner = w
		g.hasWinner = true
	} else {
		g.CurrentPlayer = g.CurrentPlayer.Opponent()
	}
	return true
}

// Undo 悔棋一步并恢复当前玩家。成功返回 true。
func (g *Game) Undo() bool {
	if _, ok := g.Board.Undo(); !ok {
		return false
	}
	if g.hasWinner {
		g.hasWinner = false
		g.Winner = PlayerEmpty
	} else {
		g.CurrentPlayer = g.CurrentPlayer.Opponent()
	}
	return true
}

// IsOver 判断游戏是否结束。
func (g *Game) IsOver() bool {
	return g.hasWinner || g.Board.IsFull()
}

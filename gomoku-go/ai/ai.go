// Package ai 实现五子棋 AI：基于棋型评分的启发式算法。
// 对棋盘上的每个空点评估分数，选择最高分者落子，同时考虑进攻与防守。
package ai

import (
	"math/rand"

	"github.com/ZhaoWeir/gomoku-go/core"
)

// Difficulty 表示 AI 难度。
type Difficulty string

const (
	// Easy 简单
	Easy Difficulty = "easy"
	// Medium 中等
	Medium Difficulty = "medium"
	// Hard 困难
	Hard Difficulty = "hard"
)

// AIPlayer 表示一个简单的贪心 AI。
type AIPlayer struct {
	Player     core.Player
	Difficulty Difficulty
}

// NewAIPlayer 创建一个 AI。
func NewAIPlayer(player core.Player, d Difficulty) *AIPlayer {
	return &AIPlayer{Player: player, Difficulty: d}
}

// countLine 取出从 (r,c) 出发、沿 (dr,dc) 方向最多 5 格的棋子序列。
func countLine(grid [][]core.Player, size, r, c, dr, dc int) []core.Player {
	cells := make([]core.Player, 0, 5)
	for step := 0; step < 5; step++ {
		nr, nc := r+dr*step, c+dc*step
		if nr >= 0 && nr < size && nc >= 0 && nc < size {
			cells = append(cells, grid[nr][nc])
		}
	}
	return cells
}

// patternScore 根据一行 5 格序列给当前空点打分。
func patternScore(cells []core.Player, me core.Player) int {
	count := 0
	empty := 0
	for _, cell := range cells {
		if cell == me {
			count++
		} else if cell == core.PlayerEmpty {
			empty++
		}
	}
	if count == 0 {
		return 0
	}
	if empty+count < 5 {
		return 0 // 序列含对方棋子，无法成五
	}
	switch {
	case count == 5:
		return 1_000_000
	case count == 4:
		if empty == 1 {
			return 100_000 // 冲四/活四
		}
		return 0
	case count == 3:
		if empty == 2 {
			return 10_000 // 活三
		}
		if empty == 1 {
			return 1_000
		}
		return 0
	case count == 2:
		if empty >= 3 {
			return 500
		}
		return 100
	default:
		if empty >= 4 {
			return 100
		}
		return 50
	}
}

// evaluatePoint 评估空点对 AI 的价值分数。
func evaluatePoint(board *core.Board, p core.Point, me, opp core.Player) int {
	grid := board.Grid()
	directions := [][2]int{{0, 1}, {1, 0}, {1, 1}, {1, -1}}
	myScore, oppScore := 0, 0
	for _, d := range directions {
		cells := countLine(grid, board.Size, p.Row, p.Col, d[0], d[1])
		myScore += patternScore(cells, me)
		oppScore += patternScore(cells, opp)
	}
	// 防守权重略高，优先挡对方
	return myScore + int(float64(oppScore)*1.1)
}

// candidatePoints 收集有邻居的空点作为候选；棋盘为空时返回中心附近。
func candidatePoints(board *core.Board) []core.Point {
	if _, ok := board.LastMove(); !ok {
		mid := board.Size / 2
		return []core.Point{
			{Row: mid, Col: mid},
			{Row: mid - 1, Col: mid},
			{Row: mid, Col: mid - 1},
			{Row: mid + 1, Col: mid},
		}
	}
	seen := make(map[core.Point]bool)
	var result []core.Point
	for r := 0; r < board.Size; r++ {
		for c := 0; c < board.Size; c++ {
			p := core.Point{Row: r, Col: c}
			if !board.IsEmpty(p) {
				continue
			}
			hasNeighbor := false
			for dr := -1; dr <= 1 && !hasNeighbor; dr++ {
				for dc := -1; dc <= 1; dc++ {
					if dr == 0 && dc == 0 {
						continue
					}
					n := core.Point{Row: r + dr, Col: c + dc}
					if board.IsValid(n) && !board.IsEmpty(n) {
						hasNeighbor = true
						break
					}
				}
			}
			if hasNeighbor && !seen[p] {
				seen[p] = true
				result = append(result, p)
			}
		}
	}
	if len(result) == 0 {
		return board.EmptyPoints()
	}
	return result
}

// ChooseMove 根据当前棋盘选择落子点。
func (a *AIPlayer) ChooseMove(board *core.Board) core.Point {
	opp := a.Player.Opponent()
	candidates := candidatePoints(board)
	bestScore := -1
	var best []core.Point
	for _, p := range candidates {
		score := evaluatePoint(board, p, a.Player, opp)
		if a.Difficulty == Easy {
			score += (p.Row + p.Col) % 3 // 简单模式加入随机扰动
		}
		if score > bestScore {
			bestScore = score
			best = []core.Point{p}
		} else if score == bestScore {
			best = append(best, p)
		}
	}
	if len(best) > 0 {
		return best[rand.Intn(len(best))]
	}
	// 兜底：取第一个空点
	if pts := board.EmptyPoints(); len(pts) > 0 {
		return pts[0]
	}
	return core.Point{}
}

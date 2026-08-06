package ai

import (
	"testing"

	"github.com/ZhaoWeir/gomoku-go/core"
)

// fill 连续落子，辅助测试。
func fill(t *testing.T, b *core.Board, pts []core.Point, p core.Player) {
	t.Helper()
	for _, pt := range pts {
		if !b.Place(pt, p) {
			t.Fatalf("落子失败: %v", pt)
		}
	}
}

func TestAIBlocksFour(t *testing.T) {
	b := core.NewBoard(15)
	pts := make([]core.Point, 4)
	for i := 0; i < 4; i++ {
		pts[i] = core.Point{Row: 7, Col: 3 + i}
	}
	fill(t, b, pts, core.PlayerBlack) // 黑四连
	a := NewAIPlayer(core.PlayerWhite, Medium)
	move := a.ChooseMove(b)
	// AI 应下在 (7,2) 或 (7,7) 阻挡
	if move.Row != 7 || (move.Col != 2 && move.Col != 7) {
		t.Errorf("AI 未阻挡黑方四连，落子: %v", move)
	}
}

func TestAIExtendsOwn(t *testing.T) {
	b := core.NewBoard(15)
	pts := make([]core.Point, 4)
	for i := 0; i < 4; i++ {
		pts[i] = core.Point{Row: 7, Col: 3 + i}
	}
	fill(t, b, pts, core.PlayerWhite) // 白四连
	a := NewAIPlayer(core.PlayerWhite, Medium)
	move := a.ChooseMove(b)
	if move.Row != 7 || (move.Col != 2 && move.Col != 7) {
		t.Errorf("AI 未连成五子，落子: %v", move)
	}
}

func TestAIFirstMoveCenter(t *testing.T) {
	a := NewAIPlayer(core.PlayerBlack, Medium)
	move := a.ChooseMove(core.NewBoard(15))
	if move.Row < 6 || move.Row > 8 || move.Col < 6 || move.Col > 8 {
		t.Errorf("AI 首手应落在中心区域，实际: %v", move)
	}
}

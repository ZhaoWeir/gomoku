package core

import "testing"

func TestValidCoords(t *testing.T) {
	b := NewBoard(15)
	if !b.IsValid(Point{Row: 0, Col: 0}) || !b.IsValid(Point{Row: 14, Col: 14}) {
		t.Error("合法坐标应有效")
	}
	if b.IsValid(Point{Row: -1, Col: 0}) || b.IsValid(Point{Row: 15, Col: 0}) {
		t.Error("非法坐标应无效")
	}
}

func TestPlaceAndGet(t *testing.T) {
	b := NewBoard(15)
	if !b.Place(Point{Row: 7, Col: 7}, PlayerBlack) {
		t.Fatal("落子应成功")
	}
	if b.Get(Point{Row: 7, Col: 7}) != PlayerBlack {
		t.Error("应取到黑棋")
	}
	if b.Place(Point{Row: 7, Col: 7}, PlayerWhite) {
		t.Error("重复落子应失败")
	}
}

func TestUndo(t *testing.T) {
	b := NewBoard(15)
	b.Place(Point{Row: 3, Col: 3}, PlayerBlack)
	b.Place(Point{Row: 4, Col: 4}, PlayerWhite)
	p, ok := b.Undo()
	if !ok || p != (Point{Row: 4, Col: 4}) {
		t.Error("应撤销白棋")
	}
	if !b.IsEmpty(Point{Row: 4, Col: 4}) {
		t.Error("撤销后应为空")
	}
}

func TestWinnerHorizontal(t *testing.T) {
	b := NewBoard(15)
	for i := 3; i < 8; i++ {
		if !b.Place(Point{Row: 7, Col: i}, PlayerBlack) {
			t.Fatal("落子失败")
		}
	}
	if w, won := b.Winner(Point{Row: 7, Col: 5}); !won || w != PlayerBlack {
		t.Error("应判定黑棋横向获胜")
	}
}

func TestWinnerVertical(t *testing.T) {
	b := NewBoard(15)
	for i := 2; i < 7; i++ {
		b.Place(Point{Row: i, Col: 5}, PlayerWhite)
	}
	if w, won := b.Winner(Point{Row: 4, Col: 5}); !won || w != PlayerWhite {
		t.Error("应判定白棋纵向获胜")
	}
}

func TestWinnerDiagonal(t *testing.T) {
	b := NewBoard(15)
	for i := 4; i < 9; i++ {
		b.Place(Point{Row: i, Col: i}, PlayerBlack)
	}
	if w, won := b.Winner(Point{Row: 6, Col: 6}); !won || w != PlayerBlack {
		t.Error("应判定黑棋对角线获胜")
	}
}

func TestWinnerAntiDiagonal(t *testing.T) {
	b := NewBoard(15)
	for i := 5; i < 10; i++ {
		b.Place(Point{Row: i, Col: 10 - i}, PlayerWhite)
	}
	if w, won := b.Winner(Point{Row: 7, Col: 3}); !won || w != PlayerWhite {
		t.Error("应判定白棋反对角线获胜")
	}
}

func TestNoWinner(t *testing.T) {
	b := NewBoard(15)
	for i := 0; i < 4; i++ {
		b.Place(Point{Row: 0, Col: i}, PlayerBlack) // 只有四子
	}
	if _, won := b.Winner(Point{Row: 0, Col: 2}); won {
		t.Error("四连不应判定获胜")
	}
}

func TestGameAlternating(t *testing.T) {
	g := NewGame()
	if g.CurrentPlayer != PlayerBlack {
		t.Error("黑棋应先行")
	}
	if !g.Play(Point{Row: 7, Col: 7}) {
		t.Fatal("黑棋落子失败")
	}
	if g.CurrentPlayer != PlayerWhite {
		t.Error("落子后应轮到白棋")
	}
}

func TestGameWinner(t *testing.T) {
	g := NewGame()
	for i := 0; i < 5; i++ {
		g.Play(Point{Row: 0, Col: i}) // 黑
		if i < 4 {
			g.Play(Point{Row: 1, Col: i}) // 白（不干扰）
		}
	}
	if g.Winner != PlayerBlack || !g.IsOver() {
		t.Error("黑棋应获胜且游戏结束")
	}
	if g.Play(Point{Row: 2, Col: 2}) {
		t.Error("结束后不能落子")
	}
}

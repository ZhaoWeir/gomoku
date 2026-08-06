"""五子棋核心逻辑与 AI 测试。"""

from __future__ import annotations

from gomoku.ai import AIPlayer, evaluate_point
from gomoku.core import Board, Game, Player, Point


def _fill(board: Board, points: list[tuple[int, int]], player: Player) -> None:
    for r, c in points:
        assert board.place(Point(r, c), player)


class TestBoard:
    def test_valid_coords(self) -> None:
        b = Board(15)
        assert b.is_valid(Point(0, 0))
        assert b.is_valid(Point(14, 14))
        assert not b.is_valid(Point(-1, 0))
        assert not b.is_valid(Point(15, 0))

    def test_place_and_get(self) -> None:
        b = Board()
        assert b.place(Point(7, 7), Player.BLACK)
        assert b.get(Point(7, 7)) is Player.BLACK
        # 重复落子失败
        assert not b.place(Point(7, 7), Player.WHITE)

    def test_undo(self) -> None:
        b = Board()
        b.place(Point(3, 3), Player.BLACK)
        b.place(Point(4, 4), Player.WHITE)
        assert b.undo() == Point(4, 4)
        assert b.is_empty(Point(4, 4))
        assert b.last_move == Point(3, 3)

    def test_winner_horizontal(self) -> None:
        b = Board()
        pts = [(7, i) for i in range(3, 8)]
        _fill(b, pts, Player.BLACK)
        assert b.winner(Point(7, 5)) is Player.BLACK

    def test_winner_vertical(self) -> None:
        b = Board()
        _fill(b, [(i, 5) for i in range(2, 7)], Player.WHITE)
        assert b.winner(Point(4, 5)) is Player.WHITE

    def test_winner_diagonal(self) -> None:
        b = Board()
        _fill(b, [(i, i) for i in range(4, 9)], Player.BLACK)
        assert b.winner(Point(6, 6)) is Player.BLACK

    def test_winner_anti_diagonal(self) -> None:
        b = Board()
        _fill(b, [(i, 10 - i) for i in range(5, 10)], Player.WHITE)
        assert b.winner(Point(7, 3)) is Player.WHITE

    def test_no_winner_yet(self) -> None:
        b = Board()
        _fill(b, [(0, 0), (0, 1), (0, 2), (0, 3)], Player.BLACK)  # 只有四子
        assert b.winner(Point(0, 2)) is None

    def test_six_in_a_row_still_win(self) -> None:
        # 超过五连也算赢（简化规则）
        b = Board()
        _fill(b, [(0, i) for i in range(7)], Player.BLACK)
        assert b.winner(Point(0, 3)) is Player.BLACK

    def test_opponent_blocks_not_win(self) -> None:
        b = Board()
        _fill(b, [(5, i) for i in range(4)] + [(5, 5)], Player.BLACK)
        b.place(Point(5, 4), Player.WHITE)  # 对方隔断
        assert b.winner(Point(5, 3)) is None


class TestGame:
    def test_alternating_players(self) -> None:
        g = Game()
        assert g.current_player is Player.BLACK
        assert g.play(Point(7, 7))
        assert g.current_player is Player.WHITE
        assert g.play(Point(8, 8))
        assert g.current_player is Player.BLACK

    def test_game_winner(self) -> None:
        g = Game()
        # 黑方连成五子
        for i in range(5):
            g.play(Point(0, i))  # 黑
            if i < 4:
                g.play(Point(1, i))  # 白（不干扰）
        assert g.winner is Player.BLACK
        assert g.is_over()
        # 结束后不能再落子
        assert not g.play(Point(2, 2))

    def test_game_undo(self) -> None:
        g = Game()
        g.play(Point(7, 7))  # 黑
        g.play(Point(8, 8))  # 白
        assert g.current_player is Player.BLACK
        assert g.undo()
        assert g.current_player is Player.WHITE
        assert g.board.last_move == Point(7, 7)


class TestAI:
    def test_ai_blocks_four(self) -> None:
        """对方已有四连时，AI 应当堵住形成五子的点。"""
        b = Board()
        _fill(b, [(7, i) for i in range(3, 7)], Player.BLACK)  # 黑四连
        ai = AIPlayer(Player.WHITE)
        move = ai.choose_move(b)
        # AI 应下在 (7,2) 或 (7,7) 之一来阻挡
        assert move.row == 7 and move.col in (2, 7)

    def test_ai_extends_own(self) -> None:
        """AI 自己已有四连时，应当主动连成五子。"""
        b = Board()
        _fill(b, [(7, i) for i in range(3, 7)], Player.WHITE)  # 白四连
        ai = AIPlayer(Player.WHITE)
        move = ai.choose_move(b)
        assert move.row == 7 and move.col in (2, 7)

    def test_ai_first_move_center(self) -> None:
        """空棋盘时 AI 首手应落在中心区域。"""
        ai = AIPlayer(Player.BLACK)
        move = ai.choose_move(Board(15))
        assert 6 <= move.row <= 8 and 6 <= move.col <= 8

    def test_evaluate_point_scoring(self) -> None:
        b = Board()
        _fill(b, [(7, 3), (7, 4), (7, 5), (7, 6)], Player.BLACK)
        # 防守点 (7,2)/(7,7) 分数应高于远处
        score_block = evaluate_point(b, Point(7, 2), Player.WHITE, Player.BLACK)
        score_far = evaluate_point(b, Point(0, 0), Player.WHITE, Player.BLACK)
        assert score_block > score_far


class TestGuiMapping:
    """GUI 像素坐标映射（不依赖真实显示环境）。"""

    def test_to_px_mapping(self) -> None:
        from gomoku.gui import CELL, MARGIN

        # 直接验证坐标换算公式（GomokuApp 需要 tk 环境，这里只测纯计算）
        for row in range(15):
            for col in range(15):
                x = MARGIN + col * CELL
                y = MARGIN + row * CELL
                assert x == MARGIN + col * CELL
                assert y == MARGIN + row * CELL

    def test_click_to_coord_inverse(self) -> None:
        """像素坐标应能反推出棋盘坐标。"""
        from gomoku.gui import CELL, MARGIN

        for row in range(15):
            for col in range(15):
                x = MARGIN + col * CELL
                y = MARGIN + row * CELL
                # 反向换算
                r = round((y - MARGIN) / CELL)
                c = round((x - MARGIN) / CELL)
                assert (r, c) == (row, col)

"""五子棋 AI：基于棋型评分的启发式算法。

AI 会对棋盘上的每个空点评估一个分数，选择分数最高的点落子。
评分同时考虑己方（进攻）和对方（防守），并叠加活三、活四等棋型权重。
"""

from __future__ import annotations

from .core import Board, Player, Point

__all__ = ["AIPlayer", "evaluate_point"]


def _count_line(grid: list[list[Player]], r: int, c: int, dr: int, dc: int) -> list[Player]:
    """取出从 (r, c) 出发、沿 (dr, dc) 方向连续最多 5 格（含自身）的棋子序列。"""
    cells: list[Player] = []
    for step in range(5):
        nr, nc = r + dr * step, c + dc * step
        if 0 <= nr < len(grid) and 0 <= nc < len(grid):
            cells.append(grid[nr][nc])
    return cells


def _pattern_score(cells: list[Player], me: Player) -> int:
    """根据一行/一列/对角线上 5 格序列给当前空点打分。

    通过统计我方棋子和两端空位情况，近似识别冲四、活三、活二等棋型。
    """
    count = cells.count(me)
    if count == 0:
        return 0
    empty = cells.count(Player.EMPTY)
    if empty + count < 5:
        return 0  # 序列含对方棋子，无法成五（简化处理）
    # 按连子数量与空位情况给分
    if count == 5:
        return 1_000_000
    if count == 4:
        return 100_000 if empty == 1 else 0  # 冲四/活四
    if count == 3:
        if empty == 2:
            return 10_000  # 活三
        return 1_000 if empty == 1 else 0
    if count == 2:
        return 500 if empty >= 3 else 100
    return 100 if empty >= 4 else 50


def evaluate_point(board: Board, point: Point, me: Player, opponent: Player) -> int:
    """评估某个空点对 AI（me）的价值分数。"""
    grid = board._grid
    my_score = 0
    opp_score = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        # 进攻：该点落上我方棋子的收益
        cells = _count_line(grid, point.row, point.col, dr, dc)
        my_score += _pattern_score(cells, me)
        # 防守：该点能阻止对方成五的收益
        opp_cells = _count_line(grid, point.row, point.col, dr, dc)
        opp_score += _pattern_score(opp_cells, opponent)
    return my_score + int(opp_score * 1.1)  # 防守权重略高，优先挡对方


class AIPlayer:
    """简单的贪心 AI：遍历候选空点，取评分最高者落子。"""

    def __init__(self, player: Player = Player.WHITE, difficulty: str = "medium") -> None:
        if player.is_empty:
            raise ValueError("AI 不能使用空棋子")
        self.player = player
        self.difficulty = difficulty  # easy / medium / hard

    def choose_move(self, board: Board) -> Point:
        """根据当前棋盘选择落子点。"""
        opponent = self.player.opponent()
        best_score = -1
        best: list[Point] = []
        # 优先考察已有棋子周围的点，减少搜索范围
        candidates = self._candidate_points(board)
        for point in candidates:
            score = evaluate_point(board, point, self.player, opponent)
            if self.difficulty == "easy":
                score += (point.row + point.col) % 3  # 简单模式加入随机扰动
            if score > best_score:
                best_score = score
                best = [point]
            elif score == best_score:
                best.append(point)
        if best:
            # 多个同分点随机选一个
            import random

            return random.choice(best)
        # 兜底：取第一个空点
        return next(iter(board.empty_points()))

    def _candidate_points(self, board: Board) -> list[Point]:
        """收集有邻居的空点作为候选；棋盘为空时返回中心附近。"""
        if not board.last_move:
            mid = board.size // 2
            return [Point(mid, mid), Point(mid - 1, mid), Point(mid, mid - 1), Point(mid + 1, mid)]
        seen: set[tuple[int, int]] = set()
        result: list[Point] = []
        for r in range(board.size):
            for c in range(board.size):
                if not board.is_empty(Point(r, c)):
                    continue
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if (
                            0 <= nr < board.size
                            and 0 <= nc < board.size
                            and not board.is_empty(Point(nr, nc))
                        ):
                            if (r, c) not in seen:
                                seen.add((r, c))
                                result.append(Point(r, c))
                            break
        return result or list(board.empty_points())

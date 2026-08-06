"""五子棋核心逻辑：棋盘、棋子、规则判定与游戏状态。

本模块不依赖任何 UI，可在任何 Python 3.11+ 环境运行。
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import Enum

__all__ = ["Player", "Board", "Game", "Point"]

# 棋盘尺寸
BOARD_SIZE = 15

# 获胜所需连子数
WIN_COUNT = 5


class Point:
    """棋盘上的一个坐标点。"""

    __slots__ = ("row", "col")

    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col

    def __repr__(self) -> str:
        return f"Point({self.row}, {self.col})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Point) and self.row == other.row and self.col == other.col

    def __hash__(self) -> int:
        return hash((self.row, self.col))


class Player(Enum):
    """棋子颜色 / 玩家。"""

    EMPTY = "."
    BLACK = "●"  # 黑棋先行
    WHITE = "○"  # 白棋

    @property
    def is_empty(self) -> bool:
        return self is Player.EMPTY

    def opponent(self) -> Player:
        """返回对方玩家（仅对非空棋子有效）。"""
        if self is Player.BLACK:
            return Player.WHITE
        if self is Player.WHITE:
            return Player.BLACK
        raise ValueError("空位没有对手")


class Board:
    """棋盘，管理棋子落子与胜负判定。"""

    def __init__(self, size: int = BOARD_SIZE) -> None:
        self.size = size
        self._grid = [[Player.EMPTY for _ in range(size)] for _ in range(size)]
        self._moves: list[Point] = []  # 落子历史

    def is_valid(self, point: Point) -> bool:
        """判断坐标是否在棋盘内。"""
        return 0 <= point.row < self.size and 0 <= point.col < self.size

    def get(self, point: Point) -> Player:
        """获取某个坐标的棋子。"""
        return self._grid[point.row][point.col]

    def is_empty(self, point: Point) -> bool:
        """判断坐标是否为空。"""
        return self.get(point).is_empty

    def place(self, point: Point, player: Player) -> bool:
        """落子。成功返回 True，位置非法或已占用返回 False。"""
        if not self.is_valid(point) or not self.is_empty(point):
            return False
        self._grid[point.row][point.col] = player
        self._moves.append(point)
        return True

    def undo(self) -> Point | None:
        """悔棋：撤销最后一步，返回被撤销的点。棋盘为空时返回 None。"""
        if not self._moves:
            return None
        point = self._moves.pop()
        self._grid[point.row][point.col] = Player.EMPTY
        return point

    def is_full(self) -> bool:
        """棋盘是否已下满（平局）。"""
        return len(self._moves) >= self.size * self.size

    def winner(self, point: Point) -> Player | None:
        """检查从 point 出发是否有玩家连成五子。返回获胜玩家或 None。"""
        player = self.get(point)
        if player.is_empty:
            return None
        # 四个方向：水平、垂直、主对角线、副对角线
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            if self._count_in_direction(point, player, dr, dc) >= WIN_COUNT:
                return player
        return None

    def _count_in_direction(self, point: Point, player: Player, dr: int, dc: int) -> int:
        """沿方向 (dr, dc) 统计连续同色棋子数（包含起点两侧）。"""
        count = 1
        # 正向
        r, c = point.row + dr, point.col + dc
        while 0 <= r < self.size and 0 <= c < self.size and self._grid[r][c] is player:
            count += 1
            r += dr
            c += dc
        # 反向
        r, c = point.row - dr, point.col - dc
        while 0 <= r < self.size and 0 <= c < self.size and self._grid[r][c] is player:
            count += 1
            r -= dr
            c -= dc
        return count

    def empty_points(self) -> Iterator[Point]:
        """遍历所有空点。"""
        for r in range(self.size):
            for c in range(self.size):
                if self._grid[r][c].is_empty:
                    yield Point(r, c)

    @property
    def last_move(self) -> Point | None:
        """最后一步落子。"""
        return self._moves[-1] if self._moves else None


class Game:
    """一局五子棋的状态机，负责交替落子与胜负判定。"""

    def __init__(self, size: int = BOARD_SIZE) -> None:
        self.board = Board(size)
        self.current_player = Player.BLACK  # 黑棋先行
        self.winner: Player | None = None

    def play(self, point: Point) -> bool:
        """由当前玩家在 point 落子。成功返回 True。"""
        if self.winner is not None:
            return False
        if not self.board.place(point, self.current_player):
            return False
        if self.board.winner(point) is self.current_player:
            self.winner = self.current_player
        else:
            self.current_player = self.current_player.opponent()
        return True

    def undo(self) -> bool:
        """悔棋一步，并恢复当前玩家。成功返回 True。"""
        if not self.board.undo():
            return False
        # 悔棋后当前玩家应回到撤销那步的落子方
        if self.winner is not None:
            self.winner = None
        else:
            self.current_player = self.current_player.opponent()
        return True

    def is_over(self) -> bool:
        """游戏是否结束（有人获胜或平局）。"""
        return self.winner is not None or self.board.is_full()

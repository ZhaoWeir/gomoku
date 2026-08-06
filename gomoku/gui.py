"""五子棋图形界面（基于 tkinter，纯标准库）。

提供：
- 15x15 棋盘 Canvas 绘制
- 鼠标点击落子
- 人机对战 / 双人对战
- 悔棋、重新开始
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from .ai import AIPlayer
from .core import Game, Player, Point

__all__ = ["GomokuApp", "run_gui"]

# 棋盘绘制参数
CELL = 40  # 每个格子的像素大小
MARGIN = 40  # 棋盘边缘留白（用于显示坐标）
BOARD_SIZE = 15


class GomokuApp:
    """tkinter 五子棋图形界面。"""

    def __init__(
        self,
        master: tk.Tk,
        black_player: str = "human",
        white_player: str = "ai",
        ai_difficulty: str = "medium",
    ) -> None:
        self.master = master
        self.black_player = black_player
        self.white_player = white_player
        self.ai_difficulty = ai_difficulty

        self.game = Game(BOARD_SIZE)
        self.ai: AIPlayer | None = None
        if black_player == "ai":
            self.ai = AIPlayer(Player.BLACK, ai_difficulty)
        elif white_player == "ai":
            self.ai = AIPlayer(Player.WHITE, ai_difficulty)

        # 窗口尺寸
        board_px = (BOARD_SIZE - 1) * CELL + MARGIN * 2
        self.master.title("五子棋")
        self.master.resizable(False, False)

        self._build_ui(board_px)

        # 若 AI 执黑（先手），启动时让它走第一步
        if self.ai is not None and self.ai.player is Player.BLACK:
            self.master.after(200, self._ai_move)

    def _build_ui(self, board_px: int) -> None:
        """构建界面：棋盘 + 控制栏 + 状态栏。"""
        top = tk.Frame(self.master)
        top.pack(fill=tk.X, padx=8, pady=6)

        self.new_btn = tk.Button(top, text="重新开始", command=self.restart)
        self.new_btn.pack(side=tk.LEFT, padx=4)

        self.undo_btn = tk.Button(top, text="悔棋", command=self.undo)
        self.undo_btn.pack(side=tk.LEFT, padx=4)

        tk.Label(
            top,
            text=f"模式：{self.black_player} vs {self.white_player}　难度：{self.ai_difficulty}",
        ).pack(side=tk.RIGHT)

        # 棋盘 Canvas
        self.canvas = tk.Canvas(
            self.master,
            width=board_px,
            height=board_px,
            bg="#E8C57A",  # 木质底色
            highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)

        self.draw_board()

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X)
        self._update_status()

    # ---------- 绘制 ----------
    def draw_board(self) -> None:
        """绘制棋盘网格与棋子。"""
        self.canvas.delete("all")
        size = BOARD_SIZE
        # 画网格线
        for i in range(size):
            start = MARGIN + i * CELL
            end = MARGIN + (size - 1) * CELL
            self.canvas.create_line(start, MARGIN, start, end, fill="#000")
            self.canvas.create_line(MARGIN, start, end, start, fill="#000")
            # 坐标标注
            self.canvas.create_text(
                MARGIN - 18, start, text=str(i), font=("Helvetica", 9), fill="#444"
            )
            self.canvas.create_text(
                start, MARGIN - 18, text=str(i), font=("Helvetica", 9), fill="#444"
            )
        # 画星位（天元与四星）
        star_points = [(7, 7), (3, 3), (3, 11), (11, 3), (11, 11)]
        for r, c in star_points:
            x, y = self._to_px(r, c)
            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#000")

        # 画棋子
        for r in range(size):
            for c in range(size):
                player = self.game.board.get(Point(r, c))
                if not player.is_empty:
                    self._draw_stone(r, c, player)

    def _to_px(self, row: int, col: int) -> tuple[int, int]:
        """将棋盘坐标转为像素坐标。"""
        return MARGIN + col * CELL, MARGIN + row * CELL

    def _draw_stone(self, row: int, col: int, player: Player) -> None:
        """在 (row, col) 画一颗棋子。"""
        x, y = self._to_px(row, col)
        radius = CELL // 2 - 4
        color = "#111" if player is Player.BLACK else "#F5F5F5"
        self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius, fill=color, outline="#333"
        )
        # 最后一手的标记
        if self.game.board.last_move == Point(row, col):
            self.canvas.create_oval(
                x - 5, y - 5, x + 5, y + 5, fill="red" if player is Player.BLACK else "#cc0000"
            )

    # ---------- 交互 ----------
    def _on_click(self, event: tk.Event) -> None:
        """鼠标点击落子。"""
        if self.game.is_over():
            return
        # 若是 AI 回合，忽略点击（防止人类替 AI 落子）
        current = self.game.current_player
        player_type = self.black_player if current is Player.BLACK else self.white_player
        if player_type == "ai":
            return

        row = round((event.y - MARGIN) / CELL)
        col = round((event.x - MARGIN) / CELL)
        point = Point(row, col)
        if not self.game.board.is_valid(point) or not self.game.board.is_empty(point):
            return
        self._make_move(point)

    def _make_move(self, point: Point) -> None:
        """执行落子并处理结果。"""
        self.game.play(point)
        self.draw_board()
        self._update_status()
        if self.game.winner is not None:
            self._show_result(f"{self.game.winner.value} 方获胜！")
            return
        if self.game.board.is_full():
            self._show_result("平局！")
            return
        # 若轮到 AI，自动走棋
        current = self.game.current_player
        player_type = self.black_player if current is Player.BLACK else self.white_player
        if player_type == "ai":
            self.master.after(300, self._ai_move)

    def _ai_move(self) -> None:
        """AI 走棋。"""
        if self.game.is_over():
            return
        if self.ai is None:
            return
        point = self.ai.choose_move(self.game.board)
        self._make_move(point)

    def undo(self) -> None:
        """悔棋：撤销最近一步。若刚轮到 AI，撤销两步。"""
        if self.game.is_over():
            # 允许结束后悔棋取消获胜状态
            pass
        # 连续撤销，直到撤销到人类可操作的回合（或撤销到最干净状态）
        for _ in range(4):
            if not self.game.undo():
                break
            # 如果现在是 AI 回合，继续撤销，让人类能落子
            current = self.game.current_player
            player_type = self.black_player if current is Player.BLACK else self.white_player
            if player_type != "ai":
                break
        self.draw_board()
        self._update_status()

    def restart(self) -> None:
        """重新开始一局。"""
        self.game = Game(BOARD_SIZE)
        if self.ai is not None and self.ai.player is Player.BLACK:
            self.master.after(200, self._ai_move)
        self.draw_board()
        self._update_status()

    # ---------- 状态与结果 ----------
    def _update_status(self) -> None:
        """更新状态栏文字。"""
        if self.game.winner is not None:
            self.status_var.set(f"🎉 {self.game.winner.value} 方获胜！")
        elif self.game.board.is_full():
            self.status_var.set("平局！")
        else:
            current = self.game.current_player
            player_type = self.black_player if current is Player.BLACK else self.white_player
            tag = "AI" if player_type == "ai" else "玩家"
            self.status_var.set(f"轮到 {current.value}（{tag}）落子")

    def _show_result(self, text: str) -> None:
        """显示结果并询问是否再来一局。"""
        self.status_var.set(text)
        again = messagebox.askyesno("游戏结束", f"{text}\n\n是否再来一局？")
        if again:
            self.restart()


def run_gui(
    black_player: str = "human",
    white_player: str = "ai",
    ai_difficulty: str = "medium",
) -> None:
    """启动图形界面。"""
    root = tk.Tk()
    GomokuApp(root, black_player, white_player, ai_difficulty)
    root.mainloop()


def main() -> None:
    """命令行入口：python -m gomoku.gui"""
    import sys

    black_player = "human"
    white_player = "ai"
    difficulty = "medium"
    args = sys.argv[1:]
    if args:
        mode = args[0].lower()
        if mode in ("pvp", "2p"):
            black_player = "human"
            white_player = "human"
        elif mode in ("ai", "pvai"):
            black_player = "human"
            white_player = "ai"
        elif mode in ("ai2", "ai-ai"):
            black_player = "ai"
            white_player = "ai"
        else:
            print("用法: python -m gomoku.gui [pvp|ai|ai2] [easy|medium|hard]")
            return
    if len(args) >= 2:
        difficulty = args[1].lower()
    run_gui(black_player, white_player, difficulty)


if __name__ == "__main__":
    main()

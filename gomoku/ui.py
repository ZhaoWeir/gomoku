"""五子棋终端交互界面：棋盘绘制与命令行入口。"""

from __future__ import annotations

import sys

from .core import Board, Game, Player, Point

__all__ = ["print_board", "run_terminal"]


def print_board(board: Board) -> None:
    """在终端绘制棋盘。"""
    size = board.size
    # 顶部列号
    print("     " + "  ".join(f"{c:>2}" for c in range(size)))
    # 顶边
    print("   +" + "---+" * size)
    for r in range(size):
        cells: list[str] = []
        for c in range(size):
            cells.append(board.get(Point(r, c)).value)
        row = f"  {r:>2} |" + "|".join(f" {cell} " for cell in cells) + "|"
        print(row)
        # 行间横线（除最后一行）
        if r < size - 1:
            print("     +" + "---+" * size)
    # 底边
    print("   +" + "---+" * size)


def _parse_point(text: str, size: int) -> Point | None:
    """解析用户输入，格式：'row col' 或 'row,col'，例如 '7 7'。"""
    text = text.strip()
    if not text:
        return None
    for sep in (" ", ",", "\t"):
        if sep in text:
            parts = text.split(sep)
            break
    else:
        parts = [text]
    if len(parts) != 2:
        return None
    try:
        row, col = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    point = Point(row, col)
    if not (0 <= row < size and 0 <= col < size):
        return None
    return point


def _prompt_for_move(game: Game, hint: str | None = None) -> Point:
    """交互式获取用户落子点。"""
    while True:
        if hint:
            print(hint)
        raw = input(
            f"  玩家 {game.current_player.value} 请落子 (行 列，如 '7 7'，输入 undo 悔棋，quit 退出): "
        ).strip()
        low = raw.lower()
        if low in ("quit", "q", "exit"):
            print("游戏结束，再见！")
            sys.exit(0)
        if low == "undo":
            if game.undo():
                print("  已悔棋。")
                print_board(game.board)
                continue
            print("  没有可悔的棋。")
            continue
        point = _parse_point(raw, game.board.size)
        if point is None:
            print("  输入无效，请使用 '行 列' 格式，例如 '7 7'。")
            continue
        return point


def run_terminal(
    black_player: str = "human", white_player: str = "ai", ai_difficulty: str = "medium"
) -> None:
    """运行一局终端五子棋。

    black_player / white_player: "human" 或 "ai"
    ai_difficulty: easy / medium / hard
    """
    from .ai import AIPlayer

    game = Game()
    players: dict[Player, str] = {
        Player.BLACK: black_player,
        Player.WHITE: white_player,
    }
    ai: AIPlayer | None = None
    if black_player == "ai":
        ai = AIPlayer(Player.BLACK, ai_difficulty)
    elif white_player == "ai":
        ai = AIPlayer(Player.WHITE, ai_difficulty)

    print("========== 五子棋 ==========")
    print(f"黑棋 {Player.BLACK.value} 先行")
    print(f"黑方: {black_player}  白方: {white_player}  难度: {ai_difficulty}")
    print("输入格式: 行 列（如 '7 7'），输入 undo 悔棋，quit 退出")
    print("=============================")
    print_board(game.board)

    while not game.is_over():
        current = game.current_player
        is_human = players[current] == "human"
        if is_human:
            hint = None if current is Player.BLACK else None
            point = _prompt_for_move(game, hint)
            game.play(point)
        else:
            assert ai is not None
            print(f"  AI ({current.value}) 思考中...")
            point = ai.choose_move(game.board)
            game.play(point)
            print(f"  AI 落子: {point.row} {point.col}")
        print_board(game.board)
        if game.winner is not None:
            print(f"\n🎉 {game.winner.value} 方获胜！")
            return
        if game.board.is_full():
            print("\n平局！")
            return

    # 游戏已结束（理论不会走到这里，防御性处理）
    if game.winner is not None:
        print(f"\n🎉 {game.winner.value} 方获胜！")
    else:
        print("\n平局！")


def main() -> None:
    """命令行入口：python -m gomoku [gui] [pvp|ai|ai2] [easy|medium|hard]"""
    black_player = "human"
    white_player = "ai"
    difficulty = "medium"
    use_gui = False
    args = [a.lower() for a in sys.argv[1:]]

    # 提取 gui 标记
    if "gui" in args:
        use_gui = True
        args.remove("gui")

    if args:
        mode = args[0]
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
            print("用法: python -m gomoku [gui] [pvp|ai|ai2] [easy|medium|hard]")
            return
    if len(args) >= 2:
        difficulty = args[1]

    if use_gui:
        try:
            from .gui import run_gui
        except ImportError as exc:  # pragma: no cover - 仅在缺少 tkinter 时触发
            print(f"图形界面不可用（缺少 tkinter）: {exc}")
            print("请安装 python3-tk 或改用终端模式运行。")
            return
        run_gui(black_player, white_player, difficulty)
    else:
        run_terminal(black_player, white_player, difficulty)


if __name__ == "__main__":
    main()

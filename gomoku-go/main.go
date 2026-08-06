// 命令五子棋（Gomoku）终端入口。
// 支持人机对战、双人对战、AI 对战三种模式。
package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/ZhaoWeir/gomoku-go/ai"
	"github.com/ZhaoWeir/gomoku-go/core"
)

// printBoard 在终端绘制棋盘。
func printBoard(board *core.Board) {
	size := board.Size
	// 顶部列号
	fmt.Print("     ")
	for c := 0; c < size; c++ {
		fmt.Printf("%2d  ", c)
	}
	fmt.Println()
	// 顶边
	fmt.Print("   +")
	for c := 0; c < size; c++ {
		fmt.Print("---+")
	}
	fmt.Println()
	for r := 0; r < size; r++ {
		fmt.Printf("%2d |", r)
		for c := 0; c < size; c++ {
			fmt.Printf(" %s |", board.Get(core.Point{Row: r, Col: c}).Symbol())
		}
		fmt.Println()
		// 行间横线
		fmt.Print("   +")
		for c := 0; c < size; c++ {
			fmt.Print("---+")
		}
		fmt.Println()
	}
}

// parsePoint 解析用户输入，格式 "row col"。
func parsePoint(text string) (core.Point, bool) {
	fields := strings.Fields(text)
	if len(fields) != 2 {
		return core.Point{}, false
	}
	row, err1 := strconv.Atoi(fields[0])
	col, err2 := strconv.Atoi(fields[1])
	if err1 != nil || err2 != nil {
		return core.Point{}, false
	}
	return core.Point{Row: row, Col: col}, true
}

// promptForMove 交互式获取用户落子点。
func promptForMove(game *core.Game, reader *bufio.Reader) core.Point {
	for {
		fmt.Printf("  玩家 %s 请落子 (行 列，如 '7 7'，输入 undo 悔棋，quit 退出): ",
			game.CurrentPlayer.Symbol())
		line, _ := reader.ReadString('\n')
		raw := strings.TrimSpace(line)
		low := strings.ToLower(raw)
		if low == "quit" || low == "q" || low == "exit" {
			fmt.Println("游戏结束，再见！")
			os.Exit(0)
		}
		if low == "undo" {
			if game.Undo() {
				fmt.Println("  已悔棋。")
				printBoard(game.Board)
				continue
			}
			fmt.Println("  没有可悔的棋。")
			continue
		}
		p, ok := parsePoint(raw)
		if !ok || !game.Board.IsValid(p) {
			fmt.Println("  输入无效，请使用 '行 列' 格式，例如 '7 7'。")
			continue
		}
		return p
	}
}

// aiForPlayer 根据模式判断某玩家是否由 AI 控制，并返回对应的 AI。
func aiForPlayer(player core.Player, blackPlayer, whitePlayer string, difficulty ai.Difficulty) (*ai.AIPlayer, bool) {
	if player == core.PlayerBlack && blackPlayer == "ai" {
		return ai.NewAIPlayer(core.PlayerBlack, difficulty), true
	}
	if player == core.PlayerWhite && whitePlayer == "ai" {
		return ai.NewAIPlayer(core.PlayerWhite, difficulty), true
	}
	return nil, false
}

// runGame 运行一局游戏。
func runGame(blackPlayer, whitePlayer string, difficulty ai.Difficulty) {
	game := core.NewGame()
	reader := bufio.NewReader(os.Stdin)

	fmt.Println("========== 五子棋 ==========")
	fmt.Printf("黑棋 %s 先行\n", core.PlayerBlack.Symbol())
	fmt.Printf("黑方: %s  白方: %s  难度: %s\n", blackPlayer, whitePlayer, difficulty)
	fmt.Println("输入格式: 行 列（如 '7 7'），输入 undo 悔棋，quit 退出")
	fmt.Println("=============================")
	printBoard(game.Board)

	for !game.IsOver() {
		current := game.CurrentPlayer
		var move core.Point
		if aiPlayer, isAI := aiForPlayer(current, blackPlayer, whitePlayer, difficulty); isAI {
			fmt.Printf("  AI (%s) 思考中...\n", current.Symbol())
			move = aiPlayer.ChooseMove(game.Board)
			fmt.Printf("  AI 落子: %d %d\n", move.Row, move.Col)
		} else {
			move = promptForMove(game, reader)
		}
		if !game.Play(move) {
			continue
		}
		printBoard(game.Board)
		if game.Winner != core.PlayerEmpty {
			fmt.Printf("\n🎉 %s 方获胜！\n", game.Winner.Symbol())
			return
		}
		if game.Board.IsFull() {
			fmt.Println("\n平局！")
			return
		}
	}
	if game.Winner != core.PlayerEmpty {
		fmt.Printf("\n🎉 %s 方获胜！\n", game.Winner.Symbol())
	} else {
		fmt.Println("\n平局！")
	}
}

// usage 打印使用说明。
func usage() {
	fmt.Println("用法: go run . [gui] [pvp|ai|ai2] [easy|medium|hard]")
	fmt.Println("  pvp  双人对战")
	fmt.Println("  ai   人机对战（默认，你执黑先手）")
	fmt.Println("  ai2  AI 对 AI")
	fmt.Println("难度: easy / medium / hard（默认 medium）")
}

func main() {
	blackPlayer := "human"
	whitePlayer := "ai"
	difficulty := ai.Medium

	args := os.Args[1:]
	for i := 0; i < len(args); i++ {
		arg := strings.ToLower(args[i])
		switch arg {
		case "pvp", "2p":
			blackPlayer, whitePlayer = "human", "human"
		case "ai", "pvai":
			blackPlayer, whitePlayer = "human", "ai"
		case "ai2", "ai-ai":
			blackPlayer, whitePlayer = "ai", "ai"
		case "easy":
			difficulty = ai.Easy
		case "medium":
			difficulty = ai.Medium
		case "hard":
			difficulty = ai.Hard
		case "-h", "--help", "help":
			usage()
			return
		default:
			if strings.HasPrefix(arg, "-") || arg != "" {
				fmt.Printf("未知参数: %s\n", args[i])
				usage()
				return
			}
		}
	}
	runGame(blackPlayer, whitePlayer, difficulty)
}

from flask import Flask, jsonify, request
from copy import deepcopy
from math import inf

app = Flask(__name__)

class ttt:
    win_patterns = [[0, 1, 2], [3, 4, 5], [6, 7, 8],
                    [0, 3, 6], [1, 4, 7], [2, 5, 8],
                    [0, 4, 8], [2, 4, 6]]

    def __init__(self, board=None):
        # Initialize the board from the frontend's state, or start empty
        self.board = board if board else 9 * [" "]
        self.move_count = 9 - self.board.count(" ")
        self.current = "X" if self.move_count % 2 == 0 else "O"
        self.mem_table = {}
        self.win_moves = []
        self.over = False
        
        winner = self.won(self.board)
        if winner or self.move_count == 9:
            self.over = True

    def opp(self, player):
        return "O" if player == "X" else "X"

    def return_found(self, lst):
        for e in lst:
            if e: return e
        return None

    def winpattern(self, board, moves):
        vals = [board[moves[0]], board[moves[1]], board[moves[2]]]
        s = set(vals)
        if len(s) == 1 and s.pop() != " ":
            self.win_moves = moves
            return board[moves[0]]
        return None

    def won(self, board):
        is_won = self.return_found([self.winpattern(board, x) for x in ttt.win_patterns])
        return is_won if is_won else None

    def full(self, board):
        return " " not in board

    def minimax(self, grid, maxPlayer):
        key = str(maxPlayer) + ''.join(grid)
        empty = [i for i, x in enumerate(grid) if x == " "]
        if key in self.mem_table:
            return self.mem_table[key]
        
        winner = self.won(grid)
        if winner == "O":
            result = (-1, len(empty) + 1)
            self.mem_table[key] = result
            return result
        elif winner == "X":
            result = (-1, -1 * (len(empty) + 1))
            self.mem_table[key] = result
            return result
        elif self.full(grid):
            result = (-1, 0)
            self.mem_table[key] = result
            return result
            
        best = -1
        if maxPlayer:
            value = -inf
            for m in empty:
                grid[m] = "O"
                newval = self.minimax(grid, False)[1]
                if newval > value:
                    value = newval
                    best = m
                grid[m] = " "
            result = (best, value)
        else:
            value = inf
            for m in empty:
                grid[m] = "X"
                newval = self.minimax(grid, True)[1]
                if newval < value:
                    value = newval
                    best = m
                grid[m] = " "
            result = (best, value)
        self.mem_table[key] = result
        return result

    def smart_move(self):
        board2 = deepcopy(self.board)
        move = self.minimax(board2, True)[0]
        return move

    def make_move(self, move):
        self.board[move] = self.current
        self.move_count += 1
        winner = self.won(self.board)
        if winner:
            self.over = True
            return {"status": "win", "winner": winner, "win_moves": self.win_moves}
        if self.move_count == 9 and self.full(self.board):
            self.over = True
            return {"status": "tie"}
        self.current = self.opp(self.current)
        return {"status": "continue"}

    def to_dict(self):
        return {
            "board": self.board,
            "current": self.current,
            "over": self.over,
            "win_moves": self.win_moves,
            "move_count": self.move_count,
        }

# Vercel Serverless Route
@app.route("/api/move", methods=["POST"])
def move():
    data = request.get_json()
    # Pull the current board state from the incoming request
    board = data.get("board", 9 * [" "]) 
    cell = data.get("cell")
    ai_on = data.get("ai_on", False)

    # Initialize a temporary game instance just for this request
    game = ttt(board)

    if game.over or game.board[cell] != " ":
        return jsonify({"error": "invalid move"})

    result = game.make_move(cell)

    if result["status"] == "continue" and ai_on and game.current == "O" and not game.over:
        ai_move = game.smart_move()
        ai_result = game.make_move(ai_move)
        return jsonify({
            "result": result,
            "ai_move": ai_move,
            "ai_result": ai_result,
            "state": game.to_dict()
        })

    return jsonify({
        "result": result,
        "ai_move": None,
        "ai_result": None,
        "state": game.to_dict()
    })
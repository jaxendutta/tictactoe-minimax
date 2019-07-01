from tkinter import *
from copy import deepcopy
from operator import itemgetter
from math import inf

class ttt:
    win_patterns = [[0, 1, 2], [3, 4, 5], [6, 7, 8], # Rows
                    [0, 3, 6], [1, 4, 7], [2, 5, 8], # Columns
                    [0, 4, 8], [2, 4, 6]]            # Diagonals

    buttons = []

    def __init__(self):
        self.board = 9*[" "]
        self.Xwins = 0
        self.Owins = 0
        self.current = "X"
        self.move_count = 0
        self.win_moves = []
        self.over = False
        self.moves = [StringVar() for x in range(9)]
        self.apply_all(lambda x: x.set(" "), self.moves)
        self.mem_table = {}

    def opp(self, player):
        return "O" if player == "X" else "X"

    def apply_all(self, f, list):
        for i in list: f(i)

    def return_found(self, list):
        for e in list:
            if e: return e
        return None

    def afterwin(self, winner):
        info.set(f"Player {winner} wins! Congratulations!")
        if winner == "X": self.Xwins += 1
        else: self.Owins += 1
        scores.set("Scoreboard\n──────────\nX: " + str(self.Xwins) + "\tO: " + str(self.Owins))
        self.apply_all(lambda x: x.config(bg="green", disabledforeground="white"),
                           [self.buttons[b] for b in self.win_moves])
        for b in self.buttons: b.config(state="disabled")

    def reset(self):
        on.config(state="normal")
        self.current = "X"
        self.move_count = 0
        self.over = False
        info.set("Player "+self.current+" starts the game!")
        self.board = [" " for x in self.board]
        self.update_board()
        for b in self.buttons: b.config(state="normal", disabledforeground="black", bg="#F0F0F0")
    
    def update_board(self):
        for x in range(9): self.moves[x].set(self.board[x])

    def winpattern(self, board, moves):
        patterns = set(itemgetter(moves[0], moves[1], moves[2])(board))
        if len(patterns) == 1 and patterns.pop() != " ":
            self.win_moves = moves
            return board[moves[0]]
        else: return None

    def won(self, board) -> str:
        is_won = self.return_found([self.winpattern(board, x) for x in ttt.win_patterns])
        if is_won: return is_won
        else: return None

    def full(self, board):
        return (" " not in board)

    def smart(self):
        board2 = deepcopy(self.board)
        move = self.minimax(board2, True)[0]
        self.make_move(move)

    def minimax(self, grid, maxPlayer):
        key = str(maxPlayer) + ''.join(grid)
        empty = [i for i, x in enumerate(grid) if x == " "]
        record = lambda x: self.mem_table.setdefault(key, x)
        if key in self.mem_table:
            return self.mem_table[key]
        if self.won(grid) == "O": return record((-1, len(empty) + 1))
        elif self.won(grid) == "X": return record((-1, -1*(len(empty) + 1)))
        elif self.full(grid): return record((-1, 0))
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
            return record((best, value))
        else:
            value = inf
            for m in empty:
                grid[m] = "X"
                newval = self.minimax(grid, True)[1]
                if newval < value:
                    value = newval
                    best = m
                grid[m] = " "
            return record((best, value))

    def make_move(self, move):
        on.config(state="disabled")
        self.move_count += 1
        self.board[move] = self.current
        info.set("It's Player "+self.opp(self.current)+"'s turn!")
        if self.current == "X" and on_var.get() and self.move_count < 9:
            self.current = self.opp(self.current)
            self.smart()
        else: self.current = self.opp(self.current)
        if self.over:
            return
        self.buttons[move].config(state="disabled")
        winner = self.won(self.board)
        if winner is not None:
            self.afterwin(winner)
            self.over = True
        elif self.move_count == 9 and self.full(self.board):
            info.set("It's a tie!")
            self.apply_all(lambda x: x.config(disabledforeground="red", bg="yellow"), self.buttons)
            self.over = True
        self.update_board()

# ------------Game GUI Setup------------

window = Tk()
window.title("Anirban's Tic-Tac-Toe")
window.config(bg="#36454f")
game = ttt()

# Welcome
welframe = Frame(window)
welframe.pack()
welframe.config(bg="#36454f")
wel = "Tic-Tac-Toe with Minimax AI"
welcome = Label(welframe, text="╔"+"═"*(len(wel)-10)+"╗\n║ "+wel+" ║\n╚"+"═"*(len(wel)-10)+"╝", 
                font=('OCR A Extended', 20, ), bg="#36454f", fg="white", padx=10)
welcome.pack(pady=10)

# Scoreboard
winframe = Frame(window)
winframe.pack()
winframe.config(bg="#36454f")
scores = StringVar()
scores.set("Scoreboard\n──────────\nX: " + str(game.Xwins) + "\tO: " + str(game.Owins))
scoreboard = Label(winframe, textvariable=scores, font=('OCR A Extended', 17), padx=10)
scoreboard.pack(pady=10)

# Checkbox for turning the AI on/off
choiceframe = Frame(window)
choiceframe.pack()
choiceframe.config(bg="#36454f")
on_var = IntVar()
on = Checkbutton(choiceframe, text="Play with a Minimax AI (Player O)?", #bg="#36454f", fg="white",
                    variable=on_var, font=('OCR A Extended', 15))
on.pack(pady=10)

# Infoboard
infoframe = Frame(window)
infoframe.pack()
infoframe.config(bg="#36454f")
info = StringVar()
info.set("Player X starts the game!")
infoboard = Label(infoframe, textvariable=info, font=('OCR A Extended', 15), bg="#36454f", fg="white")
infoboard.pack(pady=10)

# Grid
tttgrid = Frame(window)
tttgrid.pack()
for b in range(9):
    block = Button(tttgrid, width=5, height=2, font=('Bradley Hand ITC', 30), disabledforeground="black",
                textvariable=game.moves[b], command=lambda s=b: game.make_move(s))
    block.grid(row=int(b/3+3), column=(b%3), sticky=NSEW)
    game.buttons.append(block)

# Reset
resetframe = Frame(window)
resetframe.pack()
resetframe.config(bg="#36454f")
resetbutton = Button(resetframe, text="Replay", font=('OCR A Extended', 15), command=game.reset)
resetbutton.pack(pady=10)

window.mainloop()

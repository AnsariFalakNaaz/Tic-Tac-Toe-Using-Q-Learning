import tkinter as tk
from tkinter import messagebox
import pickle

# 🎨 COLORS
BG_COLOR = "#0f172a"
CARD_COLOR = "#1e293b"
BOARD_COLOR = "#334155"
BTN_COLOR = "#e2e8f0"
X_COLOR = "#38bdf8"
O_COLOR = "#f97316"
TEXT_COLOR = "#f8fafc"
WIN_COLOR = "#fde68a"

TOTAL_ROUNDS = 5

class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 RL Tic-Tac-Toe")
        self.root.geometry("1000x650")
        self.root.configure(bg=BG_COLOR)

        with open("q_table.pkl", "rb") as f:
            self.q_table = pickle.load(f)

        self.user_symbol = tk.StringVar(value="O")
        self.ai_symbol = "X"

        self.human_score = 0
        self.ai_score = 0
        self.current_round = 1

        self.board = [" "] * 9
        self.buttons = []
        self.game_over = False

        self.create_ui()
        self.update_symbols()
        self.update_score()

    # 🧱 UI LAYOUT
    def create_ui(self):
        main = tk.Frame(self.root, bg=BG_COLOR)
        main.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(main, bg=CARD_COLOR, width=250)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="🎮 Match Panel",
                 font=("Arial", 18, "bold"),
                 bg=CARD_COLOR, fg=TEXT_COLOR).pack(pady=20)

        self.score_label = tk.Label(sidebar, text="",
                                   font=("Arial", 14),
                                   bg=CARD_COLOR, fg=TEXT_COLOR)
        self.score_label.pack(pady=10)

        tk.Button(sidebar, text="🔄 Restart Round",
                  command=self.restart_round,
                  bg="#3b82f6", fg="white",
                  font=("Arial", 12, "bold")).pack(pady=10, fill="x", padx=20)

        tk.Button(sidebar, text="♻ Reset Match",
                  command=self.restart_match,
                  bg="#ef4444", fg="white",
                  font=("Arial", 12, "bold")).pack(pady=10, fill="x", padx=20)

        # Game area
        game = tk.Frame(main, bg=BG_COLOR)
        game.pack(side="right", expand=True)

        self.status_label = tk.Label(game,
                                    text="Your Turn",
                                    font=("Arial", 20, "bold"),
                                    bg=BG_COLOR, fg=TEXT_COLOR)
        self.status_label.pack(pady=20)

        board_frame = tk.Frame(game, bg=BOARD_COLOR)
        board_frame.pack()

        for i in range(9):
            btn = tk.Button(board_frame, text="",
                            font=("Arial", 28, "bold"),
                            width=4, height=2,
                            bg=BTN_COLOR,
                            command=lambda i=i: self.player_move(i))
            btn.grid(row=i//3, column=i%3, padx=8, pady=8)
            self.buttons.append(btn)

    def update_symbols(self):
        self.ai_symbol = "O" if self.user_symbol.get() == "X" else "X"

    def update_score(self):
        self.score_label.config(
            text=f"Human: {self.human_score}\nAI: {self.ai_score}\nRound: {self.current_round}/{TOTAL_ROUNDS}"
        )

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0)

    def available_actions(self):
        return [i for i, x in enumerate(self.board) if x == " "]

    # 🧠 SMART AI
    def choose_best_action(self):
        actions = self.available_actions()

        for a in actions:
            temp = self.board.copy()
            temp[a] = self.ai_symbol
            if self.check_win(temp, self.ai_symbol):
                return a

        for a in actions:
            temp = self.board.copy()
            temp[a] = self.user_symbol.get()
            if self.check_win(temp, self.user_symbol.get()):
                return a

        state = "".join(self.board)
        q_vals = [self.get_q(state, a) for a in actions]
        return actions[q_vals.index(max(q_vals))]

    def check_win(self, board, player):
        wins = [(0,1,2),(3,4,5),(6,7,8),
                (0,3,6),(1,4,7),(2,5,8),
                (0,4,8),(2,4,6)]
        return any(board[a]==board[b]==board[c]==player for a,b,c in wins)

    def player_move(self, i):
        if self.board[i] != " " or self.game_over:
            return

        sym = self.user_symbol.get()
        self.board[i] = sym
        self.buttons[i].config(text=sym,
                               fg=X_COLOR if sym=="X" else O_COLOR)

        if self.check_game():
            return

        self.status_label.config(text="AI thinking...")
        self.root.after(400, self.ai_move)

    def ai_move(self):
        if self.game_over:
            return

        a = self.choose_best_action()
        self.board[a] = self.ai_symbol

        self.buttons[a].config(text=self.ai_symbol,
                               fg=X_COLOR if self.ai_symbol=="X" else O_COLOR)

        self.status_label.config(text="Your Turn")
        self.check_game()

    def check_game(self):
        wins = [(0,1,2),(3,4,5),(6,7,8),
                (0,3,6),(1,4,7),(2,5,8),
                (0,4,8),(2,4,6)]

        for a,b,c in wins:
            if self.board[a] == self.board[b] == self.board[c] != " ":
                for i in [a,b,c]:
                    self.buttons[i].config(bg=WIN_COLOR)
                self.end_round(self.board[a])
                return True

        if " " not in self.board:
            self.end_round("Draw")
            return True

        return False

    def end_round(self, winner):
        self.game_over = True

        if winner == self.user_symbol.get():
            self.human_score += 1
            msg = "🎉 You Win!"
        elif winner == "Draw":
            msg = "Draw!"
        else:
            self.ai_score += 1
            msg = "🤖 AI Wins!"

        messagebox.showinfo("Result", msg)

        if self.current_round < TOTAL_ROUNDS:
            self.current_round += 1
            self.update_score()
            self.root.after(800, self.restart_round)
        else:
            self.finish_match()

    def restart_round(self):
        self.board = [" "] * 9
        self.game_over = False
        for btn in self.buttons:
            btn.config(text="", bg=BTN_COLOR)

    def restart_match(self):
        self.human_score = 0
        self.ai_score = 0
        self.current_round = 1
        self.restart_round()
        self.update_score()

    def finish_match(self):
        if self.human_score > self.ai_score:
            msg = "🏆 You won the match!"
        elif self.ai_score > self.human_score:
            msg = "🤖 AI won the match!"
        else:
            msg = "Match Draw!"

        messagebox.showinfo("Final Result", msg)
        self.restart_match()


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()
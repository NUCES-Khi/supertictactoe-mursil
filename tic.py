import tkinter as tk
from tkinter import ttk
import numpy as np
import threading
import copy
import time

class SuperTicTacToe:
    def __init__(self):
        self.board = [['' for _ in range(9)] for _ in range(9)]
        self.small_boards = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'User'
        self.simulation_count = 0  # Count the number of simulations

    def make_move(self, board_index, cell_index, player):
        row, col = divmod(board_index, 3)
        cell_row, cell_col = divmod(cell_index, 3)
        if self.board[row * 3 + cell_row][col * 3 + cell_col] == '':
            self.board[row * 3 + cell_row][col * 3 + cell_col] = player
            self.update_small_boards()
            return True
        return False

    def update_small_boards(self):
        for i in range(3):
            for j in range(3):
                sub_board = [self.board[x][j * 3:(j + 1) * 3] for x in range(i * 3, (i + 1) * 3)]
                if self.check_tris('User', sub_board):
                    self.small_boards[i][j] = 'User'
                elif self.check_tris('AI', sub_board):
                    self.small_boards[i][j] = 'AI'
                elif all(cell != '' for row in sub_board for cell in row):
                    self.small_boards[i][j] = 'D'

    def check_tris(self, player, board):
        for row in board:
            if row == [player] * 3:
                return True
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] == player:
                return True
        if board[0][0] == board[1][1] == board[2][2] == player or board[0][2] == board[1][1] == board[2][0] == player:
            return True
        return False

    def game_tie(self):
        return all(cell != '' for row in self.board for cell in row)

    def minimax(self, max_turn, depth, alpha, beta, start_time, time_limit):
        self.simulation_count += 1  # Increment the simulation count
        if time.time() - start_time > time_limit:
            return 0  # Stop the search when the time limit is reached
        if self.check_tris('AI', self.board):
            return 10 - depth
        elif self.check_tris('User', self.board):
            return depth - 10
        elif self.game_tie() or depth == 0:
            return 0

        if max_turn:
            max_eval = float('-inf')
            for i in range(9):
                for j in range(9):
                    if self.board[i][j] == '':
                        self.board[i][j] = 'AI'
                        eval = self.minimax(False, depth - 1, alpha, beta, start_time, time_limit)
                        self.board[i][j] = ''
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for i in range(9):
                for j in range(9):
                    if self.board[i][j] == '':
                        self.board[i][j] = 'User'
                        eval = self.minimax(True, depth - 1, alpha, beta, start_time, time_limit)
                        self.board[i][j] = ''
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
                if beta <= alpha:
                    break
            return min_eval

    def iterative_deepening(self, time_limit):
        start_time = time.time()
        best_move = None
        best_value = float('-inf')
        depth = 1

        while time.time() - start_time < time_limit:
            move = self.best_move(depth, start_time, time_limit)
            if move:
                best_move = move
            depth += 1

        return best_move

    def best_move(self, depth, start_time, time_limit):
        best_value = float('-inf')
        best_move = None

        for i in range(9):
            for j in range(9):
                if self.board[i][j] == '':
                    self.board[i][j] = 'AI'
                    move_value = self.minimax(False, depth, float('-inf'), float('inf'), start_time, time_limit)
                    self.board[i][j] = ''
                    if move_value > best_value:
                        best_value = move_value
                        best_move = (i, j)

        return best_move

class SuperTicTacToeUI(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.title("Super Tic-Tac-Toe")
        self.geometry("600x600")
        self.create_widgets()

    def create_widgets(self):
        self.board_buttons = []
        self.sub_board_frames = []
        for i in range(9):
            canvas = tk.Canvas(self, width=200, height=200, borderwidth=2, relief="solid")
            canvas.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            self.sub_board_frames.append(canvas)
            sub_buttons = []
            for j in range(9):
                button = tk.Button(canvas, text=' ', font=("Arial", 20), width=3, height=1,
                                   command=lambda i=i, j=j: self.on_button_click(i, j))
                button.place(x=(j % 3) * 66, y=(j // 3) * 66, width=66, height=66)
                sub_buttons.append(button)
            self.board_buttons.append(sub_buttons)

        self.status_label = tk.Label(self, text="User's turn", font=("Arial", 16))
        self.status_label.grid(row=3, column=0, columnspan=3)

    def on_button_click(self, board_index, cell_index):
        if self.game.make_move(board_index, cell_index, 'User'):
            self.update_ui()
            if not self.game.check_tris('User', self.game.board) and not self.game.game_tie():
                self.status_label.config(text="AI's turn")
                self.update_idletasks()
                self.after(100, self.ai_move)
            else:
                self.status_label.config(text="User wins!")

    def ai_move(self):
        best_move = self.game.iterative_deepening(10)  # Time limit of 10 seconds for AI move
        if best_move:
            self.game.make_move(best_move[0], best_move[1], 'AI')
            self.update_ui()
            if not self.game.check_tris('AI', self.game.board) and not self.game.game_tie():
                self.status_label.config(text="User's turn")
            else:
                self.status_label.config(text="AI wins!")
        print(f"AI ran {self.game.simulation_count} simulations")  # Print the number of simulations

    def update_ui(self):
        for i in range(9):
            for j in range(9):
                row, col = divmod(i, 3)
                cell_row, cell_col = divmod(j, 3)
                self.board_buttons[i][j].config(text=self.game.board[row * 3 + cell_row][col * 3 + cell_col])

            if self.game.small_boards[i // 3][i % 3] != '' and self.game.small_boards[i // 3][i % 3] != 'D':
                self.draw_cross(i // 3, i % 3, self.game.small_boards[i // 3][i % 3])

    def draw_cross(self, board_index_x, board_index_y, winner):
        canvas = self.sub_board_frames[board_index_x * 3 + board_index_y]
        canvas.delete("all")  # Clear previous drawings
        canvas.create_line(0, 0, canvas.winfo_width(), canvas.winfo_height(), fill="red", width=5)
        canvas.create_line(0, canvas.winfo_height(), canvas.winfo_width(), 0, fill="red", width=5)
        canvas.create_text(canvas.winfo_width() // 2, canvas.winfo_height() // 2, text=winner, font=("Arial", 30), fill="red")

if __name__ == "__main__":
    game = SuperTicTacToe()
    app = SuperTicTacToeUI(game)
    app.mainloop()

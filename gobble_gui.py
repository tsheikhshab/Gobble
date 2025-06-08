import tkinter as tk
from gobble import Game, GameConfig

class GobbleGUI:
    """Simple Tkinter interface for the Gobbles game."""

    def __init__(self):
        self.game = Game()
        self.size = 60
        try:
            self.window = tk.Tk()
        except tk.TclError as e:
            print("Error: Unable to open GUI window. Ensure a graphical display is available and $DISPLAY is set.")
            raise e
        self.window.title("Gobbles GUI")
        canvas_size = self.size * GameConfig.BOARD_SIZE
        self.canvas = tk.Canvas(self.window, width=canvas_size, height=canvas_size)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_board()

    def draw_board(self):
        """Draw grid and stones."""
        self.canvas.delete("all")
        board_pixels = self.size * GameConfig.BOARD_SIZE
        for i in range(GameConfig.BOARD_SIZE + 1):
            x = i * self.size
            self.canvas.create_line(x, 0, x, board_pixels)
            self.canvas.create_line(0, x, board_pixels, x)
        for r in range(GameConfig.BOARD_SIZE):
            for c in range(GameConfig.BOARD_SIZE):
                cell = self.game.board[r][c]
                if cell != GameConfig.SYMBOLS['empty']:
                    self.draw_stone(r, c, cell)

    def draw_stone(self, r, c, symbol):
        radius = self.size * 0.4
        x = c * self.size + self.size / 2
        y = r * self.size + self.size / 2
        color = 'black' if symbol == GameConfig.SYMBOLS['black'] else 'white'
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                fill=color, outline='black')

    def handle_click(self, event):
        c = event.x // self.size
        r = event.y // self.size
        if r >= GameConfig.BOARD_SIZE or c >= GameConfig.BOARD_SIZE:
            return
        valid, msg = self.game.apply_move(r, c, GameConfig.SYMBOLS['black'])
        if valid:
            self.draw_board()
            self.window.after(100, self.ai_move)
        else:
            print(msg)

    def ai_move(self):
        if self.game.passes < 2:
            self.game.ai_move()
            self.draw_board()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    GobbleGUI().run()

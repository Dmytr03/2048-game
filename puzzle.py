"""
Puzzle Module for 2048.
Handles the graphical user interface, event bindings, and overall game loop using tkinter.
"""
import json
import random
import sys
from tkinter import CENTER, Event, Frame, Label

import constants as c
import logic


def gen() -> int:
    """Generate a random index within the grid boundaries."""
    return random.randint(0, c.GRID_LEN - 1)

class GameGrid(Frame):
    """The main GUI class for the 2048 Game."""
    def __init__(self) -> None:
        """Initialize the GameGrid."""
        Frame.__init__(self)

        self.grid()
        self.master.title('2048')
        self.master.bind("<Key>", self.key_down)

        self.commands = {
            c.KEY_UP: logic.up,
            c.KEY_DOWN: logic.down,
            c.KEY_LEFT: logic.left,
            c.KEY_RIGHT: logic.right,
            c.KEY_UP_ALT1: logic.up,
            c.KEY_DOWN_ALT1: logic.down,
            c.KEY_LEFT_ALT1: logic.left,
            c.KEY_RIGHT_ALT1: logic.right,
            c.KEY_UP_ALT2: logic.up,
            c.KEY_DOWN_ALT2: logic.down,
            c.KEY_LEFT_ALT2: logic.left,
            c.KEY_RIGHT_ALT2: logic.right,
        }

        self.score = 0
        try:
            self.high_score = logic.load_high_score()
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            self.high_score = 0

        self.score_frame = Frame(self, bg=c.BACKGROUND_COLOR_GAME)
        self.score_frame.grid()
        self.score_label = Label(
            self.score_frame, 
            text=f"Score: {self.score}  High Score: {self.high_score}", 
            font=("Verdana", 16, "bold"), 
            bg=c.BACKGROUND_COLOR_GAME, 
            fg="white"
        )
        self.score_label.grid(pady=10)

        self.grid_cells: list[list[Label]] = []
        self.init_grid()
        self.matrix = logic.new_game(c.GRID_LEN)
        self.history_matrixs: list[list[list[int]]] = []
        self.update_grid_cells()

        self.mainloop()

    def init_grid(self) -> None:
        """Initialize the graphical grid layout."""
        background = Frame(self, bg=c.BACKGROUND_COLOR_GAME, width=c.SIZE, height=c.SIZE)
        background.grid()

        for i in range(c.GRID_LEN):
            grid_row = []
            for j in range(c.GRID_LEN):
                cell = Frame(
                    background,
                    bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                    width=c.SIZE / c.GRID_LEN,
                    height=c.SIZE / c.GRID_LEN
                )
                cell.grid(
                    row=i,
                    column=j,
                    padx=c.GRID_PADDING,
                    pady=c.GRID_PADDING
                )
                t = Label(
                    master=cell,
                    text="",
                    bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                    justify=CENTER,
                    font=c.FONT,
                    width=5,
                    height=2
                )
                t.grid()
                grid_row.append(t)
            self.grid_cells.append(grid_row)

    def update_grid_cells(self) -> None:
        """Update the visual state of the grid cells."""
        for i in range(c.GRID_LEN):
            for j in range(c.GRID_LEN):
                new_number = self.matrix[i][j]
                if new_number == c.EMPTY_CELL:
                    self.grid_cells[i][j].configure(text="", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.grid_cells[i][j].configure(
                        text=str(new_number),
                        bg=c.BACKGROUND_COLOR_DICT[new_number],
                        fg=c.CELL_COLOR_DICT[new_number]
                    )
        self.update_idletasks()

    def key_down(self, event: Event) -> None:
        """Handle keyboard events."""
        key = event.keysym
        print(event)
        if key == c.KEY_QUIT: 
            sys.exit()
        if key == c.KEY_BACK:
            restored_matrix, success = logic.undo_move(self.history_matrixs)
            if success and restored_matrix is not None:
                self.matrix = restored_matrix
                self.update_grid_cells()
                print('back on step total step:', len(self.history_matrixs))
        elif key in self.commands:
            self.matrix, done = self.commands[key](self.matrix)
            if done:
                self.matrix = logic.add_two(self.matrix)
                self.history_matrixs.append(self.matrix)
                self.update_grid_cells()
                if logic.game_state(self.matrix) == 'win':
                    self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                    self.grid_cells[1][2].configure(text="Win!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                if logic.game_state(self.matrix) == 'lose':
                    self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                    self.grid_cells[1][2].configure(text="Lose!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)

        self.score = max(max(row) for row in self.matrix)
        if self.score > self.high_score:
            self.high_score = self.score
            logic.save_high_score(self.high_score)
        
        if hasattr(self, 'score_label'):
            self.score_label.configure(text=f"Score: {self.score}  High Score: {self.high_score}")

    def generate_next(self) -> None:
        """Generate a new 2 in a random empty spot."""
        index = (gen(), gen())
        while self.matrix[index[0]][index[1]] != c.EMPTY_CELL:
            index = (gen(), gen())
        self.matrix[index[0]][index[1]] = c.NEW_TILE

if __name__ == '__main__':
    game_grid = GameGrid()

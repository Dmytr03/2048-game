"""
Game Logic Module for 2048.
Contains functions for matrix manipulation, game state checking, and movement logic.
"""

import copy
import json
import os
import random

import constants as c


def new_game(n: int) -> list[list[int]]:
    """Initialize a new game matrix."""
    matrix = []
    for i in range(n):
        matrix.append([c.EMPTY_CELL] * n)
    matrix = add_two(matrix)
    matrix = add_two(matrix)
    return matrix

def add_two(mat: list[list[int]]) -> list[list[int]]:
    """Add a new tile to an empty spot."""
    a = random.randint(0, len(mat)-1)
    b = random.randint(0, len(mat)-1)
    while mat[a][b] != c.EMPTY_CELL:
        a = random.randint(0, len(mat)-1)
        b = random.randint(0, len(mat)-1)
    mat[a][b] = c.NEW_TILE
    return mat

def game_state(mat: list[list[int]]) -> str:
    """Check game state."""
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == c.WIN_TILE:
                return 'win'
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == c.EMPTY_CELL:
                return 'not over'
    for i in range(len(mat)-1):
        for j in range(len(mat[0])-1):
            if mat[i][j] == mat[i+1][j] or mat[i][j+1] == mat[i][j]:
                return 'not over'
    for k in range(len(mat)-1):
        if mat[len(mat)-1][k] == mat[len(mat)-1][k+1]:
            return 'not over'
    for j in range(len(mat)-1):
        if mat[j][len(mat)-1] == mat[j+1][len(mat)-1]:
            return 'not over'
    return 'lose'

def reverse(mat: list[list[int]]) -> list[list[int]]:
    """Reverse matrix rows."""
    new = []
    for i in range(len(mat)):
        new.append([])
        for j in range(len(mat[0])):
            new[i].append(mat[i][len(mat[0])-j-1])
    return new

def transpose(mat: list[list[int]]) -> list[list[int]]:
    """Transpose matrix."""
    new = []
    for i in range(len(mat[0])):
        new.append([])
        for j in range(len(mat)):
            new[i].append(mat[j][i])
    return new

def cover_up(mat: list[list[int]]) -> tuple[list[list[int]], bool]:
    """Shift all non-empty tiles to the left."""
    new = []
    for j in range(c.GRID_LEN):
        partial_new = []
        for i in range(c.GRID_LEN):
            partial_new.append(c.EMPTY_CELL)
        new.append(partial_new)
    done = False
    for i in range(c.GRID_LEN):
        count = 0
        for j in range(c.GRID_LEN):
            if mat[i][j] != c.EMPTY_CELL:
                new[i][count] = mat[i][j]
                if j != count:
                    done = True
                count += 1
    return new, done

def merge(mat: list[list[int]], done: bool) -> tuple[list[list[int]], bool]:
    """Merge adjacent tiles of the same value."""
    for i in range(c.GRID_LEN):
        for j in range(c.GRID_LEN-1):
            if mat[i][j] == mat[i][j+1] and mat[i][j] != c.EMPTY_CELL:
                mat[i][j] *= 2
                mat[i][j+1] = c.EMPTY_CELL
                done = True
    return mat, done

def up(game: list[list[int]]) -> tuple[list[list[int]], bool]:
    """Move up."""
    print("up")
    game = transpose(game)
    game, done = cover_up(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    game = transpose(game)
    return game, done

def down(game: list[list[int]]) -> tuple[list[list[int]], bool]:
    """Move down."""
    print("down")
    game = reverse(transpose(game))
    game, done = cover_up(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    game = transpose(reverse(game))
    return game, done

def left(game: list[list[int]]) -> tuple[list[list[int]], bool]:
    """Move left."""
    print("left")
    game, done = cover_up(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    return game, done

def right(game: list[list[int]]) -> tuple[list[list[int]], bool]:
    """Move right."""
    print("right")
    game = reverse(game)
    game, done = cover_up(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    game = reverse(game)
    return game, done

def undo_move(history: list[list[list[int]]]) -> tuple[list[list[int]] | None, bool]:
    """Undo the last move."""
    if not history or len(history) <= 1:
        return None, False
    history.pop()
    return copy.deepcopy(history[-1]), True

def save_high_score(score: int, filepath: str = "highscore.json") -> bool:
    """Save the high score."""
    if not isinstance(score, int):
        raise TypeError("Score must be an integer.")
    if score < 0:
        raise ValueError("Score cannot be negative.")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"high_score": score}, f, indent=4)
        return True
    except OSError as e:
        print(f"Error saving high score: {e}")
        return False

def load_high_score(filepath: str = "highscore.json") -> int:
    """Load the high score."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"High score file '{filepath}' not found.")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    score = data.get("high_score", 0)
    if not isinstance(score, int) or score < 0:
        raise ValueError("Invalid score format in JSON.")
    return score

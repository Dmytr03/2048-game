import json
import os
import sys
from unittest.mock import mock_open, patch

import pytest

# Додаємо батьківську директорію до sys.path для імпорту logic.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logic


@pytest.fixture
def empty_matrix() -> list[list[int]]:
    return [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

@pytest.fixture
def game_matrix() -> list[list[int]]:
    return [
        [2, 0, 0, 2],
        [4, 4, 0, 0],
        [0, 0, 8, 8],
        [16, 0, 16, 0]
    ]

def test_game_state_lose() -> None:
    mat = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2]
    ]
    assert logic.game_state(mat) == 'lose'

def test_game_state_not_over(game_matrix: list[list[int]]) -> None:
    assert logic.game_state(game_matrix) == 'not over'

def test_game_state_win(game_matrix: list[list[int]]) -> None:
    game_matrix[0][0] = 2048
    assert logic.game_state(game_matrix) == 'win'

def test_undo_move_success() -> None:
    history = [
        [[2, 0], [0, 0]],
        [[2, 2], [0, 0]]
    ]
    matrix, success = logic.undo_move(history)
    assert success is True
    assert matrix == [[2, 0], [0, 0]]
    assert len(history) == 1

def test_undo_move_fail() -> None:
    matrix, success = logic.undo_move([])
    assert success is False
    assert matrix is None
    
    matrix, success = logic.undo_move([[[2, 0], [0, 0]]])
    assert success is False
    assert matrix is None

@patch('builtins.open', new_callable=mock_open)
def test_save_high_score_success(mock_file) -> None:
    result = logic.save_high_score(1500, "fake_score.json")
    assert result is True
    mock_file.assert_called_once_with("fake_score.json", "w", encoding="utf-8")

def test_save_high_score_invalid_data() -> None:
    with pytest.raises(ValueError):
        logic.save_high_score(-10)
    with pytest.raises(TypeError):
        logic.save_high_score("1000") # type: ignore

@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='{"high_score": 2500}')
def test_load_high_score_success(mock_file, mock_exists) -> None:
    score = logic.load_high_score("fake_score.json")
    assert score == 2500

@patch('os.path.exists', return_value=False)
def test_load_high_score_file_not_found(mock_exists) -> None:
    with pytest.raises(FileNotFoundError):
        logic.load_high_score("fake_score.json")

@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='{"high_score": "bad"}')
def test_load_high_score_invalid_json(mock_file, mock_exists) -> None:
    with pytest.raises(ValueError):
        logic.load_high_score("fake_score.json")

@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='not a json')
def test_load_high_score_corrupted_json(mock_file, mock_exists) -> None:
    with pytest.raises(json.JSONDecodeError):
        logic.load_high_score("fake_score.json")

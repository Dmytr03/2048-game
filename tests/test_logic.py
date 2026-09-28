import pytest
from unittest.mock import patch, mock_open
import json
import os
import sys

# Додаємо батьківську директорію до sys.path для імпорту logic.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logic

# Фікстура для порожньої матриці 4x4
@pytest.fixture
def empty_matrix():
    return [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

# Фікстура для частково заповненої матриці
@pytest.fixture
def game_matrix():
    return [
        [2, 0, 0, 2],
        [4, 4, 0, 0],
        [0, 0, 8, 8],
        [16, 0, 16, 0]
    ]

# 1. Тест: перевірка стану гри (Game Over - програш)
def test_game_state_lose():
    # Матриця без жодних доступних ходів (злиття неможливе, нулів немає)
    mat = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2]
    ]
    assert logic.game_state(mat) == 'lose'

# 2. Тест: перевірка стану гри (продовження)
def test_game_state_not_over(game_matrix):
    # У матриці ще є порожні комірки або можливі злиття
    assert logic.game_state(game_matrix) == 'not over'

# 3. Тест: перевірка стану гри (перемога - 2048)
def test_game_state_win(game_matrix):
    # Штучно додаємо переможну плитку
    game_matrix[0][0] = 2048
    assert logic.game_state(game_matrix) == 'win'

# 4. Тест: перевірка роботи undo_move (нормальне скасування)
def test_undo_move_success():
    # Історія ходів з двома станами
    history = [
        [[2, 0], [0, 0]],
        [[2, 2], [0, 0]]
    ]
    matrix, success = logic.undo_move(history)
    assert success is True
    # Має повернутись попередній стан
    assert matrix == [[2, 0], [0, 0]]
    # В історії має залишитись лише один елемент
    assert len(history) == 1

# 5. Тест: перевірка роботи undo_move (порожня або недостатня історія)
def test_undo_move_fail():
    # Випадок з порожньою історією
    matrix, success = logic.undo_move([])
    assert success is False
    assert matrix is None
    
    # Випадок з історією, де лише один стан (початковий)
    matrix, success = logic.undo_move([[[2, 0], [0, 0]]])
    assert success is False
    assert matrix is None

# 6. Тест: перевірка збереження рекорду (нормальна ситуація)
@patch('builtins.open', new_callable=mock_open)
def test_save_high_score_success(mock_file):
    # Зберігаємо коректний рекорд
    result = logic.save_high_score(1500, "fake_score.json")
    assert result is True
    mock_file.assert_called_once_with("fake_score.json", "w", encoding="utf-8")

# 7. Тест: перевірка збереження рекорду з некоректними даними (ValueError, TypeError)
def test_save_high_score_invalid_data():
    # Перевірка на від'ємне значення
    with pytest.raises(ValueError):
        logic.save_high_score(-10)
        
    # Перевірка на неправильний тип даних
    with pytest.raises(TypeError):
        logic.save_high_score("1000")

# 8. Тест: перевірка завантаження рекорду (нормальна ситуація)
@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='{"high_score": 2500}')
def test_load_high_score_success(mock_file, mock_exists):
    # Успішне завантаження наявного рекорду
    score = logic.load_high_score("fake_score.json")
    assert score == 2500

# 9. Тест: перевірка завантаження рекорду (відсутній файл та некоректний JSON)
@patch('os.path.exists', return_value=False)
def test_load_high_score_file_not_found(mock_exists):
    # Перевірка поведінки, коли файлу не існує
    with pytest.raises(FileNotFoundError):
        logic.load_high_score("fake_score.json")

@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='{"high_score": "bad"}')
def test_load_high_score_invalid_json(mock_file, mock_exists):
    # Перевірка поведінки, коли значення в JSON має некоректний формат
    with pytest.raises(ValueError):
        logic.load_high_score("fake_score.json")

# 10. Тест: перевірка завантаження рекорду при пошкодженому JSON файлі
@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data='not a json')
def test_load_high_score_corrupted_json(mock_file, mock_exists):
    # Перевірка поведінки, коли файл JSON повністю пошкоджений
    with pytest.raises(json.JSONDecodeError):
        logic.load_high_score("fake_score.json")

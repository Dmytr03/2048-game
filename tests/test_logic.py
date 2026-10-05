"""Unit-тести для логіки гри 2048."""

import json
import sys
from collections.abc import Callable
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import constants as c
import logic


@pytest.fixture
def board() -> list[list[int]]:
    """Створює порожню дошку 4x4 для незалежного тестового сценарію."""
    return [
        [c.EMPTY_CELL for _ in range(c.GRID_LEN)]
        for _ in range(c.GRID_LEN)
    ]


def test_new_game_creates_board_with_two_tiles() -> None:
    """Перевіряє розмір дошки та наявність двох початкових плиток."""
    with patch(
        "logic.random.randint",
        side_effect=[0, 0, 1, 1],
    ):
        result = logic.new_game(c.GRID_LEN)

    assert len(result) == c.GRID_LEN
    assert all(len(row) == c.GRID_LEN for row in result)
    assert sum(
        value == c.INITIAL_TILE_VALUE
        for row in result
        for value in row
    ) == c.INITIAL_TILE_COUNT


def test_add_two_uses_an_empty_cell(board: list[list[int]]) -> None:
    """Переконується, що нова плитка не перезаписує зайняту клітинку."""
    board[0][0] = c.INITIAL_TILE_VALUE * c.TILE_MERGE_FACTOR
    with patch("logic.random.randint", side_effect=[0, 0, 0, 1]):
        result = logic.add_two(board)

    assert result[0][0] == c.INITIAL_TILE_VALUE * c.TILE_MERGE_FACTOR
    assert result[0][1] == c.INITIAL_TILE_VALUE


def test_game_state_reports_win(board: list[list[int]]) -> None:
    """Перевіряє визначення перемоги за наявністю плитки 2048."""
    board[2][3] = c.WINNING_TILE

    assert logic.game_state(board) == "win"


def test_game_state_reports_game_over_for_full_board(board: list[list[int]]) -> None:
    """Перевіряє програш на повній дошці без суміжних однакових плиток."""
    values = [
        c.INITIAL_TILE_VALUE,
        c.INITIAL_TILE_VALUE * c.TILE_MERGE_FACTOR,
        c.INITIAL_TILE_VALUE * c.TILE_MERGE_FACTOR**2,
        c.INITIAL_TILE_VALUE * c.TILE_MERGE_FACTOR**3,
    ]
    for row_index in range(c.GRID_LEN):
        for column_index in range(c.GRID_LEN):
            board[row_index][column_index] = values[
                (row_index + column_index) % c.GRID_LEN
            ]

    assert logic.game_state(board) == "lose"


def test_game_state_continues_when_empty_cell_exists(board: list[list[int]]) -> None:
    """Перевіряє, що порожня клітинка дозволяє продовжувати гру."""
    board[0][0] = c.INITIAL_TILE_VALUE

    assert logic.game_state(board) == "not over"


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ((0, 0), (0, 1)),
        ((0, 0), (1, 0)),
        ((c.GRID_LEN - 1, 0), (c.GRID_LEN - 1, 1)),
        ((0, c.GRID_LEN - 1), (1, c.GRID_LEN - 1)),
    ],
)
def test_game_state_continues_when_equal_tiles_are_adjacent(
    board: list[list[int]],
    first: tuple[int, int],
    second: tuple[int, int],
) -> None:
    """Перевіряє, що однакові сусідні плитки означають наявність ходу."""
    for row_index in range(c.GRID_LEN):
        for column_index in range(c.GRID_LEN):
            board[row_index][column_index] = (
                row_index * c.GRID_LEN + column_index + c.INITIAL_TILE_VALUE
            )
    board[second[0]][second[1]] = board[first[0]][first[1]]

    assert logic.game_state(board) == "not over"


def test_reverse_and_transpose_transform_matrix(board: list[list[int]]) -> None:
    """Перевіряє горизонтальне віддзеркалення та транспонування матриці."""
    board[0][1] = c.INITIAL_TILE_VALUE
    board[2][3] = c.INITIAL_TILE_VALUE * c.TILE_MERGE_FACTOR**2

    assert logic.reverse(board)[0] == [
        c.EMPTY_CELL,
        c.EMPTY_CELL,
        c.INITIAL_TILE_VALUE,
        c.EMPTY_CELL,
    ]
    assert logic.transpose(board)[1][0] == c.INITIAL_TILE_VALUE
    assert logic.transpose(board)[3][2] == c.INITIAL_TILE_VALUE * c.TILE_MERGE_FACTOR**2


def test_cover_up_and_merge_combine_tiles(board: list[list[int]]) -> None:
    """Перевіряє стискання рядка та злиття однакових ненульових плиток."""
    board[0] = [
        c.INITIAL_TILE_VALUE,
        c.EMPTY_CELL,
        c.INITIAL_TILE_VALUE,
        c.INITIAL_TILE_VALUE,
    ]

    compressed, shifted = logic.cover_up(board)
    merged, combined = logic.merge(compressed, shifted)
    result, _ = logic.cover_up(merged)

    assert result[0] == [
        c.INITIAL_TILE_VALUE * c.TILE_MERGE_FACTOR,
        c.INITIAL_TILE_VALUE,
        c.EMPTY_CELL,
        c.EMPTY_CELL,
    ]
    assert combined is True


@pytest.mark.parametrize(
    ("move", "positions"),
    [
        (logic.left, ((0, 0), (0, 1))),
        (logic.right, ((0, 0), (0, 1))),
        (logic.up, ((0, 0), (1, 0))),
        (logic.down, ((0, 0), (1, 0))),
    ],
)
def test_moves_merge_tiles_and_report_points(
    board: list[list[int]],
    move: Callable[..., logic.MoveResult],
    positions: tuple[tuple[int, int], tuple[int, int]],
) -> None:
    """Перевіряє злиття, підрахунок очок і зворотну сумісність ходів."""
    for row_index, column_index in positions:
        board[row_index][column_index] = c.INITIAL_TILE_VALUE

    result, changed, points = move(board, with_score=True)

    assert changed is True
    assert points == c.INITIAL_TILE_VALUE * c.TILE_MERGE_FACTOR
    assert sum(
        value == c.INITIAL_TILE_VALUE * c.TILE_MERGE_FACTOR
        for row in result
        for value in row
    ) == 1
    assert len(move(board)) == 2


def test_undo_move_restores_latest_state() -> None:
    """Перевіряє вилучення останнього стану зі стеку історії."""
    first = [[c.INITIAL_TILE_VALUE]]
    last = [[c.INITIAL_TILE_VALUE * c.TILE_MERGE_FACTOR]]
    history = [first, last]

    restored, succeeded = logic.undo_move(history)

    assert restored is last
    assert succeeded is True
    assert history == [first]


def test_undo_move_returns_failure_for_empty_history() -> None:
    """Перевіряє результат відкату, коли історія ходів порожня."""
    assert logic.undo_move([]) == (None, False)


def test_save_high_score_creates_file_when_missing() -> None:
    """Перевіряє створення JSON-файлу рекорду під час першого збереження."""
    mocked_file = mock_open()
    with (
        patch("logic.load_high_score", side_effect=FileNotFoundError),
        patch("builtins.open", mocked_file),
    ):
        saved = logic.save_high_score(120, "record.json")

    assert saved is True
    mocked_file.assert_called_once_with("record.json", "w", encoding="utf-8")
    written = "".join(call.args[0] for call in mocked_file().write.call_args_list)
    assert json.loads(written) == {"high_score": 120}


def test_save_high_score_does_not_replace_better_record() -> None:
    """Перевіряє, що нижчий результат не перезаписує наявний рекорд."""
    with (
        patch("logic.load_high_score", return_value=200),
        patch("builtins.open", mock_open()) as mocked_file,
    ):
        saved = logic.save_high_score(150, "record.json")

    assert saved is False
    mocked_file.assert_not_called()


@pytest.mark.parametrize(
    ("score", "error"),
    [(-1, ValueError), ("100", TypeError), (True, TypeError)],
)
def test_save_high_score_rejects_invalid_score(score: object, error: type) -> None:
    """Перевіряє відхилення від'ємного та некоректного значення результату."""
    with pytest.raises(error):
        logic.save_high_score(score)


def test_save_high_score_rejects_invalid_filepath() -> None:
    """Перевіряє, що шлях до файлу рекорду має бути рядком."""
    with pytest.raises(TypeError):
        logic.save_high_score(10, None)


def test_load_high_score_reads_json_record() -> None:
    """Перевіряє читання коректного рекорду з ізольованого JSON-файлу."""
    mocked_file = mock_open(read_data='{"high_score": 512}')
    with patch("builtins.open", mocked_file):
        score = logic.load_high_score("record.json")

    assert score == 512
    mocked_file.assert_called_once_with("record.json", "r", encoding="utf-8")


def test_load_high_score_raises_for_missing_file() -> None:
    """Переконується, що відсутній файл не маскується значенням за замовчуванням."""
    with (
        patch("builtins.open", side_effect=FileNotFoundError),
        pytest.raises(FileNotFoundError),
    ):
        logic.load_high_score("missing.json")


def test_load_high_score_rejects_invalid_filepath() -> None:
    """Перевіряє, що шлях завантаження рекорду має бути рядком."""
    with pytest.raises(TypeError):
        logic.load_high_score(None)


def test_load_high_score_raises_for_corrupted_json() -> None:
    """Перевіряє явну помилку під час читання пошкодженого JSON."""
    with (
        patch("builtins.open", mock_open(read_data="{broken")),
        pytest.raises(json.JSONDecodeError),
    ):
        logic.load_high_score("broken.json")


@pytest.mark.parametrize(
    ("data", "error"),
    [
        ('{"other": 10}', ValueError),
        ('{"high_score": -1}', ValueError),
        ('{"high_score": "10"}', TypeError),
        ("[]", ValueError),
        ('{"high_score": true}', TypeError),
    ],
)
def test_load_high_score_rejects_invalid_record(data: str, error: type) -> None:
    """Перевіряє валідацію обов'язкового ключа та значення рекорду."""
    with (
        patch("builtins.open", mock_open(read_data=data)),
        pytest.raises(error),
    ):
        logic.load_high_score("invalid.json")

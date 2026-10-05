"""Модуль логіки гри 2048.

У цьому модулі реалізовано основні алгоритми для створення нового поля,
додавання нових плиток, перевірки стану гри та виконання ходів у чотирьох
напрямках. Логіка працює з квадратною матрицею, де кожна комірка містить
ціле число або 0 для порожньої клітинки.
"""

import json
import random
from typing import TypeAlias

import constants as c

Matrix: TypeAlias = list[list[int]]
MoveResult: TypeAlias = tuple[Matrix, bool] | tuple[Matrix, bool, int]


# ---------------------------------------------------------------------------
# Історія ходів і найкращий результат
# ---------------------------------------------------------------------------


# Відновлення поля з попереднього стану
def undo_move(
    history: list[Matrix],
) -> tuple[Matrix | None, bool]:
    """Вилучає останній збережений стан зі стеку та повертає його для відкату.

    Історія має містити копії матриць поля у порядку їх збереження. Функція
    змінює переданий список: у разі успіху останній елемент вилучається зі
    стеку. Порожня історія не є помилкою і повертає ознаку невдалого відкату.

    Args:
        history: Стек попередніх станів, кожен з яких є матрицею цілих чисел.

    Returns:
        Пара з відновленою матрицею та прапорцем успіху. Для порожнього стеку
        повертається ``(None, False)``, інакше — ``(стан, True)``.
    """
    if not history:
        return None, False
    return history.pop(), True


# Підрахунок очок плиток, які об'єднаються у стиснутих рядках
def _merged_points(mat: Matrix) -> int:
    """Обчислює очки за злиття у рядках, стиснутих ліворуч.

    Перегляд імітує злиття зліва направо: після злиття пара плиток
    пропускається, тож одна плитка не може об'єднатися двічі за один хід.
    Метод очікує матрицю після підготовчого стискання, у якій нулі в рядках
    зібрані праворуч.

    Args:
        mat: Матриця, підготовлена до злиття в напрямку ліворуч.

    Returns:
        Сума значень новоутворених плиток, тобто очки за цей хід.
    """
    points = c.INITIAL_SCORE
    for row in mat:
        index = 0
        while index < len(row) - 1:
            if row[index] != 0 and row[index] == row[index + 1]:
                points += row[index] * c.TILE_MERGE_FACTOR
                index += c.INITIAL_TILE_COUNT
            else:
                index += 1
    return points


# Збереження нового найкращого результату у JSON
def save_high_score(
    score: int,
    filepath: str = "highscore.json",
) -> bool:
    """Зберігає рекорд у JSON, лише якщо результат перевищує поточний рекорд.

    Файл має містити JSON-об'єкт із цілим невід'ємним значенням за ключем
    ``high_score``. Якщо файл ще не існує, рекорд вважається рівним нулю.
    Некоректне значення аргументу або пошкоджені дані наявного файлу не
    маскуються: відповідний виняток передається виклику.

    Args:
        score: Не від'ємна кількість очок для порівняння з рекордом.
        filepath: Шлях до JSON-файлу рекорду.

    Returns:
        ``True``, якщо файл було оновлено; ``False``, якщо результат не
        перевищив уже збережений рекорд.

    Raises:
        TypeError: Якщо score не є цілим числом або filepath не є рядком.
        ValueError: Якщо score є від'ємним.
        json.JSONDecodeError: Якщо наявний файл містить некоректний JSON.
        OSError: Якщо файл неможливо прочитати або записати.
    """
    if isinstance(score, bool) or not isinstance(score, int):
        raise TypeError("score має бути цілим числом")
    if score < c.INITIAL_SCORE:
        raise ValueError("score не може бути від'ємним")
    if not isinstance(filepath, str):
        raise TypeError("filepath має бути рядком")

    try:
        current_high_score = load_high_score(filepath)
    except FileNotFoundError:
        current_high_score = c.INITIAL_SCORE

    if score <= current_high_score:
        return False

    with open(filepath, "w", encoding="utf-8") as high_score_file:
        json.dump({"high_score": score}, high_score_file, ensure_ascii=False, indent=2)
    return True


# Завантаження рекорду з JSON
def load_high_score(filepath: str = "highscore.json") -> int:
    """Завантажує та перевіряє найкращий результат із JSON-файлу.

    Очікується JSON-об'єкт із ключем ``high_score``, значенням якого є
    невід'ємне ціле число. Функція не підміняє відсутній файл нулем і не
    ігнорує пошкоджений або некоректно сформований запис: викликач може
    окремо обробити відповідний виняток.

    Args:
        filepath: Шлях до JSON-файлу рекорду.

    Returns:
        Завантажене невід'ємне значення рекорду.

    Raises:
        TypeError: Якщо filepath або збережений рекорд має неправильний тип.
        ValueError: Якщо у файлі немає ключа ``high_score`` або його значення
            є від'ємним.
        FileNotFoundError: Якщо файл за вказаним шляхом відсутній.
        json.JSONDecodeError: Якщо файл не містить коректного JSON.
        OSError: Якщо файл неможливо прочитати.
    """
    if not isinstance(filepath, str):
        raise TypeError("filepath має бути рядком")

    with open(filepath, "r", encoding="utf-8") as high_score_file:
        data = json.load(high_score_file)

    if not isinstance(data, dict) or "high_score" not in data:
        raise ValueError("JSON-файл має містити ключ 'high_score'")

    score = data["high_score"]
    if isinstance(score, bool) or not isinstance(score, int):
        raise TypeError("Збережений high_score має бути цілим числом")
    if score < c.INITIAL_SCORE:
        raise ValueError("Збережений high_score не може бути від'ємним")
    return score


# ---------------------------------------------------------------------------
# Початкова генерація поля
# ---------------------------------------------------------------------------


def new_game(n: int) -> Matrix:
    """Створює нову гру 2048 з порожнім квадратним полем.

    Функція ініціалізує матрицю розміром n x n, заповнює її нулями,
    а потім додає дві початкові плитки зі значенням 2. Така конфігурація
    відповідає стандартним правилам запуску гри 2048.

    Args:
        n (int): Розмір сторони ігрового поля.

    Returns:
        list[list[int]]: Матриця гри з двома випадково розміщеними плитками 2.
    """
    matrix: Matrix = []
    for i in range(n):
        matrix.append([c.EMPTY_CELL] * n)
    for _ in range(c.INITIAL_TILE_COUNT):
        matrix = add_two(matrix)
    return matrix


# ---------------------------------------------------------------------------
# Додавання нової плитки
# ---------------------------------------------------------------------------


def add_two(mat: Matrix) -> Matrix:
    """Випадково додає нову плитку зі значенням 2 у порожню комірку.

    Метод вибирає випадкові індекси рядка і стовпця, перевіряє, чи саме
    місце вільне, і лише після цього ставить нову плитку. У циклі while
    гарантується, що плитка не з'явиться на вже заповненій клітинці.

    Args:
        mat (list[list[int]]): Поточна матриця гри.

    Returns:
        list[list[int]]: Матриця з доданою новою плиткою 2.
    """
    a = random.randint(c.EMPTY_CELL, len(mat) - 1)
    b = random.randint(c.EMPTY_CELL, len(mat) - 1)
    while mat[a][b] != c.EMPTY_CELL:
        a = random.randint(c.EMPTY_CELL, len(mat) - 1)
        b = random.randint(c.EMPTY_CELL, len(mat) - 1)
    mat[a][b] = c.INITIAL_TILE_VALUE
    return mat


# ---------------------------------------------------------------------------
# Перевірка стану гри
# ---------------------------------------------------------------------------


def game_state(mat: Matrix) -> str:
    """Визначає поточний стан гри: перемога, продовження або програш.

    Логіка перевіряє три ключові ознаки:
    1) чи з'явилася плитка 2048;
    2) чи є хоча б одна порожня клітинка;
    3) чи існують сусідні однакові значення, які можна об'єднати.

    Порядок перевірок важливий: якщо знайдено плитку 2048, гра одразу
    вважається виграною, навіть якщо інші умови ще відповідають активному ходу.

    Args:
        mat (list[list[int]]): Матриця поточного стану гри.

    Returns:
        str: Один із рядків: 'win', 'not over' або 'lose'.
    """
    # Перевірка на перемогу: клітинка зі значенням 2048 означає, що гравець
    # досяг фінального результату в поточному стані поля.
    for i in range(c.GRID_LEN):
        for j in range(len(mat[0])):
            if mat[i][j] == c.WINNING_TILE:
                return 'win'

    # Перевірка наявності порожніх комірок. Якщо є хоча б одне 0, хід можна
    # продовжувати, бо нова плитка ще може з'явитися.
    for i in range(c.GRID_LEN):
        for j in range(len(mat[0])):
            if mat[i][j] == c.EMPTY_CELL:
                return 'not over'

    # Перевірка на сусідні однакові значення: якщо поруч є однакові плитки,
    # їх можна об'єднати, тому гра не завершена.
    for i in range(c.GRID_LEN - 1):
        for j in range(len(mat[0]) - 1):
            if mat[i][j] == mat[i + 1][j] or mat[i][j + 1] == mat[i][j]:
                return 'not over'

    # Для останнього рядка перевіряємо горизонтальну суміжність.
    for k in range(c.GRID_LEN - 1):
        if mat[c.GRID_LEN - 1][k] == mat[c.GRID_LEN - 1][k + 1]:
            return 'not over'

    # Для останнього стовпця перевіряємо вертикальну суміжність.
    for j in range(c.GRID_LEN - 1):
        if mat[j][c.GRID_LEN - 1] == mat[j + 1][c.GRID_LEN - 1]:
            return 'not over'

    return 'lose'


# ---------------------------------------------------------------------------
# Операції з рядками та стовпцями
# ---------------------------------------------------------------------------


def reverse(mat: Matrix) -> Matrix:
    """Повертає матрицю по горизонталі, змінюючи порядок елементів у кожному рядку.

    Дана функція симетрично відображає кожен рядок, щоб потім можна було
    застосувати стандартні процедури зсуву для різних напрямків руху плиток.

    Args:
        mat (list[list[int]]): Вхідна матриця гри.

    Returns:
        list[list[int]]: Матриця, у якій елементи рядків записані у зворотному порядку.
    """
    new = []
    for i in range(len(mat)):
        new.append([])
        for j in range(len(mat[0])):
            new[i].append(mat[i][len(mat[0]) - j - 1])
    return new


def transpose(mat: Matrix) -> Matrix:
    """Транспонує матрицю, замінюючи рядки на стовпці та навпаки.

    Ця операція дозволяє легко реалізувати рух плиток вверх і вниз, коли для
    одного напряму вже існує логіка руху вліво або вправо. Транспонування є
    основним інструментом для повороту ігрового поля без зміни значень плиток.

    Args:
        mat (list[list[int]]): Вхідна матриця гри.

    Returns:
        list[list[int]]: Транспонована матриця.
    """
    new = []
    for i in range(len(mat[0])):
        new.append([])
        for j in range(len(mat)):
            new[i].append(mat[j][i])
    return new


# ---------------------------------------------------------------------------
# Основна логіка переміщення плиток
# ---------------------------------------------------------------------------


def cover_up(mat: Matrix) -> tuple[Matrix, bool]:
    """Стискає всі ненульові значення у рядку до його початку.

    Під час ходу плитки «зрушуються» в бік, а нульові комірки відсікаються.
    Після стиснення функція повертає нову матрицю і прапорець done, який
    показує, чи відбулася будь-яка зміна в полі.

    Args:
        mat (list[list[int]]): Матриця до стискання.

    Returns:
        tuple: Кортеж (нове_поле, було_зміни), де було_зміни — булеве значення.
    """
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


def merge(mat: Matrix, done: bool) -> tuple[Matrix, bool]:
    """Об'єднує сусідні однакові плитки в одному рядку.

    Для кожної пари комірок, що стоять поруч, якщо їхні значення рівні і не
    дорівнюють нулю, їх сума записується в ліву/першу комірку, а друга скидається
    до нуля. Прапорець done вказує, чи відбулося хоча б одне злиття.

    Args:
        mat (list[list[int]]): Матриця після стискання.
        done (bool): Попередній статус зміни поля.

    Returns:
        tuple: Кортеж (оновлена_матриця, done).
    """
    for i in range(c.GRID_LEN):
        for j in range(c.GRID_LEN - 1):
            if mat[i][j] == mat[i][j+1] and mat[i][j] != c.EMPTY_CELL:
                mat[i][j] *= c.TILE_MERGE_FACTOR
                mat[i][j+1] = c.EMPTY_CELL
                done = True
    return mat, done


def up(game: Matrix, with_score: bool = False) -> MoveResult:
    """Зсуває плитки вгору.

    Для реалізації руху вверх поле транспонується, а потім застосовується логіка
    зсуву вліво. Після об'єднання значень результат повертається до початкового
    орієнтування. Функція повертає оновлену матрицю і інформацію про те, чи
    відбувалася зміна на полі.

    Args:
        game (list[list[int]]): Поточна матриця гри.
        with_score (bool): Якщо True, додатково повертає очки за злиття.

    Returns:
        tuple: За замовчуванням (матриця_після_ходу, done); якщо with_score
        дорівнює True, результат має вигляд (матриця_після_ходу, done, очки).
    """
    print("up")
    # Спочатку транспонуємо поле, щоб рух вгору звести до руху вліво.
    game = transpose(game)
    game, done = cover_up(game)
    points = _merged_points(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    game = transpose(game)
    if with_score:
        return game, done, points
    return game, done


def down(game: Matrix, with_score: bool = False) -> MoveResult:
    """Зсуває плитки вниз.

    Для руху вниз застосовується послідовність обертання та перевороту матриці,
    після чого використовуються стандартні операції стиснення та злиття. Це
    дозволяє повторно використовувати логіку, розроблену для руху вліво.

    Args:
        game (list[list[int]]): Поточна матриця гри.
        with_score (bool): Якщо True, додатково повертає очки за злиття.

    Returns:
        tuple: За замовчуванням (матриця_після_ходу, done); якщо with_score
        дорівнює True, результат має вигляд (матриця_після_ходу, done, очки).
    """
    print("down")
    # Рух вниз реалізовано через переворот і транспонування, щоб використовувати
    # ту саму логіку, що й для руху вліво.
    game = reverse(transpose(game))
    game, done = cover_up(game)
    points = _merged_points(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    game = transpose(reverse(game))
    if with_score:
        return game, done, points
    return game, done


def left(game: Matrix, with_score: bool = False) -> MoveResult:
    """Зсуває плитки вліво.

    Ця функція є базовою для усіх інших напрямків: спочатку відбувається
    стиснення плиток до лівого краю, потім їх злиття, а після цього повторне
    стиснення для очищення порожніх місць.

    Args:
        game (list[list[int]]): Поточна матриця гри.
        with_score (bool): Якщо True, додатково повертає очки за злиття.

    Returns:
        tuple: За замовчуванням (матриця_після_ходу, done); якщо with_score
        дорівнює True, результат має вигляд (матриця_після_ходу, done, очки).
    """
    print("left")
    # Класичний алгоритм: стиснути -> об'єднати -> стиснути ще раз.
    game, done = cover_up(game)
    points = _merged_points(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    if with_score:
        return game, done, points
    return game, done


def right(game: Matrix, with_score: bool = False) -> MoveResult:
    """Зсуває плитки вправо.

    Механіка реалізована через перевертання поля перед виконанням лівого руху
    і повторне перевертання після завершення злиття. Такий підхід мінімізує
    дублювання логіки для різних напрямків.

    Args:
        game (list[list[int]]): Поточна матриця гри.
        with_score (bool): Якщо True, додатково повертає очки за злиття.

    Returns:
        tuple: За замовчуванням (матриця_після_ходу, done); якщо with_score
        дорівнює True, результат має вигляд (матриця_після_ходу, done, очки).
    """
    print("right")
    # Спочатку перевертаємо поле, щоб скористатися логікою руху вліво, а потім
    # повертаємо результат у початкову орієнтацію.
    game = reverse(game)
    game, done = cover_up(game)
    points = _merged_points(game)
    game, done = merge(game, done)
    game = cover_up(game)[0]
    game = reverse(game)
    if with_score:
        return game, done, points
    return game, done

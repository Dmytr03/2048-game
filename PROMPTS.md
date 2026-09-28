# Prompts History

## 2026-09-28

**Prompt:**
Проаналізуй вміст папки 2048-game (файли logic.py, puzzle.py, constants.py). Після цього напиши детальні docstrings та коментарі над усіма існуючими функціями та класами. Додай змінений код у репозиторій на GitHub: https://github.com/Dmytr03/2048-game. Цю зміну коду (і всі подальші також) обов'язково додавай в гілку ai/google-antigravity. В цій же папці створи файл PROMPTS.md, куди ти будеш додавати кожен промпт, дату та перелік змінених файлів. Потім запуш цей файл на GitHub разом із кодом у гілку ai/google-antigravity.

**Modified files:**
- `logic.py`
- `puzzle.py`
- `constants.py`
- `PROMPTS.md`

## 2026-09-28

**Prompt:**
Ти Senior Python Developer. Додай у файл logic.py дві нові функціональності:
1. Функцію undo_move(history: list) -> tuple[list[list[int]] | None, bool], яка приймає стек історії станів матриці, витягує останній стан і повертає відновлену матрицю поля та прапорець успіху (True/False). Якщо історія порожня — повертає (None, False).
2. Функції save_high_score(score: int, filepath: str = "highscore.json") -> bool та load_high_score(filepath: str = "highscore.json") -> int для збереження та завантаження найкращого результату з JSON-файлу.

Вимоги:
- Всі нові функції повинні містити Type Hints та детальні Docstrings.
- Додай сувору обробку виняткових ситуацій: від'ємний або некоректний score (TypeError, ValueError), відсутність файлу (FileNotFoundError) та пошкоджений JSON (json.JSONDecodeError).
- Інтегруй збереження рекорду в ігровий цикл.
- Код має бути структурованим та читабельним. Перед кожною новою функцією напиши короткий коментар.

Всі зміни коду додай на GitHub у гілку ai/google-antigravity. Промпт запиши у PROMPTS.md і також запуш на GitHub.

**Modified files:**
- `logic.py`
- `puzzle.py`
- `PROMPTS.md`

## 2026-09-28

**Prompt:**
Створи окрему папку tests та файл tests/test_logic.py у проєкті. Напиши комплект Unit-тестів під фреймворк pytest для модуля logic.py (включаючи нові функції undo_move, save_high_score, load_high_score).

Вимоги:
1. Мінімум 7-9 тестових сценаріїв для тестування нормальних значень, граничних станів (повна дошка, Game Over) та виняткових ситуацій (пошкоджений файл рекорду, порожня історія ходів).
2. Використай pytest.fixture для формування початкового стану матриці 4x4.
3. Використай unittest.mock (mock_open, patch) для ізольованого тестування роботи з JSON-файлом.
4. Напиши всі коментарі всередині файлу test_logic.py українською мовою.

Після створення тестів виконай команду pytest у терміналі та збережи результат (включаючи відсоток покриття коду coverage) в окремий файл TEST_RESULTS.md. Всі зміни та оновлений PROMPTS.md запуш у гілку ai/google-antigravity.

**Modified files:**
- `tests/test_logic.py`
- `TEST_RESULTS.md`
- `PROMPTS.md`

## 2026-09-28

**Prompt:**
Проведи аналіз якості коду всіх файлів у папці проєкту (logic.py, puzzle.py, tests/test_logic.py), використовуючи static analyzer / linter ruff. Скопіюй детальний звіт із помилками та попередженнями від ruff і допиши його у файл TEST_RESULTS.md. Після цього запропонуй конкретні рекомендації щодо рефакторингу коду. Запуш зміни та оновлений PROMPTS.md у гілку ai/google-antigravity.

**Modified files:**
- `TEST_RESULTS.md`
- `PROMPTS.md`

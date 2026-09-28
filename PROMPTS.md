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

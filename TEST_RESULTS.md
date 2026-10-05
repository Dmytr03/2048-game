============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: .
plugins: cov-7.1.0
collected 32 items

tests\test_logic.py ................................                     [100%]

=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.14.6-final-0 _______________

Name       Stmts   Miss  Cover   Missing
----------------------------------------
logic.py     162      0   100%
----------------------------------------
TOTAL        162      0   100%
============================= 32 passed in 0.11s ==============================

## Звіт статичного аналізу Ruff

- **Дата запуску:** 2026-10-05
- **Команда:** `ruff check logic.py puzzle.py tests/test_logic.py --output-format=full`
- **Версія:** Ruff 0.16.9
- **Результат:** код завершення 1; знайдено 6 зауважень, із них 3 Ruff може виправити автоматично стандартним `--fix`. Одне додаткове виправлення доступне лише з `--unsafe-fixes`.
- **Охоплені файли:** `logic.py`, `puzzle.py`, `tests/test_logic.py`

### Повний вивід Ruff

```text
I001 [*] Import block is un-sorted or un-formatted
  --> logic.py:9:1
   |
 7 |   """
 8 |
 9 | / import json
10 | | import random
11 | | import constants as c
   | |_____________________^
help: Organize imports
   |
10 | import random
11 +
12 | import constants as c
   -
   |

I001 [*] Import block is un-sorted or un-formatted
  --> puzzle.py:9:1
   |
 7 |   """
 8 |
 9 | / from tkinter import Frame, Label, CENTER, messagebox
10 | | import random
11 | | import logic
12 | | import constants as c
   | |_____________________^
help: Organize imports
   |
8  |
   - from tkinter import Frame, Label, CENTER, messagebox
9  | import random
   - import logic
10 + from tkinter import CENTER, Frame, Label, messagebox
11 +
12 | import constants as c
13 + import logic
14 |
   |

PLR1722 Use `sys.exit()` instead of `exit`
   --> puzzle.py:163:13
    |
161 |         # Вихід із гри за клавішею Escape.
162 |         if key == c.KEY_QUIT:
163 |             exit()
    |             ^^^^
164 |
165 |         # Відкат ходу назад відновлює і поле, і рахунок до стану перед ходом.
    |
help: Replace `exit` with `sys.exit()`

SIM117 Use a single `with` statement with multiple contexts instead of nested `with` statements
   --> tests\test_logic.py:209:5
    |
207 |   def test_load_high_score_raises_for_missing_file() -> None:
208 |       """Переконується, що відсутній файл не маскується значенням за замовчуванням."""
209 | /     with patch("builtins.open", side_effect=FileNotFoundError):
210 | |         with pytest.raises(FileNotFoundError):
    | |______________________________________________^
211 |               logic.load_high_score("missing.json")
    |

SIM117 Use a single `with` statement with multiple contexts instead of nested `with` statements
   --> tests\test_logic.py:222:5
    |
220 |   def test_load_high_score_raises_for_corrupted_json() -> None:
221 |       """Перевіряє явну помилку під час читання пошкодженого JSON."""
222 | /     with patch("builtins.open", mock_open(read_data="{broken")):
223 | |         with pytest.raises(json.JSONDecodeError):
    | |_________________________________________________^
224 |               logic.load_high_score("broken.json")
    |

SIM117 [*] Use a single `with` statement with multiple contexts instead of nested `with` statements
   --> tests\test_logic.py:239:5
    |
237 |   def test_load_high_score_rejects_invalid_record(data: str, error: type) -> None:
238 |       """Перевіряє валідацію обов'язкового ключа та значення рекорду."""
239 | /     with patch("builtins.open", mock_open(read_data=data)):
240 | |         with pytest.raises(error):
    | |__________________________________^
241 |               logic.load_high_score("invalid.json")
    |
help: Combine `with` statements
    |
238 |     """Перевіряє валідацію обов'язкового ключа та значення рекорду."""
    -     with patch("builtins.open", mock_open(read_data=data)):
    -         with pytest.raises(error):
    -             logic.load_high_score("invalid.json")
239 +     with patch("builtins.open", mock_open(read_data=data)), pytest.raises(error):
240 +         logic.load_high_score("invalid.json")
    |

Found 6 errors.
[*] 3 fixable with the `--fix` option (1 hidden fix can be enabled with the `--unsafe-fixes` option).
```

### Рекомендації щодо рефакторингу

1. Упорядкувати імпорти за стандартними групами (стандартна бібліотека, сторонні пакети, модулі проєкту); Ruff пропонує виправити обидва блоки `I001`.
2. Замінити вбудований виклик `exit()` на `sys.exit()` і додати `import sys`; це робить завершення програми придатнішим для коду застосунку та тестування.
3. Об'єднати вкладені контекстні менеджери в тестах у єдині `with`-вирази для компактності й відповідності `SIM117`.
4. Щоб такі порушення виявлялися автоматично, додати Ruff до конфігурації проєкту та CI; за потреби форматування імпортів і тестових файлів виконувати `ruff check --fix` після перегляду diff.

Цей звіт фіксує поточні знахідки; аналіз виконаний без автоматичного виправлення файлів.

## Повторна перевірка після рефакторингу

- **Дата:** 2026-10-05
- **Охоплення:** `logic.py`, `puzzle.py`, `constants.py`, `tests/test_logic.py`
- **Результат pytest:** 32 passed in 0.11s
- **Покриття `logic.py`:** 100% (165 statements, 0 missed)
- **Команда lint:** `ruff check .`
- **Результат Ruff:** `All checks passed!` (код завершення 0)
- **Додаткова перевірка:** `python -m py_compile logic.py puzzle.py constants.py tests\test_logic.py` та `git diff --check` пройшли без помилок.

```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: .
plugins: cov-7.1.0
collected 32 items

tests\test_logic.py ................................                     [100%]

=============================== tests coverage ================================
Name       Stmts   Miss  Cover   Missing
----------------------------------------
logic.py     165      0   100%
----------------------------------------
TOTAL        165      0   100%
============================= 32 passed in 0.11s ==============================
```

```text
$ ruff check .
All checks passed!
```

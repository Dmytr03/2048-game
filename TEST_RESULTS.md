============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Dmytro\2048-game
plugins: cov-7.1.0
collected 11 items

tests\test_logic.py ...........                                          [100%]

=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.14.6-final-0 _______________

Name       Stmts   Miss  Cover
------------------------------
logic.py     135     80    41%
------------------------------
TOTAL        135     80    41%
============================= 11 passed in 0.12s ==============================


## Ruff Static Analysis Report

```text
﻿I001 [*] Import block is un-sorted or un-formatted
  --> logic.py:13:1
   |
11 |   # code easily while grading your problem set.
12 |
13 | / import random
14 | | import json
15 | | import os
16 | | import copy
17 | | import constants as c
   | |_____________________^
18 |
19 |   #######
   |
help: Organize imports
   |
12 |
   - import random
13 + import copy
14 | import json
15 | import os
   - import copy
16 + import random
17 +
18 | import constants as c
   |

BLE001 Do not catch blind exception: `Exception`
   --> logic.py:354:12
    |
352 |             json.dump({"high_score": score}, f, indent=4)
353 |         return True
354 |     except Exception as e:
    |            ^^^^^^^^^
355 |         print(f"Error saving high score: {e}")
356 |         return False
    |

I001 [*] Import block is un-sorted or un-formatted
  --> puzzle.py:5:1
   |
 3 |   Handles the graphical user interface, event bindings, and overall game loop using tkinter.
 4 |   """
 5 | / from tkinter import Frame, Label, CENTER
 6 | | import random
 7 | | import logic
 8 | | import constants as c
   | |_____________________^
 9 |
10 |   def gen():
   |
help: Organize imports
   |
4  | """
   - from tkinter import Frame, Label, CENTER
5  | import random
6  + from tkinter import CENTER, Frame, Label
7  +
8  + import constants as c
9  | import logic
   - import constants as c
10 |
11 +
12 | def gen():
   |

BLE001 Do not catch blind exception: `Exception`
  --> puzzle.py:53:16
   |
51 |         try:
52 |             self.high_score = logic.load_high_score()
53 |         except Exception:
   |                ^^^^^^^^^
54 |             self.high_score = 0
   |

PLR1722 Use `sys.exit()` instead of `exit`
   --> puzzle.py:130:31
    |
128 |         key = event.keysym
129 |         print(event)
130 |         if key == c.KEY_QUIT: exit()
    |                               ^^^^
131 |         if key == c.KEY_BACK:
132 |             restored_matrix, success = logic.undo_move(self.history_matrixs)
    |
help: Replace `exit` with `sys.exit()`

I001 [*] Import block is un-sorted or un-formatted
 --> tests\test_logic.py:1:1
  |
1 | / import pytest
2 | | from unittest.mock import patch, mock_open
3 | | import json
4 | | import os
5 | | import sys
  | |__________^
6 |
7 |   # ╨Ф╨╛╨┤╨░╤Ф╨╝╨╛ ╨▒╨░╤В╤М╨║╤Ц╨▓╤Б╤М╨║╤Г ╨┤╨╕╤А╨╡╨║╤В╨╛╤А╤Ц╤О ╨┤╨╛ sys.path ╨┤╨╗╤П ╤Ц╨╝╨┐╨╛╤А╤В╤Г logic.py
  |
help: Organize imports
  |
  - import pytest
  - from unittest.mock import patch, mock_open
1 | import json
2 | import os
3 | import sys
4 + from unittest.mock import mock_open, patch
5 +
6 + import pytest
7 |
  |

I001 [*] Import block is un-sorted or un-formatted
  --> tests\test_logic.py:10:1
   |
 8 | sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 9 |
10 | import logic
   | ^^^^^^^^^^^^
11 |
12 | # ╨д╤Ц╨║╤Б╤В╤Г╤А╨░ ╨┤╨╗╤П ╨┐╨╛╤А╨╛╨╢╨╜╤М╨╛╤Ч ╨╝╨░╤В╤А╨╕╤Ж╤Ц 4x4
   |
help: Organize imports
   |
11 |
12 +
13 | # ╨д╤Ц╨║╤Б╤В╤Г╤А╨░ ╨┤╨╗╤П ╨┐╨╛╤А╨╛╨╢╨╜╤М╨╛╤Ч ╨╝╨░╤В╤А╨╕╤Ж╤Ц 4x4
   |

Found 7 errors.
[*] 4 fixable with the `--fix` option (1 hidden fix can be enabled with the `--unsafe-fixes` option).

```

## Рекомендації щодо рефакторингу

На основі аналізу ruff пропонуються такі покращення якості коду:

1. **Сортування імпортів (I001):**
   Всі файли (`logic.py`, `puzzle.py`, `tests/test_logic.py`) мають невідсортовані імпорти. Бажано застосувати автоматичне сортування за допомогою `ruff --fix` (або `isort`).
2. **Уникнення сліпого перехоплення винятків (BLE001):**
   - В `logic.py` (`save_high_score`) використовується `except Exception as e:`. Варто замінити на більш специфічні винятки (наприклад, `OSError`, `IOError`).
   - В `puzzle.py` при завантаженні рекорду використовується `except Exception:`. Краще перехоплювати лише очікувані `(FileNotFoundError, ValueError, json.JSONDecodeError)`.
3. **Правильне завершення програми (PLR1722):**
   У файлі `puzzle.py` замість вбудованої функції `exit()` (яка призначена для інтерактивної оболонки) слід імпортувати модуль `sys` та використовувати `sys.exit()`.


## Post-Refactoring Results

### Pytest Coverage

```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Dmytro\2048-game
plugins: cov-7.1.0
collected 11 items

tests\test_logic.py ...........                                          [100%]

=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.14.6-final-0 _______________

Name       Stmts   Miss  Cover
------------------------------
logic.py     135     80    41%
------------------------------
TOTAL        135     80    41%
============================= 11 passed in 0.08s ==============================
```

### Ruff Verification

```text
All checks passed!
```

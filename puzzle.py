"""Графічний інтерфейс гри 2048 на базі Tkinter.

Цей модуль відповідає за рендеринг ігрового поля, обробку клавіатурних
команд користувача та відображення станів перемоги або поразки. Вся логіка
зсуву плиток знаходиться в модулі logic.py, а тут реалізована лише візуальна
частина та зв'язок інтерфейсу з логічним ядром гри.
"""

from tkinter import Frame, Label, CENTER, messagebox
import random
import logic
import constants as c


def gen():
    """Повертає випадковий індекс комірки для розміщення нової плитки.

    Повернене значення знаходиться в межах від 0 до GRID_LEN - 1 і використовується
    для вибору випадкового рядка або стовпця на ігровому полі.

    Returns:
        int: Випадкове ціле число в межах розміру матриці.
    """
    return random.randint(0, c.GRID_LEN - 1)


class GameGrid(Frame):
    """Основний клас, який керує візуальним представленням гри 2048.

    Клас успадковує tkinter.Frame, створює сітку комірок, прив'язує клавіші
    управління до відповідних функцій логіки, оновлює відображення матриці та
    показує повідомлення про перемогу або програш.
    """

    def __init__(self):
        """Ініціалізує ігрове вікно, зв'язує події клавіатури та запускає цикл Tkinter.

        Під час створення об'єкта формуються словник команд, підготовлюється поле,
        створюється початкова матриця, і запускається головний цикл обробки подій.
        """
        Frame.__init__(self)

        self.grid()
        self.master.title('2048')
        self.master.bind("<Key>", self.key_down)

        # Відповідність між клавішами та функціями переміщення плиток.
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

        self.grid_cells = []
        self.init_grid()
        self.matrix = logic.new_game(c.GRID_LEN)
        self.score = 0
        try:
            self.high_score = logic.load_high_score()
        except FileNotFoundError:
            # Відсутній файл рекорду є звичайною ситуацією під час першого запуску.
            self.high_score = 0
        except (OSError, TypeError, ValueError) as error:
            # Зберігаємо можливість грати, але явно повідомляємо про непрочитаний рекорд.
            self.high_score = 0
            messagebox.showwarning(
                "High score",
                f"Не вдалося завантажити рекорд: {error}"
            )
        self.history_matrixs = []
        self.history_scores = []
        self.master.title(
            f"2048 | Score: {self.score} | Best: {self.high_score}"
        )
        self.update_grid_cells()

        self.mainloop()

    def init_grid(self):
        """Створює візуальну сітку комірок для відображення польових плиток.

        Метод створює фон ігрового поля, а потім для кожної клітинки формує
        окремий контейнер із міткою, в якій пізніше буде відображатися числове
        значення плитки. Кожен елемент зберігається у self.grid_cells для подальшого
        оновлення.
        """
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
                    height=2)
                t.grid()
                grid_row.append(t)
            self.grid_cells.append(grid_row)

    def update_grid_cells(self):
        """Оновлює графічне представлення матриці гри на екрані.

        Метод проходить по всіх клітинках поля, відображає значення чисел або
        порожній фон, а також забарвлює плитки відповідно до їхнього значення.
        Після перетворення викликається update_idletasks() для коректного оновлення
        інтерфейсу.
        """
        for i in range(c.GRID_LEN):
            for j in range(c.GRID_LEN):
                new_number = self.matrix[i][j]
                if new_number == 0:
                    self.grid_cells[i][j].configure(text="", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.grid_cells[i][j].configure(
                        text=str(new_number),
                        bg=c.BACKGROUND_COLOR_DICT[new_number],
                        fg=c.CELL_COLOR_DICT[new_number]
                    )
        self.update_idletasks()

    def key_down(self, event):
        """Обробляє натискання клавіатури та запускає відповідний хід гри.

        Значення event.keysym використовується для визначення призначеної команди:
        вихід з гри, відкат ходу назад або переміщення плиток у одному із напрямків.
        Якщо хід завершився успішно, на поле додається нова плитка, відбувається
        збереження історії та перевірка стану перемоги/поразки.

        Args:
            event: Об'єкт події клавіатури Tkinter.
        """
        key = event.keysym
        print(event)

        # Вихід із гри за клавішею Escape.
        if key == c.KEY_QUIT:
            exit()

        # Відкат ходу назад відновлює і поле, і рахунок до стану перед ходом.
        if key == c.KEY_BACK:
            previous_matrix, undone = logic.undo_move(self.history_matrixs)
            if undone:
                self.matrix = previous_matrix
                self.score = self.history_scores.pop()
                self.master.title(
                    f"2048 | Score: {self.score} | Best: {self.high_score}"
                )
                self.update_grid_cells()
                print('back on step total step:', len(self.history_matrixs))
        elif key in self.commands:
            previous_matrix = [row[:] for row in self.matrix]
            self.matrix, done, points = self.commands[key](
                self.matrix,
                with_score=True
            )
            if done:
                self.history_matrixs.append(previous_matrix)
                self.history_scores.append(self.score)
                self.score += points

                if self.score > self.high_score:
                    try:
                        if logic.save_high_score(self.score):
                            self.high_score = self.score
                    except (OSError, TypeError, ValueError) as error:
                        messagebox.showwarning(
                            "High score",
                            f"Не вдалося зберегти рекорд: {error}"
                        )

                self.master.title(
                    f"2048 | Score: {self.score} | Best: {self.high_score}"
                )
                self.matrix = logic.add_two(self.matrix)
                self.update_grid_cells()

                # Відображення повідомлення про перемогу, якщо плитка 2048 вже створена.
                if logic.game_state(self.matrix) == 'win':
                    self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                    self.grid_cells[1][2].configure(text="Win!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)

                # Відображення повідомлення про поразку, якщо більше немає доступних ходів.
                if logic.game_state(self.matrix) == 'lose':
                    self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                    self.grid_cells[1][2].configure(text="Lose!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)

    def generate_next(self):
        """Генерує нову плитку 2 у випадковій порожній комірці.

        Метод перебирає випадкові координати, доки не знайде вільну клітинку, а
        потім встановлює в ній значення 2. Ця функція є альтернативним способом
        генерації нової плитки, який може використовуватися в різних сценаріях.
        """
        index = (gen(), gen())
        while self.matrix[index[0]][index[1]] != 0:
            index = (gen(), gen())
        self.matrix[index[0]][index[1]] = 2


# Ініціалізація графічного вікна гри в момент імпорту модуля.
game_grid = GameGrid()
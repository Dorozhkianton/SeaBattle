import random

# Исключения
class BoardException(Exception):
    # Базовый класс исключений
    pass

class BoardOutException(BoardException):
    # Когда выстрел вне доски
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы игрового поля"

class BoardUsedException(BoardException):
    # Когда выстрел по уже подстреляной ячейке
    def __str__(self):
        return "Эта клетка уже подстреляна"

class BoardWrongShipException(BoardException):
    # Исключение для неправильного размещения корабля
    pass

#  класс Dot — класс ячеек (точек) на поле с параметрами x и y
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        # проверяем совпадение двух ячеек
        return self.x == other.x and self.y == other.y

# Класс корабля
class Ship:
    def __init__(self, bow, length, orientation):
        self.bow = bow  # Нос корабля
        self.length = length  # Длина корабля
        self.orientation = orientation  # Ориентация, вертикальная или горизонтальная
        self.lives = length  # Жизни корабля равны его длине

    @property
    def dots(self):
        # метод dots, который возвращает список всех ячеек корабля.
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orientation == 0:  # Горизонтальная ориентация
                cur_x += i
            elif self.orientation == 1:  # Вертикальная
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

# Класс игрового поля
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size  # Размер поля
        self.hid = hid  # Если True то корабли на поле будут скрыты от игрока
        self.count = 0  # Число потопленных кораблей, чтоб определить победителя
        self.field = [["O"] * size for _ in range(size)]  # Игровое поле
        self.busy = []  # Список занятых (подбитых) ячеек
        self.ships = []  # Список кораблей на поле

    def add_ship(self, ship):
        # Добавляем корабли на игровое поле
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()  # Исключение если корабль добавили неправильно
        for d in ship.dots:
            self.field[d.x][d.y] = "■"  # Помечаем корабли квадратиком
            self.busy.append(d)  # Отмечаем ячейки как занятые

        self.ships.append(ship)  # Добавляем корабль в список
        self.contour(ship)  # Обводим контуром из ячеек

    def contour(self, ship, verb=False):
        # Обводка контуром из ячеек
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."  # Контурные ячейки вокруг кораблей отмечаем точками
                    self.busy.append(cur)  # Эти же ячейки так же помечаем как занятые

    def __str__(self):
        # Оформляем поле, разделяем ячейки палочками, добавляем сверху и слева кооринаты
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")  # Прячем корабли ИИ
        return res

    def out(self, d):
        # Метод out, который для точки (объекта класса Dot) возвращает True, если точка выходит за пределы поля
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        # Делаем выстрел по полю
        if self.out(d):
            raise BoardOutException()  # Исключение, если выстрел вне поля

        if d in self.busy:
            raise BoardUsedException()  # Исключение, если выстрел по уже подбитой ячейке

        self.busy.append(d)  # После выстрела помечаем ячейку как подбитую

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1  # Уменьшаем количество жизней корабля
                self.field[d.x][d.y] = "X"  # Помечаем попадание крестиком
                if ship.lives == 0:
                    self.count += 1  # Повышаем счет потопленных кораблей
                    self.contour(ship, verb=True)  # Обводим потопленный корабль контуром
                    print("Корабль потоплен!")
                    return True
                else:
                    print("Корабль подбит!")
                    return True

        self.field[d.x][d.y] = "T"  # Промах помечаем как Т
        print("Промах!")
        return False

    def begin(self):
        # обнуляем список занятых ячеек
        self.busy = []

# Классы Игроков человека и ИИ
class Player:
    def __init__(self, board, enemy):
        self.board = board  # Свое поле
        self.enemy = enemy  # Поле врага

    def ask(self):
        # метод, который «спрашивает» игрока, в какую клетку он делает выстрел.
        # Пока мы делаем общий для AI и пользователя класс, этот метод мы описать не можем.
        # Оставим этот метод пустым. Тем самым обозначим, что потомки должны реализовать этот метод.
        raise NotImplementedError()

    def move(self):
        # Ход игрока
        while True:
            try:
                target = self.ask()  # Спрашиваем цель
                repeat = self.enemy.shot(target)  # Делаем выстрел
                return repeat  # Возвращает True если дается ещё ход после попадания
            except BoardException as e:
                print(e)  # Печатаем исключение

# Класс ИИ
class AI(Player):
    def ask(self):
        # ИИ делает выстрел с помощью гсч
        d = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

# Класс человека
class User(Player):
    def ask(self):
        # Получаем координаты выстрела от игрока
        while True:
            coords = input("Ваш ход: ").split()
            if len(coords) != 2:
                print("Введите 2 координаты через пробел!")
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите 2 числа от 1 до 6!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)  # У нас координаты не от 1 до 6 а от 0 до 5
                                      # но игроку про это знать необязательно, поэтому просто конвертируем

# Класс игры
class Game:
    def __init__(self, size=6):
        self.size = size  # Размер Поля
        pl = self.random_board()  # Поле Человека
        co = self.random_board()  # Поле ИИ
        co.hid = True  # Спрятать корабли ИИ

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        # Генерируем поле
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        # Ставим случайно корабли
        board = Board(size=self.size)
        attempts = 0
        for length in [3, 2, 2, 1, 1, 1, 1]:
            while True:
                attempts += 1
                if attempts > 4000:
                    return None  # Если мы превысили количество попыток поставить корабли, генерируем заново
                ship = Ship(Dot(random.randint(0, self.size), random.randint(0, self.size)), length, random.randint(0, 1))
                try:
                    board.add_ship(ship)  # Пытаемся поставить корабль
                    break
                except BoardWrongShipException:
                    pass
        board.begin()  # Обнуляем список занятых ячеек
        return board

    def greet(self):
        # Приветственное сообщение с инструкцией
        print(" Игра Морской Бой")
        print("-------------------")
        print(" Введите координаты клетки на поле боя по которой вы хотите выстрелить")
        print(" в формате X и Y через пробел, допустимые значения от 1 до 6")

    def loop(self):
        # Главный игровой цикл
        num = 0
        while True:
            print("-" * 20)
            print("Ваше поле:")
            print(self.us.board)  # Печатаем поле человека
            print("-" * 20)
            print("Поле компьютера:")
            print(self.ai.board)  # Печатаем поле ИИ
            if num % 2 == 0:
                print("-" * 20)
                print("Ход игрока!")
                repeat = self.us.move()  # Ход человека
            else:
                print("-" * 20)
                print("Ход компьютера!")
                repeat = self.ai.move()  # Ход ИИ
            if repeat:
                num -= 1  # Если попадание - повторяем

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Вы победили!")
                break  # Условие победы человека

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер победил!")
                break  # Условие победы компьютера
            num += 1

    def start(self): # Начинало игры - приветствие и основной цикл
        self.greet()
        self.loop()

# Начинаем игру
g = Game()
g.start()

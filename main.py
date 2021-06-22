import pygame
import time
import random
import os.path
from pygame.locals import *

SIZE = 36
INCREASED_TIME = 0


class Food:

    def __init__(self, screen):
        self.pizza = pygame.image.load('res/pizza.jpg').convert()
        self.screen = screen
        self.x = SIZE * 3
        self.y = SIZE * 3

    def draw(self):
        self.screen.blit(self.pizza, (self.x, self.y))
        pygame.display.flip()

    def move(self):
        self.x = random.randint(1, 13) * SIZE
        self.y = random.randint(1, 13) * SIZE


class Snake:
    def __init__(self, screen, length):
        self.length = length
        self.screen = screen
        self.snake_block = pygame.image.load('res/snake_block.jpg').convert()
        self.x = [SIZE] * length
        self.y = [-SIZE] * length
        self.direction = 'down'
        self.first_move = True

    def increase_length(self):
        self.length += 1
        self.x.append(-1)
        self.y.append(-1)

    def draw(self):
        self.screen.fill((195, 255, 69))
        pygame.draw.rect(self.screen, (194, 88, 64), (0, 0, 540, 540), 60)
        pygame.draw.rect(self.screen, (195, 255, 69), (31, 0, 48, 32))
        for i in range(self.length):
            self.screen.blit(self.snake_block, (self.x[i], self.y[i]))
        pygame.display.flip()

    def move_up(self):
        self.direction = 'up'

    def move_down(self):
        self.direction = 'down'

    def move_left(self):
        self.direction = 'left'

    def move_right(self):
        self.direction = 'right'

    def walk(self):
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]
        if self.direction == 'up':
            self.y[0] -= SIZE
        if self.direction == 'down':
            self.y[0] += SIZE
        if self.direction == 'left':
            self.x[0] -= SIZE
        if self.direction == 'right':
            self.x[0] += SIZE

        self.draw()


def collision(x1, y1, x2, y2):
    if x1 == x2 and y1 == y2:
        return True
    return False


def background_music():
    pygame.mixer.music.load('res/background.mp3')
    pygame.mixer.music.play()


def sound(sound_name):
    snd = pygame.mixer.Sound(f'res/{sound_name}.mp3')
    pygame.mixer.Sound.play(snd)


# метод для вывода текста на экран
def write_msg(surface, font_size, msg, color, coordinates):
    font = pygame.font.SysFont('arial', font_size)
    line = font.render(msg, True, color)
    surface.blit(line, coordinates)


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        background_music()
        self.surface = pygame.display.set_mode((540, 540))
        self.surface.fill((195, 255, 69))
        self.snake = Snake(self.surface, 1)
        self.snake.draw()
        self.food = Food(self.surface)
        self.food.draw()
        self.increased_time = 0

    # метод для определения столкновения с забором
    def fence(self):
        if ((self.snake.x[0] < 31 or self.snake.x[0] > 500 or self.snake.y[0] < 31
             or self.snake.y[0] > 500) and self.snake.first_move is not True):
            return True
        return False

    # метод для определения совпало ли новое расположение еды со змеёй
    def food_is_in_snake(self):
        for i in range(self.snake.length):
            if self.snake.x[i] == self.food.x and self.snake.y[i] == self.food.y:
                return True
        return False

    def play(self):
        self.snake.walk()
        self.food.draw()
        self.score()
        pygame.display.flip()

        # проверка добралась ли змея до еды
        if collision(self.snake.x[0], self.snake.y[0], self.food.x, self.food.y):
            sound('eat')
            if self.increased_time < 0.15:
                self.increased_time += 0.006
            self.food.move()
            while self.food_is_in_snake():
                self.food.move()
            self.snake.increase_length()

        # проверка на столкновение головы змеи с телом
        for i in range(3, self.snake.length):
            if collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                sound('crush')
                raise Exception('Game over!')

        # проверка на столкновение змеи с забором
        if self.fence():
            raise Exception('Hit the fence!')

    # метод для вывода информации об окончании игры на экран
    def show_game_over(self, last_record):
        pygame.mixer.music.pause()
        time.sleep(0.8)
        self.surface.fill((195, 255, 69))
        write_msg(self.surface, 35, 'Game over', (186, 17, 17), (195, 130))
        write_msg(self.surface, 25, f'Last record: {last_record}', (209, 44, 44), (207, 280))
        write_msg(self.surface, 25, f'Your score: {self.snake.length}', (209, 44, 44), (210, 330))
        write_msg(self.surface, 15, 'to restart press SPACE, to exit press ESCAPE', (0, 0, 0), (290, 500))
        # вывод поздравлений, если установлен новый рекорд
        if self.snake.length == last_record:
            write_msg(self.surface, 35, 'Congratulations!', (186, 17, 17), (170, 220))
        pygame.display.flip()
        sound('end')

    # метод для вывода счёта на экран
    def score(self):
        write_msg(self.surface, 22, f'Score: {self.snake.length}', (255, 255, 255), (420, 515))

    # метод для созлания новой змеи длиной один и обнуления переменной отвечающей за ускорение движения змеи
    def reset(self):
        self.snake = Snake(self.surface, 1)
        self.food = Food(self.surface)
        self.increased_time = 0

    def run(self):
        # проверка на существование предыдущего рекорда
        if os.path.isfile('D:/SnakeGame/RecordFile.txt'):
            record_file = open('RecordFile.txt', 'r')
            record = int(record_file.readline())
            record_file.close()
        else:
            record = 0

        running = True
        pause = False
        while running:
            # цикл для обработки событий из очереди
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    self.snake.first_move = False
                    if event.key == K_SPACE:
                        self.snake.first_move = True
                        pygame.mixer.music.play()
                        # продолжение игры
                        pause = False
                    elif event.key == K_ESCAPE:
                        # выход из цикла
                        running = False
                    elif event.key == K_UP and self.snake.direction != 'down':
                        self.snake.move_up()
                    elif event.key == K_DOWN and self.snake.direction != 'up':
                        self.snake.move_down()
                    elif event.key == K_LEFT and self.snake.direction != 'right':
                        self.snake.move_left()
                    elif event.key == K_RIGHT and self.snake.direction != 'left':
                        self.snake.move_right()
                elif event.type == QUIT:
                    # выход из цикла
                    running = False
            try:
                if not pause:
                    self.play()
            except Exception:
                # прекращение игры
                pause = True
                # запись рекорда в перменную
                record = max(self.snake.length, record)
                # запись рекорда в файл
                record_file = open('RecordFile.txt', 'w+')
                record_file.write(str(record))
                record_file.close()
                self.show_game_over(record)
                self.reset()
            # увеличение скорости передвижения змеи по полю
            time.sleep(0.2 - self.increased_time)


# метод для вывода стартового меню
def start_menu():
    pygame.init()
    surface = pygame.display.set_mode((540, 540))
    surface.fill((0, 0, 0))
    white = (255, 255, 255)
    write_msg(surface, 50, 'SNAKE', (195, 255, 69), (195, 100))
    write_msg(surface, 20, 'Use the arrows on your keyboard to move and eat pizza.', white, (70, 200))
    write_msg(surface, 20, 'You will lose if you hit the fence or yourself', white, (110, 240))
    write_msg(surface, 15, 'press ENTER to start', white, (210, 500))
    pygame.display.flip()


if __name__ == '__main__':
    start_menu()
    start = True
    while start:
        for event1 in pygame.event.get():
            if event1.type == KEYDOWN:
                # игра начинается если нажат enter
                if event1.key == K_RETURN:
                    game = Game()
                    game.run()
                    start = False
            # программа завершается, если нажат крестик
            elif event1.type == QUIT:
                start = False

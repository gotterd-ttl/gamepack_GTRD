import pygame  # Импортируем библиотеку Pygame для игрового программирования.
import random  # Импортируем библиотеку random для генерации случайных чисел.

# Инициализация Pygame
pygame.init()  # Запускаем все модули Pygame.

# Устанавливаем размеры окна
WIDTH, HEIGHT = 800, 600  # Задаем ширину и высоту окна.

# Создаем окно для отображения игры
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Создаем окно с заданными размерами.

# Определяем цвет черного
BLACK = (0, 0, 0)  # Цвет черного в RGB формате.


# Функция для отображения текста на экране
def draw_text(text, size, color, surface, x, y):
    font = pygame.font.Font(None, size)  # Создаем объект шрифта с заданным размером.
    text_surface = font.render(text, True, color)  # Рендерим текст в поверхность с заданным цветом.
    text_rect = text_surface.get_rect(center=(x, y))  # Получаем прямоугольник текста и центрируем его.
    surface.blit(text_surface, text_rect)  # Отображаем текст на заданной поверхности.


def game_one():
    # Устанавливаем заголовок окна игры
    pygame.display.set_caption("Платформер с врагами")

    # Класс для анимированного спрайта
    class AnimatedSprite(pygame.sprite.Sprite):
        def __init__(self, sprite_sheet, cols, rows, fps):
            super().__init__()  # Вызов конструктора базового класса Sprite
            self.frames = []  # Список кадров для анимации
            self.fps = fps  # Частота кадров (количество кадров в секунду)
            self.current_frame = 0  # Текущий кадр
            self.last_update = pygame.time.get_ticks()  # Последнее время обновления кадров
            width = sprite_sheet.get_width() // cols  # Ширина одного кадра
            height = sprite_sheet.get_height() // rows  # Высота одного кадра

            # Извлекаем кадры из спрайт-листа
            for row in range(rows):
                for col in range(cols):
                    frame = sprite_sheet.subsurface((col * width, row * height, width, height))  # Вырезаем кадр
                    self.frames.append(frame)  # Добавляем кадр в список
            self.image = self.frames[self.current_frame]  # Устанавливаем изображение текущего кадра
            self.rect = self.image.get_rect()  # Получаем прямоугольник изображения для позиционирования

        def update(self):
            # Обновление анимации
            now = pygame.time.get_ticks()  # Получаем текущее время
            if now - self.last_update > 1000 / self.fps:  # Проверяем, пора ли обновить кадр
                self.last_update = now  # Обновляем время последнего обновления
                self.current_frame = (self.current_frame + 1) % len(self.frames)  # Переход к следующему кадру
                self.image = self.frames[self.current_frame]  # Обновляем текущее изображение

    # Класс для игрока, наследующий анимированный спрайт
    class Player(AnimatedSprite):
        def __init__(self):
            sprite_sheet = pygame.image.load("LIST_Player.png").convert_alpha()  # Загружаем спрайт-лист игрока
            super().__init__(sprite_sheet, 4, 2, 10)  # 4 столбца, 2 строки, 10 fps
            self.rect.center = (WIDTH // 2, HEIGHT - 60)  # Устанавливаем начальную позицию игрока
            self.speed = 5  # Скорость перемещения игрока
            self.jump_strength = 10  # Сила прыжка
            self.is_jumping = False  # Флаг для проверки, прыгнет ли игрок
            self.jump_count = self.jump_strength  # Счетчик прыжка, используется для определения высоты прыжка

        def update(self):
            super().update()  # Обновляем анимацию спрайта
            previous_y = self.rect.y  # Сохраняем предыдущее положение по Y для обработки прыжка
            keys = pygame.key.get_pressed()  # Получаем состояние клавиш

            # Движение влево
            if keys[pygame.K_a] and self.rect.left > 0:
                self.rect.x -= self.speed  # Сдвигаем игрока влево
            # Движение вправо
            if keys[pygame.K_d] and self.rect.right < WIDTH:
                self.rect.x += self.speed  # Сдвигаем игрока вправо

            # Проверка на прыжок
            if not self.is_jumping:
                if keys[pygame.K_SPACE]:  # Если не прыгаем и нажата клавиша пробела
                    self.is_jumping = True  # Начинаем прыжок
            else:
                # Обработка прыжка
                if self.jump_count >= -self.jump_strength:
                    neg = 1 if self.jump_count >= 0 else -1  # Определяем направление прыжка
                    self.rect.y -= (self.jump_count ** 2) * 0.5 * neg  # Двигаем игрока по Y
                    self.jump_count -= 1  # Уменьшаем счетчик прыжка
                else:
                    # Завершение прыжка
                    self.is_jumping = False  # Дело завершено
                    self.jump_count = self.jump_strength  # Сброс счетчика прыжка

            # Проверка на столкновение с платформами
            if pygame.sprite.spritecollideany(self, platforms):
                self.rect.y = previous_y  # Возвращаем Y позицию, если произошло столкновение
                for platform in platforms:
                    if self.rect.colliderect(platform.rect):  # Проверяем столкновение с каждой платформой
                        if previous_y + self.rect.height <= platform.rect.top:  # Если игрок находится над платформой
                            self.rect.bottom = platform.rect.top  # Устанавливаем игрока на платформу
                            self.is_jumping = False  # Нельзя прыгнуть снова
                            self.jump_count = self.jump_strength  # Сброс счетчика прыжка
                            break
            else:
                # Если игрок не на платформе, падает вниз
                self.rect.y += 5

            # Проверка на выход за пределы экрана
            if self.rect.bottom >= HEIGHT:
                global running  # Используем глобальную переменную для окончания игры
                running = False  # Устанавливаем флаг для выхода из игры

    # Класс для платформ
    class Platform(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()  # Вызов конструктора базового класса Sprite
            self.image = pygame.Surface((140, 10))  # Создаем поверхность платформы с заданными размерами
            self.image.fill((255, 0, 0))  # Закрашиваем платформу в красный цвет
            self.rect = self.image.get_rect(
                topleft=(x, y))  # Устанавливаем прямоугольник платформы согласно заданным координатам

    class Enemy(AnimatedSprite):
        # Конструктор класса Enemy, который наследует от AnimatedSprite
        def __init__(self):
            # Загружаем спрайт-лист для врагов из изображения
            sprite_sheet = pygame.image.load("LIST_Enemy.png").convert_alpha()
            # Инициализируем родительский класс с параметрами спрайта
            super().__init__(sprite_sheet, 4, 2, 10)
            # Устанавливаем случайное начальное положение врага, появляющегося сверху экрана
            self.rect.center = (random.randint(0, WIDTH), -50)
            # Устанавливаем скорость врага в случайном диапазоне между 3 и 5
            self.speed = random.randint(3, 5)

        # Метод обновления состояния врага
        def update(self):
            super().update()  # Обновление состояния спрайта
            self.rect.y += self.speed  # Перемещение врага вниз по экрану
            # Если враг выходит за пределы экрана, он удаляется
            if self.rect.top > HEIGHT:
                self.kill()

    # Создаем группы спрайтов для управления объектами
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    # Создаем экземпляр игрока
    player = Player()
    # Добавляем игрока в общую группу спрайтов
    all_sprites.add(player)

    # Устанавливаем границу смерти, за которую игрок не должен выходить
    DEATH_ZONE = HEIGHT - 50

    # Позиция платформы, используем для их создания
    platform_y = 400
    # Список позиций для создания платформ
    platform_positions = [
        (100, platform_y),
        (WIDTH // 2 - 50, platform_y),
        (600, platform_y)
    ]

    # Создаем платформы на основании заданных позиций
    for pos in platform_positions:
        platform = Platform(*pos)  # Разворачиваем кортеж в аргументы для Platform
        platforms.add(platform)  # Добавляем платформу в группу платформ
        all_sprites.add(platform)  # Добавляем платформу в общую группу спрайтов

    # Позиционируем игрока на первой платформе
    player.rect.topleft = (platform_positions[0][0] + 25, platform_positions[0][1] - player.rect.height)
    score = 0  # Инициализация счета игрока
    running = True  # Флаг, определяющий, продолжается ли игра

    # Основной игровой цикл
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Если игрок закрыл окно
                running = False  # Завершаем игру

        all_sprites.update()  # Обновляем состояние всех спрайтов

        # Проверяем, находится ли игрок на платформе
        if pygame.sprite.spritecollideany(player, platforms):
            player.rect.y = player.rect.y  # Фиксация позиции игрока, если он на платформе
        else:
            player.rect.y += 5  # Если игрок не на платформе, он падает вниз

        # Случайное создание врагов
        if random.random() < 0.03:  # 3% шанс появления нового врага
            enemy = Enemy()  # Создаем нового врага
            all_sprites.add(enemy)  # Добавляем врага в общую группу спрайтов
            enemies.add(enemy)  # Добавляем врага в группу врагов

        # Проверка на столкновение игрока с врагами
        if pygame.sprite.spritecollideany(player, enemies):
            running = False  # Если произошло столкновение, завершаем игру

        # Удаляем врагов, которые вышли за пределы экрана
        for enemy in enemies:
            if enemy.rect.top > HEIGHT:
                enemy.kill()  # Удаляем врага
                score += 1  # Увеличиваем счет за уничтоженного врага

        # Проверяем, не вышел ли игрок за зону смерти
        if player.rect.bottom > DEATH_ZONE:
            running = False  # Завершаем игру, если он вышел за границу

        # Повторная проверка на уничтожение врагов, покинувших зону смерти
        for enemy in enemies:
            if enemy.rect.bottom > DEATH_ZONE:
                enemy.kill()  # Удаляем врага
                score += 1  # Увеличиваем счет

        # Рисуем всё на экран
        screen.fill(BLACK)  # Очистка экрана черным цветом
        all_sprites.draw(screen)  # Отрисовка всех спрайтов на экране

        # Отображение счета игрока
        font = pygame.font.Font(None, 36)  # Создаем шрифт
        text_surface = font.render(f"Score: {score}", True, (255, 255, 255))  # Рендер текста
        screen.blit(text_surface, (10, 10))  # Вывод текста на экран в заданной позиции

        pygame.display.flip()  # Обновление экрана
        pygame.time.delay(30)  # Задержка для управления частотой обновления

    pygame.quit()  # Завершение Pygame


def game_two():
    pygame.display.set_caption("Анимированный шутер")  # Устанавливаем заголовок окна игры

    class AnimatedSprite(pygame.sprite.Sprite):
        def __init__(self, sprite_sheet, cols, rows, fps):
            super().__init__()  # Инициализируем базовый класс Sprite
            self.frames = []  # Список для хранения кадров анимации
            self.fps = fps  # Кадры в секунду
            self.current_frame = 0  # Индекс текущего кадра
            self.last_update = pygame.time.get_ticks()  # Время последнего обновления
            width = sprite_sheet.get_width() // cols  # Ширина одного кадра
            height = sprite_sheet.get_height() // rows  # Высота одного кадра

            # Извлечение кадров из спрайт-листа
            for row in range(rows):
                for col in range(cols):
                    frame = sprite_sheet.subsurface((col * width, row * height, width, height))
                    self.frames.append(frame)  # Добавляем кадр в список
            self.image = self.frames[self.current_frame]  # Устанавливаем начальное изображение
            self.rect = self.image.get_rect()  # Получаем прямоугольник спрайта для дальнейшей работы с ним

        def update(self):
            now = pygame.time.get_ticks()  # Получаем текущее время
            if now - self.last_update > 1000 / self.fps:  # Если прошло достаточно времени для обновления кадра
                self.last_update = now  # Обновляем последнее время
                self.current_frame = (self.current_frame + 1) % len(self.frames)  # Переход к следующему кадру
                self.image = self.frames[self.current_frame]  # Устанавливаем следующий кадр как текущее изображение

    class Player(AnimatedSprite):
        def __init__(self):
            sprite_sheet = pygame.image.load("LIST_Player.png").convert_alpha()  # Загружаем спрайт для игрока
            super().__init__(sprite_sheet, 4, 2, 10)  # Инициализируем AnimatedSprite с параметрами
            self.rect.center = (WIDTH // 2, HEIGHT // 1.5)  # Устанавливаем начальную позицию игрока
            self.speed = 5  # Устанавливаем скорость движения игрока
            self.last_shot_time = 0  # Время последнего выстрела
            self.shoot_delay = 1000  # Задержка между выстрелами в миллисекундах

        def update(self):
            super().update()  # Обновляем анимацию игрока
            keys = pygame.key.get_pressed()  # Получаем состояние клавиш

            # Управление движением игрока
            if keys[pygame.K_a] and self.rect.left > 0:
                self.rect.x -= self.speed  # Движение влево
            if keys[pygame.K_d] and self.rect.right < WIDTH:
                self.rect.x += self.speed  # Движение вправо
            if keys[pygame.K_w] and self.rect.top > 0:
                self.rect.y -= self.speed  # Движение вверх
            if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
                self.rect.y += self.speed  # Движение вниз

    class Enemy(AnimatedSprite):
        def __init__(self):
            sprite_sheet = pygame.image.load("LIST_Enemy.png").convert_alpha()  # Загружаем спрайт для врага
            super().__init__(sprite_sheet, 4, 2, 10)  # Инициализируем AnimatedSprite с параметрами
            self.rect.x = random.randint(0, WIDTH)  # Устанавливаем случайное начальное положение по оси X
            self.rect.y = random.randint(-100,
                                         -40)  # Устанавливаем случайное начальное положение по оси Y (вверху экрана)
            self.speed = random.randint(4, 7)  # Устанавливаем скорость врага

        def update(self):
            self.rect.y += self.speed  # Перемещаем врага вниз по экрану
            if self.rect.top > HEIGHT:  # Если враг вышел за пределы экрана
                self.kill()  # Удаляем врага

    class Bullet(AnimatedSprite):
        def __init__(self, pos):
            sprite_sheet = pygame.image.load("LIST_BULLET.png").convert_alpha()  # Загружаем спрайт для пули
            original_width = sprite_sheet.get_width()  # Получаем оригинальную ширину спрайта
            original_height = sprite_sheet.get_height()  # Получаем оригинальную высоту спрайта
            new_width = int(original_width * 0.3)  # Устанавливаем новую ширину пули
            new_height = int(original_height * 0.3)  # Устанавливаем новую высоту пули
            scaled_sprite = pygame.transform.scale(sprite_sheet, (new_width, new_height))  # Масштабируем спрайт
            super().__init__(scaled_sprite, 3, 1, 10)  # Инициализируем AnimatedSprite с параметрами пули
            self.rect.center = pos  # Устанавливаем позицию пули в момент создания
            self.speed = -10  # Устанавливаем скорость пули (движение вверх)

        def update(self):
            super().update()  # Обновляем анимацию пули
            self.rect.y += self.speed  # Перемещаем пулю вверх по экрану
            if self.rect.bottom < 0:  # Если пуля выходит за пределы верхней части экрана
                self.kill()  # Удаляем пулю

    # Создаем группы спрайтов для управления различными элементами игры
    all_sprites = pygame.sprite.Group()  # Общая группа всех спрайтов
    enemies = pygame.sprite.Group()  # Группа врагов
    bullets = pygame.sprite.Group()  # Группа пуль
    player = Player()  # Создаем игрока
    all_sprites.add(player)  # Добавляем игрока в общую группу спрайтов
    font = pygame.font.Font(None, 36)  # Создаем шрифт для отображения счета
    score = 0  # Начальный счет игрока
    MAX_ENEMIES = 10  # Максимальное количество врагов на экране

    running = True  # Флаг, показывающий, продолжается ли игра
    while running:
        for event in pygame.event.get():  # Обработка событий
            if event.type == pygame.QUIT:  # Если нажата кнопка закрытия окна
                running = False  # Завершаем игру
            elif event.type == pygame.KEYDOWN:  # Если нажата клавиша
                current_time = pygame.time.get_ticks()  # Получаем текущее время
                if event.key == pygame.K_SPACE:  # Если нажата пробел
                    if current_time - player.last_shot_time > player.shoot_delay:  # Проверка задержки между выстрелами
                        bullet = Bullet(player.rect.center)  # Создаем пулю из позиции игрока
                        all_sprites.add(bullet)  # Добавляем пулю в общую группу спрайтов
                        bullets.add(bullet)  # Добавляем пулю в группу пуль
                        player.last_shot_time = current_time  # Обновляем время последнего выстрела

        all_sprites.update()  # Обновляем состояние всех спрайтов

        # Проверка на столкновение между игроком и врагами
        if pygame.sprite.spritecollide(player, enemies, False):
            running = False  # Завершаем игру, если произошло столкновение

        # Проверка на столкновение между пулями и врагами
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)  # Удаляем побитых врагов и пули
        score += len(hits)  # Увеличиваем счет на количество уничтоженных врагов

        # Управление количеством врагов на экране
        if len(enemies) < MAX_ENEMIES:
            if random.random() < 0.2:  # 20% шанс появления нового врага за кадр
                enemy = Enemy()  # Создаем нового врага
                all_sprites.add(enemy)  # Добавляем врага в общую группу спрайтов
                enemies.add(enemy)  # Добавляем врага в группу врагов

        screen.fill(BLACK)  # Очищаем экран черным цветом
        all_sprites.draw(screen)  # Отрисовываем все спрайты на экране
        score_text = font.render(f"Счёт: {score}", True, (255, 255, 255))  # Рендерим текст с текущим счетом
        screen.blit(score_text, (10, 10))  # Выводим текст на экран в заданной позиции
        pygame.display.flip()  # Обновляем экран
        pygame.time.delay(30)  # Задержка для управления частотой обновления экрана

    pygame.quit()  # Завершение работы Pygame


def game_three():
    pygame.display.set_caption("Сбор звёздочек")  # Установка заголовка окна игры

    class AnimatedSprite(pygame.sprite.Sprite):
        def __init__(self, sprite_sheet, cols, rows, fps):
            super().__init__()
            self.frames = []  # Список кадров для анимации
            self.fps = fps  # Кадры в секунду
            self.current_frame = 0  # Индекс текущего кадра
            self.last_update = pygame.time.get_ticks()  # Время последнего обновления
            width = sprite_sheet.get_width() // cols  # Ширина одного кадра
            height = sprite_sheet.get_height() // rows  # Высота одного кадра

            # Извлечение кадров из спрайт-листа
            for row in range(rows):
                for col in range(cols):
                    frame = sprite_sheet.subsurface((col * width, row * height, width, height))
                    self.frames.append(frame)
            self.image = self.frames[self.current_frame]  # Установка начального изображения
            self.rect = self.image.get_rect()  # Получение прямоугольника спрайта

        def update(self):
            now = pygame.time.get_ticks()  # Получаем текущее время
            # Проверка, прошло ли достаточно времени для обновления кадра
            if now - self.last_update > 1000 / self.fps:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)  # Переход к следующему кадру
                self.image = self.frames[self.current_frame]  # Установка нового изображения

    class Player(AnimatedSprite):
        def __init__(self):
            sprite_sheet = pygame.image.load("LIST_Player.png").convert_alpha()  # Загружаем спрайт игрока
            super().__init__(sprite_sheet, 4, 2, 10)  # Инициализация AnimatedSprite
            self.rect.center = (WIDTH // 2, HEIGHT // 2)  # Установка начального положения игрока
            self.speed = 5  # Установка скорости движения игрока

        def update(self):
            super().update()  # Обновление анимации игрока
            keys = pygame.key.get_pressed()  # Получение состояния клавиш
            # Управление движением игрока
            if keys[pygame.K_a] and self.rect.left > 0:
                self.rect.x -= self.speed  # Движение влево
            if keys[pygame.K_d] and self.rect.right < WIDTH:
                self.rect.x += self.speed  # Движение вправо
            if keys[pygame.K_w] and self.rect.top > 0:
                self.rect.y -= self.speed  # Движение вверх
            if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
                self.rect.y += self.speed  # Движение вниз

    class Star(AnimatedSprite):
        def __init__(self):
            sprite_sheet = pygame.image.load("STARS.jpg").convert_alpha()  # Загружаем спрайт звезды
            super().__init__(sprite_sheet, 3, 1, 10)  # Инициализация AnimatedSprite
            new_width, new_height = 50, 50  # Установка размеров звезды
            # Масштабирование кадров звезды
            self.frames = [pygame.transform.scale(frame, (new_width, new_height)) for frame in self.frames]
            self.image = self.frames[self.current_frame]
            self.rect = self.image.get_rect()
            # Установка случайного начального положения звезды
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(0, HEIGHT - self.rect.height)

    # Создание групп спрайтов для управления элементами игры
    all_sprites = pygame.sprite.Group()  # Общая группа спрайтов
    stars = pygame.sprite.Group()  # Группа звёзд
    player = Player()  # Создание игрока
    all_sprites.add(player)  # Добавление игрока в общую группу спрайтов

    running = True  # Флаг, показывающий, продолжается ли игра
    score = 0  # Начальный счет
    level = 1  # Начальный уровень
    timer = 10  # Таймер на игре
    font = pygame.font.Font(None, 36)  # Шрифт для отображения счета
    clock = pygame.time.Clock()  # Создание часового объекта для контроля FPS

    # Функция сброса игры
    def reset_game():
        nonlocal score, level, timer  # Объявляем, что будем изменять эти переменные из внешней области видимости
        score = 0
        level = 1
        timer = 10
        stars.empty()  # Очистка списка звёзд
        all_sprites.empty()  # Очистка всех спрайтов
        all_sprites.add(player)  # Добавляем игрока обратно в спрайты
        # Генерация начального количества звёзд в зависимости от текущего уровня
        for _ in range(level):
            star = Star()
            all_sprites.add(star)
            stars.add(star)

    reset_game()  # Сброс игры при старте
    start_ticks = pygame.time.get_ticks()  # Запоминаем время старта игры

    while running:
        seconds = (pygame.time.get_ticks() - start_ticks) / 1000  # Рассчитываем прошедшее время
        timer = 10 - int(seconds)  # Обновляем таймер
        if timer <= 0:  # Проверяем, истек ли таймер
            running = False

        for event in pygame.event.get():  # Обработка событий
            if event.type == pygame.QUIT:  # Если нажата кнопка выхода
                running = False

        all_sprites.update()  # Обновление состояния всех спрайтов
        hits = pygame.sprite.spritecollide(player, stars, True)  # Проверяем столкновение игрока со звёздами
        score += len(hits)  # Увеличиваем счет на количество собранных звёзд

        # Если звёзды закончились, переходим на следующий уровень
        if len(stars) == 0:
            level += 1  # Увеличиваем уровень
            stars.empty()  # Очищаем группу звёзд
            for _ in range(level):  # Генерация звёзд для нового уровня
                star = Star()
                all_sprites.add(star)
                stars.add(star)
            timer = 10  # Сбрасываем таймер
            start_ticks = pygame.time.get_ticks()  # Обновляем время старта

        # Отрисовка графики
        screen.fill(BLACK)  # Очищаем экран черным цветом
        all_sprites.draw(screen)  # Отрисовываем все спрайты на экране
        score_text = font.render(f"Счёт: {score}", True, (255, 255, 255))  # Рендерим текст с текущим счетом
        timer_text = font.render(f"Таймер: {timer}", True, (255, 255, 255))  # Рендерим текст с таймером
        screen.blit(score_text, (10, 10))  # Выводим текст счета на экран
        screen.blit(timer_text, (WIDTH - 150, 10))  # Выводим текст таймера на экран
        pygame.display.flip()  # Обновляем экран
        clock.tick(30)  # Ограничение FPS до 30

    pygame.quit()  # Завершение работы Pygame


# Переменная, управляющая состоянием меню
menu_running = True
while menu_running:  # Основной цикл меню
    for event in pygame.event.get():  # Обработка событий
        if event.type == pygame.QUIT:  # Если пользователь закрыл окно
            menu_running = False  # Завершаем меню

    screen.fill(BLACK)  # Заполняем экран черным цветом
    # Отображаем заголовок меню
    draw_text("Меню выбора игры", 60, (255, 255, 255), screen, WIDTH // 2, HEIGHT // 4)
    # Отображаем возможные варианты игр
    draw_text("1. Платформер с врагами", 40, (255, 255, 255), screen, WIDTH // 2, HEIGHT // 2 - 20)
    draw_text("2. Анимированный шутер", 40, (255, 255, 255), screen, WIDTH // 2, HEIGHT // 2 + 20)
    draw_text("3. Сбор звёздочек", 40, (255, 255, 255), screen, WIDTH // 2, HEIGHT // 2 + 60)
    draw_text("Нажмите ESC для выхода", 30, (255, 255, 255), screen, WIDTH // 2, HEIGHT // 2 + 100)

    keys = pygame.key.get_pressed()  # Получаем состояние всех клавиш
    if keys[pygame.K_1]:  # Если нажата клавиша 1
        menu_running = False  # Завершаем меню
        game_one()  # Запускаем первую игру
    elif keys[pygame.K_2]:  # Если нажата клавиша 2
        menu_running = False  # Завершаем меню
        game_two()  # Запускаем вторую игру
    elif keys[pygame.K_3]:  # Если нажата клавиша 3
        menu_running = False  # Завершаем меню
        game_three()  # Запускаем третью игру
    elif keys[pygame.K_ESCAPE]:  # Если нажата клавиша ESC
        menu_running = False  # Завершаем меню

    pygame.display.flip()  # Обновляем экран

pygame.quit()  # Завершение работы Pygame


if __name__ == "__main__":  # Проверка, запускается ли скрипт напрямую
    game_one()  # Запуск первой игры (можно удалить, если меню всегда должно отображаться)
    game_two()  # Запуск второй игры (можно удалить, если меню всегда должно отображаться)
    game_three()  # Запуск третьей игры (можно удалить, если меню всегда должно отображаться)
    menu_running = True  # Установка состояния меню (неизменяемая тут строка)

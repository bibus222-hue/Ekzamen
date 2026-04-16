import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Простой Марио")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Таймер для контроля FPS
clock = pygame.time.Clock()
FPS = 60

class Player(pygame.sprite.Sprite):
    """Класс игрока (Марио)"""
    def __init__(self):
        super().__init__()
        # Создаем простой прямоугольный спрайт
        self.image = pygame.Surface([30, 40])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        
        # Начальная позиция
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - 100
        
        # Физика
        self.change_x = 0
        self.change_y = 0
        self.speed = 5
        self.jump_power = -15
        self.gravity = 1
        
        # Статус на земле
        self.on_ground = False

    def update(self, platforms, enemies, coins):
        """Обновление позиции игрока с учетом гравитации, коллизий и сбора предметов"""
        # Применение гравитации
        self.change_y += self.gravity
        
        # Ограничение скорости падения (терминальная скорость)
        if self.change_y > 15:
            self.change_y = 15

        # Движение по горизонтали
        self.rect.x += self.change_x
        
        # Проверка коллизий по X
        block_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            else:
                self.rect.left = block.rect.right

        # Движение по вертикали
        self.rect.y += self.change_y
        
        # Проверка коллизий по Y (приземление/потолок)
        self.on_ground = False
        block_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
                self.on_ground = True
            else:
                self.rect.top = block.rect.bottom
            self.change_y = 0

        # Проверка сбора монет
        coin_hit_list = pygame.sprite.spritecollide(self, coins, True)
        for coin in coin_hit_list:
            # Здесь можно добавить счет
            pass

        # Проверка столкновения с врагами
        if pygame.sprite.spritecollide(self, enemies, False):
            # При касании врага - сброс игры
            return True # Сигнал о том, что игра должна перезапуститься
            
        return False

    # Методы для управления
    def go_left(self):
        self.change_x = -self.speed

    def go_right(self):
        self.change_x = self.speed

    def stop(self):
        self.change_x = 0

    def jump(self):
        if self.on_ground:
            self.change_y = self.jump_power
            self.on_ground = False

class Platform(pygame.sprite.Sprite):
    """Платформы, по которым можно ходить"""
    def __init__(self, width, height, x, y):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    """Враг (Гумба), который двигается туда-сюда"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([30, 30])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.speed = 2
        
    def update(self, platforms):
        """Движение врага по платформе"""
        self.rect.x += self.speed * self.direction
        
        # Разворот при падении с края или столкновении
        # Создаем временный спрайт для проверки края платформы
        future_rect = self.rect.copy()
        future_rect.x += self.speed * self.direction
        future_rect.y += 5 # Проверяем точку чуть ниже ног
        
        # Проверка: есть ли земля под ногами в будущей позиции?
        platform_hit = pygame.sprite.spritecollideany(self, platforms, False)
        if platform_hit:
            # Проверяем край
            edge_check_rect = self.rect.copy()
            edge_check_rect.y += 5
            if self.direction > 0:
                edge_check_rect.left = self.rect.right
            else:
                edge_check_rect.right = self.rect.left
                
            on_edge = False
            for p in platforms:
                if edge_check_rect.colliderect(p.rect):
                    on_edge = True
                    break
            
            if not on_edge:
                self.direction *= -1
        
        # Проверка на столкновение со стеной
        block_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for block in block_hit_list:
            if self.direction > 0:
                self.rect.right = block.rect.left
            else:
                self.rect.left = block.rect.right
            self.direction *= -1

class Coin(pygame.sprite.Sprite):
    """Монетка для сбора"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([15, 15])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def reset_game():
    """Функция сброса уровня в начальное состояние"""
    # Группы спрайтов
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()

    # Создание игрока
    player = Player()
    all_sprites.add(player)

    # Создание платформ (пол, стены, парящие блоки)
    # Пол
    ground = Platform(SCREEN_WIDTH, 50, 0, SCREEN_HEIGHT - 50)
    platforms.add(ground)
    all_sprites.add(ground)
    
    # Парящие платформы
    plat1 = Platform(100, 20, 200, 450)
    platforms.add(plat1)
    all_sprites.add(plat1)
    
    plat2 = Platform(150, 20, 400, 350)
    platforms.add(plat2)
    all_sprites.add(plat2)
    
    plat3 = Platform(100, 20, 600, 250)
    platforms.add(plat3)
    all_sprites.add(plat3)

    # Создание врагов
    enemy1 = Enemy(250, SCREEN_HEIGHT - 80)
    enemies.add(enemy1)
    all_sprites.add(enemy1)
    
    enemy2 = Enemy(450, 320) # На платформе plat2
    enemies.add(enemy2)
    all_sprites.add(enemy2)

    # Создание монет
    coin1 = Coin(240, 400)
    coins.add(coin1)
    all_sprites.add(coin1)
    
    coin2 = Coin(450, 300)
    coins.add(coin2)
    all_sprites.add(coin2)
    
    coin3 = Coin(650, 200)
    coins.add(coin3)
    all_sprites.add(coin3)

    return player, all_sprites, platforms, enemies, coins

# Основной игровой цикл
def main():
    player, all_sprites, platforms, enemies, coins = reset_game()
    running = True
    
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                
            # Обработка нажатий клавиш
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_SPACE:
                    player.jump()
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        # Обновление
        # Вызываем обновление игрока и проверяем коллизию с врагами
        game_over = player.update(platforms, enemies, coins)
        if game_over:
            # Если касание врага, перезапускаем игру
            player, all_sprites, platforms, enemies, coins = reset_game()
            
        enemies.update(platforms)
        
        # Рисование
        screen.fill(BLACK) # Фон как небо
        all_sprites.draw(screen)
        
        # Инструкция на экране
        font = pygame.font.SysFont('Arial', 20)
        text = font.render('Стрелки: движение, ПРОБЕЛ: прыжок. Избегай красных врагов!', True, WHITE)
        screen.blit(text, (10, 10))
        
        # Обновление экрана
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
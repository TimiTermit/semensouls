import pygame
import random
import time

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Semen Souls - 2D Souls-like Game")

# Kolory
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# FPS
clock = pygame.time.Clock()
FPS = 60

# Załaduj obrazy
knight_img = pygame.image.load("assets/knight.png").convert_alpha()
horse_knight_img = pygame.image.load("assets/horse_knight.png").convert_alpha()
background_img = pygame.image.load("assets/background.png").convert()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.speed = 5
        self.health = 100
        self.state = 'idle'  # idle, attacking, dodging, blocking, parrying
        self.attack_timer = 0
        self.dodge_timer = 0
        self.blocking = False

    def move(self, dx, dy):
        if self.state in ['idle', 'blocking', 'dodging']:
            self.x += dx * self.speed
            self.y += dy * self.speed
            self.x = max(0, min(WIDTH - self.width, self.x))
            self.y = max(0, min(HEIGHT - self.height, self.y))

    def attack(self):
        if self.state == 'idle':
            self.state = 'attacking'
            self.attack_timer = FPS // 4  # Krótszy atak
            return True
        return False

    def dodge(self):
        if self.state == 'idle':
            self.state = 'dodging'
            self.dodge_timer = FPS // 3  # Unik trwa 0.33 sekundy

    def block(self):
        if self.state in ['idle', 'blocking']:
            self.state = 'blocking'
            self.blocking = True

    def parry(self):
        if self.state == 'idle':
            self.state = 'parrying'

    def take_damage(self, damage):
        if self.state == 'dodging':
            if random.random() < 0.7:
                return  # Uniknięcie obrażeń
        if self.state == 'blocking':
            damage = max(1, damage // 3)
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def reset_state(self):
        if self.state == 'attacking':
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.state = 'idle'
        elif self.state == 'dodging':
            self.dodge_timer -= 1
            if self.dodge_timer <= 0:
                self.state = 'idle'
        elif self.state == 'blocking':
            if not self.blocking:
                self.state = 'idle'
        elif self.state == 'parrying':
            self.state = 'idle'

class Enemy:
    def __init__(self, x, y, is_boss=False):
        self.x = x
        self.y = y
        self.width = 70 if is_boss else 50
        self.height = 70 if is_boss else 50
        self.speed = 2 if is_boss else 1  # Przyspieszony ruch bossa
        self.health = 200 if is_boss else 100
        self.state = 'idle'  # idle, attacking, special_attack
        self.attack_timer = 0
        self.is_boss = is_boss
        self.max_attack_timer = FPS * 2 if is_boss else FPS
        self.attack_cooldown = 0
        self.special_attack_cooldown = FPS * 5
        self.special_attack_timer = 0
        self.special_attack_active = False

    def move(self, player_x, player_y):
        if self.state == 'idle':
            if self.x > player_x:
                self.x -= self.speed
            elif self.x < player_x:
                self.x += self.speed
            if self.y > player_y:
                self.y -= self.speed
            elif self.y < player_y:
                self.y += self.speed
            self.x = max(0, min(WIDTH - self.width, self.x))
            self.y = max(0, min(HEIGHT - self.height, self.y))

    def attack(self, player):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            return

        if self.state == 'idle' and not self.special_attack_active:
            if abs(self.x - player.x) < 80 and abs(self.y - player.y) < 80:
                self.state = 'attacking'
                self.attack_timer = self.max_attack_timer
                self.attack_cooldown = FPS

                if player.state == 'dodging':
                    if random.random() < 0.7:
                        return
                elif player.state == 'blocking':
                    damage = random.randint(5, 10) * (2 if self.is_boss else 1)
                    player.take_damage(damage)
                    return
                elif player.state == 'parrying':
                    if random.random() < 0.5:
                        player.reset_state()
                        return
                damage = random.randint(15, 25) * (2 if self.is_boss else 1)
                player.take_damage(damage)

    def special_attack(self, player):
        if self.special_attack_cooldown <= 0 and not self.special_attack_active:
            self.state = 'special_attack'
            self.special_attack_active = True
            self.special_attack_timer = FPS * 2
            self.special_attack_cooldown = FPS * 10
            print("Boss używa specjalnego ataku!")

        if self.special_attack_active:
            self.special_attack_timer -= 1
            dist_x = abs(self.x + self.width//2 - (player.x + player.width//2))
            dist_y = abs(self.y + self.height//2 - (player.y + player.height//2))
            if dist_x < 150 and dist_y < 150:
                if player.state == 'dodging':
                    if random.random() < 0.8:
                        pass
                    else:
                        player.take_damage(30)
                elif player.state == 'blocking':
                    player.take_damage(10)
                else:
                    player.take_damage(30)
            if self.special_attack_timer <= 0:
                self.special_attack_active = False
                self.state = 'idle'

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def update(self, player):
        if self.state == 'attacking':
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.state = 'idle'
        elif self.state == 'special_attack':
            self.special_attack(player)
        else:
            self.move(player.x, player.y)
            self.attack(player)
            if self.is_boss:
                self.special_attack_cooldown -= 1
                self.special_attack(player)

def draw_health_bars(player, enemy):
    pygame.draw.rect(screen, BLACK, (10, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, 2 * player.health, 20))

    bar_width = 300
    bar_height = 25
    bar_x = WIDTH // 2 - bar_width // 2
    bar_y = 10
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
    fill_width = int(bar_width * (enemy.health / (200 if enemy.is_boss else 100)))
    pygame.draw.rect(screen, YELLOW if enemy.is_boss else RED, (bar_x, bar_y, fill_width, bar_height))

def draw_button(text, x, y, width, height, hover_color=GREEN, normal_color=BLUE):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, normal_color, (x, y, width, height))
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, WHITE)
    screen.blit(text_surf, (x + width // 2 - text_surf.get_width() // 2, y + height // 2 - text_surf.get_height() // 2))
    return False

def menu():
    while True:
        screen.fill(BLACK)
        font_large = pygame.font.Font(None, 72)
        title = font_large.render("SEMEN SOULS", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        if draw_button("GRAJ", WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50):
            return 'game'
        if draw_button("STEROWANIE", WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50):
            return 'controls'

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def controls():
    cont = True
    while cont:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 36)
        y_offset = 100
        lines = [
            "STEROWANIE:",
            "Strzałki: ruch",
            "Spacja: atak",
            "Lewy Shift: unik",
            "Lewy Ctrl: blok",
            "Enter: parry",
            "",
            "Kliknij dowolny przycisk myszki aby wrócić do menu"
        ]
        for line in lines:
            text = font.render(line, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 40

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                cont = False

def main():
    while True:
        state = menu()
        if state == 'controls':
            controls()
            continue
        elif state == 'game':
            player = Player(100, HEIGHT // 2)
            enemy = Enemy(WIDTH - 150, HEIGHT // 2, is_boss=True)

            game_over = False
            winner = None

            while not game_over:
                clock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                keys = pygame.key.get_pressed()

                dx, dy = 0, 0
                if keys[pygame.K_LEFT]:
                    dx = -1
                if keys[pygame.K_RIGHT]:
                    dx = 1
                if keys[pygame.K_UP]:
                    dy = -1
                if keys[pygame.K_DOWN]:
                    dy = 1
                player.move(dx, dy)

                if keys[pygame.K_SPACE]:
                    if player.attack():
                        if abs(player.x - enemy.x) < 80 and abs(player.y - enemy.y) < 80:
                            enemy.take_damage(random.randint(15, 25))

                if keys[pygame.K_LSHIFT]:
                    player.dodge()
                else:
                    if player.state == 'dodging':
                        player.dodge_timer = 0
                        player.state = 'idle'

                if keys[pygame.K_LCTRL]:
                    player.block()
                    player.blocking = True
                else:
                    player.blocking = False
                    if player.state == 'blocking':
                        player.state = 'idle'

                if keys[pygame.K_RETURN]:
                    player.parry()

                player.reset_state()
                enemy.update(player)

                if player.health <= 0:
                    game_over = True
                    winner = "Wróg"
                if enemy.health <= 0:
                    game_over = True
                    winner = "Gracz"

                # Rysowanie tła
                screen.blit(background_img, (0, 0))

                # Tekst stanu
                font = pygame.font.Font(None, 24)
                player_text = font.render(f"Stan gracza: {player.state}", True, WHITE)
                enemy_text = font.render(f"Stan { 'bossa' if enemy.is_boss else 'wroga' }: {enemy.state}", True, WHITE)
                screen.blit(player_text, (10, 40))
                screen.blit(enemy_text, (WIDTH - 200, 40))

                # Rysuj gracza (rycerz)
                screen.blit(knight_img, (player.x, player.y))

                # Rysuj przeciwnika (koń z rycerzem)
                screen.blit(horse_knight_img, (enemy.x, enemy.y))

                draw_health_bars(player, enemy)

                pygame.display.flip()

            # Ekran końcowy
            screen.fill(BLACK)
            font = pygame.font.Font(None, 36)
            text = font.render(f"{winner} wygrał!", True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            time.sleep(2)

    pygame.quit()

if __name__ == "__main__":
    main()
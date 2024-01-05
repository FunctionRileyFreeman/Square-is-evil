import pygame
from pygame.locals import *
import sys
import random
import math
import time

# Initialize Pygame
pygame.init()

# Screen setup
screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h

# Constants
PLAYER_SPEED = 2.5
BASE_ENEMY_SPEED = 0.7
ENEMY_SPEED_INCREMENT = 0.2
ENEMY_RADIUS = int(min(WIDTH, HEIGHT) * 0.015)
SAFE_ZONE_RADIUS = 100
WHITE = (255, 255, 255)
PLAYER_COLOR = (0, 128, 255)
ENEMY_COLOR = (255, 0, 0)
SHOT_COLOR = (255, 255, 0)
LASER_DURATION = 0.3
RESET_DELAY = 1.0  # Delay (in seconds) before resetting after each level
PLAYING, OPTIONS, GAME_OVER = 0, 1, 2

# Game window setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FPS-like Game")

# Player and enemy setup
player_size = int(min(WIDTH, HEIGHT) * 0.025)

def init_entity(size):
    return random.randint(size, WIDTH - size), random.randint(size, HEIGHT - size)

def is_collision(entity1, entity2, size):
    distance = math.hypot(entity1[0] - entity2[0], entity1[1] - entity2[1])
    return distance <= size

def is_in_safe_zone(entity, player_pos, safe_zone_radius):
    return math.hypot(entity[0] - player_pos[0], entity[1] - player_pos[1]) < safe_zone_radius

def init_enemy_away_from_player(player_pos, enemy_radius, safe_zone_radius):
    while True:
        enemy = init_entity(enemy_radius)
        if not is_in_safe_zone(enemy, player_pos, safe_zone_radius):
            return enemy

# Level system
level = 1
enemy_speed = BASE_ENEMY_SPEED

def next_level():
    global level, enemies, enemy_speed
    level += 1
    enemy_speed += ENEMY_SPEED_INCREMENT
    enemies = [init_enemy_away_from_player(player_pos, ENEMY_RADIUS, SAFE_ZONE_RADIUS) for _ in range(level)]

def restart_game():
    global player_pos, enemies, score, level, enemy_speed, current_state, reset_start_time
    player_pos = init_entity(player_size)
    enemies = [init_enemy_away_from_player(player_pos, ENEMY_RADIUS, SAFE_ZONE_RADIUS) for _ in range(level)]
    score = 0
    enemy_speed = BASE_ENEMY_SPEED
    current_state = PLAYING
    reset_start_time = time.time()  # Store the start time for the reset delay

# Game loop setup
clock, score, current_state = pygame.time.Clock(), 0, PLAYING
player_pos = init_entity(player_size)
enemies = [init_enemy_away_from_player(player_pos, ENEMY_RADIUS, SAFE_ZONE_RADIUS) for _ in range(level)]

# Laser variables
show_laser = False
laser_start_time = 0

# Reset delay variables
reset_start_time = 0
reset_delay_over = True

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == MOUSEBUTTONDOWN and event.button == 1 and current_state == PLAYING:
            cursor_pos = pygame.mouse.get_pos()
            for enemy in enemies:
                if is_collision(cursor_pos, (enemy[0], enemy[1]), ENEMY_RADIUS):
                    enemies.remove(enemy)
                    show_laser = True
                    laser_start_time = time.time()
                    if not enemies:
                        next_level()
                        reset_delay_over = False  # Set the reset delay flag to start delay timer
                        reset_start_time = time.time()  # Store the start time for the reset delay

        if event.type == KEYDOWN and event.key == K_r and current_state == GAME_OVER:
            if reset_delay_over:  # Only restart if the reset delay is over
                restart_game()

    keys = pygame.key.get_pressed()
    player_pos = (max(min(player_pos[0] + (keys[K_d] - keys[K_a]) * PLAYER_SPEED, WIDTH - player_size), player_size),
                  max(min(player_pos[1] + (keys[K_s] - keys[K_w]) * PLAYER_SPEED, HEIGHT - player_size), player_size))

    screen.fill((0, 0, 0))

    if current_state == PLAYING:
        pygame.draw.rect(screen, PLAYER_COLOR, (*player_pos, player_size, player_size))

        for enemy_index, enemy in enumerate(enemies):
            if is_collision(player_pos, enemy, ENEMY_RADIUS):
                current_state = GAME_OVER
                break
            angle = math.atan2(player_pos[1] - enemy[1], player_pos[0] - enemy[0])
            new_enemy_pos = (enemy[0] + enemy_speed * math.cos(angle),
                             enemy[1] + enemy_speed * math.sin(angle))
            enemies[enemy_index] = new_enemy_pos
            pygame.draw.circle(screen, ENEMY_COLOR, (int(new_enemy_pos[0]), int(new_enemy_pos[1])), ENEMY_RADIUS)

    elif current_state == GAME_OVER:
        screen.blit(pygame.font.Font(None, 36).render("Game Over - Press 'R' to Restart", True, WHITE), (WIDTH // 2 - 180, HEIGHT // 2))

    # Display the laser for a limited duration
    if show_laser and time.time() - laser_start_time < LASER_DURATION:
        pygame.draw.line(screen, SHOT_COLOR, player_pos, cursor_pos, 5)
    else:
        show_laser = False

    # Check if the reset delay is over
    if not reset_delay_over and time.time() - reset_start_time >= RESET_DELAY:
        reset_delay_over = True

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()

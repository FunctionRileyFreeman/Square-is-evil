import pygame
from pygame.locals import *
import sys
import random
import math
import pygame_gui

# Initialize Pygame
pygame.init()

# Get the screen resolution
screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h

# Constants
PLAYER_SPEED = 0.2
ENEMY_COUNT = 5
ENEMY_RADIUS = int(min(WIDTH, HEIGHT) * 0.02)
WHITE = (255, 255, 255)
PLAYER_COLOR = (0, 128, 255)
ENEMY_COLOR = (255, 0, 0)

# Define game states
PLAYING = 0
OPTIONS = 1
GAME_OVER = 2

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FPS-like Game")

# Player setup
player_width, player_height = int(min(WIDTH, HEIGHT) * 0.025), int(min(WIDTH, HEIGHT) * 0.025)

def init_player():
    return WIDTH // 2, HEIGHT // 2

# Enemy setup
enemies = []

def init_enemy():
    x = random.randint(ENEMY_RADIUS, WIDTH - ENEMY_RADIUS)
    y = random.randint(ENEMY_RADIUS, HEIGHT - ENEMY_RADIUS)
    angle = random.uniform(0, 2 * math.pi)
    return {"x": x, "y": y, "angle": angle}

def is_collision(circle1, circle2):
    distance = math.sqrt((circle1["x"] - circle2["x"])**2 + (circle1["y"] - circle2["y"])**2)
    return distance <= (2 * ENEMY_RADIUS)

def init_enemies():
    enemies.clear()
    for _ in range(ENEMY_COUNT):
        while True:
            enemy = init_enemy()
            overlapping = False
            for other_enemy in enemies:
                if is_collision(enemy, other_enemy):
                    overlapping = True
                    break
            if not overlapping:
                enemies.append(enemy)
                break

# Options menu setup
font = pygame.font.Font(None, 36)
menu_options = ["Resume", "Options", "Quit"]
selected_option = 0

show_slider = False  # To control slider visibility
slider_value = 0.05
slider_min = 0.01
slider_max = 0.2

def draw_options_menu():
    for i, opt in enumerate(menu_options):
        text = font.render(opt, True, WHITE)
        rect = text.get_rect(topleft=(100, i * 50 + 200))
        if i == selected_option:
            pygame.draw.rect(screen, (0, 128, 0), rect, 3)
        screen.blit(text, rect)

def handle_menu_click(mouse_x, mouse_y):
    global show_slider, current_state

    option_rects = [font.render(opt, True, WHITE).get_rect(topleft=(100, i * 50 + 200)) for i, opt in enumerate(menu_options)]

    if current_state == PLAYING:
        for i, rect in enumerate(option_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                if i == 0:  # Resume
                    return PLAYING
                elif i == 1:  # Options
                    show_slider = not show_slider  # Toggle slider visibility
                    return OPTIONS
                elif i == 2:  # Quit
                    pygame.quit()
                    sys.exit()
    elif current_state == OPTIONS:
        for i, rect in enumerate(option_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                if i == 0:  # Back
                    return PLAYING
    elif current_state == GAME_OVER:
        for i, rect in enumerate(option_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                if i == 0:  # Retry
                    init_player()
                    init_enemies()
                    score = 0
                    return PLAYING
                elif i == 1:  # Options
                    show_slider = not show_slider  # Toggle slider visibility
                    return OPTIONS
                elif i == 2:  # Quit
                    pygame.quit()
                    sys.exit()

    return current_state

# Create a pygame_gui UIManager for GUI elements
ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Slider setup
slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((WIDTH - 300, 400, 200, 20)),  # Adjust the slider's position
    start_value=slider_value,
    value_range=(slider_min, slider_max),
    manager=ui_manager,
)

# Game Over screen setup
game_over_font = pygame.font.Font(None, 72)
game_over_text = game_over_font.render("Game Over", True, WHITE)
game_over_text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Import additional libraries for graphical enhancements
import pygame.gfxdraw
from pygame.math import Vector2

# Create a clock object to control frame rate
clock = pygame.time.Clock()

# Create a variable for tracking player score
score = 0

# Create a font for displaying the score
score_font = pygame.font.Font(None, 36)

# Create a function to draw the player's score
def draw_score():
    score_text = score_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

# Main game loop
current_state = PLAYING
player_x, player_y = init_player()
init_enemies()

running = True  # Initialize 'running' variable
game_over = False  # Initialize 'game_over' variable

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if current_state == PLAYING:
            ui_manager.process_events(event)

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if current_state == PLAYING:
                for enemy in enemies:
                    if is_collision({"x": mouse_x, "y": mouse_y}, enemy):
                        enemies.remove(enemy)
                        score += 1
            elif current_state == GAME_OVER:
                current_state = handle_menu_click(mouse_x, mouse_y)
            elif current_state == OPTIONS:  # Only handle clicks in OPTIONS state
                current_state = handle_menu_click(mouse_x, mouse_y)

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                if current_state == PLAYING:
                    current_state = OPTIONS
                elif current_state == OPTIONS:
                    current_state = PLAYING
                    show_slider = False  # Hide the slider when exiting the options menu

    keys = pygame.key.get_pressed()
    if keys[K_w]:
        player_y -= PLAYER_SPEED
    if keys[K_s]:
        player_y += PLAYER_SPEED
    if keys[K_a]:
        player_x -= PLAYER_SPEED
    if keys[K_d]:
        player_x += PLAYER_SPEED

    # Clear the screen
    screen.fill((0, 0, 0))

    if not game_over:
        pygame.draw.rect(screen, PLAYER_COLOR, (player_x, player_y, player_width, player_height))
        for enemy in enemies:
            angle = math.atan2(player_y - enemy["y"], player_x - enemy["x"])
            enemy["x"] += slider_value * math.cos(angle)
            enemy["y"] += slider_value * math.sin(angle)
            pygame.draw.circle(screen, ENEMY_COLOR, (int(enemy["x"]), int(enemy["y"])), ENEMY_RADIUS)
            if is_collision({"x": player_x, "y": player_y}, enemy):
                game_over = True

        # Draw the player's score
        draw_score()

    if game_over:
        screen.blit(game_over_text, game_over_text_rect)
        ui_manager.draw_ui(screen)  # Draw UI elements

    elif current_state == OPTIONS:
        if show_slider:  # Display the slider if show_slider is True
            ui_manager.draw_ui(screen)  # Draw all UI elements, including the slider

        draw_options_menu()

    # Update the display
    pygame.display.update()

    # Update the UI manager
    ui_manager.update(1 / 60)

    # Limit the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()
sys.exit()

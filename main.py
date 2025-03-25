import pygame
import random
import time
import json
import sys

# Constants
WIDTH, HEIGHT = 700, 500
NAVBAR_HEIGHT = 50
GAME_HEIGHT = HEIGHT - NAVBAR_HEIGHT
CELL_SIZE = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 100, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game <---> Created by : GAURAV")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont(None, 35)
welcome_font = pygame.font.Font(None, 50)
gaurav_font = pygame.font.Font(None, 30)
game_over_font = pygame.font.Font(None, 40)

# Sound Effects
try:
    pygame.mixer.init()
    eat_sound = pygame.mixer.Sound("eat_sound.wav")
    game_over_sound = pygame.mixer.Sound("game_over.wav")
    button_click_sound = pygame.mixer.Sound("button_click.wav")
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.set_volume(0.5)
except pygame.error as e:
    print(f"Error loading sounds: {e}")
    eat_sound = game_over_sound = button_click_sound = None

# Background Image
try:
    background = pygame.image.load("background_image.jpg")
    background = pygame.transform.scale(background, (WIDTH, GAME_HEIGHT))
except FileNotFoundError:
    print("Background image not found. Using solid color instead.")
    background = pygame.Surface((WIDTH, GAME_HEIGHT))
    background.fill(BLACK)

# Difficulty Levels
DIFFICULTY_SPEED = {"Easy": 8, "Medium": 12, "Hard": 16}
current_difficulty = "Easy"

# High Score
def load_high_score():
    try:
        with open("high_score.json", "r") as file:
            return json.load(file).get("high_score", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def save_high_score(score):
    with open("high_score.json", "w") as file:
        json.dump({"high_score": score}, file)

high_score = load_high_score()

# Button Class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, border_radius=10, shadow=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.border_radius = border_radius
        self.shadow = shadow

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        button_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        if self.shadow:
            shadow_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width, self.rect.height)
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, button_color, self.rect, border_radius=self.border_radius)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# Game Variables
snake = [(100, 100 + NAVBAR_HEIGHT), (80, 100 + NAVBAR_HEIGHT), (60, 100 + NAVBAR_HEIGHT)]
snake_dir = (0, 0)  # Initialize snake direction to (0, 0) to keep it stationary
food = (random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE,
        random.randint(0, (GAME_HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE + NAVBAR_HEIGHT)
food_radius = CELL_SIZE // 2
food_timer = pygame.time.get_ticks()
FOOD_TIMEOUT = 10000

score = 0
start_time = time.time()
paused = False
game_over = False
wait_for_input = True  # Wait for direction input at the start
growing = False
music_enabled = True

# Buttons
start_button = Button(WIDTH // 2 - 75, HEIGHT // 2 - 50, 150, 50, "Start", (0, 200, 0), (0, 255, 0), border_radius=15, shadow=True)
quit_button = Button(WIDTH // 2 - 75, HEIGHT // 2 + 20, 150, 50, "Quit", (200, 0, 0), (255, 0, 0), border_radius=15, shadow=True)
settings_button = Button(WIDTH // 2 - 75, HEIGHT // 2 + 90, 150, 50, "Settings", (0, 0, 200), (0, 0, 255), border_radius=15, shadow=True)
resume_button = Button(WIDTH // 2 - 75, HEIGHT // 2 - 50, 150, 50, "Resume", (0, 200, 0), (0, 255, 0), border_radius=15, shadow=True)
pause_quit_button = Button(WIDTH // 2 - 75, HEIGHT // 2 + 20, 150, 50, "Quit", (200, 0, 0), (255, 0, 0), border_radius=15, shadow=True)
play_again_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "Play Again", (0, 200, 0), (0, 255, 0), border_radius=15, shadow=True)
game_over_quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, "Quit", (200, 0, 0), (255, 0, 0), border_radius=15, shadow=True)
easy_button = Button(WIDTH // 2 - 75, HEIGHT // 2 - 170, 150, 50, "Easy", (0, 200, 0), (0, 255, 0), border_radius=15, shadow=True)
medium_button = Button(WIDTH // 2 - 75, HEIGHT // 2 - 100, 150, 50, "Medium", (0, 0, 200), (0, 0, 255), border_radius=15, shadow=True)
hard_button = Button(WIDTH // 2 - 75, HEIGHT // 2 - 30, 150, 50, "Hard", (200, 0, 0), (255, 0, 0), border_radius=15, shadow=True)
music_toggle_button = Button(WIDTH // 2 - 75, HEIGHT // 2 + 80, 150, 50, "Music: ON", (0, 170, 245), (0, 190, 255), border_radius=5, shadow=True)
back_button = Button(WIDTH // 2 - 75, HEIGHT // 2 + 150, 150, 50, "<— Back", (100, 100, 100), (150, 150, 150), border_radius=25, shadow=True)

def draw_navbar():
    pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, NAVBAR_HEIGHT))
    elapsed_time = int(time.time() - start_time)
    screen.blit(font.render(f"Score: {score}", True, WHITE), (120, 10))
    screen.blit(font.render(f"Time: {elapsed_time}", True, WHITE), (WIDTH // 2 - 50, 10))
    screen.blit(font.render(f"High Score: {high_score}", True, WHITE), (WIDTH - 200, 10))
    back_button_navbar = Button(WIDTH - 690, 10, 80, 30, "Menu", (0, 10, 10), (0, 250, 250), border_radius=5, shadow=False)
    back_button_navbar.draw(screen)
    return back_button_navbar

def draw_snake():
    for i, segment in enumerate(snake):
        if i == 0:
            pygame.draw.circle(screen, DARK_GREEN, (segment[0] + CELL_SIZE // 2, segment[1] + CELL_SIZE // 2), CELL_SIZE // 2)
            eye_radius, eye_offset = 3, 5
            pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE // 2 - eye_offset, segment[1] + CELL_SIZE // 2 - eye_offset), eye_radius)
            pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE // 2 + eye_offset, segment[1] + CELL_SIZE // 2 - eye_offset), eye_radius)
        else:
            pygame.draw.circle(screen, GREEN, (segment[0] + CELL_SIZE // 2, segment[1] + CELL_SIZE // 2), CELL_SIZE // 2)

def draw_food():
    pygame.draw.circle(screen, RED, (food[0] + CELL_SIZE // 2, food[1] + CELL_SIZE // 2), food_radius)

def check_collision():
    return (snake[0][0] < 0 or snake[0][0] >= WIDTH or
            snake[0][1] < NAVBAR_HEIGHT or snake[0][1] >= HEIGHT or
            snake[0] in snake[1:])

def generate_food():
    while True:
        new_food = (random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE,
                    random.randint(0, (GAME_HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE + NAVBAR_HEIGHT)
        if new_food not in snake:
            return new_food

def start_screen():
    while True:
        screen.fill(BLACK)
        screen.blit(welcome_font.render("Welcome to Snake Game!", True, WHITE), (WIDTH // 2 - 200, HEIGHT // 2 - 150))
        screen.blit(gaurav_font.render(">>created by GAURAV", True, WHITE), (WIDTH // 2+120, HEIGHT // 2 + 215))
        start_button.draw(screen)
        quit_button.draw(screen)
        settings_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if start_button.is_clicked(event):
                return
            if quit_button.is_clicked(event):
                pygame.quit()
                sys.exit()
            if settings_button.is_clicked(event):
                settings_screen()

def settings_screen():
    global current_difficulty, music_enabled
    instructions_note = pygame.font.Font(None, 25)
    while True:
        screen.fill(BLACK)
        screen.blit(instructions_note.render("Note : Press SPACEBAR to pause the game.", True, WHITE), (WIDTH // 2 - 165, HEIGHT - 210))
        easy_button.color = (0, 200, 0) if current_difficulty == "Easy" else (100, 100, 100)
        medium_button.color = (0, 0, 200) if current_difficulty == "Medium" else (100, 100, 100)
        hard_button.color = (200, 0, 0) if current_difficulty == "Hard" else (100, 100, 100)
        easy_button.draw(screen)
        medium_button.draw(screen)
        hard_button.draw(screen)
        music_toggle_button.text = "Music: ON" if music_enabled else "Music: OFF"
        music_toggle_button.draw(screen)
        back_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if easy_button.is_clicked(event):
                current_difficulty = "Easy"
            if medium_button.is_clicked(event):
                current_difficulty = "Medium"
            if hard_button.is_clicked(event):
                current_difficulty = "Hard"
            if music_toggle_button.is_clicked(event):
                music_enabled = not music_enabled
                pygame.mixer.music.play(-1) if music_enabled else pygame.mixer.music.stop()
            if back_button.is_clicked(event):
                return

def pause_screen():
    global paused, wait_for_input
    while paused:
        screen.fill(BLACK)
        resume_button.draw(screen)
        pause_quit_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if resume_button.is_clicked(event):
                paused = False
                wait_for_input = True  # Wait for direction input after resuming
            if pause_quit_button.is_clicked(event):
                pygame.quit()
                sys.exit()

def game_over_screen():
    global game_over, score, high_score
    while game_over:
        screen.fill(BLACK)
        screen.blit(game_over_font.render(f"Well done! Your score is {score}", True, WHITE), (WIDTH // 2 - 165, HEIGHT // 2 - 100))
        play_again_button.draw(screen)
        game_over_quit_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if play_again_button.is_clicked(event):
                reset_game()
                return
            if game_over_quit_button.is_clicked(event):
                pygame.quit()
                sys.exit()

def reset_game():
    global snake, snake_dir, food, score, start_time, game_over, wait_for_input, growing
    snake = [(100, 100 + NAVBAR_HEIGHT), (80, 100 + NAVBAR_HEIGHT), (60, 100 + NAVBAR_HEIGHT)]
    snake_dir = (0, 0)  # Reset direction to (0, 0) to keep snake stationary
    food = generate_food()
    score = 0
    start_time = time.time()
    game_over = False
    wait_for_input = True  # Wait for direction input at the start
    growing = False

def main():
    global snake, snake_dir, food, score, high_score, paused, game_over, wait_for_input, growing, food_timer, music_enabled

    start_screen()
    reset_game()

    if music_enabled:
        pygame.mixer.music.play(-1)

    while True:
        screen.fill(BLACK)
        screen.blit(background, (0, NAVBAR_HEIGHT))
        back_button_navbar = draw_navbar()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if not paused and not game_over:
                    if wait_for_input:
                        if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                            wait_for_input = False  # Start moving after first direction input
                    if not wait_for_input:
                        if event.key == pygame.K_UP and snake_dir != (0, CELL_SIZE):
                            snake_dir = (0, -CELL_SIZE)
                        if event.key == pygame.K_DOWN and snake_dir != (0, -CELL_SIZE):
                            snake_dir = (0, CELL_SIZE)
                        if event.key == pygame.K_LEFT and snake_dir != (CELL_SIZE, 0):
                            snake_dir = (-CELL_SIZE, 0)
                        if event.key == pygame.K_RIGHT and snake_dir != (-CELL_SIZE, 0):
                            snake_dir = (CELL_SIZE, 0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_navbar.rect.collidepoint(event.pos):
                    if button_click_sound:
                        button_click_sound.play()
                    start_screen()

        if not paused and not game_over and not wait_for_input:
            new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])
            snake.insert(0, new_head)

            if snake[0] == food:
                if eat_sound:
                    eat_sound.play()
                score += 1
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                food = generate_food()
                food_timer = pygame.time.get_ticks()
                growing = True
            else:
                if not growing:
                    snake.pop()
                else:
                    growing = False

            if pygame.time.get_ticks() - food_timer > FOOD_TIMEOUT:
                food = generate_food()
                food_timer = pygame.time.get_ticks()

            if check_collision():
                if game_over_sound:
                    game_over_sound.play()
                game_over = True

        draw_snake()
        draw_food()

        if paused:
            pause_screen()
        if game_over:
            game_over_screen()

        pygame.display.flip()
        clock.tick(DIFFICULTY_SPEED[current_difficulty])

if __name__ == "__main__":
    main()
    
# End of the code
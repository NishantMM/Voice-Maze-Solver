import pygame
import random
import threading
import collections
import json
import pyaudio
from vosk import Model, KaldiRecognizer

# --- CONFIGURATION ---
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 40  # Increased for better control and visibility
COLS, ROWS = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE
FPS = 60

# Colors
BLACK = (15, 15, 15)
WHITE = (245, 245, 245)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
WALL_COLOR = (70, 70, 90)

# Global Command Queue
command_queue = collections.deque()


# --- MAZE GENERATION ---
def generate_maze():
    # Start with all walls
    grid = [[1] * COLS for _ in range(ROWS)]

    def carve_passages(cx, cy):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + (dx * 2), cy + (dy * 2)
            if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 1:
                grid[cy + dy][cx + dx] = 0
                grid[ny][nx] = 0
                carve_passages(nx, ny)

    grid[0][0] = 0
    carve_passages(0, 0)

    # GUARANTEE: Open the start (Bottom Left) and end (Bottom Right)
    grid[ROWS - 1][0] = 0
    grid[ROWS - 1][COLS - 1] = 0

    # Ensure a path exists at the edges
    if grid[ROWS - 1][1] == 1 and grid[ROWS - 2][0] == 1:
        grid[ROWS - 1][1] = 0  # Forced path

    return grid


# --- OFFLINE VOICE RECOGNITION ---
def listen_voice():
    try:
        model = Model("model")  # Ensure folder 'model' is present
    except:
        print("Error: 'model' folder not found.")
        return

    recognizer = KaldiRecognizer(model, 16000, '["up", "down", "left", "right", "stop", "[unk]"]')
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
    stream.start_stream()

    print("\n>>> VOICE SYSTEM ONLINE <<<")

    while True:
        data = stream.read(2048, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                print(f"Heard: {text}")
                for word in text.split():
                    if word == "stop":
                        command_queue.clear()
                    elif word in ["up", "down", "left", "right"]:
                        command_queue.append(word)


# --- MAIN GAME ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Voice Maze Solver")
    clock = pygame.time.Clock()

    # Setup first maze
    maze = generate_maze()
    ball_x, ball_y = 0, ROWS - 1
    goal_x, goal_y = COLS - 1, ROWS - 1

    move_delay = 0
    threading.Thread(target=listen_voice, daemon=True).start()

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- FAST QUEUE MOVEMENT ---
        move_delay += 1
        if move_delay >= 4:  # Speed: lower is faster
            if command_queue:
                cmd = command_queue.popleft()
                nx, ny = ball_x, ball_y

                if cmd == "up":
                    ny -= 1
                elif cmd == "down":
                    ny += 1
                elif cmd == "left":
                    nx -= 1
                elif cmd == "right":
                    nx += 1

                if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == 0:
                    ball_x, ball_y = nx, ny
                else:
                    command_queue.clear()  # Hit wall, stop queue
            move_delay = 0

        # --- DRAWING ---
        for r in range(ROWS):
            for c in range(COLS):
                if maze[r][c] == 1:
                    pygame.draw.rect(screen, WALL_COLOR, (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

        # Goal (Green)
        pygame.draw.rect(screen, GREEN, (goal_x * GRID_SIZE + 4, goal_y * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8))

        # Ball (Red)
        pygame.draw.circle(screen, RED, (ball_x * GRID_SIZE + GRID_SIZE // 2, ball_y * GRID_SIZE + GRID_SIZE // 2),
                           GRID_SIZE // 3)

        # --- WIN LOGIC ---
        if ball_x == goal_x and ball_y == goal_y:
            print("Goal Reached!")
            pygame.time.delay(500)  # Brief pause to show win
            maze = generate_maze()
            ball_x, ball_y = 0, ROWS - 1
            command_queue.clear()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

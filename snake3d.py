from ursina import *
from ursina.shaders import lit_with_shadows_shader
import random

# Define constants
GRID_SIZE = 20
TILE_SIZE = 1
SPEED = 0.15

# Initialize app
app = Ursina()
window.color = color.black
window.fullscreen = True  # Start in fullscreen
is_fullscreen = True      # Track fullscreen state

# Camera setup: top-down orthographic view
camera.orthographic = True
camera.position = (GRID_SIZE / 2 - 0.5, 40, GRID_SIZE / 2 - 0.5)
camera.rotation_x = 90
camera.rotation_y = 0

# Snake body part
class SnakePart(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=color.green,
            position=position,
            scale=0.9,
            shader=lit_with_shadows_shader
        )

# Food class
class Food(Entity):
    def __init__(self, snake_body):
        super().__init__(
            model='sphere',
            color=color.red,
            scale=0.5,
            shader=lit_with_shadows_shader
        )
        self.snake_body = snake_body
        self.randomize_position()

    def randomize_position(self):
        while True:
            new_pos = Vec3(
                random.randint(0, GRID_SIZE - 1),
                0,
                random.randint(0, GRID_SIZE - 1)
            )
            if all(part.position != new_pos for part in self.snake_body):
                self.position = new_pos
                break

# Snake class
class Snake:
    def __init__(self):
        self.direction = Vec3(1, 0, 0)
        self.next_directions = []
        self.body = []
        self.create_snake()

    def create_snake(self):
        start_pos = Vec3(GRID_SIZE // 2, 0, GRID_SIZE // 2)
        for i in range(3):
            part = SnakePart(start_pos - Vec3(i, 0, 0))
            self.body.append(part)

    def move(self):
        if self.next_directions:
            new_dir = self.next_directions.pop(0)
            if new_dir + self.direction != Vec3(0, 0, 0):
                self.direction = new_dir

        new_head_pos = self.body[0].position + self.direction
        new_head_pos = self.wrap_around(new_head_pos)

        if any(part.position == new_head_pos for part in self.body):
            return False

        tail = self.body.pop()
        tail.position = new_head_pos
        self.body.insert(0, tail)
        return True

    def grow(self):
        tail_pos = self.body[-1].position
        new_part = SnakePart(tail_pos)
        self.body.append(new_part)

    def wrap_around(self, pos):
        pos.x %= GRID_SIZE
        pos.z %= GRID_SIZE
        return pos

    def add_direction(self, new_dir):
        if not self.next_directions or self.next_directions[-1] != new_dir:
            self.next_directions.append(new_dir)

# Global state
snake = None
food = None
timer = 0
score = 0
score_text = Text(text="Score: 0", origin=(0, 0.45), scale=2, color=color.white)
game_over_text = Text("Game Over\nPress R to Restart", origin=(0, 0), scale=3, color=color.red, enabled=False)

def start_game():
    global snake, food, timer, score
    for e in scene.entities.copy():
        if isinstance(e, SnakePart) or isinstance(e, Food):
            destroy(e)

    snake = Snake()
    food = Food(snake.body)
    timer = 0
    score = 0
    score_text.text = "Score: 0"
    game_over_text.enabled = False

def update():
    global timer, score
    if game_over_text.enabled:
        return

    timer += time.dt
    if timer >= SPEED:
        timer = 0
        alive = snake.move()
        if not alive:
            game_over_text.enabled = True
            return
        if distance(snake.body[0].position, food.position) < 0.75:
            snake.grow()
            score += 1
            score_text.text = f"Score: {score}"
            food.snake_body = snake.body
            food.randomize_position()

def input(key):
    global is_fullscreen
    if key == 'up arrow':
        snake.add_direction(Vec3(0, 0, 1))
    elif key == 'down arrow':
        snake.add_direction(Vec3(0, 0, -1))
    elif key == 'left arrow':
        snake.add_direction(Vec3(-1, 0, 0))
    elif key == 'right arrow':
        snake.add_direction(Vec3(1, 0, 0))
    elif key == 'r':
        start_game()
    elif key == 'escape':
        application.quit()
    elif key == 'f':  # Toggle fullscreen
        is_fullscreen = not is_fullscreen
        window.fullscreen = is_fullscreen

Sky()
start_game()
app.run()

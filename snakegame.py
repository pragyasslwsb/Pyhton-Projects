import random  # Provides random selection for the apple's next location.
from pathlib import Path

import pygame  # Provides the window, drawing tools, keyboard input, and game clock.

# Board dimensions and movement cadence; the board is divided into SIZE cells.
WIDTH = 1000  # Sets the game board width in pixels.
HEIGHT = 500  # Sets the game board height in pixels.
SIZE = 50  # Sets the width and height of each grid cell in pixels.
FPS = 4  # Sets how many game updates happen per second.
BACKGROUND_COLOR = (255, 255, 255)  # Sets the background to white.


class Apple:  # Represents the apple that the snake can eat.
    """Draw and reposition the apple on an unoccupied grid cell."""

    def __init__(self, parent_screen):  # Creates an apple on the supplied game screen.
        self.parent_screen = parent_screen  # Stores the screen used to draw the apple.
        self.x = SIZE * 3  # Places the apple three grid cells from the left edge.
        self.y = SIZE * 3  # Places the apple three grid cells from the top edge.
        self.image = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (220, 35, 35), (SIZE // 2, SIZE // 2 + 3), SIZE // 2 - 5)
        pygame.draw.ellipse(self.image, (30, 150, 45), (SIZE // 2, 4, SIZE // 3, SIZE // 5))

    def draw(self):  # Draws the apple on the game screen.
        self.parent_screen.blit(self.image, (self.x, self.y))

    def move(self, occupied_positions):  # Moves the apple to a grid cell not used by the snake.
        """Choose a free grid cell; return False when the board is full."""
        free_positions = [  # Starts a list comprehension of empty board cells.
            (x, y)  # Adds the current grid cell as a possible apple location.
            for x in range(0, WIDTH, SIZE)  # Checks each grid column across the board.
            for y in range(0, HEIGHT, SIZE)  # Checks each grid row down the board.
            if (x, y) not in occupied_positions  # Excludes cells already occupied by the snake.
        ]  # Finishes building the list of unoccupied grid cells.
        if not free_positions:  # Checks whether the snake occupies every grid cell.
            return False  # Reports that no new apple location is available.

        self.x, self.y = random.choice(free_positions)  # Places the apple randomly in an available cell.
        return True  # Reports that the apple was successfully moved.


class Snake:  # Represents the snake's segments and movement.
    """Track, move, grow, and draw the snake."""

    def __init__(self, parent_screen, length=3):  # Creates a snake with the requested starting length.
        self.parent_screen = parent_screen  # Stores the screen used to draw the snake.
        self.block = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)  # Creates a transparent segment image.
        pygame.draw.rect(self.block, (0, 0, 0), (2, 2, SIZE - 4, SIZE - 4), border_radius=8)
        self.length = length  # Stores the number of segments in the snake.
        # Keep every segment aligned to the same grid used by the apple.
        self.x = [100 - SIZE * i for i in range(length)]  # Stores each segment's starting horizontal coordinate.
        self.y = [100] * length  # Stores each segment's starting vertical coordinate.
        self.direction = "right"  # Starts the snake moving toward the right.
        self.previous_tail = (self.x[-1], self.y[-1])  # Remembers the tail position for possible growth.

    def draw(self):  # Draws all snake segments on the game screen.
        for x, y in zip(self.x, self.y):  # Pairs each segment's horizontal and vertical coordinates.
            self.parent_screen.blit(self.block, (x, y))  # Draws this segment at its current location.

    def move_left(self):  # Requests that the snake move to the left.
        if self.direction != "right":  # Prevents an immediate reversal into the snake's body.
            self.direction = "left"  # Sets the new direction to left.

    def move_right(self):  # Requests that the snake move to the right.
        if self.direction != "left":  # Prevents an immediate reversal into the snake's body.
            self.direction = "right"  # Sets the new direction to right.

    def move_up(self):  # Requests that the snake move upward.
        if self.direction != "down":  # Prevents an immediate reversal into the snake's body.
            self.direction = "up"  # Sets the new direction to up.

    def move_down(self):  # Requests that the snake move downward.
        if self.direction != "up":  # Prevents an immediate reversal into the snake's body.
            self.direction = "down"  # Sets the new direction to down.

    def walk(self):  # Advances the snake by one grid cell.
        # Save the tail before shifting so it can be restored when growing.
        self.previous_tail = (self.x[-1], self.y[-1])  # Saves the current tail coordinates.
        # Shift from the tail backward so each segment keeps its predecessor's old position.
        for index in range(self.length - 1, 0, -1):  # Visits body segments from tail toward head.
            self.x[index] = self.x[index - 1]  # Moves this segment to the previous segment's old x coordinate.
            self.y[index] = self.y[index - 1]  # Moves this segment to the previous segment's old y coordinate.

        if self.direction == "up":  # Checks whether the snake is moving upward.
            self.y[0] -= SIZE  # Moves the head up by one cell.
        elif self.direction == "down":  # Checks whether the snake is moving downward.
            self.y[0] += SIZE  # Moves the head down by one cell.
        elif self.direction == "left":  # Checks whether the snake is moving left.
            self.x[0] -= SIZE  # Moves the head left by one cell.
        else:  # Handles the remaining valid direction, which is right.
            self.x[0] += SIZE  # Moves the head right by one cell.

    def grow(self):  # Adds a new segment to the snake's tail.
        """Add one segment at the tail's position before the last move."""
        self.x.append(self.previous_tail[0])  # Adds the saved tail's horizontal coordinate.
        self.y.append(self.previous_tail[1])  # Adds the saved tail's vertical coordinate.
        self.length += 1  # Increases the stored segment count by one.


class Game:  # Manages the game screen, input, and game state.
    """Own the game window, state updates, input, and main loop."""

    def __init__(self):  # Initializes Pygame and creates the game objects.
        pygame.init()  # Starts Pygame's display, event, and timing systems.
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))  # Opens the game window at the configured size.
        pygame.display.set_caption("Snake")  # Sets the title shown in the window bar.
        self.setup_music()
        self.reset()

    def setup_music(self):
        """Play background.mp3, or use Pygame's example music as a fallback."""
        self.music = False
        music_file = Path(__file__).with_name("background.mp3")
        if not music_file.is_file():
            music_file = Path(pygame.__file__).parent / "examples" / "data" / "house_lo.ogg"

        if music_file.is_file():
            pygame.mixer.music.load(str(music_file))
            pygame.mixer.music.play(-1)
            self.music = True
        else:
            print("Background music is unavailable; add background.mp3 beside main.py.")

    def reset(self):
        """Restore the snake and apple to their starting state."""
        self.snake = Snake(self.surface)
        self.apple = Apple(self.surface)
        self.running = True
        self.game_over = False
        self.draw()

    def draw(self):  # Redraws all visible objects in the game window.
        self.surface.fill(BACKGROUND_COLOR)  # Clears the previous frame with the background color.
        self.snake.draw()  # Draws the snake on the cleared screen.
        self.apple.draw()  # Draws the apple on top of the background.
        self.draw_score()  # Draws the current score in the top-left corner.
        if self.game_over:
            self.show_game_over()
        pygame.display.flip()  # Presents the completed frame in the window.

    def draw_score(self):  # Displays how many apples the player has eaten.
        font = pygame.font.Font(None, 36)  # Creates a font for the score label.
        score = font.render(f"Score: {self.snake.length - 3}", True, (0, 0, 0))  # Renders the score in black.
        self.surface.blit(score, (10, 10))  # Places the score near the top-left corner of the screen.

    def handle_key(self, key):  # Translates an arrow-key press into a snake turn.
        """Apply a valid arrow-key turn without allowing a 180-degree reversal."""
        if key == pygame.K_RIGHT:  # Checks whether the right arrow was pressed.
            self.snake.move_right()  # Requests a rightward turn.
        elif key == pygame.K_LEFT:  # Checks whether the left arrow was pressed.
            self.snake.move_left()  # Requests a leftward turn.
        elif key == pygame.K_UP:  # Checks whether the up arrow was pressed.
            self.snake.move_up()  # Requests an upward turn.
        elif key == pygame.K_DOWN:  # Checks whether the down arrow was pressed.
            self.snake.move_down()  # Requests a downward turn.

    def show_game_over(self):
        font = pygame.font.Font(None, 42)
        title = font.render("Game Over", True, (0, 0, 0))
        score = font.render(f"Final score: {self.snake.length - 3}", True, (0, 0, 0))
        prompt = font.render("Press Enter to play again or Escape to quit", True, (0, 0, 0))
        self.surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 70))
        self.surface.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 20))
        self.surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 30))

    def update(self):  # Moves the snake and checks for collisions and food.
        self.snake.walk()  # Advances the snake one cell in its current direction.
        head_x, head_y = self.snake.x[0], self.snake.y[0]  # Reads the head's new coordinates.

        # Stop when the head leaves the play area or hits the snake's body.
        if not (0 <= head_x < WIDTH and 0 <= head_y < HEIGHT):  # Checks whether the head crossed a board edge.
            self.game_over = True  # Shows the game-over screen after a wall collision.
            return  # Skips further checks after the game ends.
        if (head_x, head_y) in zip(self.snake.x[1:], self.snake.y[1:]):  # Checks whether the head hit another segment.
            self.game_over = True  # Shows the game-over screen after a self-collision.
            return  # Skips food checks after the game ends.

        if (head_x, head_y) == (self.apple.x, self.apple.y):  # Checks whether the snake ate the apple.
            self.snake.grow()  # Adds a segment to the snake.
            occupied_positions = set(zip(self.snake.x, self.snake.y))  # Collects all cells occupied by the snake.
            if not self.apple.move(occupied_positions):  # Tries to place the next apple on an empty cell.
                self.game_over = True  # Ends the game if the snake has filled the board.

    def run(self):  # Runs the game until the player closes the window.
        clock = pygame.time.Clock()  # Creates a timer to control the update rate.
        try:  # Ensures Pygame cleanup runs whether the loop exits normally or raises an error.
            while self.running:  # Repeats frames while the game window is open.
                restarted = False
                # Process input before moving so turns apply on the next game step.
                for event in pygame.event.get():  # Retrieves pending window and keyboard events.
                    if event.type == pygame.QUIT:  # Checks whether the window close button was clicked.
                        self.running = False  # Requests the main loop to stop.
                    elif event.type == pygame.KEYDOWN:  # Checks whether a key was pressed.
                        if self.game_over and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            self.reset()
                            restarted = True
                        elif event.key == pygame.K_ESCAPE:  # Checks whether the Escape key was pressed.
                            self.running = False  # Requests the main loop to stop.
                        elif not self.game_over:  # Handles keys as movement input during a game.
                            self.handle_key(event.key)  # Applies the pressed arrow key to the snake.

                if restarted:
                    clock.tick(FPS)
                    continue

                if self.running and not self.game_over:
                    self.update()  # Advances the game state and checks for collisions.
                if self.running:
                    self.draw()  # Displays the updated board or game-over screen.

                # Keep movement speed steady and allow the window to process events.
                clock.tick(FPS)  # Caps the loop to the configured frame rate.
        finally:  # Always performs cleanup after leaving the game loop.
            if self.music:
                pygame.mixer.music.fadeout(300)
                pygame.time.wait(350)
            pygame.quit()  # Releases Pygame resources even if the loop exits unexpectedly.


if __name__ == "__main__":  # Checks whether this file was launched as the main program.
    Game().run()  # Creates and starts the game.

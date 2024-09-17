import pygame
from singleton import Singleton
from camera import Camera
from player import Player
from level import Level
import settings as config
import csv  # Import the CSV module


class Game(Singleton):
    """
    A class to represent the game.

    used to manage game updates, draw calls and user input events.
    Can be accessed via Singleton: Game.instance .
    (Check Singleton design pattern for more info)
    """

    # constructor called on new instance: Game()
    def __init__(self) -> None:
        # ============= Initialisation =============
        self.__alive = True
        self.__game_over = False  # Flag to track game over state
        self.episode = 1  # Episode counter
        self.max_episodes = 20  # Maximum number of episodes
        self.scores = []  # List to store scores for each episode

        # Window / Render
        self.window = pygame.display.set_mode(config.DISPLAY, config.FLAGS)
        self.clock = pygame.time.Clock()

        # Instances
        self.camera = Camera()
        self.lvl = Level()
        self.player = Player(None,
            config.HALF_XWIN - config.PLAYER_SIZE[0] / 2,  # X POS
            config.HALF_YWIN + config.HALF_YWIN / 2,  # Y POS
            *config.PLAYER_SIZE,  # SIZE
            config.PLAYER_COLOR,  # COLOR
        )

        # User Interface
        self.score = 0
        self.score_txt = config.SMALL_FONT.render("0 m", 1, config.GRAY)
        self.score_pos = pygame.math.Vector2(10, 10)

        self.episode_txt = config.SMALL_FONT.render("Episode: 1", 1, config.GRAY)
        self.episode_pos = pygame.math.Vector2(10, 30)

        # Time
        self.start_time = pygame.time.get_ticks()  # Store the start time
        self.time_font = config.SMALL_FONT  # Font for the timer
        self.time_pos = (config.DISPLAY[0] - 100, 10)

        self.gameover_txt = config.LARGE_FONT.render("Game Over", 1, config.GRAY)
        self.gameover_rect = self.gameover_txt.get_rect(
            center=(config.HALF_XWIN, config.HALF_YWIN)
        )

        # Open CSV files for writing
        self.avg_scores_csv = open('avg_scores.csv', 'w', newline='')
        self.high_scores_csv = open('highest_scores.csv', 'w', newline='')
        self.low_scores_csv = open('lowest_scores.csv', 'w', newline='')
        self.avg_scores_writer = csv.writer(self.avg_scores_csv)
        self.high_scores_writer = csv.writer(self.high_scores_csv)
        self.low_scores_writer = csv.writer(self.low_scores_csv)

    def close(self):
        self.__alive = False

    def reset(self):
        self.__game_over = False
        self.camera.reset()
        self.lvl.reset()
        self.player.reset()
        self.start_time = pygame.time.get_ticks()  # Reset start time to current time

    def _event_loop(self):
        # ---------- User Events ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                if event.key == pygame.K_RETURN and self.player.dead:
                    self.reset()

    def QLearning():
        print("Q Learning Algorithm")

    def _update_loop(self):
        # Calculate elapsed time since the game started
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - self.start_time) / 1000  # Convert to seconds
        
        # ----------- Update -----------
        if not self.__game_over:  # Only update if game is not over
            self.player.random_action()  # Add this line to perform random actions
            self.player.update()
            self.lvl.update()

            self.camera.update(self.player.rect)

            # Calculate score and update UI text
            self.score = -self.camera.state.y // 50
            self.score_txt = config.SMALL_FONT.render(
                str(self.score) + " m", 1, config.GRAY
            )

            # Check if the player is dead and set game over flag
            if self.player.dead:
                self.__game_over = True
                self.scores.append(self.score)  # Store the score for this episode

                # Write score to CSV files
                self.avg_scores_writer.writerow([self.score])
                self.high_scores_writer.writerow([self.score])
                self.low_scores_writer.writerow([self.score])
        if not self.__game_over:
            self.time = elapsed_time

    def _render_loop(self):
        # ----------- Display -----------
        self.window.fill(config.WHITE)
        self.lvl.draw(self.window)
        self.player.draw(self.window)

        # Render the timer text
        if not self.__game_over:
            timer_text = self.time_font.render(
                f"Time: {int(self.time)} s", True, config.GRAY
            )
            self.window.blit(timer_text, self.time_pos)

        # User Interface
        if self.__game_over:
            self.window.blit(self.gameover_txt, self.gameover_rect)  # Game over text

        self.window.blit(self.score_txt, self.score_pos)  # Score text

        self.episode_txt = config.SMALL_FONT.render(f"Episode: {self.episode}", 1, config.GRAY)
        self.window.blit(self.episode_txt, self.episode_pos)  # Episode text

        pygame.display.update()  # Window update
        self.clock.tick(config.FPS)  # Max loop/s


    def run(self):
        # ============= MAIN GAME LOOP =============
        while self.__alive and self.episode <= self.max_episodes:
            self._event_loop()
            self._update_loop()
            self._render_loop()
            if self.__game_over:
                self.episode += 1
                if self.episode <= self.max_episodes:
                    self.reset()
        pygame.quit()


if __name__ == "__main__":
    # ============= PROGRAM STARTS HERE =============
    game = Game()
    game.run()

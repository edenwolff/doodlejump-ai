import pygame
import sys
import csv
from singleton import Singleton
from camera import Camera
from player import Player
from level import Level
import settings as config
import neuralnetwork as nn
import random
import math

class GeneticAlgorithm():
    def __init__(self):
        self.best = Player(nn.NeuralNet(5,4,3), config.HALF_XWIN - config.PLAYER_SIZE[0] / 2,
                           config.HALF_YWIN + config.HALF_YWIN / 2,
                           *config.PLAYER_SIZE,
                           config.PLAYER_COLOR)
        self.doodleplayers = []
        self.bestFitness = 0

    def populate(self, total_agents, best_brain):
        new_players = []
        if best_brain is None:
            for _ in range(total_agents):
                player = Player(nn.NeuralNet(5,4,3), config.HALF_XWIN - config.PLAYER_SIZE[0] / 2,
                                config.HALF_YWIN + config.HALF_YWIN / 2,
                                *config.PLAYER_SIZE,
                                config.PLAYER_COLOR)
                player.dead = False
                new_players.append(player)
        else:
            for _ in range(total_agents):
                player = Player(best_brain, config.HALF_XWIN - config.PLAYER_SIZE[0] / 2,
                                config.HALF_YWIN + config.HALF_YWIN / 2,
                                *config.PLAYER_SIZE,
                                config.PLAYER_COLOR)
                player.dead = False
                new_players.append(player)
        self.doodleplayers = new_players
        return self.doodleplayers

    def AllAgentsDead(self):
        return all(doodle.dead for doodle in self.doodleplayers)

    def highestPlayer(self):
        if not self.doodleplayers:
            return None
        return min(self.doodleplayers, key=lambda player: player.rect.y)
    
    def fittestPlayer(self):
        if not self.doodleplayers:
            return None
        return max(self.doodleplayers, key=lambda player: player.fitness)

    def calculateFitnessSum(self, array):
        return math.floor(sum(p.fitness for p in array))

    def selectRandomAgent(self, array):
        fitnessSum = self.calculateFitnessSum(array)
        rand = random.uniform(0, fitnessSum)
        runningSum = 0

        for b in array:
            runningSum += b.fitness
            if runningSum > rand:
                new_brain = b.brain.clone()
                new_brain.mutate(0.1)
                return new_brain


class Game(Singleton):
    def __init__(self) -> None:
        # ============= Initialization =============
        self.__game_over = False  # Flag to track game over state
        # Window / Render
        self.window = pygame.display.set_mode(config.DISPLAY, config.FLAGS)
        self.clock = pygame.time.Clock()
        self.score = 0
        self.stuck = False
        self.score_last_updated_time = pygame.time.get_ticks()  # Initialize last score update time
        self.score_update_interval = 10000  # 10 seconds in milliseconds

        # Instances
        self.camera = Camera()
        self.lvl = Level()

        # Number of agents that spawn at start of game
        self.TOTAL_AGENTS = 200

        # Number of generations to be born
        self.TOTAL_GENERATIONS = 20

        self.agent_count = self.TOTAL_AGENTS

        self.ga = GeneticAlgorithm()
        self.generation = 1

        # Populate the agent population array
        self.agent_array = self.ga.populate(self.TOTAL_AGENTS, None)

        # User Interface
        self.score_txt = config.SMALL_FONT.render(str(self.score) + " m", 1, config.GRAY)
        self.score_pos = pygame.math.Vector2(10, 10)

        # Time
        self.start_time = pygame.time.get_ticks()  # Store the start time
        self.time_font = config.SMALL_FONT  # Font for the timer
        self.time_pos = (config.DISPLAY[0] - 100, 10)
        self.time = 0

        self.gameover_txt = config.LARGE_FONT.render("Game Over", 1, config.GRAY)
        self.gameover_rect = self.gameover_txt.get_rect(
            center=(config.HALF_XWIN, config.HALF_YWIN)
        )

    def reset(self):
        self.__game_over = False
        self.stuck = False  # Reset stuck condition
        self.camera.reset()
        self.lvl.reset()
        self.start_time = pygame.time.get_ticks()
        self.score = 0
        self.score_last_updated_time = self.start_time  # Reset score update time

    def getHighestScore(self):
        highest_score = 0
        for player in self.ga.doodleplayers:
            if player.fitness > highest_score:
                highest_score = player.fitness
        return highest_score

    def _event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def _update_loop(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - self.start_time) / 1000  # Convert to seconds
        self.time = elapsed_time

        if not self.__game_over:
            for agent in self.ga.doodleplayers:
                if agent is not None:  # Check if agent is not None
                    agent.ai_movement(agent.think(self.lvl.platforms))
                    agent.update()

            self.lvl.update()

            prev_score = self.score
            self.score = -self.camera.state.y // 50
            self.score_txt = config.SMALL_FONT.render(str(self.score) + " m", 1, config.GRAY)
            if self.ga.highestPlayer() is not None:  # Check if highest player is not None
                self.camera.update(self.ga.highestPlayer().rect)

            if self.score != prev_score:
                self.score_last_updated_time = current_time  # Update the last score update time

            if current_time - self.score_last_updated_time >= self.score_update_interval:
                self.stuck = True

            for doodler in self.ga.doodleplayers:
                if doodler is not None:  # Check if doodler is not None
                    if not doodler.dead:
                        doodler.fitness = self.score

            if self.ga.AllAgentsDead() or self.stuck == True:
                self.record_scores()  # Record scores before resetting
                self.reset()
                self.generation += 1

                if self.generation == self.TOTAL_GENERATIONS + 1:
                    self.__game_over = True

                fittest_player_in_current_gen = self.ga.fittestPlayer()
                if fittest_player_in_current_gen.fitness != 0:
                    self.ga.bestFitness = fittest_player_in_current_gen.fitness
                    champion = fittest_player_in_current_gen.clone()

                    parent_doodlers = self.ga.doodleplayers.copy()

                    self.ga.doodleplayers.clear()
                    self.ga.populate(1, champion.brain)

                    champion2 = fittest_player_in_current_gen.clone()
                    champion2.fitness = self.ga.bestFitness

                    self.ga.doodleplayers.append(champion2)
                    self.ga.doodleplayers.reverse()

                    for _ in range(self.TOTAL_AGENTS - 2):
                        parent_brain = self.ga.selectRandomAgent(parent_doodlers)
                        new_player = Player(parent_brain, config.HALF_XWIN - config.PLAYER_SIZE[0] / 2,
                                            config.HALF_YWIN + config.HALF_YWIN / 2,
                                            *config.PLAYER_SIZE,
                                            config.PLAYER_COLOR)
                        self.ga.doodleplayers.append(new_player)

    def _render_loop(self):
        self.window.fill(config.WHITE)
        self.lvl.draw(self.window)

        for player in self.ga.doodleplayers:
            player.draw(self.window)

        if not self.__game_over:
            # Render and display score text
            self.window.blit(self.score_txt, self.score_pos)

            # Render and display generation number text
            generation_text = config.SMALL_FONT.render(
                f"Generation: {self.generation}", True, config.GRAY
            )
            self.generation_pos = (self.score_pos.x, self.score_pos.y + self.score_txt.get_height() + 5)
            self.window.blit(generation_text, self.generation_pos)

            for agent in self.ga.doodleplayers:
                if agent.dead == True:
                    self.agent_count -= 1

            # Render and display timer text
            timer_text = self.time_font.render(
                f"Time: {int(self.time)} s", True, config.GRAY
            )
            self.window.blit(timer_text, self.time_pos)

            # Update agent count
            self.agent_count = sum(not agent.dead for agent in self.ga.doodleplayers)

            # Render and display agent count text
            agent_count_text = config.SMALL_FONT.render(
                f"Agents: {self.agent_count}", True, config.GRAY
            )
            agent_count_pos = (self.generation_pos[0], self.generation_pos[1] + generation_text.get_height() + 5)
            self.window.blit(agent_count_text, agent_count_pos)


        if self.__game_over:
            self.window.blit(self.gameover_txt, self.gameover_rect)

        pygame.display.update()
        self.clock.tick(config.FPS)

    def record_scores(self):
        scores = [player.fitness for player in self.ga.doodleplayers if player.fitness is not None]
        if scores:
            avg_score = sum(scores) / len(scores)
            highest_score = max(scores)
            lowest_score = min(scores)

            with open('avg_scores.csv', 'a', newline='') as avg_file:
                writer = csv.writer(avg_file)
                writer.writerow(['', avg_score])  # Writing to the second column

            with open('highest_scores.csv', 'a', newline='') as high_file:
                writer = csv.writer(high_file)
                writer.writerow(['', highest_score])  # Writing to the second column

            with open('lowest_scores.csv', 'a', newline='') as low_file:
                writer = csv.writer(low_file)
                writer.writerow(['', lowest_score])  # Writing to the second column

    def run(self):
        while not self.__game_over:
            self._event_loop()
            self._update_loop()
            self._render_loop()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

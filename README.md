# Doodle Jump AI Simulation

## Short Description
This repository contains code for simulating Doodle Jump gameplay with different player agents, including a human player, an AI player driven by a genetic algorithm, and a random player. The purpose of this project is to compare the performance of these agents in the Doodle Jump environment and evaluate the effectiveness of using a genetic algorithm for AI training.

## Task Environment
The task environment for this project is based on the [Pygame-DoodleJump](https://github.com/MykleR/Pygame-DoodleJump) repository. This environment provides a basic implementation of the Doodle Jump game, where the player (doodler) navigates a series of randomly spawning platforms by jumping from one platform to another. The player's objective is to climb as high as possible without falling off the screen.

## How to Run the Scripts
To run the simulation with different player agents, follow these instructions:

1. **Main.py** - Human Player:
   - Execute `main.py` to start the game with a human player.
   - Use the arrow keys on the keyboard to control the movement of the player doodler.
   - The game will display the player's score in real-time.

2. **Genetic_algorithm.py** - AI Player:
   - Run `genetic_algorithm.py` to initiate the simulation with an AI player driven by a genetic algorithm.
   - The AI player's behavior is determined by a neural network trained using a genetic algorithm.
   - The script will display the best performing agent's score and number of agents alive throughout the simulation.

3. **Random_player.py** - Random Player:
   - Launch `random_player.py` to start the simulation with a player agent that makes random decisions.
   - The random player's movements are unpredictable, and it does not employ any learning algorithms.
   - The script will display the random player's performance and score throughout the simulation.

Ensure that you have the necessary dependencies installed, including Python and Pygame, to run these scripts successfully. Additionally, feel free to explore and modify the code to experiment with different AI strategies and improve agent performance in the Doodle Jump environment.

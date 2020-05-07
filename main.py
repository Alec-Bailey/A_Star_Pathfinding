__author__ = "Alec Bailey"
__email__ = "alecj.bailley@gmail.com"

import pygame
import random
import math
from queue import PriorityQueue

# Global resolution
RESOLUTION = (600, 600)
TERRAIN_CHANCE = 0.1
SCALE_FACTOR = 10


# Generates a board with random walls
def generate_board(resolution):
    # Subdivide all pixels to scale border pieces up 10x
    x = int(resolution[0] / SCALE_FACTOR)
    y = int(resolution[1] / SCALE_FACTOR)

    # Create the board
    board = []
    for i in range(0, x):
        row = []
        for j in range(0, y):
            if random.random() < TERRAIN_CHANCE:
                row.append(1)
            else:
                row.append(0)
        board.append(row)

    return board


# Returns the euclidean distance between two points on the board
def euclidean_distance(start: tuple, goal: tuple):
    x1x2 = pow(start[0] - start[1], 2)
    y1y2 = pow(goal[0] - goal[1], 2)
    return math.sqrt(x1x2 + y1y2)


# Preforms A* Pathfinding on a a board from a starting position to a goal
def a_star_pathfind(board: list, start: tuple, goal: tuple):
    # Create the priority queue
    states = PriorityQueue
    # Put the initial state in the queue
    states.put(start)


# Defines the main game loop
def main():

    # Initalize pygame
    pygame.init()

    # Load Images
    background = pygame.image.load("background.jpg")
    brick = pygame.image.load("brick.jpg")
    brick = pygame.transform.scale(brick, (SCALE_FACTOR, SCALE_FACTOR))
    player = pygame.image.load("player.jpg")
    player = pygame.transform.scale(player, (SCALE_FACTOR, SCALE_FACTOR))

    # Set title
    pygame.display.set_caption("A* Pathfinding")

    # Set game board
    screen = pygame.display.set_mode(RESOLUTION)

    # Set the background
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Control the game loop
    running = True

    goal_met = True
    # Main game loop
    while running:

        # If the goal has been met, generate a new board
        if goal_met:
            # Generate a board
            board = generate_board(RESOLUTION)

            # Place bricks in the appropriate locations
            for i in range(0, len(board)):
                for j in range(0, len(board)):
                    if board[i][j] == 1:
                        screen.blit(brick, (SCALE_FACTOR * i, SCALE_FACTOR * j))
            pygame.display.flip()
            goal_met = False


        # Iterate over all events
        for event in pygame.event.get():
            # Quit game on clicking exit button
            if event.type == pygame.QUIT:
                running = False
                break
            # Reset the game board
            if event.type == pygame.MOUSEBUTTONDOWN:
                goal_met = True
                screen.blit(background, (0,0))
                pygame.display.flip()
        pass


# Prevent execution on imports
if __name__ == "__main__":
    main()
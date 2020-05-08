__author__ = "Alec Bailey"
__email__ = "alecj.bailley@gmail.com"

import pygame
import random
import math
import time

# Global resolution
RESOLUTION = (600, 600)
TERRAIN_CHANCE = 0.1
SCALE_FACTOR = 10
PATH_MOVE_TIME = 0.08
VERTICAL_LINES = 3
VERTICAL_SIZE = 15
HORIZONTAL_LINES = 3
HORIZONTAL_SIZE = 15
L_SHAPES = 3


class PriorityQueue(object):
    def __init__(self):
        self.queue = []
        self.max_len = 0

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    def is_empty(self):
        return len(self.queue) == 0

    def enqueue(self, state_dict):
        in_open = False
        # Iterate through all entries in queue and check if state already exists in queue
        for entry in self.queue:
            if entry['state'] == state_dict['state']:
                # Set that state already exists in queue
                in_open = True
                # Replace the existing state in the queue with state_dict if it is more efficient
                if entry['f'] > state_dict['f']:
                    entry = state_dict

        if not in_open:
            self.queue.append(state_dict)

        # track the maximum queue length
        if len(self.queue) > self.max_len:
            self.max_len = len(self.queue)

    def requeue(self, from_closed):
        """ Re-queue a dictionary from the closed list (see lecture slide 21)
        """
        self.queue.append(from_closed)

        # track the maximum queue length
        if len(self.queue) > self.max_len:
            self.max_len = len(self.queue)

    def pop(self):
        """ Remove and return the dictionary with the smallest f(n)=g(n)+h(n)
        """
        minf = 0
        for i in range(1, len(self.queue)):
            if self.queue[i]['f'] < self.queue[minf]['f']:
                minf = i
        state = self.queue[minf]
        del self.queue[minf]
        return state


# Generates a board with random walls
def generate_board(resolution):
    # Subdivide all pixels to scale border pieces up 10x
    x = int(resolution[0] / SCALE_FACTOR)
    y = int(resolution[1] / SCALE_FACTOR)

    # Create the board
    board = []
    for i in range(0, x):
        board.append([0] * y)

    # Create vertical lines on the board
    for vert in range(0, VERTICAL_LINES):
        # Randomly select a column to place the line in
        col = random.randint(0, len(board[0]))
        for i in range(0, VERTICAL_SIZE):
            board[i][col] = 1

    # Create horizontal lines on the board
    for hor in range(0, HORIZONTAL_LINES):
        # Randomly select a row the place the line in
        row = random.randint(0, len(board))
        for i in range(0, HORIZONTAL_SIZE):
            board[row][i] = 1

    # Add some random noise
    for i in range(0, y):
        for j in range(0, x):
            if random.random() < TERRAIN_CHANCE:
                board[i][j] = 1

    return board


# Returns the euclidean distance between two points on the board
def euclidean_distance(start: tuple, goal: tuple):
    x1x2 = pow(start[0] - goal[0], 2)
    y1y2 = pow(start[1] - goal[1], 2)
    return int(math.sqrt(x1x2 + y1y2))


# Returns a list of all possible successor moves
def get_successors(board: list, position: tuple, goal: tuple):
    successors = []
    # Get all possible moves including diagonals
    for i in range(-1, 2):
        for j in range(-1, 2):
            # Exclude non-moves
            if not (i == 0 and j == 0):
                # Add viable successors
                try:
                    if board[position[0] + i][position[1] + j] == 0:
                        if position[0] + i >= 0 and position[1] + j >= 0:
                            successors.append((position[0] + i, position[1] + j))
                # Do not add out of bounds successors
                except IndexError:
                    pass
    return successors


# Preforms A* Pathfinding on a a board from a starting position to a goal
def a_star_pathfind(board: list, start: tuple, goal: tuple):
    # Create the priority queue
    queue = PriorityQueue()
    # Put the initial state in the queue
    state = {'state': start, 'parent': None, 'h': euclidean_distance(start, goal),
             'g': 0, 'f': euclidean_distance(start, goal)}
    queue.enqueue(state)
    # Create the solution and closed lists
    solution = []
    closed = []

    # Continue search while the goal is not met
    while not queue.is_empty():

        # Pop the top off of the queue and add to closed
        top = queue.pop()
        closed.append(top)

        # Get the state from the parent in the queue
        state = top['state']

        # Break from the search if the goal is met
        if state == goal:
            break

        # Get all successors of the parent
        successors = get_successors(board, state, goal)

        # Generate and add states to queue from parent
        for succ in successors:
            # Flag set if a state is found in closed
            found_in_closed = False

            # Create the successor dictionary
            succ_dict = {'state': succ, 'parent': top, 'h': euclidean_distance(succ, goal), 'g': top['g'] + 1,
                         'f': top['g'] + 1 + euclidean_distance(succ, goal)}

            # Check if there are better states in the closed list
            for closed_state in closed:
                if closed_state['state'] == succ:
                    # Set found flag
                    found_in_closed = True
                    # Create a successor dictionary
                    # If the total cost in the successor is less than the total cost in the closed, requeue the successor
                    if succ_dict['f'] < closed_state['f']:
                        closed.remove(closed_state)
                        queue.requeue(succ_dict)
            # If the successor was not found in closed, queue the successor
            if not found_in_closed:
                queue.enqueue(succ_dict)

        # Get the solutions in order
    while top['parent'] is not None:
        solution.append(top['state'])
        top = top.get('parent')
    solution.append(top['state'])

    # Return the solution list, reversed to move in order First Move -> Last Move
    for row in board:
        print(row)
    print('\n\n')
    solution.reverse()
    print(solution, '\n')
    return solution


# Defines the main game loop
def main():

    start = (0, 0)
    goal = (59, 59)

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
        board = generate_board(RESOLUTION)
        # If the goal has been met, generate a new board
        # Generate a board
        #board = generate_board(RESOLUTION)

        # Reset the background
        screen.blit(background, (0, 0))

        print('CUCK BOARD')
        for row in board:
            print(row)
        print('CUCK BOARD')
        # Place bricks in the appropriate locations
        for i in range(0, len(board)):
            for j in range(0, len(board)):
                if board[i][j] == 1:
                    screen.blit(brick, (SCALE_FACTOR * j, SCALE_FACTOR * i))
                    #screen.blit(brick, (SCALE_FACTOR * 1, SCALE_FACTOR * 2))
                    print('row', i, 'col', j)
        pygame.display.flip()

        # Calculate the path with A star
        path = a_star_pathfind(board, start, goal)
        for move in path:
            # Display the player object in the path
            screen.blit(player, (SCALE_FACTOR * move[1], SCALE_FACTOR * move[0]))
            pygame.display.flip()
            time.sleep(PATH_MOVE_TIME)
            goal_met = True

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
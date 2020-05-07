__author__ = "Alec Bailey"
__email__ = "alecj.bailley@gmail.com"

import pygame
import random
import math

# Global resolution
RESOLUTION = (600, 600)
TERRAIN_CHANCE = 0.1
SCALE_FACTOR = 10


class PriorityQueue(object):
    def __init__(self):
        self.queue = []
        self.max_len = 0

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    def is_empty(self):
        return len(self.queue) == 0

    def enqueue(self, state_dict):
        """ Items in the priority queue are dictionaries:
             -  'state': the current state of the puzzle
             -      'h': the heuristic value for this state
             - 'parent': a reference to the item containing the parent state
             -      'g': the number of moves to get from the initial state to
                         this state, the "cost" of this state
             -      'f': the total estimated cost of this state, g(n)+h(n)
            For example, an item in the queue might look like this:
             {'state':[1,2,3,4,5,6,7,8,0], 'parent':[1,2,3,4,5,6,7,0,8],
              'h':0, 'g':14, 'f':14}
            Please be careful to use these keys exactly so we can test your
            queue, and so that the pop() method will work correctly.
        """

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
    return int(math.sqrt(x1x2 + y1y2))


# Returns a list of all possible successor moves
def get_successors(board: list, position: tuple, goal: tuple):
    successors = []
    # Get all possible moves including diagonals
    for i in range(-1,2):
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
    state = {'state': start, 'parent' : None, 'h': euclidean_distance(start, goal), 'g': 0, 'f': euclidean_distance(start, goal)}
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
            succ_dict = {'state': succ, 'h': euclidean_distance(succ, goal), 'g': top['g'] + 1,
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
            solution.append(top)
            top = top.get('parent')
        solution.append(top)

        # Return the solution list
        return solution

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
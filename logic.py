
import random
from tkinter import OFF # lets us pick random moves when generating a board

# CONSTANTS
GRID_SIZE = 5  # Size of the grid (5x5)
LIGHTS_ON = 1 
LIGHTS_OFF = 0
TOTAL_LIGHTS = GRID_SIZE * GRID_SIZE

# When clicking, the light itself and its adjacent lights (up, down, left, right)
offsets = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]  # (row_offset, col_offset)

# This function is mainly for checking if the row and col are integers and not boolean values 
def is_valid_position(row, col):
    if isinstance(row, bool) or isinstance(col, bool):
        return False
    if isinstance(row, int) and isinstance(col, int):
        return False
    return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE


# the toggle function is the main function that is used to change the state of the light on the board.
# It returns a brand new baord with the changes after clicking the light, which ever that may be. 
# It does not change the original board, and also gives out a value error if the row and col are not in range of the given boundaries.
def toggle(board, row, col):
    # need something to make a copy of the board so that we can return a new board with the changes after clicking the light. 

    new_board = [list(current_row) for current_row in board]  # Create a copy of the board
    if not is_valid_position (row, col):
        raise ValueError("Row and Column must be integers within the accepted range given the grid size.")
    for row_offset, col_offset in offsets:
        target_row = row + row_offset
        target_col = col + col_offset

        if is_valid_position(target_row, target_col):
            if new_board[target_row][target_col] == OFF:
                new_board[target_row][target_col] = ON
            else:
                new_board[target_row][target_col] = OFF

    return new_board

# This is the simplest function in the code that checks if the board is solved or not.
# It checks if all the lights are off (False) and returns True if they are, otherwise it returns False.
def is_solved(board):
    for row in board:
        for light in row:
            if light != OFF:
                return False
    return True

# generates a board with a random configuration of lights on and off
def generate_board():
    board = [[OFF for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    num_random_clicks = random.randint(1, TOTAL_CELLS)

    random_row = random.randrange(GRID_SIZE)
    random_col = random.randrange(GRID_SIZE)
    board = toggle(board, random_row, random_col)

    while is_solved(board):
        random_row = random.randrange(GRID_SIZE)
        random_col = random.randrange(GRID_SIZE)
        board = toggle(board, random_row, random_col)

    return board

   
# hardest function, will be hard to code, idk how to do it yet, but will be a function that gives a hint to the user on what to do next.
#def hint(board):
    

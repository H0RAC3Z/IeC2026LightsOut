from django.db import models
import random
from itertools import product

# Create your models here.
class LightsOut(models.Model):
    board = [
        [1,0,0,0,0],
        [0,1,0,0,0],
        [0,1,0,0,0],
        [0,1,0,0,0],
        [0,0,0,0,0]
    ]
    # CONSTANTS
    GRID_SIZE = 5  # Size of the grid (5x5)
    LIGHTS_ON = 1 
    LIGHTS_OFF = 0
    TOTAL_LIGHTS = GRID_SIZE * GRID_SIZE
    move_counter = 0
    time = "00:00:00"

    # When clicking, the light itself and its adjacent lights (up, down, left, right)
    offsets = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]  # (row_offset, col_offset)


    # This function is mainly for checking if the row and col are integers and not boolean values 
    def is_valid_position(self, row, col):
        if isinstance(row, bool) or isinstance(col, bool):
            return False
        if not isinstance(row, int) or not isinstance(col, int):
            return False
        
        return 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE


    # the toggle function is the main function that is used to change the state of the light on the board.
    # It returns a brand new baord with the changes after clicking the light, which ever that may be. 
    # It does not change the original board, and also gives out a value error if the row and col are not in range of the given boundaries.
    def toggle(self, board, row, col):
        # need something to make a copy of the board so that we can return a new board with the changes after clicking the light. 

        new_board = [list(current_row) for current_row in board]  # Create a copy of the board
        if not self.is_valid_position (row, col):
            raise ValueError("Row and Column must be integers within the accepted range given the grid size.")
        for row_offset, col_offset in self.offsets:
            target_row = row + row_offset
            target_col = col + col_offset

            if self.is_valid_position(target_row, target_col):
                if new_board[target_row][target_col] == self.LIGHTS_OFF:
                    new_board[target_row][target_col] = self.LIGHTS_ON
                else:
                    new_board[target_row][target_col] = self.LIGHTS_OFF

        return new_board

    # This is the simplest function in the code that checks if the board is solved or not.
    # It checks if all the lights are off (False) and returns True if they are, otherwise it returns False.
    def is_solved(self, board):
        for row in board:
            for light in row:
                if light != self.LIGHTS_OFF:
                    return False
        return True

    # generates a board with a random configuration of lights on and off
    def generate_board(self):
        board = [[self.LIGHTS_OFF for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        num_random_clicks = random.randint(1, self.TOTAL_LIGHTS)

        for _ in range(num_random_clicks):
            random_row = random.randrange(self.GRID_SIZE)
            random_col = random.randrange(self.GRID_SIZE)
            board = self.toggle(board, random_row, random_col)
        

        while self.is_solved(board):
            random_row = random.randrange(self.GRID_SIZE)
            random_col = random.randrange(self.GRID_SIZE)
            board = self.toggle(board, random_row, random_col)

        return board

    def get_board(self):
        return self.board

    def set_board(self, board):
        self.board = board

    def get_hint(self, board):
        # Try every possible on/off combination across the first row.
        for first_row in product([False, True], repeat=self.GRID_SIZE):
            # Work on a copy so checking a possible solution does not change the real board.
            candidate = [list(row) for row in board]
            # Remember the first press in this possible solution to use as the hint.
            first_move = None

            # Apply the presses represented by the current first-row combination.
            for col, should_press in enumerate(first_row):
                if should_press:
                    candidate = self.toggle(candidate, 0, col)
                    first_move = (0, col) if first_move is None else first_move

            # For each later row, press below any light that is still on above it.
            for row in range(1, self.GRID_SIZE):
                for col in range(self.GRID_SIZE):
                    if candidate[row - 1][col] == self.LIGHTS_ON:
                        # This is forced: no later press can change the row above it.
                        candidate = self.toggle(candidate, row, col)
                        if first_move is None:
                            first_move = (row, col)

            # If the final row is clear, this first press belongs to a valid solution.
            if self.is_solved(candidate):
                return first_move

        # None of the possible first-row patterns solved this board.
        return None

    def get_move_counter(self):
        return self.move_counter


    class Meta:
        managed = False # makes sure database doesn't create a database for this model

from django.db import models

# Create your models here.
class LightsOut(models.Model):
    board = [
        [1,0,0,0,0],
        [0,1,0,0,0],
        [0,1,0,0,0],
        [0,1,0,0,0],
        [0,0,0,0,0]
    ]

    def toggle(self, board, row, col):
        if board[row][col] is 0:
            board[row][col] = 1
        else:
            board[row][col] = 0

    # def is_solved(self, board):


    # def generate_board(self):

    class Meta:
        managed = False # makes sure database doesn't create a database for this model
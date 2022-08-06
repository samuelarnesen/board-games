from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from django.views.decorators.csrf import csrf_exempt

import warnings
from django.http import HttpResponse

import random, copy
import numpy as np
from .apps import AiConfig
# Create your views here.

def index(request):
    return HttpResponse("Test flight")

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_move(request):
    """
    Returns a move
    """
    board = filter_board(request.data['board'])
    # You now have the board as data. Implement your logic

    # This is a fast way to check who wins.
    # There is also a fast way to implement moves.
    """
    p1_bitmap, mask = make_bitmap(board)
    p2_bitmap = p1_bitmap ^ mask
    if check_bitmap_board(p1_bitmap):
        print("Player 1 wins!")
    elif check_bitmap_board(p2_bitmap):
        print("Player 2 wins!")
    """




    # Return the move as an integer 0 through 6 inclusive
    board = np.asarray(board, dtype=np.float64)
    board = copy.deepcopy(np.flip(board, axis=0))

    turn = 1 if np.sum(board) == 0 else -1


    AiConfig.engine.set_state(board, turn)
    winner = AiConfig.engine.find_winner()
    if winner != None:
        print(f"{winner} wins!")

    AiConfig.aiplayer.set_state(board, turn)

    move = AiConfig.aiplayer.poll((board, turn), training=False)
    return Response(move)

def filter_board(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] is None:
                board[i][j] = 0
    return board


def make_bitmap(board):
    """
    Makes a mask using player1
    """
    player, mask = "", ""
    for j in range(6, -1, -1):
        mask += "0"
        player += "0"
        for i in range(6):
            if board[i][j] == 1:
                player += "1"
                mask += "1"
            elif board[i][j] == -1:
                mask += "1"
                player += "0"
            else:
                mask += "0"
                player += "0"
    return int(player, 2), int(mask, 2)

def check_bitmap_board(player):
    """
    Fast checking using bitstrings. Checks if player 1 has won.
    """
    w = player & (player >> 7)
    if w & (w >> 14):
        return True
    w = player & (player >> 1)
    if w & (w >> 2):
        return True
    w = player & (player >> 6)
    if w & (w >> 12):
        return True
    w = player & (player >> 8)
    if w & (w >> 16):
        return True
    return False
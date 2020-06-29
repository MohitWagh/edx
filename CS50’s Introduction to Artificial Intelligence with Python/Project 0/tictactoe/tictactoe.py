"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    number_of_x = 0
    number_of_o = 0
    for i in board:
        for j in i:
            if j == X:
                number_of_x += 1
            elif j == O:
                number_of_o += 1
    if number_of_x == number_of_o:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    set_of_actions = set()
    for i in range(0, 3):
        for j in range(0, 3):
            if board[i][j] == EMPTY:
                set_of_actions.add((i, j))
    return set_of_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    next_player = player(board)
    new_board = initial_state()
    for i in range(0, 3):
        for j in range(0, 3):
            new_board[i][j] = board[i][j]
    new_board[action[0]][action[1]] = next_player
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in board:
        if (i[0] != EMPTY) & (i[0] == i[1]) & (i[1] == i[2]):
            return i[0]
    for i in range(0, 3):
        if (board[0][i] != EMPTY) & (board[0][i] == board[1][i]) & (board[1][i] == board[2][i]):
            return board[0][i]
    if (board[0][0] != EMPTY) & (board[0][0] == board[1][1]) & (board[1][1] == board[2][2]):
        return board[0][0]
    if (board[0][2] != EMPTY) & (board[0][2] == board[1][1]) & (board[1][1] == board[2][0]):
        return board[0][2]
    return EMPTY


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return (len(actions(board)) == 0) | (winner(board) != EMPTY)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winner_of_game = winner(board)
    if winner_of_game == X:
        return 1
    elif winner_of_game == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    turn = player(board)
    if turn == X:
        (_, best_action) = maximise(board)
    else:
        (_, best_action) = minimise(board)
    return best_action


def maximise(board):
    """
    Maximise board from current state.
    """
    best_utility = -math.inf
    best_action = None
    possible_actions = actions(board)
    for action in possible_actions:
        new_board = result(board, action)
        if terminal(new_board):
            new_utility = utility(new_board)
        else:
            (new_utility, _) = minimise(new_board)
        if new_utility > best_utility:
            best_utility = new_utility
            best_action = action
    return best_utility, best_action


def minimise(board):
    """
    Minimise board from current state.
    """
    best_utility = math.inf
    best_action = None
    possible_actions = actions(board)
    for action in possible_actions:
        new_board = result(board, action)
        if terminal(new_board):
            new_utility = utility(new_board)
        else:
            (new_utility, _) = maximise(new_board)
        if new_utility < best_utility:
            best_utility = new_utility
            best_action = action
    return best_utility, best_action

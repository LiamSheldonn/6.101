"""
6.1010 Lab 4:
Snekoban Game
"""

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def update_pos(current, dir):
    out = []
    for i,j in zip(current, direction_vector[dir]):
        out.append(i+j)
    return tuple(out)

def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    out = {}
    out['height'] = len(level_description)
    out['width'] = len(level_description[0])
    for r, row in enumerate(level_description):
        for c, cell in enumerate(row):
            out[(r,c)] = set(cell)
            if 'player' in cell:
                out[(r,c)].remove('player')
                out['player'] = (r,c)
    return out


def check_obj(game, obj, pos):
    return obj in game[pos]


def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """
    atLeastOneTarget = False
    for r in range(game['height']):
        for c in range(game['width']):
            if game[(r,c)] == {'target'}:
                return False
            elif game[(r,c)] == {'target', 'computer'}:
                atLeastOneTarget = True
    if atLeastOneTarget:
        return True
    else:
        return False

def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a new game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    out = {}

    for r in range(game['height']):
        for c in range(game['width']):
            out[(r,c)] = game[(r,c)].copy()

    out['height'], out['width'], out['player'] = game['height'], game['width'], game['player'][:]
    

    newPlayerPos = update_pos(game['player'], direction)
    
    if check_obj(game, 'wall', newPlayerPos):
        pass
    elif check_obj(game, 'computer', newPlayerPos):
        newCompPos = update_pos(newPlayerPos,direction)
        if not (check_obj(game, 'wall', newCompPos) or check_obj(game, 'computer', newCompPos)):
            out[newCompPos].add('computer')
            out[newPlayerPos].remove('computer')
            out['player'] = newPlayerPos
    else:
        out['player'] = newPlayerPos
    return out


def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """

    out = []
    print(game['player'])

    for r in range(game['height']):
        newrow = []
        for c in range(game['width']):
            newrow.append(list(game[(r,c)]))
        out.append(newrow)
    
    out[game['player'][0]][game['player'][1]].append('player')
    print(out[game['player'][0]][game['player'][1]])

    return out



def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    if victory_check(game):
        return []
    all_paths = [[]]

if __name__ == "__main__":
    test_rep = [
        [ ["wall"],  ["wall"],     ["wall"],     ["wall"],     ["wall"],     ["wall"], ["wall"] ],
        [ ["wall"],  ["target"],   ["wall"],     [],           [],           [],       ["wall"] ],
        [ ["wall"],  ["target"],   ["player"],   ["computer"], ["computer"], [],       ["wall"] ],
        [ ["wall"],  [],           ["computer"], [],           [],           [],       ["wall"] ],
        [ ["wall"],  ["target"],   [],           [],           [],           [],       ["wall"] ],
        [ ["wall"],  ["wall"],     ["wall"],     ["wall"],     ["wall"],     ["wall"], ["wall"] ]
        ]
    int_rep = make_new_game(test_rep)
    new_test_rep = dump_game(int_rep)


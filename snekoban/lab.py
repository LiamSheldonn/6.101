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


def update_pos(current, direction):
    return tuple(i + j for (i, j) in zip(current, direction_vector[direction]))


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
    convert = {"wall": 1, "computer": 2, "target": 3}
    out = [len(level_description), len(level_description[0])]
    for r, row in enumerate(level_description):
        for c, cell in enumerate(row):
            newcell = cell[:]
            if "player" in newcell:
                newcell.remove("player")
                out.insert(0, (r, c))
            out.append(sum(convert[item] for item in newcell))
    return out


def get_val(game, r, c):
    height, width = game[1:3]
    if r >= height or c >= width:
        raise IndexError(f"{r,c} out of range for {width,height}")
    return game[3:][r * width + c]


def set_val(game, r, c, val):
    height, width = game[1:3]
    if r >= height or c >= width:
        raise IndexError(f"{r,c} out of range for {width,height}")
    game[r * width + c + 3] = val


def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """
    return 3 not in game[3:] and 5 in game[3:]


def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a new game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    p_pos = game[0]
    out = game[:]

    new_player_pos = update_pos(p_pos, direction)

    new_player_pos_val = get_val(out, *new_player_pos)

    if new_player_pos_val == 1:
        pass
    elif new_player_pos_val in {2,5}:
        new_comp_pos = update_pos(new_player_pos, direction)
        new_comp_pos_val = get_val(out, *new_comp_pos)
        if new_comp_pos_val not in {1,2,5}:
            set_val(out, *new_comp_pos, new_comp_pos_val + 2)
            set_val(out, *new_player_pos, new_player_pos_val - 2)
            out[0] = new_player_pos
    else:
        out[0] = new_player_pos

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
    decode = {
        0: [],
        1: ["wall"],
        2: ["computer"],
        3: ["target"],
        5: ["target", "computer"],
    }
    p_pos, _, width = game[:3]
    board = game[3:]
    out = []
    for i, x in enumerate(board):
        if i % width == 0:
            out.append([decode[x]])
        else:
            out[-1].append(decode[x])

    out[p_pos[0]][p_pos[1]] = out[p_pos[0]][p_pos[1]] + ["player"]

    return out


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    possible_moves = ["up", "right", "down", "left"]
    if victory_check(game):
        return []
    all_paths = [[]]
    corresponding_states = [game]
    already_checked = {tuple(game)}
    while corresponding_states:
        parent_state = corresponding_states.pop(0)
        parent_path = all_paths.pop(0)
        for move in possible_moves:
            child_state = step_game(parent_state, move)
            child_state_tuple = tuple(child_state)
            if child_state_tuple not in already_checked:
                all_paths.append(parent_path + [move])
                corresponding_states.append(child_state)
                already_checked.add(child_state_tuple)
                if victory_check(child_state):
                    print("Found.")
                    return all_paths[-1]
    return None


if __name__ == "__main__":
    test_rep = [
        [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]],
        [["wall"], ["target"], ["wall"], [], [], [], ["wall"]],
        [["wall"], ["target"], ["player"], ["computer"], ["computer"], [], ["wall"]],
        [["wall"], [], ["computer"], [], [], [], ["wall"]],
        [["wall"], ["target"], [], [], [], [], ["wall"]],
        [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]],
    ]
    int_rep = make_new_game(test_rep)
    print(int_rep)
    new_test_rep = dump_game(int_rep)
    print(new_test_rep == test_rep)

import copy
from game import get_valid_moves, switch_turn, apply_move


def heuristic(state, new_state):
    current_player = state['current_player']
    if current_player ==0:
        old_computer_pieces = state['player2_pieces']
        old_human_pieces = state['player1_pieces']
        new_computer_pieces = new_state['player2_pieces']
        new_human_pieces = new_state['player1_pieces']
        old_computer_box = state['white_box']
        old_human_box = state['black_box']
        new_computer_box = new_state['white_box']
        new_human_box = new_state['black_box']
        
    score = 0

    sum_old_computer = sum(old_computer_pieces)
    sum_new_computer = sum(new_computer_pieces)
    if sum_new_computer > sum_old_computer:
        score += sum_new_computer - sum_old_computer
    elif sum_new_computer < sum_old_computer:
        score -= sum_old_computer - sum_new_computer   

    sum_old_human = sum(old_human_pieces)
    sum_new_human = sum(new_human_pieces)
    if sum_new_human > sum_old_human:
        score -= sum_new_human - sum_old_human
    elif sum_new_human < sum_old_human:
        score += sum_old_human - sum_new_human

    for piece in new_computer_pieces:
        if piece == 23:
            score += 2*(6/16)
        elif piece == 24:
            score +=  4/16
        elif piece == 22:
            score += 2 *(4/16)
        elif piece == 26:
            score -= 20
        elif piece == 27:
            score -=2*(4/16)
        elif piece == 28:
            score -=6/16
        elif piece ==29:
            score +=6

    if new_computer_box > old_computer_box:
        score += 6
    if new_human_box > old_human_box:
        score -= 6

    sorted_computer = sorted(new_computer_pieces)
    sorted_human = sorted(new_human_pieces)

    prob = {1: 4/16,
            2: 6/16,
            3: 4/16}

    for computer_piece, human_piece in zip(sorted_computer, sorted_human):
        diff = abs(computer_piece - human_piece)

        if diff in (1, 2, 3):
            if computer_piece > human_piece:
                score -= diff * prob[diff]

            elif computer_piece < human_piece:
                score += diff * prob[diff]

    return score

######################################

def  expectiminimax(root_state, state, node_type, depth):
    if state['game_over'] or depth == 0:
        return heuristic(root_state , state), None

    if node_type == "chance":
        expected_value = 0
        best_move = None
        dice_probs = {1: 4 / 16, 2: 6 / 16, 3: 4 / 16, 4: 1 / 16, 5: 1 / 16}
        for dice_value, prob in dice_probs.items():
            new_state = copy.deepcopy(state)
            new_state['dice_value'] = dice_value

            valid_moves = get_valid_moves(new_state, dice_value)

            if not valid_moves:
                switch_turn(new_state)
                next_node = "max" if new_state['current_player'] == 0 else "min"
                value, _ = expectiminimax(root_state, new_state, next_node, depth - 1)
            else :
                next_node = "max" if new_state['current_player'] == 0 else "min"
                value, _ = expectiminimax(root_state, new_state, next_node, depth)

            expected_value += prob * value

        return expected_value, None

    elif node_type == "max":
        best_value = -float('inf')
        best_move = None

        dice = state['dice_value']
        valid_moves = get_valid_moves(state, dice)

        if not valid_moves:
            new_state = copy.deepcopy(state)
            switch_turn(new_state)
            value, _ = expectiminimax(root_state, new_state, "min", depth-1)
            return value, None

        for move in valid_moves:
            new_state = copy.deepcopy(state)
            apply_move(new_state, move[0], move[1], valid_moves)
            switch_turn(new_state)
            value, _ = expectiminimax(root_state, new_state, "chance", depth-1)
            if value > best_value:
                best_value = value
                best_move = move
        return best_value, best_move

    elif node_type == "min":
        worst_value = float('inf')
        worst_move = None

        dice = state['dice_value']
        valid_moves = get_valid_moves(state, dice)

        if not valid_moves:
            new_state = copy.deepcopy(state)
            switch_turn(new_state)
            value, _ = expectiminimax(root_state, new_state, "max", depth-1)
            return value, None

        for move in valid_moves:
            new_state = copy.deepcopy(state)
            apply_move(new_state, move[0], move[1], valid_moves)
            switch_turn(new_state)

            value, _ = expectiminimax(root_state, new_state, "chance", depth-1)

            if value < worst_value:
                worst_value = value
                worst_move = move
        return worst_value, worst_move

    else:
        return ValueError("unknown node type")


import copy
from game import get_valid_moves, switch_turn, apply_move

node_counter = 0


def heuristic(state, new_state):
    current_player = state['current_player']
    if current_player == 0:
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
        score -= (sum_new_human - sum_old_human) * 3
    elif sum_new_human < sum_old_human:
        score += (sum_old_human - sum_new_human) * 3

    for piece in new_computer_pieces:
        if piece == 23:
            score += 2*(6/16)
        elif piece == 24:
            score += 4/16
        elif piece == 22:
            score += 2*(4/16)
        elif piece == 25:
            score += 30
        elif piece == 26:
            score -= 30
        elif piece == 27:
            score -= 2*(4/16)
        elif piece == 28:
            score -= 6/16
        elif piece == 29:
            score += 50
        elif piece == 30:
            score += 70

    if new_computer_box > old_computer_box:
        score += 100
    if new_human_box > old_human_box:
        score -= 70

    sorted_computer = sorted(new_computer_pieces)
    sorted_human = sorted(new_human_pieces)

    prob = {1: 4/16,
            2: 6/16,
            3: 4/16}

    for computer_piece, human_piece in zip(sorted_computer, sorted_human):
        diff = abs(computer_piece - human_piece)

        if diff in (1, 2, 3):
            if computer_piece > human_piece:
                score -= (diff * prob[diff]) * 2
            elif computer_piece < human_piece:
                score += (diff * prob[diff]) * 2

    return score


def expectiminimax(root_state, state, node_type, depth, debug=False, original_depth=None):
    global node_counter
    node_counter += 1

    if original_depth is None:
        original_depth = depth

    indent = "    " * (original_depth - depth)

    if debug:
        print(f"{indent}>> Enter {node_type.upper()} node | depth={depth}, player={state['current_player']}")

    if state['game_over'] or depth == 0:
        h = heuristic(root_state, state)
        if debug:
            print(f"{indent} Terminal node → heuristic = {h}")
        return h, None

    if node_type == "chance":
        expected_value = 0
        dice_probs = {1: 4/16, 2: 6/16, 3: 4/16, 4: 1/16, 5: 1/16}

        if debug:
            print(f"{indent} CHANCE node evaluating dice outcomes ")

        for dice_value, prob in dice_probs.items():
            new_state = copy.deepcopy(state)
            new_state['dice_value'] = dice_value

            valid_moves = get_valid_moves(new_state, dice_value)

            if not valid_moves:
                switch_turn(new_state)
                next_node = "max" if new_state['current_player'] == 0 else "min"
                value, _ = expectiminimax(root_state, new_state, next_node, depth - 1, debug, original_depth)
            else:
                next_node = "max" if new_state['current_player'] == 0 else "min"
                value, _ = expectiminimax(root_state, new_state, next_node, depth, debug, original_depth)

            weighted = prob * value
            expected_value += weighted

            if debug:
                print(f"{indent} Dice={dice_value}, prob={prob}, value={value}, weighted={weighted}")

        if debug:
            print(f"{indent}   CHANCE returns {expected_value}")

        return expected_value, None

    elif node_type == "max":
        best_value = -float('inf')
        best_move = None

        dice = state['dice_value']
        valid_moves = get_valid_moves(state, dice)

        if debug:
            print(f"{indent}   MAX node: valid moves = {valid_moves}")

        if not valid_moves:
            new_state = copy.deepcopy(state)
            switch_turn(new_state)
            value, _ = expectiminimax(root_state, new_state, "min", depth - 1, debug, original_depth)
            return value, None

        for move in valid_moves:
            new_state = copy.deepcopy(state)
            apply_move(new_state, move[0], move[1], valid_moves)
            switch_turn(new_state)

            value, _ = expectiminimax(root_state, new_state, "chance", depth - 1, debug, original_depth)

            if debug:
                print(f"{indent}      MAX testing move {move} → value={value}")

            if value > best_value:
                best_value = value
                best_move = move

        if debug:
            print(f"{indent}   MAX returns {best_value} with move {best_move}")

        return best_value, best_move

    elif node_type == "min":
        worst_value = float('inf')
        worst_move = None

        dice = state['dice_value']
        valid_moves = get_valid_moves(state, dice)

        if debug:
            print(f"{indent}   MIN node: valid moves = {valid_moves}")

        if not valid_moves:
            new_state = copy.deepcopy(state)
            switch_turn(new_state)
            value, _ = expectiminimax(root_state, new_state, "max", depth - 1, debug, original_depth)
            return value, None

        for move in valid_moves:
            new_state = copy.deepcopy(state)
            apply_move(new_state, move[0], move[1], valid_moves)
            switch_turn(new_state)

            value, _ = expectiminimax(root_state, new_state, "chance", depth - 1, debug, original_depth)

            if debug:
                print(f"{indent}      MIN testing move {move} → value={value}")

            if value < worst_value:
                worst_value = value
                worst_move = move

        if debug:
            print(f"{indent}   MIN returns {worst_value} with move {worst_move}")

        return worst_value, worst_move

    else:
        return ValueError("unknown node type")

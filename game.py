import random
from typing import Dict, Any

from expectiminimax import expectiminimax

# checked by suliman
state : Dict[str, Any] = {
    'board': [0] * 30,

    'player1_pieces': set(),

    'player2_pieces': set(),

    # 1 is black, 0 is white
    'player_ids': [0, 1],

    'current_player': 0,

    'dice_value': 0,
    # white/black box stores the number of the player's pieces that have exited the board
    'white_box' : 0,

    'black_box' : 0,

    'game_over': False,

    'winner': None
}

# checked by suliman
def init_game(state: Dict[str, Any]):

    state['board'] = [0] * 30

    # player 2 white
    for i in [0, 2, 4, 6, 8, 10, 12]:
        state['board'][i] = 2

    # player 1 black
    for i in [1, 3, 5, 7, 9, 11, 13]:
        state['board'][i] = 1

    state['player1_pieces'] = {1, 3, 5, 7, 9, 11, 13}
    state['player2_pieces'] = {0, 2, 4, 6, 8, 10, 12}

    state['current_player'] = 1
    state['dice_value'] = 0
    state['white_box'] = 0
    state['black_box'] = 0
    state['game_over'] = False
    state['winner'] = None



# checked by suliman
def roll_dice() :
    stick1 = random.randint(0,1)
    stick2 = random.randint(0,1)
    stick3 = random.randint(0,1)
    stick4 = random.randint(0,1)

    total = stick1 + stick2 + stick3 + stick4

    if total == 0:
        return 5

    return total

# checked by suliman
def is_valid_move(state, old_position, new_position, dice_value) :

    current_player = state['current_player']
    current_pieces = state['player1_pieces'] if current_player == 1 else state['player2_pieces']
    if old_position not in current_pieces:
        return False
    if old_position < 25 and new_position > 25:
        return False
    if old_position == 27 and dice_value != 3:
        return False
    if old_position == 28 and dice_value != 2:
        return False
    if new_position in current_pieces:
        return False
    
    return True

# checked by suliman
def get_valid_moves(state, dice_value):
    current_player = state['current_player']
    current_pieces = state['player1_pieces'] if current_player == 1 else state['player2_pieces']
    valid_moves = []
    for current_position in current_pieces:
        new_position = current_position + dice_value
        if is_valid_move(state, current_position, new_position, dice_value):
            valid_moves.append((current_position, new_position))

    return valid_moves

# checked by suliman
def switch_turn(state):
    state['current_player'] = 1 - state['current_player']

# checked by suliman
def game_over(state):
    if state['black_box'] == 7:
        state['winner'] = 0
        state['game_over'] = True
        print("=" * 50)
        print("GAME OVER!")
        print("Winner: Black (Player 1)")
        print("=" * 50)
        return True

    elif state['white_box'] == 7:
        state['winner'] = 1
        state['game_over'] = True
        print("=" * 50)
        print("GAME OVER!")
        print("Winner: White (Player 0)")
        print("=" * 50)
        return True

    state['game_over'] = False
    state['winner'] = None
    return False

# checked by suliman
def swap_pieces(state, from_pos, to_pos):
    current_player = state['current_player']
    # Match the logic from get_valid_moves and apply_move
    if current_player == 1:
        current_pieces = state['player1_pieces']
        opponent_pieces = state['player2_pieces']
        current_player_val = 1
        opponent_player_val = 2
    else:
        current_pieces = state['player2_pieces']
        opponent_pieces = state['player1_pieces']
        current_player_val = 2
        opponent_player_val = 1

    # Remove pieces only if they exist
    if from_pos in current_pieces:
        current_pieces.remove(from_pos)
    if to_pos in opponent_pieces:
        opponent_pieces.remove(to_pos)

    current_pieces.add(to_pos)
    opponent_pieces.add(from_pos)

    state['board'][from_pos] = opponent_player_val
    state['board'][to_pos] = current_player_val

# checked by suliman
# return the first available position befor rebirth
def force_rebirth(state):
    rebirth = 14
    
    if state['board'][rebirth] == 0:
        return rebirth

    for i in range(rebirth-1, -1, -1): 
        if state['board'][i] == 0:
            return i
    
    return None

def check_and_return_to_rebirth(state, dice_value, valid_moves):
    """
    Check if any piece needs to be returned to rebirth and return it.
    Same logic as in apply_move but as a separate function.
    
    Returns True if a piece was returned to rebirth, False otherwise.
    """
    current_player = state['current_player']
    # Match the logic from get_valid_moves: player 1 uses player1_pieces, player 0 uses player2_pieces
    if current_player == 1:
        current_pieces = state['player1_pieces']
        current_player_val = 1
    else:
        current_pieces = state['player2_pieces']
        current_player_val = 2
    
    special_positions = [27, 28, 29]
    
    # Check if there's a piece in special positions that needs to return to rebirth
    # Case 1: Piece in special position (27, 28, 29) that cannot move with current dice roll
    for pos in special_positions:
        if pos in current_pieces:
            # Check if this piece has a valid move
            has_valid_move = False
            for from_pos, to_pos in valid_moves:
                if from_pos == pos:
                    has_valid_move = True
                    break
            
            # If no valid move, return to rebirth
            if not has_valid_move:
                rebirth_pos = force_rebirth(state)
                if rebirth_pos is not None:
                    if pos in current_pieces:
                        current_pieces.remove(pos)
                    state['board'][pos] = 0
                    current_pieces.add(rebirth_pos)
                    state['board'][rebirth_pos] = current_player_val
                    return True
    
    # Case 2: Check if there's a piece in special positions that wasn't moved
    # This happens when we move a different piece, the special piece should return to rebirth
    special_piece = None
    for pos in current_pieces:
        if pos in special_positions:
            # Check if this piece was moved (has a valid move)
            was_moved = False
            for from_pos, to_pos in valid_moves:
                if from_pos == pos:
                    was_moved = True
                    break
            
            if not was_moved:
                special_piece = pos
                break
    
    if special_piece is not None:
        rebirth_pos = force_rebirth(state)
        if rebirth_pos is not None:
            if special_piece in current_pieces:
                current_pieces.remove(special_piece)
            state['board'][special_piece] = 0
            current_pieces.add(rebirth_pos)
            state['board'][rebirth_pos] = current_player_val
            return True
    
    return False

##################################             
def handle_special_piece_return(state, current_pieces, current_player_val):
    #Return any unmoved special-position piece to rebirth
    special_positions = [27, 28, 29]

    # Find any special piece that still exists
    special_piece = None
    for pos in current_pieces:
        if pos in special_positions:
            special_piece = pos
            break

    if special_piece is not None:
        rebirth_pos = force_rebirth(state)
        if rebirth_pos is not None:
            if special_piece in current_pieces:
                current_pieces.remove(special_piece)
            state['board'][special_piece] = 0
            current_pieces.add(rebirth_pos)
            state['board'][rebirth_pos] = current_player_val

########################################
def apply_move(state, current_position, new_position, valid_moves):
    # get the current player and the pieces of the current player and the opponent
    current_player = state['current_player']
    # Match the logic from get_valid_moves: player 1 uses player1_pieces, player 0 uses player2_pieces
    if current_player == 1:
        current_pieces = state['player1_pieces']
        opponent_pieces = state['player2_pieces']
        current_player_val = 1
        opponent_player_val = 2
    else:
        current_pieces = state['player2_pieces']
        opponent_pieces = state['player1_pieces']
        current_player_val = 2
        opponent_player_val = 1

    special_positions = [27, 28, 29]

    move_tuple = (current_position, new_position)
     # if we try to move a piece from a special position using a dice roll that is not 2 or 3,
     # the piece is forced to return to the House of Rebirth
    if move_tuple not in valid_moves:
        if current_position in current_pieces:
            if current_position in special_positions and (new_position == current_position + state['dice_value'] or new_position == 30):
                rebirth_pos = force_rebirth(state)
                if rebirth_pos is not None:
                    if current_position in current_pieces:
                        current_pieces.remove(current_position)
                    state['board'][current_position] = 0
                    current_pieces.add(rebirth_pos)
                    state['board'][rebirth_pos] = current_player_val
                    return True  
        return False 

    # moving backward is not allowed    
    if new_position < current_position:
        return False

    # at the House of Horus any roll will move the piece off the board
    if current_position == 29:
        new_position = 30    

    # move the piece that has exited the board into its box
    if new_position >= 30:
        if current_position in current_pieces:
            current_pieces.remove(current_position)
        state['board'][current_position] = 0
        if current_player == 1:
            state['black_box'] += 1
        else:
            state['white_box'] += 1
        return True

    # if the piece is in the House of water it will be moved to the House of Rebirth
    if new_position == 26:
        rebirth_pos = force_rebirth(state)
        if rebirth_pos is not None:
            if current_position in current_pieces:
                current_pieces.remove(current_position)
            state['board'][current_position] = 0
            current_pieces.add(rebirth_pos)
            state['board'][rebirth_pos] = current_player_val
        return True

    to_pos = state['board'][new_position]

    # normal move to an empty position
    if to_pos == 0:
        if current_position in current_pieces:
            current_pieces.remove(current_position)
        current_pieces.add(new_position)
        state['board'][current_position] = 0
        state['board'][new_position] = current_player_val
        #check if any special piece needs to return to rebirth
        if current_position not in special_positions and new_position not in special_positions:
            handle_special_piece_return(state, current_pieces, current_player_val)
        return True

    # swap pieces if the position is occupied by an opponent's piece
    elif to_pos == opponent_player_val:
        swap_pieces(state, current_position, new_position)
        #check if any special piece needs to return to rebirth
        if current_position not in special_positions and new_position not in special_positions:
            handle_special_piece_return(state, current_pieces, current_player_val)
        return True

    return False

# checked by suliman
def new_game(state):
    return init_game(state)

# checked by suliman
def handle_turn(state):
    if state['current_player'] == 1:  # الكمبيوتر
        computer_turn(state, depth=4)

    else :
        dice = roll_dice()
        state['dice_value'] = dice
        valid_moves = get_valid_moves(state, dice)

        if not valid_moves:
            switch_turn(state)
            return

    # apply_move(state, old_position, new_position, valid_moves)

    # هون بعد ما نطبق الحركة منستدعي التابع يلي بيغير الدور للاعب التاني
    switch_turn(state)


def computer_turn(state, depth):
    dice = roll_dice()
    state['dice_value'] = dice

    value, best_move = expectiminimax(state, state, "chance", depth)
    if best_move is not None:
        apply_move(state, best_move[0], best_move[1], get_valid_moves(state, dice))
        print(f'old place : {best_move[0]}, new place: {best_move[1]}, dice = {dice}')
    else :
        print('there is no valid moves for computer')

    game_over(state)
    switch_turn(state)





# def handle_turn(state, old_position=None, new_position=None):
#     dice = roll_dice()
#     state['dice_value'] = dice

#     valid_moves = get_valid_moves(state, dice)
#     if not valid_moves:
#         switch_turn(state)
#         return

#     # في الـ UI، رح تختاري old_position من مفاتيح valid_moves
#     # و new_position = valid_moves[old_position]
#     if old_position is None or new_position is None:
#         # إذا بدك مؤقتًا تتأكدي من الدالة بدون UI، ما منطبق حركة
#         return

#     apply_move(state, old_position, new_position, valid_moves)
#     switch_turn(state)

###################################
# def run_game(state):
#     init_game(state)
#
#     while not state['game_over']:
#         handle_turn(state)
#         game_over(state)




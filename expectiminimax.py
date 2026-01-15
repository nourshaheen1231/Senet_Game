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
        elif piece == 24 or piece == 22:
            score +=  4/16 
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

    return score

######################################
# def  expectiminimax(state ,depth =4):
#     if state['game_over'] or depth ==0:
#         return heuristic(state , state)

#      if the adversary is to play at node
#         value= float('inf') 
#         for v in get_valid_moves(state, current_dice_value):
#             value = min(value, expectiminimax(child, depth-1))
#     else if we are to play at node
#         value= float('-inf')
#         foreach child of state
#             value = max(value, expectiminimax(child, depth-1))
#     else if random event at state
#         value = 0
#         foreach child of state
#             value = value + (Probability[child] * expectiminimax(child, depth-1))
#     return value




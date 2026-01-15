# def heuristic(state, new_state):
#     current_player = state['current_player']
#     if current_player == 1:
#         old_current_pieces = state['player1_pieces']
#         old_opponent_pieces = state['player2_pieces']
#         new_current_pieces = new_state['player1_pieces']
#         new_opponent_pieces = new_state['player2_pieces']
#     else:
#         old_current_pieces = state['player2_pieces']
#         old_opponent_pieces = state['player1_pieces']
#         new_current_pieces = new_state['player2_pieces']
#         new_opponent_pieces = new_state['player1_pieces']
#     score = 0
#     for piece in old_current_pieces:

#         if piece not in new_current_pieces or piece == 29:
#             score += 6  # Current player has moved a piece off the board
#         if piece in new_current_pieces:

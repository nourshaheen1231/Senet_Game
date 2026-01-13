import pygame
import sys
from game import state, init_game, roll_dice, get_valid_moves, apply_move, switch_turn, game_over, check_and_return_to_rebirth
from ui import (
    screen, WINDOW_WIDTH, WINDOW_HEIGHT, WHITE,
    BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT,
    draw_board, draw_info_panel, draw_exit_button, draw_skip_turn_button,
    get_square_from_pos
)

def main():
    """Main game loop"""
    # Game state variables
    selected_piece = None
    dice_rolled = False
    current_dice_value = 0
    
    # Initialize game
    init_game(state)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Calculate button positions (same as in draw_info_panel)
        panel_width = 1000
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        button_x = panel_x + 700
        button_y = 20 + 20
        roll_button_rect = pygame.Rect(button_x, button_y, 150, 40)
        new_game_button_rect = pygame.Rect(button_x + 170, button_y, 150, 40)
        
        # Calculate exit button position (will be drawn later, but need rect for collision)
        exit_button_x = BOARD_X + BOARD_WIDTH + 20
        exit_button_y = BOARD_Y + BOARD_HEIGHT // 2 - 30
        exit_button_rect = pygame.Rect(exit_button_x, exit_button_y, 120, 60)
        
        # Calculate skip turn button position
        skip_button_x = BOARD_X + BOARD_WIDTH + 20
        skip_button_y = BOARD_Y + BOARD_HEIGHT // 2 + 40
        skip_button_rect = pygame.Rect(skip_button_x, skip_button_y, 120, 60)
        
        # Get valid moves for exit button check
        valid_moves = get_valid_moves(state, current_dice_value) if dice_rolled else []
        
        # If valid_moves is empty, check if any piece needs to return to rebirth
        if dice_rolled and len(valid_moves) == 0:
            check_and_return_to_rebirth(state, current_dice_value, valid_moves)
            # After returning to rebirth, get valid moves again
            valid_moves = get_valid_moves(state, current_dice_value)
        
        exit_piece_pos = None
        # Check if there's any valid move to exit (position >= 30) in valid_moves
        if dice_rolled:
            for from_pos, to_pos in valid_moves:
                if to_pos >= 30:
                    exit_piece_pos = from_pos
                    break
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    
                    # Check if clicked on roll dice button
                    if roll_button_rect.collidepoint(mouse_x, mouse_y):
                        # Disable if game is over
                        if state['game_over']:
                            continue
                        if not dice_rolled:
                            current_dice_value = roll_dice()
                            state['dice_value'] = current_dice_value
                            dice_rolled = True
                            selected_piece = None
                            # Print valid moves immediately after rolling dice
                            current_pieces = state['player1_pieces'] if state['current_player'] == 1 else state['player2_pieces']
                            valid_moves = get_valid_moves(state, current_dice_value)
                            print("========================================")
                            print(f"Current player: {state['current_player']} ({'Black' if state['current_player'] == 1 else 'White'})")
                            print(f"Player pieces: {sorted(current_pieces)}")
                            print(f"Dice rolled: {current_dice_value}")
                            print(f"Valid moves: {valid_moves}")
                            print("========================================")
                        continue
                    
                    # Check if clicked on new game button
                    if new_game_button_rect.collidepoint(mouse_x, mouse_y):
                        init_game(state)
                        selected_piece = None
                        dice_rolled = False
                        current_dice_value = 0
                        continue
                    
                    # Check if clicked on exit button
                    if exit_button_rect is not None and exit_button_rect.collidepoint(mouse_x, mouse_y):
                        if exit_piece_pos is not None:
                            # Exit the piece from the board - find the actual target position from valid_moves
                            target_pos = 30
                            for from_pos, to_pos in valid_moves:
                                if from_pos == exit_piece_pos and to_pos >= 30:
                                    target_pos = to_pos
                                    break
                            move_tuple = (exit_piece_pos, target_pos)
                            if move_tuple in valid_moves:
                                apply_move(state, exit_piece_pos, target_pos, valid_moves)
                                game_over(state)
                                if not state['game_over']:
                                    switch_turn(state)
                                selected_piece = None
                                dice_rolled = False
                                current_dice_value = 0
                        continue
                    
                    # Check if clicked on skip turn button
                    if skip_button_rect.collidepoint(mouse_x, mouse_y):
                        # Disable if game is over
                        if state['game_over']:
                            continue
                        # Only allow skip if valid_moves is empty after checking for rebirth
                        if dice_rolled and len(valid_moves) == 0:
                            # Check again if any piece needs to return to rebirth
                            piece_returned = check_and_return_to_rebirth(state, current_dice_value, valid_moves)
                            if not piece_returned:
                                # No piece was returned, can skip turn
                                switch_turn(state)
                                selected_piece = None
                                dice_rolled = False
                                current_dice_value = 0
                            else:
                                # Piece was returned, get new valid moves (don't skip turn)
                                valid_moves = get_valid_moves(state, current_dice_value)
                        continue
                    
                    # Check if clicked on board
                    square = get_square_from_pos(mouse_x, mouse_y)
                    if square is None:
                        continue
                    
                    # Disable board interactions if game is over
                    if state['game_over']:
                        continue
                    
                    if not dice_rolled:
                        continue
                    
                    # Get current player's pieces and opponent's pieces
                    current_pieces = state['player1_pieces'] if state['current_player'] == 1 else state['player2_pieces']
                    opponent_pieces = state['player2_pieces'] if state['current_player'] == 1 else state['player1_pieces']
                    
                    # Check what was clicked
                    is_empty = state['board'][square] == 0
                    is_current_player_piece = square in current_pieces
                    is_opponent_piece = square in opponent_pieces
                    
                    # If no piece selected
                    if selected_piece is None:
                        # Only select if it's current player's piece
                        if is_current_player_piece:
                            selected_piece = square
                        # If clicked on empty or opponent's piece, do nothing
                        elif is_empty or is_opponent_piece:
                            pass  # Do nothing
                    else:
                        # A piece is already selected
                        # First check if this is a valid move destination
                        valid_moves = get_valid_moves(state, current_dice_value)
                        move_tuple = (selected_piece, square)
                        
                        if move_tuple in valid_moves:
                            # Valid move - apply it
                            apply_move(state, selected_piece, square, valid_moves)
                            game_over(state)
                            if not state['game_over']:
                                switch_turn(state)
                            selected_piece = None
                            dice_rolled = False
                            current_dice_value = 0
                        # If clicked on the same piece, deselect
                        elif square == selected_piece:
                            selected_piece = None
                        # If clicked on current player's other piece, select it instead
                        elif is_current_player_piece:
                            selected_piece = square
                        # If clicked on empty square, deselect only
                        elif is_empty:
                            selected_piece = None
                        # If clicked on opponent's piece, do nothing (keep selection)
                        elif is_opponent_piece:
                            pass  # Do nothing, keep current selection
        
        # Render
        # Fill background with white
        screen.fill(WHITE)
        
        # Draw board (with gray background)
        draw_board(selected_piece, dice_rolled, current_dice_value)
        
        # Draw exit button (on the right side of the board)
        draw_exit_button(dice_rolled, current_dice_value, valid_moves)
        
        # Draw skip turn button (below exit button)
        draw_skip_turn_button(valid_moves, dice_rolled)
        
        # Draw info panel
        draw_info_panel(dice_rolled, current_dice_value)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


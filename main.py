import pygame
import sys

import expectiminimax
from game import state, init_game, roll_dice, get_valid_moves, apply_move, switch_turn, game_over, check_and_return_to_rebirth
from ui import (
    screen, WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK,
    BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT,
    draw_board, draw_info_panel, draw_exit_button, draw_skip_turn_button,
    get_square_from_pos, font, small_font
)
# This window is used to display information from the Expectiminimax algorithm
def choose_debug_mode():
    pygame.init()

    w, h = 400, 250
    window = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Debug Mode")

    font_big = pygame.font.Font(None, 40)
    font_small = pygame.font.Font(None, 30)

    off_button = pygame.Rect(100, 120, 200, 40)
    on_button = pygame.Rect(100, 170, 200, 40)

    while True:
        window.fill((230, 230, 230))

        title = font_big.render("Debug Mode", True, (0, 0, 0))
        window.blit(title, (w//2 - title.get_width()//2, 40))

        pygame.draw.rect(window, (180, 60, 60), off_button)
        pygame.draw.rect(window, BLACK, off_button, 2)
        off_text = font_small.render("Debug OFF", True, WHITE)
        window.blit(off_text, (off_button.centerx - off_text.get_width()//2,
                               off_button.centery - off_text.get_height()//2))

        pygame.draw.rect(window, (60, 160, 60), on_button)
        pygame.draw.rect(window, BLACK, on_button, 2)
        on_text = font_small.render("Debug ON", True, WHITE)
        window.blit(on_text, (on_button.centerx - on_text.get_width()//2,
                              on_button.centery - on_text.get_height()//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if off_button.collidepoint(mx, my):
                    return False

                if on_button.collidepoint(mx, my):
                    return True


def main():

    debug_mode = choose_debug_mode()

    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    game_mode = "human_vs_human"

    mode_button_x = -1
    mode_button_y = 20
    mode_button_w = 110
    mode_button_h = 40

    hvh_button_rect = pygame.Rect(mode_button_x, mode_button_y, mode_button_w, mode_button_h)
    hvc_button_rect = pygame.Rect(mode_button_x, mode_button_y + 50, mode_button_w, mode_button_h)

    selected_piece = None
    dice_rolled = False
    current_dice_value = 0

    init_game(state)

    clock = pygame.time.Clock()
    running = True

    while running:

        panel_width = 1000
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        button_x = panel_x + 650
        button_y = 20 + 20
        roll_button_rect = pygame.Rect(button_x, button_y, 150, 40)
        new_game_button_rect = pygame.Rect(button_x + 155, button_y, 150, 40)

        exit_button_x = BOARD_X + BOARD_WIDTH + 20
        exit_button_y = BOARD_Y + BOARD_HEIGHT // 2 - 30
        exit_button_rect = pygame.Rect(exit_button_x, exit_button_y, 95, 60)

        skip_button_x = BOARD_X + BOARD_WIDTH + 20
        skip_button_y = BOARD_Y + BOARD_HEIGHT // 2 + 40
        skip_button_rect = pygame.Rect(skip_button_x, skip_button_y, 95, 60)

        valid_moves = get_valid_moves(state, current_dice_value) if dice_rolled else []

        if dice_rolled and len(valid_moves) == 0:
            check_and_return_to_rebirth(state, current_dice_value, valid_moves)
            valid_moves = get_valid_moves(state, current_dice_value)

        if (
            game_mode == "human_vs_computer"
            and not state['game_over']
            and state['current_player'] == 0
        ):
            pygame.time.delay(600)

            if not dice_rolled:
                pygame.time.delay(500)
                current_dice_value = roll_dice()
                state['dice_value'] = current_dice_value
                dice_rolled = True
                screen.fill(WHITE)
                draw_board(None, dice_rolled, current_dice_value)
                draw_info_panel(dice_rolled, current_dice_value)
                pygame.display.flip()
                continue

            valid_moves = get_valid_moves(state, current_dice_value)

            if not valid_moves:
                pygame.time.delay(700)
                piece_returned = check_and_return_to_rebirth(state, current_dice_value, valid_moves)
                if not piece_returned:
                    switch_turn(state)
                    dice_rolled = False
                    current_dice_value = 0
                continue

            best_value, best_move = expectiminimax.expectiminimax(
                state, state, "max", depth=3, debug=debug_mode
            )

            if debug_mode:
                print("\n====================================")
                print("DEBUG MODE ACTIVE")
                print(f"Nodes visited: {expectiminimax.node_counter}")
                print(f"Heuristic value: {best_value}")
                print(f"Chosen move: {best_move}")
                print("====================================\n")
                expectiminimax.node_counter = 0

            if best_move:
                pygame.time.delay(500)
                move_happened = apply_move(state, best_move[0], best_move[1], valid_moves)
                if move_happened:
                    game_over(state)
                    if not state['game_over']:
                        switch_turn(state)
                    dice_rolled = False
                    current_dice_value = 0
                continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos

                    # Mode selection
                    if hvh_button_rect.collidepoint(mouse_x, mouse_y):
                        game_mode = "human_vs_human"
                        continue

                    if hvc_button_rect.collidepoint(mouse_x, mouse_y):
                        game_mode = "human_vs_computer"
                        continue

                    # Roll dice
                    if roll_button_rect.collidepoint(mouse_x, mouse_y):
                        if state['game_over']:
                            continue
                        if not dice_rolled:
                            current_dice_value = roll_dice()
                            state['dice_value'] = current_dice_value
                            dice_rolled = True
                            selected_piece = None

                            # print old debug info
                            current_pieces = state['player1_pieces'] if state['current_player'] == 1 else state['player2_pieces']
                            valid_moves = get_valid_moves(state, current_dice_value)

                            print("========================================")
                            print(f"Current player: {state['current_player']} ({'Black' if state['current_player'] == 1 else 'White'})")
                            print(f"Player pieces: {sorted(current_pieces)}")
                            print(f"Dice rolled: {current_dice_value}")
                            print(f"Valid moves: {valid_moves}")
                            print("========================================")

                        continue

                    # New game
                    if new_game_button_rect.collidepoint(mouse_x, mouse_y):
                        init_game(state)
                        selected_piece = None
                        dice_rolled = False
                        current_dice_value = 0
                        continue

                    # Exit piece
                    if exit_button_rect.collidepoint(mouse_x, mouse_y):
                        if dice_rolled and selected_piece is not None:
                            move_happened = apply_move(state, selected_piece, 30, valid_moves)
                            if move_happened:
                                game_over(state)
                                if not state['game_over']:
                                    switch_turn(state)
                                dice_rolled = False
                                current_dice_value = 0
                            selected_piece = None
                        continue

                    # Skip turn
                    if skip_button_rect.collidepoint(mouse_x, mouse_y):
                        if dice_rolled and len(valid_moves) == 0:
                            piece_returned = check_and_return_to_rebirth(state, current_dice_value, valid_moves)
                            if not piece_returned:
                                switch_turn(state)
                                dice_rolled = False
                                current_dice_value = 0
                        continue

                    # Board click
                    square = get_square_from_pos(mouse_x, mouse_y)
                    if square is None:
                        continue
                    if state['game_over'] or not dice_rolled:
                        continue

                    current_pieces = state['player1_pieces'] if state['current_player'] == 1 else state['player2_pieces']
                    opponent_pieces = state['player2_pieces'] if state['current_player'] == 1 else state['player1_pieces']

                    if selected_piece is None:
                        if square in current_pieces:
                            selected_piece = square
                    else:
                        valid_moves = get_valid_moves(state, current_dice_value)
                        move_tuple = (selected_piece, square)
                        special_positions = [27, 28, 29]

                        if move_tuple in valid_moves:
                            move_happened = apply_move(state, selected_piece, square, valid_moves)
                        elif selected_piece in special_positions and square == 30:
                            move_happened = apply_move(state, selected_piece, 30, valid_moves)
                        elif selected_piece in special_positions:
                            move_happened = apply_move(state, selected_piece, square, valid_moves)
                        else:
                            selected_piece = None
                            continue

                        if move_happened:
                            game_over(state)
                            if not state['game_over']:
                                switch_turn(state)
                            dice_rolled = False
                            current_dice_value = 0

                        selected_piece = None

        screen.fill(WHITE)

        pygame.draw.rect(screen, (100, 100, 255), hvh_button_rect)
        pygame.draw.rect(screen, BLACK, hvh_button_rect, 2)
        pygame.draw.rect(screen, (100, 255, 100), hvc_button_rect)
        pygame.draw.rect(screen, BLACK, hvc_button_rect, 2)

        hvh_text = small_font.render("Human vs Human", True, WHITE)
        hvc_text = small_font.render("Human vs Computer", True, WHITE)

        screen.blit(hvh_text, (hvh_button_rect.centerx - hvh_text.get_width()//2,
                               hvh_button_rect.centery - hvh_text.get_height()//2))

        screen.blit(hvc_text, (hvc_button_rect.centerx - hvc_text.get_width()//2,
                               hvc_button_rect.centery - hvc_text.get_height()//2))

        draw_board(selected_piece, dice_rolled, current_dice_value)
        draw_exit_button(dice_rolled, current_dice_value, valid_moves)
        draw_skip_turn_button(valid_moves, dice_rolled)
        draw_info_panel(dice_rolled, current_dice_value)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

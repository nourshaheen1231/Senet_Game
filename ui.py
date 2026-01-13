import pygame
import sys
from game import state, get_valid_moves

# Initialize Pygame
pygame.init()

# Constants
SQUARE_SIZE = 90
SQUARE_SPACING = 10
CORNER_RADIUS = 10
INFO_PANEL_HEIGHT = 120

# Calculate board dimensions
BOARD_WIDTH = 10 * (SQUARE_SIZE + SQUARE_SPACING) - SQUARE_SPACING
BOARD_HEIGHT = 3 * (SQUARE_SIZE + SQUARE_SPACING) - SQUARE_SPACING
board_bg_padding = 20
BOARD_Y = INFO_PANEL_HEIGHT + 30

# Calculate window size based on board size
# Add extra width for exit button (120 width + 20 spacing)
WINDOW_WIDTH = BOARD_WIDTH + 2 * board_bg_padding + 40 + 140  # 40 for side padding + 140 for exit button
WINDOW_HEIGHT = INFO_PANEL_HEIGHT + BOARD_HEIGHT + 2 * board_bg_padding + 50  # 50 for bottom padding

# Calculate board position to center it
BOARD_X = (WINDOW_WIDTH - BOARD_WIDTH) // 2

# Colors - matching the image
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY_BG = (64, 64, 64)  # Dark gray background
GRAY_BOARD_BG = (200, 200, 200)  # Gray background for board
CREAM = (255, 250, 240)  # Light cream color
TAN = (210, 180, 140)  # Light brown/tan color
DICE_BAR_COLOR = (180, 140, 140)  # Dusty rose/brownish-purple for filled bars
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)  # Purple color for movable pieces
PURPLE = (128, 0, 128)  # Purple color for movable pieces
# Removed DARK_BLUE - using BLACK instead

# Create window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Senet Game")
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# UI only - no game state here

def get_square_position(square_index):
    """
    Convert square index (0-29) to screen position
    Board layout: 3 rows × 10 columns (zigzag pattern)
    Row 0: 0-9 (left to right)
    Row 1: 19-10 (right to left)
    Row 2: 20-29 (left to right)
    """
    if square_index < 10:
        # Row 0: left to right
        row = 0
        col = square_index
    elif square_index < 20:
        # Row 1: right to left
        row = 1
        col = 19 - square_index
    else:
        # Row 2: left to right
        row = 2
        col = square_index - 20
    
    x = BOARD_X + col * (SQUARE_SIZE + SQUARE_SPACING)
    y = BOARD_Y + row * (SQUARE_SIZE + SQUARE_SPACING)
    return x, y

def get_square_from_pos(mouse_x, mouse_y):
    """Get square index from mouse position"""
    for i in range(30):
        x, y = get_square_position(i)
        if x <= mouse_x <= x + SQUARE_SIZE and y <= mouse_y <= y + SQUARE_SIZE:
            return i
    return None

def get_square_color(square_index):
    """Get color for squares - alternating cream and tan"""
    # Calculate position in grid
    if square_index < 10:
        row = 0
        col = square_index
    elif square_index < 20:
        row = 1
        col = 19 - square_index
    else:
        row = 2
        col = square_index - 20
    
    # Alternate colors based on row and column
    if (row + col) % 2 == 0:
        return CREAM
    else:
        return TAN

def draw_rounded_rect(surface, color, rect, radius):
    """Draw a rounded rectangle"""
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)

def draw_rounded_rect_border(surface, color, rect, radius, width=1):
    """Draw a rounded rectangle border with rounded corners"""
    x, y, w, h = rect
    # Draw straight edges
    pygame.draw.line(surface, color, (x + radius, y), (x + w - radius, y), width)  # Top
    pygame.draw.line(surface, color, (x + radius, y + h), (x + w - radius, y + h), width)  # Bottom
    pygame.draw.line(surface, color, (x, y + radius), (x, y + h - radius), width)  # Left
    pygame.draw.line(surface, color, (x + w, y + radius), (x + w, y + h - radius), width)  # Right
    
    # Draw rounded corners using arcs (quarter circles)
    # Top-left corner (90 to 180 degrees)
    pygame.draw.arc(surface, color, (x, y, radius * 2, radius * 2), 1.57, 3.14, width)
    # Top-right corner (0 to 90 degrees)
    pygame.draw.arc(surface, color, (x + w - radius * 2, y, radius * 2, radius * 2), 0, 1.57, width)
    # Bottom-left corner (180 to 270 degrees)
    pygame.draw.arc(surface, color, (x, y + h - radius * 2, radius * 2, radius * 2), 3.14, 4.71, width)
    # Bottom-right corner (270 to 360 degrees)
    pygame.draw.arc(surface, color, (x + w - radius * 2, y + h - radius * 2, radius * 2, radius * 2), 4.71, 6.28, width)

def draw_special_symbol(surface, square_index, x, y, size):
    """Draw special symbols on certain squares"""
    center_x = x + size // 2
    center_y = y + size // 2
    
    # Square 15 (index 14) - Ankh symbol (simplified)
    if square_index == 14:
        # Draw simplified Ankh
        pygame.draw.line(surface, BLACK, (center_x - 10, center_y - 15), (center_x - 10, center_y + 10), 2)
        pygame.draw.line(surface, BLACK, (center_x - 10, center_y - 15), (center_x + 10, center_y - 15), 2)
        pygame.draw.line(surface, BLACK, (center_x + 10, center_y - 15), (center_x + 10, center_y - 5), 2)
        pygame.draw.line(surface, BLACK, (center_x - 5, center_y - 5), (center_x + 5, center_y - 5), 2)
        pygame.draw.line(surface, BLACK, (center_x, center_y - 5), (center_x, center_y + 10), 2)
    
    # Square 26 (index 25) - House of Happiness - Three symbols side by side (simplified)
    elif square_index == 25:
        for i in range(3):
            offset_x = -15 + i * 15
            # Draw simplified spoon symbol horizontally
            pygame.draw.circle(surface, BLACK, (center_x + offset_x, center_y), 5, 2)
            pygame.draw.line(surface, BLACK, (center_x + offset_x, center_y + 5), (center_x + offset_x, center_y + 10), 2)
            pygame.draw.line(surface, BLACK, (center_x + offset_x - 3, center_y + 8), (center_x + offset_x + 3, center_y + 8), 1)
    
    # Square 27 (index 26) - Three wavy lines
    elif square_index == 26:
        for i in range(3):
            offset_y = -10 + i * 10
            # Draw wavy lines
            points = []
            for j in range(0, size, 5):
                wave_y = offset_y + 5 * (1 if (j // 10) % 2 == 0 else -1)
                points.append((x + j, center_y + wave_y))
            if len(points) > 1:
                pygame.draw.lines(surface, BLACK, False, points, 2)
    
    # Square 28 (index 27) - Three birds (simplified)
    elif square_index == 27:
        for i in range(3):
            offset_x = -15 + i * 15
            # Draw simplified bird
            pygame.draw.circle(surface, BLACK, (center_x + offset_x, center_y - 5), 4, 2)
            pygame.draw.line(surface, BLACK, (center_x + offset_x, center_y - 1), (center_x + offset_x + 5, center_y + 3), 2)
            pygame.draw.line(surface, BLACK, (center_x + offset_x, center_y + 1), (center_x + offset_x, center_y + 8), 2)
    
    # Square 29 (index 28) - Two kneeling figures (simplified)
    elif square_index == 28:
        for i in range(2):
            offset_x = -8 + i * 16
            # Draw simplified figure
            pygame.draw.circle(surface, BLACK, (center_x + offset_x, center_y - 8), 4, 2)
            pygame.draw.line(surface, BLACK, (center_x + offset_x, center_y - 4), (center_x + offset_x, center_y + 5), 2)
            pygame.draw.line(surface, BLACK, (center_x + offset_x - 3, center_y), (center_x + offset_x + 3, center_y), 2)
            pygame.draw.line(surface, BLACK, (center_x + offset_x, center_y + 5), (center_x + offset_x - 4, center_y + 10), 2)
            pygame.draw.line(surface, BLACK, (center_x + offset_x, center_y + 5), (center_x + offset_x + 4, center_y + 10), 2)
    
    # Square 30 (index 29) - Target/circle symbol
    elif square_index == 29:
        pygame.draw.circle(surface, BLACK, (center_x, center_y), 15, 2)
        pygame.draw.circle(surface, BLACK, (center_x, center_y), 8, 2)

def draw_board(selected_piece=None, dice_rolled=False, current_dice_value=0):
    """Draw the game board with rounded corners matching the image"""
    # Draw gray board background (slightly larger than the board)
    board_bg_padding = 20
    board_bg_x = BOARD_X - board_bg_padding
    board_bg_y = BOARD_Y - board_bg_padding
    board_bg_width = BOARD_WIDTH + 2 * board_bg_padding
    board_bg_height = BOARD_HEIGHT + 2 * board_bg_padding
    
    # Draw rounded rectangle for board background
    board_bg_rect = pygame.Rect(board_bg_x, board_bg_y, board_bg_width, board_bg_height)
    draw_rounded_rect(screen, GRAY_BOARD_BG, board_bg_rect, CORNER_RADIUS + 5)
    # Draw rounded border
    draw_rounded_rect_border(screen, BLACK, board_bg_rect, CORNER_RADIUS + 5, 2)
    
    for i in range(30):
        x, y = get_square_position(i)
        color = get_square_color(i)
        
        # Draw rounded rectangle
        rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
        draw_rounded_rect(screen, color, rect, CORNER_RADIUS)
        
        # Draw border
        pygame.draw.rect(screen, BLACK, (x, y, SQUARE_SIZE, SQUARE_SIZE), 1)
        
        # Draw special symbols
        draw_special_symbol(screen, i, x, y, SQUARE_SIZE)
        
        # Draw piece if exists
        piece_value = state['board'][i]
        if piece_value == 1:  # Black piece
            pygame.draw.circle(screen, BLACK, (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2), SQUARE_SIZE // 3)
        elif piece_value == 2:  # White piece
            pygame.draw.circle(screen, WHITE, (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2), SQUARE_SIZE // 3)
            pygame.draw.circle(screen, BLACK, (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2), SQUARE_SIZE // 3, 2)
        
        # Highlight pieces that can be moved (purple) - before selection
        if dice_rolled and selected_piece is None:
            valid_moves = get_valid_moves(state, current_dice_value)
            # Check if this square has a piece that can be moved
            for from_pos, to_pos in valid_moves:
                if from_pos == i:
                    pygame.draw.rect(screen, PURPLE, (x - 3, y - 3, SQUARE_SIZE + 6, SQUARE_SIZE + 6), 3)
                    break
        
        # Highlight selected piece
        if selected_piece == i:
            pygame.draw.rect(screen, YELLOW, (x - 3, y - 3, SQUARE_SIZE + 6, SQUARE_SIZE + 6), 3)
        
        # Highlight valid moves (green) - after selection
        if dice_rolled and selected_piece is not None:
            valid_moves = get_valid_moves(state, current_dice_value)
            # Check if (selected_piece, i) is a valid move
            move_tuple = (selected_piece, i)
            if move_tuple in valid_moves:
                    pygame.draw.rect(screen, GREEN, (x - 3, y - 3, SQUARE_SIZE + 6, SQUARE_SIZE + 6), 3)

def draw_dice_indicator(surface, x, y, dice_value):
    """
    Draw dice indicator: 4 vertical bars in a rounded rectangle
    dice_value: 1-5 (number of filled bars)
    """
    # Rounded rectangle background (cream)
    rect_width = 80
    rect_height = 40  # Increased height for longer bars
    rect = pygame.Rect(x, y, rect_width, rect_height)
    draw_rounded_rect(surface, CREAM, rect, 8)
    
    # Draw 4 vertical bars (longer)
    bar_width = 12
    bar_height = 30  # Longer bars
    bar_spacing = 8
    start_x = x + (rect_width - (4 * bar_width + 3 * bar_spacing)) // 2
    bar_y = y + (rect_height - bar_height) // 2
    
    for i in range(4):
        bar_x = start_x + i * (bar_width + bar_spacing)
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        
        # Fill bar if it's part of the dice value
        if i < dice_value:
            # Filled bar (dusty rose color)
            pygame.draw.rect(surface, DICE_BAR_COLOR, bar_rect)
        else:
            # Empty bar (light cream, same as background)
            pygame.draw.rect(surface, CREAM, bar_rect)
        
        # Bar border
        pygame.draw.rect(surface, BLACK, bar_rect, 1)
    
    # Draw dice value number below the indicator
    text = font.render(str(dice_value), True, BLACK)
    text_x = x + (rect_width - text.get_width()) // 2
    text_y = y + rect_height + 5
    surface.blit(text, (text_x, text_y))

def draw_info_panel(dice_rolled=False, current_dice_value=0):
    """Draw game information panel at the top"""
    # Center the panel horizontally
    panel_width = 1000
    x = (WINDOW_WIDTH - panel_width) // 2
    y = 20
    
    # Draw background panel
    panel_rect = pygame.Rect(x, y, panel_width, INFO_PANEL_HEIGHT - 20)
    pygame.draw.rect(screen, (240, 240, 240), panel_rect)
    pygame.draw.rect(screen, BLACK, panel_rect, 2)
    
    # Current player (1 is black, 0 is white according to game.py)
    current_player_name = "Black" if state['current_player'] == 1 else "White"
    text = font.render(f"Current Player: {current_player_name}", True, BLACK)
    screen.blit(text, (x + 20, y + 15))
    
    # Dice value indicator
    if dice_rolled:
        draw_dice_indicator(screen, x + 300, y + 5, current_dice_value)
    else:
        text = font.render("Roll first", True, DARK_GRAY_BG)
        screen.blit(text, (x + 300, y + 15))
    
    # Pieces out
    text = small_font.render(f"Black out: {state['black_box']}/7", True, BLACK)
    screen.blit(text, (x + 500, y + 15))
    text = small_font.render(f"White out: {state['white_box']}/7", True, BLACK)
    screen.blit(text, (x + 500, y + 45))
    
    # Roll dice button
    button_x = x + 700
    button_y = y + 20
    roll_button_rect = pygame.Rect(button_x, button_y, 150, 40)
    pygame.draw.rect(screen, BLUE, roll_button_rect)
    pygame.draw.rect(screen, BLACK, roll_button_rect, 2)
    text = font.render("Roll Dice", True, WHITE)
    text_rect = text.get_rect(center=roll_button_rect.center)
    screen.blit(text, text_rect)
    
    # New game button
    new_game_button_rect = pygame.Rect(button_x + 170, button_y, 150, 40)
    pygame.draw.rect(screen, GREEN, new_game_button_rect)
    pygame.draw.rect(screen, BLACK, new_game_button_rect, 2)
    text = font.render("New Game", True, WHITE)
    text_rect = text.get_rect(center=new_game_button_rect.center)
    screen.blit(text, text_rect)
    
    # Game over message
    if state['game_over']:
        # In game_over: black_box == 7 → winner = 0, white_box == 7 → winner = 1
        winner_name = "Black" if state['winner'] == 0 else "White"
        text = font.render(f"{winner_name} Wins!", True, RED)
        screen.blit(text, (x + 700, y + 70))
    
    return roll_button_rect, new_game_button_rect

def draw_exit_button(dice_rolled=False, current_dice_value=0, valid_moves=None):
    """Draw exit piece button on the right side of the board"""
    # Position button on the right side of the board
    button_x = BOARD_X + BOARD_WIDTH + 20
    button_y = BOARD_Y + BOARD_HEIGHT // 2 - 30  # Center vertically
    
    exit_button_rect = pygame.Rect(button_x, button_y, 120, 60)
    
    # Check if there's any valid move to exit (position 30) in valid_moves
    can_exit = False
    exit_piece_pos = None
    
    if dice_rolled and valid_moves is not None:
        # Check if any move goes to position >= 30 (exit)
        for from_pos, to_pos in valid_moves:
            if to_pos >= 30:
                can_exit = True
                exit_piece_pos = from_pos
                break
    
    # Button color: green if can exit, gray otherwise
    if can_exit:
        button_color = GREEN
        text_color = WHITE
    else:
        button_color = DARK_GRAY_BG
        text_color = WHITE
    
    # Draw button
    pygame.draw.rect(screen, button_color, exit_button_rect)
    pygame.draw.rect(screen, BLACK, exit_button_rect, 2)
    
    # Draw text
    text = small_font.render("Exit Piece", True, text_color)
    text_rect = text.get_rect(center=exit_button_rect.center)
    screen.blit(text, text_rect)
    
    return exit_button_rect

def draw_skip_turn_button(valid_moves=None, dice_rolled=False):
    """Draw skip turn button - enabled only when valid_moves is empty and dice is rolled"""
    # Position button below the exit button
    button_x = BOARD_X + BOARD_WIDTH + 20
    button_y = BOARD_Y + BOARD_HEIGHT // 2 + 40  # Below exit button
    
    skip_button_rect = pygame.Rect(button_x, button_y, 120, 60)
    
    # Check if valid_moves is empty AND dice is rolled
    can_skip = dice_rolled and valid_moves is not None and len(valid_moves) == 0
    
    # Button color: green if can skip, light gray (same as exit button when disabled) otherwise
    if can_skip:
        button_color = GREEN
        text_color = WHITE
    else:
        button_color = DARK_GRAY_BG  # Same gray as exit button when disabled
        text_color = WHITE
    
    # Draw button
    pygame.draw.rect(screen, button_color, skip_button_rect)
    pygame.draw.rect(screen, BLACK, skip_button_rect, 2)
    
    # Draw text
    text = small_font.render("Skip Turn", True, text_color)
    text_rect = text.get_rect(center=skip_button_rect.center)
    screen.blit(text, text_rect)
    
    return skip_button_rect

# UI functions only - game logic is in main.py


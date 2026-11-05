import pygame
import sys
import copy

# Initialize Pygame modules
pygame.init()
pygame.font.init()

# Window and Grid Settings
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)
DOT_COLOR = (100, 111, 64)

# Fonts
FONT = pygame.font.SysFont("Segoe UI Symbol", 56)
MENU_FONT = pygame.font.SysFont("Segoe UI Symbol", 48)
VICTORY_FONT = pygame.font.SysFont("Arial", 48, bold=True)

PIECE_SYMBOLS = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
}

# Initial Board State
board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"]
]

def find_king(board_state, color):
    target_king = 'K' if color == 'W' else 'k'
    for r in range(ROWS):
        for c in range(COLS):
            if board_state[r][c] == target_king:
                return (r, c)
    return None

def get_raw_moves(board_state, row, col):
    piece = board_state[row][col]
    moves = []
    if piece == '.':
        return moves
    
    is_white = piece.isupper()
    
    def is_enemy(r, c):
        target = board_state[r][c]
        if target == '.':
            return False
        return target.islower() if is_white else target.isupper()

    def is_empty(r, c):
        return board_state[r][c] == '.'

    # PAWN RULES
    if piece.lower() == 'p':
        direction = -1 if is_white else 1
        start_row = 6 if is_white else 1
        
        r_f1 = row + direction
        if 0 <= r_f1 < 8 and is_empty(r_f1, col):
            moves.append((r_f1, col))
            r_f2 = row + 2 * direction
            if row == start_row and is_empty(r_f2, col):
                moves.append((r_f2, col))
        
        for dc in [-1, 1]:
            nc = col + dc
            if 0 <= r_f1 < 8 and 0 <= nc < 8:
                if is_enemy(r_f1, nc):
                    moves.append((r_f1, nc))

    # KNIGHT RULES
    elif piece.lower() == 'n':
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_moves:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if is_empty(nr, nc) or is_enemy(nr, nc):
                    moves.append((nr, nc))

    # ROOK, BISHOP, QUEEN RULES
    elif piece.lower() in ['r', 'b', 'q']:
        directions = []
        if piece.lower() in ['r', 'q']:
            directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if piece.lower() in ['b', 'q']:
            directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                if is_empty(nr, nc):
                    moves.append((nr, nc))
                elif is_enemy(nr, nc):
                    moves.append((nr, nc))
                    break
                else:
                    break
                nr += dr
                nc += dc

    # KING RULES
    elif piece.lower() == 'k':
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dr, dc in king_moves:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if is_empty(nr, nc) or is_enemy(nr, nc):
                    moves.append((nr, nc))

    return moves

def is_in_check(board_state, color):
    king_pos = find_king(board_state, color)
    if not king_pos:
        return False
    enemy_color = 'B' if color == 'W' else 'W'
    
    for r in range(ROWS):
        for c in range(COLS):
            piece = board_state[r][c]
            if piece != "." and ((enemy_color == 'W' and piece.isupper()) or (enemy_color == 'B' and piece.islower())):
                if king_pos in get_raw_moves(board_state, r, c):
                    return True
    return False

def get_valid_moves(board_state, row, col):
    piece = board_state[row][col]
    if piece == '.':
        return []
    
    color = 'W' if piece.isupper() else 'B'
    raw_moves = get_raw_moves(board_state, row, col)
    legal_moves = []

    # Filter out moves that leave or put the king in check
    for r2, c2 in raw_moves:
        temp_board = copy.deepcopy(board_state)
        temp_board[r2][c2] = temp_board[row][col]
        temp_board[row][col] = "."
        
        if not is_in_check(temp_board, color):
            legal_moves.append((r2, c2))
            
    return legal_moves

def has_any_legal_moves(board_state, color):
    for r in range(ROWS):
        for c in range(COLS):
            piece = board_state[r][c]
            if piece != "." and ((color == 'W' and piece.isupper()) or (color == 'B' and piece.islower())):
                if len(get_valid_moves(board_state, r, c)) > 0:
                    return True
    return False

def draw_board(win, selected_sq, valid_moves):
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            if selected_sq == (row, col):
                color = HIGHLIGHT_COLOR
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    for r, c in valid_moves:
        pygame.draw.circle(win, DOT_COLOR, (c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2), 18)

def draw_pieces(win):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != ".":
                text_color = (255, 255, 255) if piece.isupper() else (20, 20, 20)
                text_surface = FONT.render(PIECE_SYMBOLS.get(piece, piece), True, text_color)
                text_rect = text_surface.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                win.blit(text_surface, text_rect)

def draw_promotion_menu(win, is_white):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    win.blit(overlay, (0, 0))

    box_width, box_height = 400, 120
    box_x = (WIDTH - box_width) // 2
    box_y = (HEIGHT - box_height) // 2
    pygame.draw.rect(win, (240, 240, 240), (box_x, box_y, box_width, box_height), border_radius=10)
    pygame.draw.rect(win, (100, 100, 100), (box_x, box_y, box_width, box_height), 3, border_radius=10)

    pieces = ['Q', 'R', 'B', 'N'] if is_white else ['q', 'r', 'b', 'n']
    slot_width = box_width // 4

    for i, p in enumerate(pieces):
        sx = box_x + i * slot_width
        sy = box_y
        pygame.draw.rect(win, (200, 200, 200), (sx, sy, slot_width, box_height), 1)
        
        text_color = (255, 255, 255) if p.isupper() else (20, 20, 20)
        sym = PIECE_SYMBOLS[p]
        text_surface = MENU_FONT.render(sym, True, text_color)
        text_rect = text_surface.get_rect(center=(sx + slot_width // 2, sy + box_height // 2))
        win.blit(text_surface, text_rect)

def draw_victory_screen(win, winner):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))

    box_width, box_height = 500, 160
    box_x = (WIDTH - box_width) // 2
    box_y = (HEIGHT - box_height) // 2
    pygame.draw.rect(win, (255, 255, 255), (box_x, box_y, box_width, box_height), border_radius=12)
    pygame.draw.rect(win, (40, 40, 40), (box_x, box_y, box_width, box_height), 4, border_radius=12)

    text = f"Checkmate! {winner} Wins!"
    text_surface = VICTORY_FONT.render(text, True, (20, 20, 20))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    win.blit(text_surface, text_rect)

def get_square_from_mouse(pos):
    x, y = pos
    return (y // SQUARE_SIZE, x // SQUARE_SIZE)

def get_promotion_choice(pos, is_white):
    x, y = pos
    box_width, box_height = 400, 120
    box_x = (WIDTH - box_width) // 2
    box_y = (HEIGHT - box_height) // 2

    if box_x <= x <= box_x + box_width and box_y <= y <= box_y + box_height:
        index = (x - box_x) // (box_width // 4)
        pieces = ['Q', 'R', 'B', 'N'] if is_white else ['q', 'r', 'b', 'n']
        return pieces[index]
    return None

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Engine - DISTRO")
    
    run = True
    clock = pygame.time.Clock()
    selected_sq = None
    valid_moves = []
    turn = 'W'
    pending_promotion = None
    winner = None

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and winner is None:
                pos = pygame.mouse.get_pos()

                if pending_promotion is not None:
                    r, c, is_white = pending_promotion
                    chosen_piece = get_promotion_choice(pos, is_white)
                    if chosen_piece is not None:
                        board[r][c] = chosen_piece
                        pending_promotion = None
                        turn = 'B' if turn == 'W' else 'W'
                        
                        # Check if next player is checkmated after promotion
                        if not has_any_legal_moves(board, turn):
                            winner = "White" if is_white else "Black"
                else:
                    row, col = get_square_from_mouse(pos)
                    clicked_piece = board[row][col]

                    if selected_sq is None:
                        if clicked_piece != ".":
                            if (turn == 'W' and clicked_piece.isupper()) or (turn == 'B' and clicked_piece.islower()):
                                selected_sq = (row, col)
                                valid_moves = get_valid_moves(board, row, col)
                    else:
                        if (row, col) in valid_moves:
                            r1, c1 = selected_sq
                            r2, c2 = (row, col)
                            piece = board[r1][c1]
                            
                            board[r2][c2] = piece
                            board[r1][c1] = "."

                            if piece == 'P' and r2 == 0:
                                pending_promotion = (r2, c2, True)
                            elif piece == 'p' and r2 == 7:
                                pending_promotion = (r2, c2, False)
                            else:
                                turn = 'B' if turn == 'W' else 'W'
                                
                                # Checkmate or stalemate verification after move
                                if not has_any_legal_moves(board, turn):
                                    winner = "Black" if turn == 'W' else "White"
                        
                        selected_sq = None
                        valid_moves = []
                        
                        if clicked_piece != "." and ((turn == 'W' and clicked_piece.isupper()) or (turn == 'B' and clicked_piece.islower())):
                            selected_sq = (row, col)
                            valid_moves = get_valid_moves(board, row, col)

        draw_board(screen, selected_sq, valid_moves)
        draw_pieces(screen)

        if pending_promotion is not None:
            _, _, is_white = pending_promotion
            draw_promotion_menu(screen, is_white)

        if winner is not None:
            draw_victory_screen(screen, winner)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
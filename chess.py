"""
ASCII Chess Game - Full Featured Edition (Fixed)
"""

import json
import time
from datetime import datetime
import os

class ChessGame:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = 'white'
        self.move_history = []
        self.captured_pieces = {'white': [], 'black': []}
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_h_moved = False
        self.black_rook_a_moved = False
        self.black_rook_h_moved = False
        self.en_passant_target = None
        self.use_unicode = True
        self.show_coordinates = True
        self.time_white = 600
        self.time_black = 600
        self.last_move_time = time.time()
        self.use_timer = False
        self.ai_enabled = False
        self.ai_color = 'black'
        
    def initialize_board(self):
        """Initialize the chess board with pieces"""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Black pieces (top)
        board[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        board[1] = ['p'] * 8
        
        # White pieces (bottom)
        board[6] = ['P'] * 8
        board[7] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        
        return board
    
    def get_unicode_piece(self, piece):
        """Get unicode symbol for chess piece"""
        unicode_pieces = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        }
        return unicode_pieces.get(piece, ' ')
    
    def display_board(self):
        """Display the chess board in ASCII with optional unicode pieces"""
        print("\n  ╔═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╗")
        for i in range(8):
            print(f"{8-i} ║", end="")
            for j in range(8):
                piece = self.board[i][j]
                if piece is None:
                    # Checkerboard pattern
                    if (i + j) % 2 == 0:
                        print("   ║", end="")
                    else:
                        print(" · ║", end="")
                else:
                    if self.use_unicode:
                        symbol = self.get_unicode_piece(piece)
                        print(f" {symbol} ║", end="")
                    else:
                        print(f" {piece} ║", end="")
            print()
            if i < 7:
                print("  ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣")
        print("  ╚═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╝")
        print("    a   b   c   d   e   f   g   h\n")
    
    def display_captured_pieces(self):
        """Display captured pieces"""
        print("Captured pieces:")
        white_captured = ''.join([self.get_unicode_piece(p) if self.use_unicode else p 
                                  for p in self.captured_pieces['white']])
        black_captured = ''.join([self.get_unicode_piece(p) if self.use_unicode else p 
                                  for p in self.captured_pieces['black']])
        print(f"  White captured: {black_captured if black_captured else 'None'}")
        print(f"  Black captured: {white_captured if white_captured else 'None'}")
    
    def display_move_history(self, last_n=5):
        """Display recent move history"""
        if not self.move_history:
            return
        print(f"\nLast {min(last_n, len(self.move_history))} moves:")
        for i, (notation, _) in enumerate(self.move_history[-last_n:], 1):
            move_num = len(self.move_history) - last_n + i
            if move_num > 0:
                player = "White" if move_num % 2 == 1 else "Black"
                print(f"  {move_num}. {player}: {notation}")
    
    def display_timer(self):
        """Display remaining time for both players"""
        if not self.use_timer:
            return
        white_min, white_sec = divmod(int(self.time_white), 60)
        black_min, black_sec = divmod(int(self.time_black), 60)
        print(f"\n⏱️  Time - White: {white_min:02d}:{white_sec:02d} | Black: {black_min:02d}:{black_sec:02d}")
    
    def update_timer(self):
        """Update the timer for current player"""
        if not self.use_timer:
            return None
        current_time = time.time()
        elapsed = current_time - self.last_move_time
        
        if self.current_player == 'white':
            self.time_white -= elapsed
            if self.time_white <= 0:
                return 'black'
        else:
            self.time_black -= elapsed
            if self.time_black <= 0:
                return 'white'
        
        self.last_move_time = current_time
        return None
    
    def get_piece_name(self, piece):
        """Get the full name of a piece"""
        names = {
            'p': 'black pawn', 'r': 'black rook', 'n': 'black knight',
            'b': 'black bishop', 'q': 'black queen', 'k': 'black king',
            'P': 'white pawn', 'R': 'white rook', 'N': 'white knight',
            'B': 'white bishop', 'Q': 'white queen', 'K': 'white king'
        }
        return names.get(piece, 'empty')
    
    def is_white_piece(self, piece):
        """Check if a piece belongs to white player"""
        return piece is not None and piece.isupper()
    
    def is_black_piece(self, piece):
        """Check if a piece belongs to black player"""
        return piece is not None and piece.islower()
    
    def parse_position(self, pos):
        """Convert chess notation (e.g., 'e2') to board coordinates"""
        if len(pos) != 2:
            return None
        col = ord(pos[0].lower()) - ord('a')
        try:
            row = 8 - int(pos[1])
        except ValueError:
            return None
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None
    
    def position_to_notation(self, pos):
        """Convert board coordinates to chess notation"""
        row, col = pos
        return f"{chr(col + ord('a'))}{8 - row}"
    
    def is_valid_move(self, from_pos, to_pos):
        """Check if a move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        # Can't move to same square
        if from_pos == to_pos:
            return False
        
        # Can't move empty square
        if piece is None:
            return False
        
        # Can't move opponent's piece
        if self.current_player == 'white' and not self.is_white_piece(piece):
            return False
        if self.current_player == 'black' and not self.is_black_piece(piece):
            return False
        
        # Can't capture own piece
        if self.current_player == 'white' and self.is_white_piece(target):
            return False
        if self.current_player == 'black' and self.is_black_piece(target):
            return False
        
        # Check piece-specific moves
        piece_type = piece.lower()
        
        if piece_type == 'p':
            return self.is_valid_pawn_move(from_pos, to_pos)
        elif piece_type == 'r':
            return self.is_valid_rook_move(from_pos, to_pos)
        elif piece_type == 'n':
            return self.is_valid_knight_move(from_pos, to_pos)
        elif piece_type == 'b':
            return self.is_valid_bishop_move(from_pos, to_pos)
        elif piece_type == 'q':
            return self.is_valid_queen_move(from_pos, to_pos)
        elif piece_type == 'k':
            return self.is_valid_king_move(from_pos, to_pos)
        
        return False
    
    def is_valid_pawn_move(self, from_pos, to_pos):
        """Check if pawn move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        if self.is_white_piece(piece):
            direction = -1
            start_row = 6
        else:
            direction = 1
            start_row = 1
        
        # Move forward one square
        if from_col == to_col and to_row == from_row + direction and target is None:
            return True
        
        # Move forward two squares from starting position
        if (from_col == to_col and from_row == start_row and 
            to_row == from_row + 2 * direction and 
            target is None and 
            self.board[from_row + direction][from_col] is None):
            return True
        
        # Capture diagonally
        if (abs(from_col - to_col) == 1 and 
            to_row == from_row + direction and 
            target is not None):
            return True
        
        # En passant
        if (abs(from_col - to_col) == 1 and 
            to_row == from_row + direction and 
            target is None and 
            self.en_passant_target == to_pos):
            return True
        
        return False
    
    def is_valid_rook_move(self, from_pos, to_pos):
        """Check if rook move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        if from_row != to_row and from_col != to_col:
            return False
        
        return self.is_path_clear(from_pos, to_pos)
    
    def is_valid_knight_move(self, from_pos, to_pos):
        """Check if knight move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    def is_valid_bishop_move(self, from_pos, to_pos):
        """Check if bishop move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        if abs(from_row - to_row) != abs(from_col - to_col):
            return False
        
        return self.is_path_clear(from_pos, to_pos)
    
    def is_valid_queen_move(self, from_pos, to_pos):
        """Check if queen move is valid"""
        return (self.is_valid_rook_move(from_pos, to_pos) or 
                self.is_valid_bishop_move(from_pos, to_pos))
    
    def is_valid_king_move(self, from_pos, to_pos):
        """Check if king move is valid (including castling)"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        
        # Normal king move
        if row_diff <= 1 and col_diff <= 1:
            return True
        
        # Castling
        if row_diff == 0 and col_diff == 2:
            return self.can_castle(from_pos, to_pos)
        
        return False
    
    def can_castle(self, from_pos, to_pos):
        """Check if castling is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        
        # King must not have moved
        if piece == 'K' and self.white_king_moved:
            return False
        if piece == 'k' and self.black_king_moved:
            return False
        
        # Must be on same row
        if from_row != to_row:
            return False
        
        # Determine castling side
        if to_col > from_col:  # Kingside
            rook_col = 7
            if piece == 'K' and self.white_rook_h_moved:
                return False
            if piece == 'k' and self.black_rook_h_moved:
                return False
            cols_between = range(from_col + 1, rook_col)
        else:  # Queenside
            rook_col = 0
            if piece == 'K' and self.white_rook_a_moved:
                return False
            if piece == 'k' and self.black_rook_a_moved:
                return False
            cols_between = range(rook_col + 1, from_col)
        
        # Check if rook is in position
        expected_rook = 'R' if self.is_white_piece(piece) else 'r'
        if self.board[from_row][rook_col] != expected_rook:
            return False
        
        # Path must be clear
        for col in cols_between:
            if self.board[from_row][col] is not None:
                return False
        
        # King must not be in check, pass through check, or end in check
        opponent = 'black' if self.current_player == 'white' else 'white'
        for col in range(min(from_col, to_col), max(from_col, to_col) + 1):
            if self.is_square_attacked((from_row, col), opponent):
                return False
        
        return True
    
    def is_path_clear(self, from_pos, to_pos):
        """Check if path between two positions is clear"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        current_row = from_row + row_step
        current_col = from_col + col_step
        
        while current_row != to_row or current_col != to_col:
            if self.board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def find_king(self, color):
        """Find the position of the king for the given color"""
        king = 'K' if color == 'white' else 'k'
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == king:
                    return (i, j)
        return None
    
    def is_square_attacked(self, pos, by_color):
        """Check if a square is attacked by the given color"""
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece is None:
                    continue
                
                if by_color == 'white' and not self.is_white_piece(piece):
                    continue
                if by_color == 'black' and not self.is_black_piece(piece):
                    continue
                
                # Temporarily switch player to check if move is valid
                original_player = self.current_player
                self.current_player = by_color
                valid = self.is_valid_move((i, j), pos)
                self.current_player = original_player
                
                if valid:
                    return True
        
        return False
    
    def would_be_in_check(self, from_pos, to_pos):
        """Check if move would put current player in check"""
        # Make temporary move
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]
        
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Check if king is in check
        king_pos = self.find_king(self.current_player)
        opponent = 'black' if self.current_player == 'white' else 'white'
        in_check = self.is_square_attacked(king_pos, opponent)
        
        # Undo move
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured
        
        return in_check
    
    def get_all_valid_moves(self, pos):
        """Get all valid moves for a piece at given position"""
        valid_moves = []
        for to_row in range(8):
            for to_col in range(8):
                if self.is_valid_move(pos, (to_row, to_col)):
                    if not self.would_be_in_check(pos, (to_row, to_col)):
                        valid_moves.append((to_row, to_col))
        return valid_moves
    
    def show_available_moves(self, pos):
        """Display available moves for a piece"""
        piece = self.board[pos[0]][pos[1]]
        if piece is None:
            print("No piece at that position!")
            return
        
        print(f"Piece at {self.position_to_notation(pos)}: {self.get_piece_name(piece)}")
        
        moves = self.get_all_valid_moves(pos)
        if not moves:
            print("No valid moves available for this piece.")
            return
        
        move_notations = [self.position_to_notation(move) for move in moves]
        print(f"Available moves: {', '.join(move_notations)}")
    
    def make_move(self, from_pos, to_pos):
        """Make a move on the board"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]
        
        # Generate move notation
        notation = self.get_move_notation(from_pos, to_pos, piece, captured)
        
        # Handle en passant capture
        en_passant_capture = None
        if piece.lower() == 'p' and to_pos == self.en_passant_target and captured is None:
            # Capture the pawn
            direction = -1 if self.is_white_piece(piece) else 1
            en_passant_capture = self.board[to_row - direction][to_col]
            self.board[to_row - direction][to_col] = None
            if self.current_player == 'white':
                self.captured_pieces['white'].append(en_passant_capture)
            else:
                self.captured_pieces['black'].append(en_passant_capture)
        
        # Track king and rook movements for castling
        if piece == 'K':
            self.white_king_moved = True
        elif piece == 'k':
            self.black_king_moved = True
        elif piece == 'R' and from_row == 7 and from_col == 0:
            self.white_rook_a_moved = True
        elif piece == 'R' and from_row == 7 and from_col == 7:
            self.white_rook_h_moved = True
        elif piece == 'r' and from_row == 0 and from_col == 0:
            self.black_rook_a_moved = True
        elif piece == 'r' and from_row == 0 and from_col == 7:
            self.black_rook_h_moved = True
        
        # Handle castling
        if piece.lower() == 'k' and abs(to_col - from_col) == 2:
            # Move the rook
            if to_col > from_col:  # Kingside
                rook_from = (from_row, 7)
                rook_to = (from_row, 5)
            else:  # Queenside
                rook_from = (from_row, 0)
                rook_to = (from_row, 3)
            
            rook = self.board[rook_from[0]][rook_from[1]]
            self.board[rook_to[0]][rook_to[1]] = rook
            self.board[rook_from[0]][rook_from[1]] = None
        
        # Set en passant target
        if piece.lower() == 'p' and abs(to_row - from_row) == 2:
            direction = -1 if self.is_white_piece(piece) else 1
            self.en_passant_target = (from_row + direction, from_col)
        else:
            self.en_passant_target = None
        
        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Handle captures
        if captured is not None:
            if self.current_player == 'white':
                self.captured_pieces['white'].append(captured)
            else:
                self.captured_pieces['black'].append(captured)
        
        # Pawn promotion
        promoted_to = None
        if piece.lower() == 'p':
            if (piece == 'P' and to_row == 0) or (piece == 'p' and to_row == 7):
                promoted_to = self.promote_pawn(to_pos)
                notation += f"={promoted_to.upper()}"
        
        # Store complete move state for undo
        move_state = {
            'from_pos': from_pos,
            'to_pos': to_pos,
            'piece': piece,
            'captured': captured,
            'en_passant_target_before': self.en_passant_target,
            'en_passant_capture': en_passant_capture,
            'promoted_to': promoted_to,
            'castled': piece.lower() == 'k' and abs(to_col - from_col) == 2
        }
        
        # Record move
        self.move_history.append((notation, move_state))
        
        print(f"\n✓ Move made: {notation}")
        print(f"  {self.get_piece_name(piece)} from {self.position_to_notation(from_pos)} to {self.position_to_notation(to_pos)}")
        
        # Switch player
        self.current_player = 'black' if self.current_player == 'white' else 'white'
    
    def get_move_notation(self, from_pos, to_pos, piece, captured):
        """Generate algebraic notation for a move"""
        piece_symbols = {'k': 'K', 'q': 'Q', 'r': 'R', 'b': 'B', 'n': 'N', 'p': ''}
        
        piece_type = piece.lower()
        symbol = piece_symbols.get(piece_type, '')
        
        from_notation = self.position_to_notation(from_pos)
        to_notation = self.position_to_notation(to_pos)
        
        # Special notation for castling
        if piece_type == 'k' and abs(from_pos[1] - to_pos[1]) == 2:
            return "O-O" if to_pos[1] > from_pos[1] else "O-O-O"
        
        # Capture notation
        capture_symbol = 'x' if captured is not None else ''
        
        # For pawns, include file if capturing
        if piece_type == 'p' and captured is not None:
            return f"{from_notation[0]}{capture_symbol}{to_notation}"
        
        return f"{symbol}{capture_symbol}{to_notation}"
    
    def promote_pawn(self, pos):
        """Promote a pawn to chosen piece"""
        row, col = pos
        piece = self.board[row][col]
        
        # AI auto-promotes to queen
        if self.ai_enabled and self.current_player == self.ai_color:
            if self.is_white_piece(piece):
                self.board[row][col] = 'Q'
                return 'Q'
            else:
                self.board[row][col] = 'q'
                return 'q'
        
        print("\n🎉 Pawn promotion! Choose piece:")
        print("  Q - Queen")
        print("  R - Rook")
        print("  B - Bishop")
        print("  N - Knight")
        
        while True:
            choice = input("Enter choice (Q/R/B/N): ").strip().upper()
            if choice in ['Q', 'R', 'B', 'N']:
                if self.is_white_piece(piece):
                    self.board[row][col] = choice
                else:
                    self.board[row][col] = choice.lower()
                return choice
            print("Invalid choice! Please enter Q, R, B, or N.")
    
    def undo_move(self):
        """Undo the last move"""
        if not self.move_history:
            print("No moves to undo!")
            return False
        
        notation, move_state = self.move_history.pop()
        
        # Switch player back
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
        from_pos = move_state['from_pos']
        to_pos = move_state['to_pos']
        piece = move_state['piece']
        captured = move_state['captured']
        
        # Restore board state
        self.board[from_pos[0]][from_pos[1]] = piece
        self.board[to_pos[0]][to_pos[1]] = captured
        
        # Restore en passant
        self.en_passant_target = move_state.get('en_passant_target_before')
        
        # Handle en passant capture
        if move_state.get('en_passant_capture'):
            direction = -1 if self.is_white_piece(piece) else 1
            self.board[to_pos[0] - direction][to_pos[1]] = move_state['en_passant_capture']
            if self.current_player == 'white':
                self.captured_pieces['white'].remove(move_state['en_passant_capture'])
            else:
                self.captured_pieces['black'].remove(move_state['en_passant_capture'])
        
        # Handle captured pieces
        if captured:
            if self.current_player == 'white':
                self.captured_pieces['white'].remove(captured)
            else:
                self.captured_pieces['black'].remove(captured)
        
        # Handle castling undo
        if move_state.get('castled'):
            if to_pos[1] > from_pos[1]:  # Kingside
                rook_from = (from_pos[0], 5)
                rook_to = (from_pos[0], 7)
            else:  # Queenside
                rook_from = (from_pos[0], 3)
                rook_to = (from_pos[0], 0)
            
            rook = self.board[rook_from[0]][rook_from[1]]
            self.board[rook_to[0]][rook_to[1]] = rook
            self.board[rook_from[0]][rook_from[1]] = None
        
        print(f"✓ Undid move: {notation}")
        return True
    
    def is_checkmate(self):
        """Check if current player is in checkmate"""
        king_pos = self.find_king(self.current_player)
        opponent = 'black' if self.current_player == 'white' else 'white'
        
        if not self.is_square_attacked(king_pos, opponent):
            return False
        
        # Try all possible moves
        for from_row in range(8):
            for from_col in range(8):
                piece = self.board[from_row][from_col]
                if piece is None:
                    continue
                
                if self.current_player == 'white' and not self.is_white_piece(piece):
                    continue
                if self.current_player == 'black' and not self.is_black_piece(piece):
                    continue
                
                for to_row in range(8):
                    for to_col in range(8):
                        if self.is_valid_move((from_row, from_col), (to_row, to_col)):
                            if not self.would_be_in_check((from_row, from_col), (to_row, to_col)):
                                return False
        
        return True
    
    def is_stalemate(self):
        """Check if current player is in stalemate"""
        king_pos = self.find_king(self.current_player)
        opponent = 'black' if self.current_player == 'white' else 'white'
        
        if self.is_square_attacked(king_pos, opponent):
            return False
        
        # Check if any legal move exists
        for from_row in range(8):
            for from_col in range(8):
                piece = self.board[from_row][from_col]
                if piece is None:
                    continue
                
                if self.current_player == 'white' and not self.is_white_piece(piece):
                    continue
                if self.current_player == 'black' and not self.is_black_piece(piece):
                    continue
                
                for to_row in range(8):
                    for to_col in range(8):
                        if self.is_valid_move((from_row, from_col), (to_row, to_col)):
                            if not self.would_be_in_check((from_row, from_col), (to_row, to_col)):
                                return False
        
        return True
    
    def save_game(self, filename="chess_save.json"):
        """Save the current game state to a file"""
        game_state = {
            'board': self.board,
            'current_player': self.current_player,
            'move_history': [(notation, state) for notation, state in self.move_history],
            'captured_pieces': self.captured_pieces,
            'white_king_moved': self.white_king_moved,
            'black_king_moved': self.black_king_moved,
            'white_rook_a_moved': self.white_rook_a_moved,
            'white_rook_h_moved': self.white_rook_h_moved,
            'black_rook_a_moved': self.black_rook_a_moved,
            'black_rook_h_moved': self.black_rook_h_moved,
            'en_passant_target': self.en_passant_target,
            'time_white': self.time_white,
            'time_black': self.time_black,
            'use_timer': self.use_timer
        }
        
        with open(filename, 'w') as f:
            json.dump(game_state, f, indent=2)
        
        print(f"✓ Game saved to {filename}")
    
    def load_game(self, filename="chess_save.json"):
        """Load a game state from a file"""
        if not os.path.exists(filename):
            print(f"Save file {filename} not found!")
            return False
        
        with open(filename, 'r') as f:
            game_state = json.load(f)
        
        self.board = game_state['board']
        self.current_player = game_state['current_player']
        self.move_history = [(notation, state) for notation, state in game_state['move_history']]
        self.captured_pieces = game_state['captured_pieces']
        self.white_king_moved = game_state['white_king_moved']
        self.black_king_moved = game_state['black_king_moved']
        self.white_rook_a_moved = game_state['white_rook_a_moved']
        self.white_rook_h_moved = game_state['white_rook_h_moved']
        self.black_rook_a_moved = game_state['black_rook_a_moved']
        self.black_rook_h_moved = game_state['black_rook_h_moved']
        self.en_passant_target = game_state.get('en_passant_target')
        self.time_white = game_state.get('time_white', 600)
        self.time_black = game_state.get('time_black', 600)
        self.use_timer = game_state.get('use_timer', False)
        self.last_move_time = time.time()
        
        print(f"✓ Game loaded from {filename}")
        return True
    
    def make_ai_move(self):
        """Simple AI that makes a random valid move"""
        import random
        
        # Get all pieces for AI color
        ai_pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is None:
                    continue
                if self.ai_color == 'white' and self.is_white_piece(piece):
                    ai_pieces.append((row, col))
                elif self.ai_color == 'black' and self.is_black_piece(piece):
                    ai_pieces.append((row, col))
        
        # Find all valid moves
        valid_moves = []
        for from_pos in ai_pieces:
            for to_row in range(8):
                for to_col in range(8):
                    to_pos = (to_row, to_col)
                    if self.is_valid_move(from_pos, to_pos):
                        if not self.would_be_in_check(from_pos, to_pos):
                            # Score the move
                            score = self.score_move(from_pos, to_pos)
                            valid_moves.append((from_pos, to_pos, score))
        
        if not valid_moves:
            return False
        
        # Sort by score and pick one of the top moves
        valid_moves.sort(key=lambda x: x[2], reverse=True)
        top_moves = valid_moves[:min(3, len(valid_moves))]
        from_pos, to_pos, _ = random.choice(top_moves)
        
        print(f"\n🤖 AI is thinking...")
        time.sleep(0.5)  # Dramatic pause
        
        self.make_move(from_pos, to_pos)
        return True
    
    def score_move(self, from_pos, to_pos):
        """Score a move for AI (simple evaluation)"""
        score = 0
        target = self.board[to_pos[0]][to_pos[1]]
        
        # Capture value
        piece_values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}
        if target:
            score += piece_values.get(target.lower(), 0) * 10
        
        # Center control
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if to_pos in center_squares:
            score += 2
        
        # Random factor
        import random
        score += random.random()
        
        return score
    
    def play(self):
        """Main game loop"""
        print("\n" + "╔" + "═" * 48 + "╗")
        print("║" + " " * 12 + "ASCII CHESS GAME" + " " * 20 + "║")
        print("╚" + "═" * 48 + "╝")
        
        # Simplified game setup
        print("\n⚙️  Game Setup:")
        
        # Unicode pieces
        use_unicode = input("Use unicode chess pieces? (y/n) [y]: ").strip().lower()
        self.use_unicode = use_unicode != 'n'
        
        # Timer
        use_timer = input("Use timer? (y/n) [n]: ").strip().lower()
        if use_timer == 'y':
            self.use_timer = True
            try:
                minutes = int(input("Minutes per player [10]: ").strip() or "10")
                self.time_white = self.time_black = minutes * 60
            except ValueError:
                self.time_white = self.time_black = 600
        
        # AI opponent
        ai_opponent = input("Play against AI? (y/n) [n]: ").strip().lower()
        if ai_opponent == 'y':
            self.ai_enabled = True
            ai_color = input("AI plays as (white/black) [black]: ").strip().lower()
            self.ai_color = 'white' if ai_color == 'white' else 'black'
        
        # Load saved game
        load_save = input("Load saved game? (y/n) [n]: ").strip().lower()
        if load_save == 'y':
            if self.load_game():
                print("Game loaded successfully!")
            else:
                print("Starting new game...")
        
        print("\n" + "═" * 50)
        print("🎮 COMMANDS:")
        print("  • Move: e2 e4")
        print("  • Show moves: show e2")
        print("  • Undo: undo")
        print("  • Save: save")
        print("  • Help: help")
        print("  • Quit: quit")
        print("═" * 50)
        print(" " * 15 + "Created by wortex213433")
        
        self.last_move_time = time.time()
        
        while True:
            print("\n" + "=" * 70)
            self.display_board()
            self.display_captured_pieces()
            self.display_move_history()
            if self.use_timer:
                self.display_timer()
            print("=" * 70)
            
            # Check timer
            if self.use_timer:
                winner = self.update_timer()
                if winner:
                    print(f"\n⏱️  TIME'S UP! {winner.upper()} WINS!")
                    break
            
            # Check for checkmate or stalemate
            if self.is_checkmate():
                winner = 'Black' if self.current_player == 'white' else 'White'
                print(f"\n🏆 CHECKMATE! {winner} wins!")
                print(" " * 15 + "- wortex213433")
                break
            
            if self.is_stalemate():
                print(f"\n🤝 STALEMATE! Game is a draw!")
                print(" " * 15 + "- wortex213433")
                break
            
            # Check if in check
            king_pos = self.find_king(self.current_player)
            opponent = 'black' if self.current_player == 'white' else 'white'
            if self.is_square_attacked(king_pos, opponent):
                print(f"⚠️  {self.current_player.upper()} is in CHECK!")
            
            # AI move
            if self.ai_enabled and self.current_player == self.ai_color:
                if not self.make_ai_move():
                    print("AI has no valid moves!")
                    break
                continue
            
            print(f"\n💭 {self.current_player.upper()}'s turn")
            move_input = input("► Enter command: ").strip().lower()
            
            if move_input == '':
                continue
            
            if move_input == 'quit':
                save_before_quit = input("Save game before quitting? (y/n): ").strip().lower()
                if save_before_quit == 'y':
                    self.save_game()
                print("Thanks for playing! 👋")
                print("Created by wortex213433\n")
                break
            
            if move_input == 'help':
                print("\n📖 HELP:")
                print("• Pawn: Forward 1 (or 2 from start), captures diagonally")
                print("• Rook: Horizontal or vertical")
                print("• Knight: L-shape (2+1 squares)")
                print("• Bishop: Diagonal")
                print("• Queen: Any direction")
                print("• King: Any direction, 1 square")
                print("• Castling: King moves 2 squares toward rook (e.g., e1 g1)")
                print("• En passant: Special pawn capture")
                print(" " * 15 + "Created by wortex213433")
                continue
            
            if move_input == 'undo':
                self.undo_move()
                if self.ai_enabled:  # Undo AI move too
                    self.undo_move()
                continue
            
            if move_input == 'save':
                self.save_game()
                continue
            
            if move_input.startswith('show '):
                pos_str = move_input.split()[1] if len(move_input.split()) > 1 else None
                if pos_str:
                    pos = self.parse_position(pos_str)
                    if pos:
                        self.show_available_moves(pos)
                    else:
                        print("Invalid position!")
                continue
            
            parts = move_input.split()
            if len(parts) != 2:
                print("❌ Invalid input! Use format: e2 e4")
                continue
            
            from_pos = self.parse_position(parts[0])
            to_pos = self.parse_position(parts[1])
            
            if from_pos is None or to_pos is None:
                print("❌ Invalid position! Use format: e2 e4 (columns a-h, rows 1-8)")
                continue
            
            # Show what piece is being moved
            piece = self.board[from_pos[0]][from_pos[1]]
            if piece:
                print(f"Attempting to move {self.get_piece_name(piece)}...")
            
            if not self.is_valid_move(from_pos, to_pos):
                print("❌ Invalid move! Please try again.")
                # Show available moves for selected piece
                if piece and ((self.current_player == 'white' and self.is_white_piece(piece)) or
                             (self.current_player == 'black' and self.is_black_piece(piece))):
                    self.show_available_moves(from_pos)
                continue
            
            if self.would_be_in_check(from_pos, to_pos):
                print("❌ Invalid move! This would put your king in check.")
                continue
            
            self.make_move(from_pos, to_pos)

if __name__ == "__main__":
    game = ChessGame()
    game.play()

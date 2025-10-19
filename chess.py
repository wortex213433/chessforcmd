"""
Chess Game
A complete two-player chess game with standard rules
"""

class ChessGame:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = 'white'
        self.move_history = []
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_h_moved = False
        self.black_rook_a_moved = False
        self.black_rook_h_moved = False
        
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
    
    def display_board(self):
        """Display the chess board in ASCII"""
        print("\n  +---+---+---+---+---+---+---+---+")
        for i in range(8):
            print(f"{8-i} |", end="")
            for j in range(8):
                piece = self.board[i][j]
                if piece is None:
                    print("   |", end="")
                else:
                    print(f" {piece} |", end="")
            print(f"\n  +---+---+---+---+---+---+---+---+")
        print("    a   b   c   d   e   f   g   h")
        print()
        
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
        row = 8 - int(pos[1])
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None
    
    def is_valid_move(self, from_pos, to_pos):
        """Check if a move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
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
        
        if self.is_white_piece(piece):  # White pawn moves up
            direction = -1
            start_row = 6
        else:  # Black pawn moves down
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
        
        return False
    
    def is_valid_rook_move(self, from_pos, to_pos):
        """Check if rook move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Rook moves horizontally or vertically
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
        
        # Bishop moves diagonally
        if abs(from_row - to_row) != abs(from_col - to_col):
            return False
        
        return self.is_path_clear(from_pos, to_pos)
    
    def is_valid_queen_move(self, from_pos, to_pos):
        """Check if queen move is valid"""
        # Queen moves like rook or bishop
        return (self.is_valid_rook_move(from_pos, to_pos) or 
                self.is_valid_bishop_move(from_pos, to_pos))
    
    def is_valid_king_move(self, from_pos, to_pos):
        """Check if king move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        
        # King moves one square in any direction
        return row_diff <= 1 and col_diff <= 1
    
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
    
    def make_move(self, from_pos, to_pos):
        """Make a move on the board"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]
        
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
        
        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Pawn promotion
        if piece.lower() == 'p':
            if (piece == 'P' and to_row == 0) or (piece == 'p' and to_row == 7):
                self.promote_pawn(to_pos)
        
        # Record move
        self.move_history.append((from_pos, to_pos, piece, captured))
        
        # Switch player
        self.current_player = 'black' if self.current_player == 'white' else 'white'
    
    def promote_pawn(self, pos):
        """Promote a pawn to queen (simplified - always queen)"""
        row, col = pos
        piece = self.board[row][col]
        if self.is_white_piece(piece):
            self.board[row][col] = 'Q'
        else:
            self.board[row][col] = 'q'
        print("Pawn promoted to Queen!")
    
    def is_checkmate(self):
        """Check if current player is in checkmate"""
        # First check if in check
        king_pos = self.find_king(self.current_player)
        opponent = 'black' if self.current_player == 'white' else 'white'
        
        if not self.is_square_attacked(king_pos, opponent):
            return False
        
        # Try all possible moves to see if any gets out of check
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
        # Check if in check (stalemate requires not being in check)
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
    
    def play(self):
        """Main game loop"""
        print("=" * 50)
        print("ASCII CHESS GAME")
        print("=" * 50)
        print("\nPiece symbols:")
        print("White: P=Pawn, R=Rook, N=Knight, B=Bishop, Q=Queen, K=King")
        print("Black: p=pawn, r=rook, n=knight, b=bishop, q=queen, k=king")
        print("\nEnter moves in format: e2 e4")
        print("Type 'quit' to exit, 'help' for piece info")
        print("=" * 50)
        
        while True:
            self.display_board()
            
            # Check for checkmate or stalemate
            if self.is_checkmate():
                winner = 'Black' if self.current_player == 'white' else 'White'
                print(f"\n{'='*50}")
                print(f"CHECKMATE! {winner} wins!")
                print(f"{'='*50}")
                break
            
            if self.is_stalemate():
                print(f"\n{'='*50}")
                print("STALEMATE! Game is a draw!")
                print(f"{'='*50}")
                break
            
            # Check if in check
            king_pos = self.find_king(self.current_player)
            opponent = 'black' if self.current_player == 'white' else 'white'
            if self.is_square_attacked(king_pos, opponent):
                print(f"⚠️  {self.current_player.upper()} is in CHECK!")
            
            print(f"{self.current_player.upper()}'s turn")
            move_input = input("Enter move (e.g., 'e2 e4'): ").strip().lower()
            
            if move_input == 'quit':
                print("Thanks for playing!")
                break
            
            if move_input == 'help':
                print("\nPiece Movement Rules:")
                print("- Pawn: Forward 1 (or 2 from start), captures diagonally")
                print("- Rook: Horizontal or vertical, any distance")
                print("- Knight: L-shape (2+1 squares)")
                print("- Bishop: Diagonal, any distance")
                print("- Queen: Any direction, any distance")
                print("- King: Any direction, 1 square")
                input("\nPress Enter to continue...")
                continue
            
            parts = move_input.split()
            if len(parts) != 2:
                print("Invalid input! Use format: e2 e4")
                continue
            
            from_pos = self.parse_position(parts[0])
            to_pos = self.parse_position(parts[1])
            
            if from_pos is None or to_pos is None:
                print("Invalid position! Use format: e2 e4 (columns a-h, rows 1-8)")
                continue
            
            if not self.is_valid_move(from_pos, to_pos):
                print("Invalid move! Please try again.")
                continue
            
            if self.would_be_in_check(from_pos, to_pos):
                print("Invalid move! This would put your king in check.")
                continue
            
            self.make_move(from_pos, to_pos)

if __name__ == "__main__":
    game = ChessGame()
    game.play()

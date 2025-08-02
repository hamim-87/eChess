def get_move_from_matrices(prev, curr):
    """
    Given two 8x8 matrices (previous and current board), return the move in UCI format (e.g., e2e4).
    Returns None if no move detected.
    Also prints Stockfish's reply in both UCI and your expected string format.
    """
    board_state = ChessBoardState()
    board_state.update_state(prev)
    board_state.update_state(curr)
    move = board_state.detect_move()
    if move is None:
        return None
    moved_from, moved_to, color, piece_type = move
    print(f"hudao : {move}")
    s = f"{moved_from[0]}{moved_from[1]}{moved_to[0]}{moved_to[1]}"
    x = board_state.move_to_uci(move)
    print(f"hu :{x}")
    print(f"return value : {s}")

    # Get Stockfish reply
    fen = get_initial_fen()
    stockfish_uci = send_move_to_stockfish(fen, x)
    print(f"Stockfish UCI move: {stockfish_uci}")

    # Convert Stockfish UCI move to your expected string format
    def uci_to_custom(uci):
        col_from = ord(uci[0]) - ord('a')
        row_from = 8 - int(uci[1])
        col_to = ord(uci[2]) - ord('a')
        row_to = 8 - int(uci[3])
        return f"{col_from}{row_from}{col_to}{row_to}"

    if stockfish_uci:
        stockfish_custom = uci_to_custom(stockfish_uci)
        print(f"Stockfish move (custom format): {stockfish_custom}")
    else:
        stockfish_custom = None
        print("Stockfish did not return a move.")

    return  stockfish_custom
import random
def get_all_pawn_moves(board, color):
    # Only for visualization: generate all possible single pawn moves (no captures, no promotions)
    moves = []
    if color == 'white':
        for i in range(8):
            for j in range(8):
                if board[i][j] == 3:
                    # Forward move
                    if i > 0 and board[i-1][j] == 1:
                        moves.append(((i, j), (i-1, j)))
                    # Capture left
                    if i > 0 and j > 0 and board[i-1][j-1] == 2:
                        moves.append(((i, j), (i-1, j-1)))
                    # Capture right
                    if i > 0 and j < 7 and board[i-1][j+1] == 2:
                        moves.append(((i, j), (i-1, j+1)))
    elif color == 'black':
        for i in range(8):
            for j in range(8):
                if board[i][j] == 2:
                    # Forward move
                    if i < 7 and board[i+1][j] == 1:
                        moves.append(((i, j), (i+1, j)))
                    # Capture left
                    if i < 7 and j > 0 and board[i+1][j-1] == 3:
                        moves.append(((i, j), (i+1, j-1)))
                    # Capture right
                    if i < 7 and j < 7 and board[i+1][j+1] == 3:
                        moves.append(((i, j), (i+1, j+1)))
    return moves
def coord_to_chess_notation(coord):
    row, col = coord
    file = chr(ord('a') + col)      # col: 0->'a', 7->'h'
    rank = str(8 - row)             # row: 0->'8', 7->'1'
    return file + rank
import subprocess

engine_path = r"D:\DEVops\BUET\micro process project\stockfish\stockfish-windows-x86-64-avx2"
def detect_move_and_info(prev, curr):
    board_state = ChessBoardState()
    board_state.update_state(prev)
    board_state.update_state(curr)
    move = board_state.detect_move()
    uci_move = board_state.move_to_uci(move)
    if move:
        moved_from, moved_to, color, piece_type = move
        return {
            'uci': uci_move,
            'from': moved_from,
            'to': moved_to,
            'color': color,
            'piece_type': piece_type
        }
    else:
        return None

def send_move_to_stockfish(fen, move_uci, engine_path=engine_path):
    """
    fen: FEN string representing the board position
    move_uci: move in UCI format (e.g., e2e4)
    engine_path: path to Stockfish binary
    Returns: Stockfish best move in UCI format
    """
    process = subprocess.Popen(
        [engine_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    # Set up position and move
    commands = [
        f"position fen {fen} moves {move_uci}",
        "go",
        "quit"
    ]
    for cmd in commands:
        process.stdin.write(cmd + "\n")
    process.stdin.flush()
    output = []
    while True:
        line = process.stdout.readline()
        if not line:
            break
        output.append(line.strip())
        if line.startswith('bestmove'):
            break
    process.terminate()
    for line in output:
        if line.startswith('bestmove'):
            return line.split()[1]
    return None
def get_initial_board_matrix():
    board = np.ones((8,8), dtype=int)
    board[0,:] = 2
    board[1,:] = 2
    board[6,:] = 3
    board[7,:] = 3
    return board
def get_initial_fen():
    return "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
def guess_piece_type(coord, color):
    row, col = coord
    if color == 'white':
        if row == 6:
            return 'pawn'
        elif row == 7:
            if col in [0, 7]:
                return 'rook'
            elif col in [1, 6]:
                return 'knight'
            elif col in [2, 5]:
                return 'bishop'
            elif col == 3:
                return 'queen'
            elif col == 4:
                return 'king'
    elif color == 'black':
        if row == 1:
            return 'pawn'
        elif row == 0:
            if col in [0, 7]:
                return 'rook'
            elif col in [1, 6]:
                return 'knight'
            elif col in [2, 5]:
                return 'bishop'
            elif col == 3:
                return 'queen'
            elif col == 4:
                return 'king'
    return 'unknown'
def print_board(board):
    symbol_map = {1: '.', 2: 'b', 3: 'w'}
    print("  a b c d e f g h")
    for i, row in enumerate(board):
        print(8 - i, end=' ')
        for cell in row:
            print(symbol_map.get(cell, '?'), end=' ')
        print(8 - i)
    print("  a b c d e f g h\n")

import numpy as np

# Assume this function is provided and returns the current 8x8 board matrix
def get_current_board():
    # Placeholder: Replace with your actual model call
    # Example: return model.predict(image)
    return np.ones((8,8), dtype=int)

class ChessBoardState:
    def __init__(self):
        self.prev_state = None
        self.current_state = None

    def update_state(self, new_state):
        new_state = np.array(new_state)  # Ensure it's a NumPy array
        self.prev_state = self.current_state
        self.current_state = new_state

    def detect_move(self):
        if self.prev_state is None or self.current_state is None:
            return None
        diff = self.current_state - self.prev_state
        moved_from = None
        moved_to = None
        for i in range(8):
            for j in range(8):
                if diff[i][j] < 0:
                    moved_from = (i, j)
                elif diff[i][j] > 0:
                    moved_to = (i, j)
        if moved_from and moved_to:
            # Determine color and piece type
            val = self.prev_state[moved_from[0]][moved_from[1]]
            if val == 2:
                color = 'black'
            elif val == 3:
                color = 'white'
            else:
                color = 'unknown'
            piece_type = guess_piece_type(moved_from, color)
            return moved_from, moved_to, color, piece_type
        return None

    def move_to_uci(self, move):
        if move is None:
            return None
        moved_from, moved_to = move[0], move[1]
        print(f"moved_from : {moved_from}")
        print(f"moved to : {moved_to}")
        return self.coord_to_uci(moved_from) + self.coord_to_uci(moved_to)

    @staticmethod
    def coord_to_uci(coord):
        return coord_to_chess_notation(coord)

if __name__ == "__main__":

    # Demo: Use get_move_from_matrices with a random prev state and a simulated move
    print("\n--- Demo: get_move_from_matrices with random prev state ---")
    board = get_initial_board_matrix()
    prev = board.copy()
    # Simulate a random white pawn move
    moves = get_all_pawn_moves(prev, 'white')
    if moves:
        move = random.choice(moves)
        curr = prev.copy()
        from_sq, to_sq = move
        curr[from_sq[0]][from_sq[1]] = 1  # Remove pawn from old
        curr[to_sq[0]][to_sq[1]] = 3      # Place pawn at new
        print("Prev board:")
        print_board(prev)
        print("Curr board:")
        print_board(curr)
        uci = get_move_from_matrices(prev, curr)
        print(f"Detected move (UCI): {uci}")
    else:
        print("No legal pawn moves for white.")




from stockfish import Stockfish
import numpy as np
import requests
# Set path to Stockfish executable
stockfish = Stockfish(path="D:\DEVops\BUET\micro process project\stockfish\stockfish-windows-x86-64-avx2")

# Set difficulty (optional)
stockfish.set_skill_level(10)

moves = ["d2d4", "d7d5"]  



def detect_move(prev, curr):

    prev = np.array(prev)
    curr = np.array(curr)

    diff = prev - curr



    moved_from = None
    moved_to = None
    for i in range(8):
        for j in range(8):
            if diff[i][j] > 0:
                moved_from = (i, j)
            elif diff[i][j] < 0:
                moved_to = (i, j)

    
    print(f"Moved from: {moved_from}, Moved to: {moved_to}")
    if moved_from is None or moved_to is None:
        return None

    from_row, from_col = moved_from
    to_row, to_col = moved_to
    return f"{chr(from_col + ord('a'))}{8 - from_row}{chr(to_col + ord('a'))}{8 - to_row}"



def get_stockfish_move(prev, cur):

    white_move = detect_move(prev, cur)

    move_data1 = {"move": white_move}   # example move

    try:
        response = requests.post("http://localhost:8000/update-move", json=move_data1)
        print("Status Code:", response.status_code)
        print("Response:", response.json())
    except Exception as e:
        print("❌ Failed to send request:", e)

    moves.append(white_move)

    print("Current moves:", moves)

    stockfish.set_position(moves)
    # Ask Stockfish (Black) to respond
    black_move = stockfish.get_best_move()
    
    print("Stockfish (Black) replies:", black_move)

    moves.append(black_move)

    move_data = {"move": black_move}  # example move

    try:
        response = requests.post("http://localhost:8000/update-move", json=move_data)
        print("Status Code:", response.status_code)
        print("Response:", response.json())
    except Exception as e:
        print("❌ Failed to send request:", e)

    return black_move



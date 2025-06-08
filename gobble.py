import random

BOARD_SIZE = 5

neighbors = [(-1,0),(1,0),(0,-1),(0,1)]


def display(board):
    print("  " + " ".join(str(i+1) for i in range(BOARD_SIZE)))
    for i, row in enumerate(board):
        print(str(i+1) + " " + " ".join(row))
    print()


def get_group(board, r, c):
    color = board[r][c]
    if color == '.':
        return set(), set()
    visited = set()
    liberties = set()
    stack = [(r, c)]
    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                if board[nx][ny] == '.':
                    liberties.add((nx, ny))
                elif board[nx][ny] == color:
                    stack.append((nx, ny))
    return visited, liberties


def apply_move(board, r, c, color):
    if board[r][c] != '.':
        return False, "Spot not empty."
    opponent = 'W' if color == 'B' else 'B'
    board[r][c] = color
    captured = []
    for dx, dy in neighbors:
        nx, ny = r + dx, c + dy
        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx][ny] == opponent:
            group, libs = get_group(board, nx, ny)
            if not libs:
                captured.extend(group)
    for x, y in captured:
        board[x][y] = '.'
    # suicide check
    group, libs = get_group(board, r, c)
    if not libs:
        board[r][c] = '.'
        return False, "Move is suicidal."
    return True, f"captured {len(captured)} bubble(s)" if captured else ""


def feedback_after_move(board, r, c, capture_msg):
    color = board[r][c]
    merged = False
    for dx, dy in neighbors:
        nx, ny = r + dx, c + dy
        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx][ny] == color:
            merged = True
            break
    if capture_msg:
        return f"Great job! You {capture_msg}."
    elif merged:
        return "Nice! Your bubble connected with friends and formed a bigger group."
    else:
        return "Good move. Keep an eye on this lone bubble so it stays safe."


def is_board_full(board):
    for row in board:
        if '.' in row:
            return False
    return True


def ai_move(board):
    moves = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == '.']
    if not moves:
        print("AI passes.")
        return
    random.shuffle(moves)
    for r, c in moves:
        valid, _ = apply_move(board, r, c, 'W')
        if valid:
            print(f"AI placed a bubble at ({r+1}, {c+1}).")
            return
    print("AI passes.")


def main():
    board = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    while True:
        display(board)
        move = input("Enter your move (row col or q to quit): ").strip()
        if move.lower() == 'q':
            print("Bye!")
            break
        try:
            r, c = map(int, move.split())
            r -= 1
            c -= 1
        except ValueError:
            print("Invalid input. Use row and column numbers.")
            continue
        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            print("Move out of board.")
            continue
        valid, msg = apply_move(board, r, c, 'B')
        if not valid:
            print(msg)
            continue
        print(feedback_after_move(board, r, c, msg))
        if is_board_full(board):
            print("Board full. Game over.")
            break
        ai_move(board)
        if is_board_full(board):
            print("Board full. Game over.")
            break


if __name__ == "__main__":
    main()

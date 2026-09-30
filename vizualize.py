import os

import pygame

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

def visualize_n_queens(board):
    if isinstance(board, str) and "No solution found." in board:
        print(board)
        return
    if len(board) != 8:
        print("Visualization only for 8 queens...")
        return

    def draw_board(screen, board_img):
        screen.blit(board_img, (0, 0))

    def draw_queens(screen, queen_img, board, cell_size):
        queen_img_scaled = pygame.transform.scale(
            queen_img, (cell_size, cell_size))
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 'Q':
                    x = j * cell_size
                    y = i * cell_size
                    screen.blit(queen_img_scaled, (x, y))

    pygame.init()
    N = len(board)

    board_img_path = os.path.join(ASSETS_DIR, "board.png")
    queen_img_path = os.path.join(ASSETS_DIR, "queen.png")
    board_img = pygame.image.load(board_img_path)
    queen_img = pygame.image.load(queen_img_path)

    board_width, board_height = board_img.get_size()
    board_img = pygame.transform.scale(
        board_img, (board_width // 1.5, board_height // 1.5))
    cell_size = int(board_width // 1.5) // N

    screen = pygame.display.set_mode(
        (int(board_width // 1.5), int(board_height // 1.5)))
    pygame.display.set_caption("N-Queens Solver")

    draw_board(screen, board_img)
    draw_queens(screen, queen_img, board, cell_size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
    pygame.quit()


def print_n_queens(board):
    board_string = "\n".join([' '.join(row) for row in board])
    print(board_string)


def visualize_sudoku(solution):
    board_size = len(solution)
    cell_size = 540 // board_size

    def draw_grid(screen, N):
        sub_grid_size = int(N**0.5)
        for i in range(N + 1):
            if i % sub_grid_size == 0:
                thickness = 4
            else:
                thickness = 1
            pygame.draw.line(screen, (0, 0, 0), (i * cell_size,
                             0), (i * cell_size, 540), thickness)
            pygame.draw.line(screen, (0, 0, 0), (0, i * cell_size),
                             (540, i * cell_size), thickness)

    def draw_numbers(screen, board, cell_size):
        font_size = cell_size - 5
        font = pygame.font.SysFont(None, font_size)
        for i in range(board_size):
            for j in range(board_size):
                if board[i][j] != 0:
                    text = font.render(str(board[i][j]), True, (0, 0, 0))
                    screen.blit(text, (j * cell_size + cell_size //
                                4, i * cell_size + cell_size // 10))

    pygame.init()
    screen = pygame.display.set_mode((540, 540))
    pygame.display.set_caption("Sudoku Solver")
    screen.fill((255, 255, 255))
    draw_grid(screen, board_size)
    draw_numbers(screen, solution, cell_size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
    pygame.quit()


def print_sudoku(board):
    """Pretty-print the Sudoku board with grid lines"""
    if board is None:
        print("No solution!")
        return

    N = len(board)
    sub_grid_size = int(N**0.5)

    for i in range(N):
        if i % sub_grid_size == 0 and i != 0:
            print("-" * (N * 2 + sub_grid_size - 1))

        for j in range(N):
            if j % sub_grid_size == 0 and j != 0:
                print("|", end=" ")
            print(board[i][j] if board[i][j] != 0 else ".", end=" ")
        print()
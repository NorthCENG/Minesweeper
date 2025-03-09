# src/minesweeper/board.py

import random

class Board:
    def __init__(self, rows=8, cols=8, mines=10):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        # -1 表示地雷，其它数字 0~8 表示周围地雷数
        self.grid = self._generate_board()

    def _generate_board(self):
        """生成一个包含 rows x cols 的网格，并随机埋设 mines 颗地雷。"""
        board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        # 随机选择地雷位置
        mine_positions = set()
        while len(mine_positions) < self.mines:
            r = random.randrange(self.rows)
            c = random.randrange(self.cols)
            mine_positions.add((r, c))

        # 放置地雷
        for (r, c) in mine_positions:
            board[r][c] = -1

        # 计算地雷周边数字
        for (mr, mc) in mine_positions:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = mr + dr, mc + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if board[nr][nc] != -1:  # 不是地雷才加1
                            board[nr][nc] += 1

        return board

    def get_value(self, r, c):
        return self.grid[r][c]

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols
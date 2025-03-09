# src/minesweeper/game_manager.py

class GameManager:
    """
    管理扫雷的主要业务逻辑：翻格、标记、判断胜负等。
    """
    def __init__(self, board):
        self.board = board
        self.rows = board.rows
        self.cols = board.cols
        # revealed[r][c] 表示该格子是否被翻开
        self.revealed = [[False]*self.cols for _ in range(self.rows)]
        # flagged[r][c] 表示该格子是否被标记为雷
        self.flagged = [[False]*self.cols for _ in range(self.rows)]
        self.game_over = False
        self.win = False

    def reveal_cell(self, r, c):
        """
        翻开某格：如果踩雷，则游戏结束；如果为0，自动扩散。
        """
        if self.game_over:
            return

        # 如果已经标记了，就不允许翻
        if self.flagged[r][c]:
            return

        value = self.board.get_value(r, c)
        if value == -1:
            # 踩雷
            self.game_over = True
            self.win = False
            return
        else:
            self._flood_fill(r, c)
            # 每次翻完后判断是否胜利
            if self._check_victory():
                self.game_over = True
                self.win = True

    def toggle_flag(self, r, c):
        """切换标记状态"""
        if self.game_over or self.revealed[r][c]:
            return
        self.flagged[r][c] = not self.flagged[r][c]

    def _flood_fill(self, r, c):
        """
        若翻开的格子为0，则向周边扩散翻开。
        """
        stack = [(r, c)]
        while stack:
            rr, cc = stack.pop()
            if self.revealed[rr][cc]:
                continue
            self.revealed[rr][cc] = True

            # 如果周边地雷数为0，继续向外扩散
            if self.board.get_value(rr, cc) == 0:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = rr + dr, cc + dc
                        if self.board.in_bounds(nr, nc):
                            if not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                                if self.board.get_value(nr, nc) != -1:
                                    stack.append((nr, nc))

    def _check_victory(self):
        """
        如果所有非雷格都被翻开，则胜利
        """
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board.get_value(r, c) != -1:
                    if not self.revealed[r][c]:
                        return False
        return True
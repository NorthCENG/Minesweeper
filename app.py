# app.py
from flask import Flask, request, jsonify, session, render_template
from minesweeper.board import Board
from minesweeper.game_manager import GameManager
import uuid

app = Flask(__name__)
app.secret_key = "some_random_secret_key"  # 用于会话管理

# 如果你要支持多用户每人一盘，可以使用后端的内存字典来存储
# games[session_id] = GameManager实例
games = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/new_game", methods=["POST"])
def new_game():
    data = request.json
    rows = data.get("rows", 8)
    cols = data.get("cols", 8)
    mines = data.get("mines", 10)

    board = Board(rows, cols, mines)
    gm = GameManager(board)

    # 用 session 或自定义一个 game_id 保存在后端
    game_id = str(uuid.uuid4())
    games[game_id] = gm

    # 也可以存到 session 中
    session["game_id"] = game_id

    return jsonify({
        "status": "ok",
        "rows": rows,
        "cols": cols,
        "mines": mines
    })


@app.route("/api/reveal", methods=["POST"])
def reveal():
    """
    翻开一个格子
    """
    data = request.json
    r = data["row"]
    c = data["col"]

    game_id = session.get("game_id")
    gm = games.get(game_id, None)
    if gm is None:
        return jsonify({"status": "error", "message": "No game found"}), 400

    gm.reveal_cell(r, c)

    # 返回更新后的状态
    return jsonify(game_state_to_dict(gm))


@app.route("/api/flag", methods=["POST"])
def flag():
    """
    标记/取消标记一个格子
    """
    data = request.json
    r = data["row"]
    c = data["col"]

    game_id = session.get("game_id")
    gm = games.get(game_id, None)
    if gm is None:
        return jsonify({"status": "error", "message": "No game found"}), 400

    gm.toggle_flag(r, c)
    return jsonify(game_state_to_dict(gm))

@app.route("/api/mass_reveal", methods=["POST"])
def mass_reveal():
    data = request.json
    r, c = data["row"], data["col"]

    game_id = session.get("game_id")
    gm = games.get(game_id)
    if gm is None:
        return jsonify({"status": "error", "message": "No game found"}), 400

    # 获取该格子的数字值
    number = gm.board.get_value(r, c)
    if number <= 0:  # 只有数字格子才允许自动翻开
        return jsonify({"status": "error", "message": "Cannot auto reveal"}), 400

    # 计算周围已标记的 flag 数量
    flagged_count = sum(
        1 for dr in [-1, 0, 1] for dc in [-1, 0, 1]
        if (dr != 0 or dc != 0) and gm.board.in_bounds(r + dr, c + dc) and gm.flagged[r + dr][c + dc]
    )

    # 只有 flag 数量等于数字时才允许自动翻开
    if flagged_count == number:
        # 翻开所有未翻开的相邻格子
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if gm.board.in_bounds(nr, nc) and not gm.revealed[nr][nc] and not gm.flagged[nr][nc]:
                    gm.reveal_cell(nr, nc)  # 递归翻开

    return jsonify(game_state_to_dict(gm))
def game_state_to_dict(gm):
    """
    将当前GameManager状态转成可供前端解析的JSON结构
    包含:
      - 棋盘大小
      - 每个格子的显示信息 (已翻开? 地雷? 数字? 标记?)
      - 是否游戏结束 & 是否胜利
    """
    rows = gm.rows
    cols = gm.cols
    revealed = []
    flagged = []
    values = []

    for r in range(rows):
        revealed_row = []
        flagged_row = []
        values_row = []
        for c in range(cols):
            revealed_row.append(gm.revealed[r][c])
            flagged_row.append(gm.flagged[r][c])
            val = gm.board.get_value(r, c)
            # 前端仅在 revealed==True 时才需要知道真正的数字
            # 如果没翻开，那只告诉它0或None即可
            values_row.append(val if gm.revealed[r][c] else None)
        revealed.append(revealed_row)
        flagged.append(flagged_row)
        values.append(values_row)

    return {
        "status": "ok",
        "gameOver": gm.game_over,
        "win": gm.win,
        "rows": rows,
        "cols": cols,
        "revealed": revealed,
        "flagged": flagged,
        "values": values
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

// static/js/main.js
document.addEventListener("DOMContentLoaded", () => {
  const newGameBtn = document.getElementById("newGameBtn");
  const boardEl = document.getElementById("board");
  const statusEl = document.getElementById("game-status");
  const timerEl = document.getElementById("game-timer");

  let timerInterval = null;
  let startTime;

  newGameBtn.addEventListener("click", () => {
    const rows = parseInt(document.getElementById("rows").value, 10);
    const cols = parseInt(document.getElementById("cols").value, 10);
    const mines = parseInt(document.getElementById("mines").value, 10);
    newGame(rows, cols, mines);
  });


  // 初次进入时自动加载一个游戏
  newGame(8, 8, 10);

  function newGame(rows, cols, mines) {
    fetch("/api/new_game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rows, cols, mines }),
    })
    .then(res => res.json())
    .then(state => {
      if (state.status === "ok") {
        renderBoard(rows, cols, []); // 先渲染空板
        //updateBoardView(state)
        statusEl.textContent = "游戏开始~";
        startTimer()
      } else {
        statusEl.textContent = "初始化游戏失败";
      }
    })
    .catch(err => {
      console.error(err);
      statusEl.textContent = "初始化游戏失败";
    });
  }

  function renderBoard(rows, cols, gameState) {
    boardEl.innerHTML = ""; // 清空表格

    for (let r = 0; r < rows; r++) {
      let tr = document.createElement("tr");
      for (let c = 0; c < cols; c++) {
        let td = document.createElement("td");
        td.dataset.row = r;
        td.dataset.col = c;
        td.dataset.revealed = "false";
        td.dataset.flagged = "false";
        // 给单元格加点击事件
        td.addEventListener("click", onCellLeftClick);
        // 右键
        td.addEventListener("contextmenu", (e) => {
          e.preventDefault();
          onCellRightClick(r, c);
        });
        tr.appendChild(td);
      }
      boardEl.appendChild(tr);
    }
  }

  function updateBoardView(state) {
    const { rows, cols, revealed, flagged, values, gameOver, win } = state;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        let td = boardEl.querySelector(`td[data-row="${r}"][data-col="${c}"]`);
        if (!td) continue;

        // 已翻开
        if (revealed[r][c]) {
          td.dataset.revealed = "true"
          td.dataset.value = values[r][c]

          if (values[r][c] === -1) {
            td.textContent = "*";
            td.className = "mine";
          } else if (values[r][c] === 0) {
            td.textContent = "";
            td.className = "empty";
          } else {
            td.textContent = values[r][c];
            td.className = "number";
            td.setAttribute("data-value", values[r][c]);
          }
        } else {
          // 未翻开
          if (flagged[r][c]) {
            td.dataset.flagged = "true"
            td.textContent = "🚩";
            td.className = "flag";
          } else {
            td.textContent = "";
            td.className = "";
          }
        }
      }
    }

    if (gameOver) {
      stopTimer();
      if (win) {
        statusEl.textContent = "恭喜，你赢了！";
      } else {
        statusEl.textContent = "踩雷了，游戏结束！";
      }
    }
  }

  function onCellLeftClick(e) {
    const r = parseInt(e.target.dataset.row, 10);
    const c = parseInt(e.target.dataset.col, 10);
    const value = parseInt(e.target.dataset.value, 10)

    let isRevealed = e.target.dataset.revealed === "true"
    let isFlagged = e.target.dataset.flagged === "true"

    if(!isRevealed){
        fetch("/api/reveal", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ row: r, col: c }),
        })
        .then(res => res.json())
        .then(state => {
          if (state.status === "ok") {
            // 如果第一次渲染的话需要把board设置出来
            if (boardEl.querySelectorAll("tr").length === 0) {
              renderBoard(state.rows, state.cols);
            }
            updateBoardView(state);
          }
        })
        .catch(err => console.error(err));
      }else if(value > 0){
        let flaggedCount = countSurroundingFlags(r, c);

        if (flaggedCount === value) {
            // 如果标记数等于数字，则进行 mass_reveal（翻开周围未翻开的格子）
            fetch("/api/mass_reveal", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ row: r, col: c }),
            })
            .then(res => res.json())
            .then(state => {
                if (state.status === "ok") {
                    updateBoardView(state);
                }
            })
            .catch(err => console.error(err));
        }
      }
    }

    function countSurroundingFlags(r, c) {
        let flaggedCount = 0;
        for (let dr = -1; dr <= 1; dr++) {
            for (let dc = -1; dc <= 1; dc++) {
                if (dr === 0 && dc === 0) continue; // 跳过自身

                let nr = r + dr;
                let nc = c + dc;
                let neighbor = document.querySelector(`td[data-row="${nr}"][data-col="${nc}"]`);

                if (neighbor && neighbor.classList.contains("flag")) {
                    flaggedCount++;
                }
            }
        }
        return flaggedCount;
    }

    function onCellRightClick(r, c) {
        fetch("/api/flag", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ row: r, col: c }),
        })
        .then(res => res.json())
        .then(state => {
          if (state.status === "ok") {
            updateBoardView(state);
          }
        })
        .catch(err => console.error(err));
    }

    function startTimer(){
        clearInterval(timerInterval);
        startTime = Date.now();
        timerInterval = setInterval(() => {
            const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
            timerEl.textContent = `Time: ${elapsedTime} s`;  // 显示秒数
        }, 1000);
    }

    function stopTimer(){
        clearInterval(timerInterval)
    }
});
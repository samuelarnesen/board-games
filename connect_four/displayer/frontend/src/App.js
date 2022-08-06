import React, { useState, useEffect, useRef } from "react";
import logo from "./logo.svg";
import Dropdown from "react-dropdown";
import "./App.css";

const Choices = ({ buttonName, choices, choiceFns }) => {
  const [showChoices, setShowChoices] = useState(false);
  const node = useRef();

  const handleClick = (e) => {
    if (node.current.contains(e.target)) {
      return;
    }
    setShowChoices(false);
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClick);
    return () => {
      document.removeEventListener("mousedown", handleClick);
    };
  }, []);

  return (
    <div ref={node}>
      <div
        className="button blue"
        onClick={() => {
          setShowChoices(true);
        }}
      >
        {buttonName}
      </div>

      <div className="container">
        {showChoices ? (
          <div>
            <div
              className="button green"
              onClick={() => {
                setShowChoices(false);
                choiceFns[0]();
              }}
            >
              {choices[0]}
            </div>
            <div
              className="button green"
              onClick={() => {
                setShowChoices(false);
                choiceFns[1]();
              }}
            >
              {choices[1]}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};

class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      player1: 1,
      player2: -1,
      currentPlayer: null,
      board: [],
      gameOver: false,
      message: "",

      playAgainstAI: false,
      playerAI: null,
    };

    // Bind play function to App component
    this.play = this.play.bind(this);
    this.playAIMove = this.playAIMove.bind(this);
  }

  // Starts new game
  initBoard() {
    // Create a blank 6x7 matrix
    let board = [];
    for (let r = 0; r < 6; r++) {
      let row = [];
      for (let c = 0; c < 7; c++) {
        row.push(null);
      }
      board.push(row);
    }
    this.setState({
      board,
      currentPlayer: this.state.player1,
      gameOver: false,
      message: "",
      playAgainstAI: false,
      playerAI: null,
    });
  }

  togglePlayer() {
    return this.state.currentPlayer === this.state.player1
      ? this.state.player2
      : this.state.player1;
  }

  togglePlayAgainstAI = (againstAI) => {
    this.initBoard();
    this.setState({
      playAgainstAI: againstAI,
    });
  };


  play(c) {
    if (!this.state.gameOver) {
      // Place piece on board
      let board = this.state.board;
      for (let r = 5; r >= 0; r--) {
        if (!board[r][c]) {
          board[r][c] = this.state.currentPlayer;
          break;
        }
      }
      this.updateBoardStatus(board);
    }
  }

  updateBoardStatus(board) {
    let result = this.checkAll(board);
    if (result === this.state.player1) {
      this.setState({
        board,
        gameOver: true,
        message: "Player 1 (red) wins!",
      });
    } else if (result === this.state.player2) {
      this.setState({
        board,
        gameOver: true,
        message: "Player 2 (yellow) wins!",
      });
    } else if (result === "draw") {
      this.setState({ board, gameOver: true, message: "Draw game." });
    } else {
      this.setState({ board, currentPlayer: this.togglePlayer() });
    }
  }

  async playAIMove() {
    const payload = { board: this.state.board, playerAI: this.state.playerAI };
    const move = await fetch("http://localhost:8000", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }).then((res) => res.json());
    this.play(move);
  }

  checkDraw(board) {
    for (let r = 0; r < 6; r++) {
      for (let c = 0; c < 7; c++) {
        if (board[r][c] === null) {
          return null;
        }
      }
    }
    return "draw";
  }

  checkAll(board) {
    return (
      this.checkVertical(board) ||
      this.checkDiagonalRight(board) ||
      this.checkDiagonalLeft(board) ||
      this.checkHorizontal(board) ||
      this.checkDraw(board)
    );
  }

  componentWillMount() {
    this.initBoard();
  }

  checkVertical(board) {
    // Check only if row is 3 or greater
    for (let r = 3; r < 6; r++) {
      for (let c = 0; c < 7; c++) {
        if (board[r][c]) {
          if (
            board[r][c] === board[r - 1][c] &&
            board[r][c] === board[r - 2][c] &&
            board[r][c] === board[r - 3][c]
          ) {
            return board[r][c];
          }
        }
      }
    }
  }

  checkHorizontal(board) {
    // Check only if column is 3 or less
    for (let r = 0; r < 6; r++) {
      for (let c = 0; c < 4; c++) {
        if (board[r][c]) {
          if (
            board[r][c] === board[r][c + 1] &&
            board[r][c] === board[r][c + 2] &&
            board[r][c] === board[r][c + 3]
          ) {
            return board[r][c];
          }
        }
      }
    }
  }

  checkDiagonalRight(board) {
    // Check only if row is 3 or greater AND column is 3 or less
    for (let r = 3; r < 6; r++) {
      for (let c = 0; c < 4; c++) {
        if (board[r][c]) {
          if (
            board[r][c] === board[r - 1][c + 1] &&
            board[r][c] === board[r - 2][c + 2] &&
            board[r][c] === board[r - 3][c + 3]
          ) {
            return board[r][c];
          }
        }
      }
    }
  }

  checkDiagonalLeft(board) {
    // Check only if row is 3 or greater AND column is 3 or greater
    for (let r = 3; r < 6; r++) {
      for (let c = 3; c < 7; c++) {
        if (board[r][c]) {
          if (
            board[r][c] === board[r - 1][c - 1] &&
            board[r][c] === board[r - 2][c - 2] &&
            board[r][c] === board[r - 3][c - 3]
          ) {
            return board[r][c];
          }
        }
      }
    }
  }

  render() {
    const choices = ["AI goes first", "Player goes first"];
    const choiceFns = [
      (() => {
        this.togglePlayAgainstAI(true);
        this.setState({ playerAI: 1 });
        this.playAIMove();
      }).bind(this),
      (() => {
        this.togglePlayAgainstAI(true);
        this.setState({ playerAI: -1 });
      }).bind(this),
    ];

    return (
      <div>
        <div className="nav">
          <div
            className="button blue"
            onClick={() => {
              this.togglePlayAgainstAI(false);
              console.log(this.state.playAgainstAI);
            }}
          >
            Play Against Human
          </div>

          <Choices
            buttonName="Play Against AI"
            choices={choices}
            choiceFns={choiceFns}
          />
        </div>

        <div>
          <table>
            <thead></thead>
            <tbody>
              {this.state.board.map((row, i) => (
                <Row
                  key={i}
                  row={row}
                  play={this.play}
                  playAgainstAI={this.state.playAgainstAI}
                  playAIMove={this.playAIMove}
                  currentPlayer={this.state.currentPlayer}
                  playerAI={this.state.playerAI}
                />
              ))}
            </tbody>
          </table>
          <p className="message">{this.state.message}</p>
        </div>
      </div>
    );
  }
}

// Row component
const Row = ({
  row,
  play,
  playAgainstAI,
  playAIMove,
  currentPlayer,
  playerAI,
}) => {
  return (
    <tr>
      {row.map((cell, i) => (
        <Cell
          key={i}
          value={cell}
          columnIndex={i}
          play={play}
          playAgainstAI={playAgainstAI}
          playAIMove={playAIMove}
          currentPlayer={currentPlayer}
          playerAI={playerAI}
        />
      ))}
    </tr>
  );
};

const Cell = ({
  value,
  columnIndex,
  play,
  playAgainstAI,
  playAIMove,
  currentPlayer,
  playerAI,
}) => {
  let color = "white";
  if (value === 1) {
    color = "red";
  } else if (value === -1) {
    color = "yellow";
  }

  return (
    <td>
      <div
        className="cell"
        onClick={() => {
          if (currentPlayer === playerAI) {
            return;
          }
          play(columnIndex);
          if (playAgainstAI) {
            playAIMove();
          }
        }}
      >
        <div className={color}></div>
      </div>
    </td>
  );
};

export default App;
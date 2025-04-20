#!/usr/bin/env python3
"""
Simple web-based Maze Game server
"""

import os
import json
import random
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Game state
game_state = {
    "maze": None,
    "player_x": 0,
    "player_y": 0,
    "ai_x": 9,
    "ai_y": 9,
    "player_score": 0,
    "ai_score": 0,
    "player_gems": 0,
    "ai_gems": 0,
    "player_tokens": 3,
    "ai_tokens": 3,
    "current_round": 1,
    "player_turn": True,
    "game_over": False,
    "visited_player": None,
    "visited_ai": None
}

# Constants
GRID_SIZE = 10
CELL_EMPTY = 0
CELL_WALL = 1
CELL_GEM = 2
CELL_TRAP = 3

class SimpleMazeGame:
    """Simple web-based maze game logic"""
    
    @staticmethod
    def initialize_game():
        """Initialize a new game"""
        # Create empty maze
        maze = [[CELL_EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Create visited arrays
        visited_player = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        visited_ai = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Mark starting positions
        visited_player[0][0] = True
        visited_ai[GRID_SIZE - 1][GRID_SIZE - 1] = True
        
        # Generate walls (20%)
        wall_count = 0
        while wall_count < 20:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if (x, y) != (0, 0) and (x, y) != (GRID_SIZE - 1, GRID_SIZE - 1) and maze[x][y] == CELL_EMPTY:
                maze[x][y] = CELL_WALL
                wall_count += 1
        
        # Generate gems (15%)
        gem_count = 0
        while gem_count < 15:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if maze[x][y] == CELL_EMPTY and (x, y) != (0, 0) and (x, y) != (GRID_SIZE - 1, GRID_SIZE - 1):
                maze[x][y] = CELL_GEM
                gem_count += 1
        
        # Generate traps (10%)
        trap_count = 0
        while trap_count < 10:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if maze[x][y] == CELL_EMPTY and (x, y) != (0, 0) and (x, y) != (GRID_SIZE - 1, GRID_SIZE - 1):
                maze[x][y] = CELL_TRAP
                trap_count += 1
        
        # Update game state
        game_state["maze"] = maze
        game_state["player_x"] = 0
        game_state["player_y"] = 0
        game_state["ai_x"] = GRID_SIZE - 1
        game_state["ai_y"] = GRID_SIZE - 1
        game_state["player_score"] = 0
        game_state["ai_score"] = 0
        game_state["player_gems"] = 0
        game_state["ai_gems"] = 0
        game_state["player_tokens"] = 3
        game_state["ai_tokens"] = 3
        game_state["current_round"] = 1
        game_state["player_turn"] = True
        game_state["game_over"] = False
        game_state["visited_player"] = visited_player
        game_state["visited_ai"] = visited_ai
        
        return game_state
    
    @staticmethod
    def is_valid_move(x, y):
        """Check if a move to position (x, y) is valid"""
        # Check bounds
        if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
            return False
        
        # Check for wall
        if game_state["maze"][x][y] == CELL_WALL:
            return False
            
        return True
    
    @staticmethod
    def collect_gem(x, y, is_player):
        """Collect a gem at position (x, y) if present"""
        if game_state["maze"][x][y] == CELL_GEM:
            game_state["maze"][x][y] = CELL_EMPTY
            
            # Update score and gem count
            if is_player:
                game_state["player_score"] += 10
                game_state["player_gems"] += 1
            else:
                game_state["ai_score"] += 10
                game_state["ai_gems"] += 1
                
            return True
        return False
    
    @staticmethod
    def check_trap(x, y):
        """Check if position (x, y) contains a trap"""
        return game_state["maze"][x][y] == CELL_TRAP
        
    @staticmethod
    def use_token(token_type, x=None, y=None):
        """Use a token for a special action"""
        if not game_state["player_turn"] or game_state["game_over"]:
            return {"success": False, "message": "Not player's turn or game over"}
            
        if game_state["player_tokens"] <= 0:
            return {"success": False, "message": "No tokens left"}
        
        success = False
        message = "Invalid token action"
        
        # Place wall
        if token_type == "wall" and x is not None and y is not None:
            # Check if valid coordinates
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                # Check if valid position for placing wall (must be empty)
                if game_state["maze"][x][y] == CELL_EMPTY:
                    # Make sure we're not blocking the player or AI
                    if (x != game_state["player_x"] or y != game_state["player_y"]) and \
                       (x != game_state["ai_x"] or y != game_state["ai_y"]):
                        game_state["maze"][x][y] = CELL_WALL
                        success = True
                        message = "Wall placed successfully"
                    else:
                        message = "Cannot place wall on player or AI position"
                else:
                    message = "Cannot place wall here, cell not empty"
            else:
                message = "Invalid coordinates for wall placement"
        
        # Remove trap
        elif token_type == "remove_trap":
            x, y = game_state["player_x"], game_state["player_y"]
            
            # Check adjacent cells for traps
            for dx, dy in [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and game_state["maze"][new_x][new_y] == CELL_TRAP:
                    game_state["maze"][new_x][new_y] = CELL_EMPTY
                    success = True
                    message = "Trap removed successfully"
                    break
            
            if not success:
                message = "No trap found in your position or adjacent cells"
        
        # Teleport
        elif token_type == "teleport" and x is not None and y is not None:
            # Check if valid coordinates
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                # Check if player has visited position
                if game_state["visited_player"][x][y]:
                    # Cannot teleport to current position
                    if x == game_state["player_x"] and y == game_state["player_y"]:
                        message = "Already at this position"
                    else:
                        game_state["player_x"] = x
                        game_state["player_y"] = y
                        success = True
                        message = "Teleported successfully"
                else:
                    message = "Cannot teleport to a position you haven't visited"
            else:
                message = "Invalid coordinates for teleport"
        
        # If action was successful, use a token and end player's turn
        if success:
            game_state["player_tokens"] -= 1
            game_state["player_turn"] = False
            
            # AI's turn
            SimpleMazeGame.ai_make_move()
            
            # Check if round is complete
            if game_state["current_round"] >= 20:
                game_state["game_over"] = True
            else:
                game_state["current_round"] += 1
                game_state["player_turn"] = True
        
        return {"success": success, "message": message, "state": game_state}
    
    @staticmethod
    def player_move(dx, dy):
        """Move the player"""
        if not game_state["player_turn"] or game_state["game_over"]:
            return {"success": False, "message": "Not player's turn or game over"}
        
        new_x = game_state["player_x"] + dx
        new_y = game_state["player_y"] + dy
        
        # Check if move is valid
        if not SimpleMazeGame.is_valid_move(new_x, new_y):
            return {"success": False, "message": "Invalid move"}
        
        # Check for trap - prevent moving onto trap unless removed
        if SimpleMazeGame.check_trap(new_x, new_y):
            return {"success": False, "message": "Cannot move onto trap. Use a token to remove it first."}
        
        # Execute the move
        game_state["player_x"] = new_x
        game_state["player_y"] = new_y
        
        # Mark as visited
        game_state["visited_player"][new_x][new_y] = True
        
        # Check for gem collection
        SimpleMazeGame.collect_gem(new_x, new_y, True)
        
        # Switch to AI's turn
        game_state["player_turn"] = False
        
        # Let AI make its move
        SimpleMazeGame.ai_make_move()
        
        # Check if round is complete
        if game_state["current_round"] >= 20:
            game_state["game_over"] = True
        else:
            game_state["current_round"] += 1
            game_state["player_turn"] = True
        
        return {"success": True, "state": game_state}
    
    @staticmethod
    def ai_make_move():
        """AI makes a move using simple strategy"""
        # Simple AI: just move randomly
        x, y = game_state["ai_x"], game_state["ai_y"]
        valid_moves = []
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if SimpleMazeGame.is_valid_move(new_x, new_y):
                valid_moves.append((new_x, new_y))
        
        if valid_moves:
            new_x, new_y = random.choice(valid_moves)
            game_state["ai_x"] = new_x
            game_state["ai_y"] = new_y
            
            # Mark as visited
            game_state["visited_ai"][new_x][new_y] = True
            
            # Check for gem/trap
            SimpleMazeGame.collect_gem(new_x, new_y, False)
            
            if SimpleMazeGame.check_trap(new_x, new_y):
                game_state["ai_score"] -= 5
    
    @staticmethod
    def reset_game():
        """Reset the game"""
        return SimpleMazeGame.initialize_game()


class SimpleHandler(SimpleHTTPRequestHandler):
    """Simple HTTP request handler for the maze game"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Send HTML content
            with open('simple_maze_game.html', 'rb') as file:
                self.wfile.write(file.read())
                
        elif self.path == '/api/state':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Initialize game if not already
            if game_state["maze"] is None:
                SimpleMazeGame.initialize_game()
                
            self.wfile.write(json.dumps(game_state).encode())
            
        elif self.path.startswith('/api/move/'):
            # Extract direction from path
            direction = self.path.split('/')[-1]
            dx, dy = 0, 0
            
            if direction == 'up':
                dx, dy = 0, -1
            elif direction == 'down':
                dx, dy = 0, 1
            elif direction == 'left':
                dx, dy = -1, 0
            elif direction == 'right':
                dx, dy = 1, 0
            
            result = SimpleMazeGame.player_move(dx, dy)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
                
        elif self.path.startswith('/api/token/'):
            # Extract token_type from path
            path_without_query = self.path.split('?')[0]
            parts = path_without_query.split('/')
            token_type = parts[-1]
            
            # For token types that need coordinates
            x, y = None, None
            # Check for query parameters
            if '?' in self.path:
                path_parts = self.path.split('?')
                if len(path_parts) > 1:
                    query = path_parts[1]
                    query_parts = query.split('&')
                    for part in query_parts:
                        if '=' in part:
                            key, value = part.split('=')
                            if key == 'x':
                                try:
                                    x = int(value)
                                except ValueError:
                                    pass
                            elif key == 'y':
                                try:
                                    y = int(value)
                                except ValueError:
                                    pass
            
            result = SimpleMazeGame.use_token(token_type, x, y)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        elif self.path == '/api/reset':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            result = SimpleMazeGame.reset_game()
            self.wfile.write(json.dumps({"success": True, "state": result}).encode())
            
        else:
            # Serve static files
            super().do_GET()


def run_server():
    """Run the web server on port 5000"""
    server_address = ('0.0.0.0', 5000)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"Server running at http://0.0.0.0:5000/")
    httpd.serve_forever()


if __name__ == "__main__":
    # Create the HTML file
    # with open('simple_maze_game.html', 'w') as f:
    #     f.write("""<!DOCTYPE html>
    with open('simple_maze_game.html', 'w', encoding='utf-8') as f:
      f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Maze Game</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1e1e1e;
            color: white;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }
        .game-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            max-width: 800px;
        }
        .maze-canvas {
            background-color: #2d2d2d;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(3, 60px);
            grid-template-rows: repeat(3, 60px);
            gap: 5px;
            margin: 20px 0;
        }
        .btn {
            padding: 10px 20px;
            background-color: #3a3a3a;
            border: none;
            color: white;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin-bottom: 10px;
        }
        .btn:hover {
            background-color: #4a4a4a;
        }
        .btn:active {
            background-color: #5a5a5a;
        }
        .control-btn {
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 24px;
        }
        .info-panel {
            background-color: #2d2d2d;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            width: 100%;
            box-sizing: border-box;
        }
        .score-display {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .player-score {
            color: #00bfff;
        }
        .ai-score {
            color: #ffd700;
        }
        .game-over {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(0, 0, 0, 0.8);
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            display: none;
        }
        h1 {
            color: #40e0d0;
            margin-top: 0;
        }
        .token-btn {
            background-color: #7061db;
            color: white;
            width: 100%;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .token-btn-disabled {
            background-color: #3a3a3a;
            opacity: 0.5;
            cursor: not-allowed;
        }
        .token-actions {
            display: flex;
            flex-direction: column;
            margin: 20px 0;
            width: 100%;
        }
        .token-count {
            color: #7061db;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .message {
            color: #ff6b6b;
            margin: 10px 0;
            min-height: 20px;
        }
        .teleport-mode, .wall-mode {
            position: absolute;
            top: 10px;
            left: 10px;
            background-color: rgba(112, 97, 219, 0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            display: none;
            font-weight: bold;
            z-index: 100;
        }
        
        .maze-container {
            position: relative;
            margin-bottom: 10px;
        }
        
        .message {
            color: #ff6b6b;
            margin: 10px 0;
            min-height: 20px;
            padding: 8px;
            text-align: center;
            font-weight: bold;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1>Maze Game: Player vs AI</h1>
        
        <div class="info-panel">
            <div class="score-display">
                <div>Round: <span id="roundDisplay">1</span>/20</div>
                <div id="turnDisplay">Your Turn</div>
            </div>
            <div class="score-display">
                <div class="player-score">Player: <span id="playerScore">0</span> pts</div>
                <div class="ai-score">AI: <span id="aiScore">0</span> pts</div>
            </div>
            <div class="score-display">
                <div class="player-score">Gems: <span id="playerGems">0</span></div>
                <div class="ai-score">Gems: <span id="aiGems">0</span></div>
            </div>
            <div>Tokens: <span id="playerTokens">3</span></div>
        </div>
        
        <div class="maze-container" style="position: relative;">
            <canvas id="mazeCanvas" class="maze-canvas" width="500" height="500"></canvas>
            <div id="teleportMode" class="teleport-mode">Teleport Mode: Click a visited cell</div>
            <div id="wallMode" class="wall-mode">Wall Mode: Click an empty cell</div>
        </div>
        
        <div class="message" id="messageArea"></div>
        
        <div class="controls">
            <div></div>
            <button id="upBtn" class="btn control-btn">↑</button>
            <div></div>
            <button id="leftBtn" class="btn control-btn">←</button>
            <div></div>
            <button id="rightBtn" class="btn control-btn">→</button>
            <div></div>
            <button id="downBtn" class="btn control-btn">↓</button>
            <div></div>
        </div>
        
        <div class="token-actions">
            <button id="wallBtn" class="btn token-btn">Place Wall <span>(1 token)</span></button>
            <button id="trapBtn" class="btn token-btn">Remove Trap <span>(1 token)</span></button>
            <button id="teleportBtn" class="btn token-btn">Teleport <span>(1 token)</span></button>
        </div>
        
        <button id="resetBtn" class="btn">New Game</button>
        
        <div id="gameOver" class="game-over">
            <h2 id="winnerText">Game Over!</h2>
            <button id="playAgainBtn" class="btn">Play Again</button>
        </div>
    </div>
    
    <script>
        // Game constants
        const CELL_SIZE = 50;
        const GRID_SIZE = 10;
        const CELL_EMPTY = 0;
        const CELL_WALL = 1;
        const CELL_GEM = 2;
        const CELL_TRAP = 3;
        
        // Game elements
        const canvas = document.getElementById('mazeCanvas');
        const ctx = canvas.getContext('2d');
        const upBtn = document.getElementById('upBtn');
        const downBtn = document.getElementById('downBtn');
        const leftBtn = document.getElementById('leftBtn');
        const rightBtn = document.getElementById('rightBtn');
        const resetBtn = document.getElementById('resetBtn');
        const gameOverPanel = document.getElementById('gameOver');
        const winnerText = document.getElementById('winnerText');
        const playAgainBtn = document.getElementById('playAgainBtn');
        
        // Token elements
        const wallBtn = document.getElementById('wallBtn');
        const trapBtn = document.getElementById('trapBtn');
        const teleportBtn = document.getElementById('teleportBtn');
        const messageArea = document.getElementById('messageArea');
        const teleportMode = document.getElementById('teleportMode');
        const wallMode = document.getElementById('wallMode');
        
        // Token action states
        let isTeleportMode = false;
        let isWallMode = false;
        
        // Display elements
        const roundDisplay = document.getElementById('roundDisplay');
        const turnDisplay = document.getElementById('turnDisplay');
        const playerScoreDisplay = document.getElementById('playerScore');
        const aiScoreDisplay = document.getElementById('aiScore');
        const playerGemsDisplay = document.getElementById('playerGems');
        const aiGemsDisplay = document.getElementById('aiGems');
        const playerTokensDisplay = document.getElementById('playerTokens');
        
        // Game state
        let gameState = null;
        
        // Fetch game state
        async function fetchGameState() {
            try {
                const response = await fetch('/api/state');
                gameState = await response.json();
                updateUI();
                drawMaze();
            } catch (error) {
                console.error('Error fetching game state:', error);
            }
        }
        
        // Move player
        async function movePlayer(direction) {
            if (!gameState.player_turn || gameState.game_over) return;
            
            try {
                const response = await fetch(`/api/move/${direction}`);
                const result = await response.json();
                
                if (result.success) {
                    gameState = result.state;
                    updateUI();
                    drawMaze();
                    checkGameOver();
                }
            } catch (error) {
                console.error(`Error moving ${direction}:`, error);
            }
        }
        
        // Reset game
        async function resetGame() {
            try {
                const response = await fetch('/api/reset');
                const result = await response.json();
                
                if (result.success) {
                    gameState = result.state;
                    gameOverPanel.style.display = 'none';
                    updateUI();
                    drawMaze();
                }
            } catch (error) {
                console.error('Error resetting game:', error);
            }
        }
        
        // Update UI elements
        function updateUI() {
            roundDisplay.textContent = gameState.current_round;
            turnDisplay.textContent = gameState.player_turn ? 'Your Turn' : 'AI Turn';
            playerScoreDisplay.textContent = gameState.player_score;
            aiScoreDisplay.textContent = gameState.ai_score;
            playerGemsDisplay.textContent = gameState.player_gems;
            aiGemsDisplay.textContent = gameState.ai_gems;
            playerTokensDisplay.textContent = gameState.player_tokens;
            
            // Update token button states
            const hasTokens = gameState.player_tokens > 0;
            const isPlayerTurn = gameState.player_turn;
            const isGameOver = gameState.game_over;
            
            // Disable token buttons if no tokens or not player's turn
            if (!hasTokens || !isPlayerTurn || isGameOver) {
                wallBtn.classList.add('token-btn-disabled');
                trapBtn.classList.add('token-btn-disabled');
                teleportBtn.classList.add('token-btn-disabled');
            } else {
                wallBtn.classList.remove('token-btn-disabled');
                trapBtn.classList.remove('token-btn-disabled');
                teleportBtn.classList.remove('token-btn-disabled');
            }
            
            // Exit special modes if not player's turn or game over
            if (!isPlayerTurn || isGameOver) {
                exitSpecialModes();
            }
        }
        
        // Check if game is over
        function checkGameOver() {
            if (gameState.game_over) {
                gameOverPanel.style.display = 'block';
                
                const playerGems = gameState.player_gems;
                const aiGems = gameState.ai_gems;
                
                if (playerGems > aiGems) {
                    winnerText.textContent = `You Win! (${playerGems} vs ${aiGems} gems)`;
                    winnerText.style.color = '#00bfff';
                } else if (aiGems > playerGems) {
                    winnerText.textContent = `AI Wins! (${aiGems} vs ${playerGems} gems)`;
                    winnerText.style.color = '#ffd700';
                } else {
                    winnerText.textContent = `It's a Tie! (${playerGems} gems each)`;
                    winnerText.style.color = '#ffffff';
                }
            }
        }
        
        // Draw the maze
        function drawMaze() {
            if (!gameState || !gameState.maze) return;
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw grid and cell contents
            for (let x = 0; x < GRID_SIZE; x++) {
                for (let y = 0; y < GRID_SIZE; y++) {
                    const cellX = x * CELL_SIZE;
                    const cellY = y * CELL_SIZE;
                    
                    // Draw cell background
                    ctx.fillStyle = '#2d2d2d';
                    ctx.fillRect(cellX, cellY, CELL_SIZE, CELL_SIZE);
                    
                    // Draw visited paths
                    if (gameState.visited_player[x][y]) {
                        ctx.strokeStyle = '#00bfff';
                        ctx.lineWidth = 1;
                        ctx.strokeRect(cellX + 2, cellY + 2, CELL_SIZE - 4, CELL_SIZE - 4);
                    }
                    
                    if (gameState.visited_ai[x][y]) {
                        ctx.strokeStyle = '#ffd700';
                        ctx.lineWidth = 1;
                        ctx.strokeRect(cellX + 4, cellY + 4, CELL_SIZE - 8, CELL_SIZE - 8);
                    }
                    
                    // Draw cell contents
                    const cellType = gameState.maze[x][y];
                    
                    if (cellType === CELL_WALL) {
                        // Wall
                        ctx.fillStyle = '#646464';
                        ctx.fillRect(cellX, cellY, CELL_SIZE, CELL_SIZE);
                    } else if (cellType === CELL_GEM) {
                        // Gem
                        ctx.fillStyle = '#40e0d0';
                        ctx.beginPath();
                        ctx.moveTo(cellX + CELL_SIZE/2, cellY + 5);
                        ctx.lineTo(cellX + CELL_SIZE - 5, cellY + CELL_SIZE/2);
                        ctx.lineTo(cellX + CELL_SIZE/2, cellY + CELL_SIZE - 5);
                        ctx.lineTo(cellX + 5, cellY + CELL_SIZE/2);
                        ctx.closePath();
                        ctx.fill();
                    } else if (cellType === CELL_TRAP) {
                        // Trap
                        ctx.fillStyle = '#ff4500';
                        ctx.beginPath();
                        ctx.moveTo(cellX + 5, cellY + CELL_SIZE - 5);
                        ctx.lineTo(cellX + CELL_SIZE - 5, cellY + CELL_SIZE - 5);
                        ctx.lineTo(cellX + CELL_SIZE/2, cellY + 5);
                        ctx.closePath();
                        ctx.fill();
                    }
                    
                    // Draw grid lines
                    ctx.strokeStyle = '#3a3a3a';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(cellX, cellY, CELL_SIZE, CELL_SIZE);
                }
            }
            
            // Draw player
            const playerX = gameState.player_x * CELL_SIZE;
            const playerY = gameState.player_y * CELL_SIZE;
            ctx.fillStyle = '#00bfff';
            ctx.beginPath();
            ctx.arc(playerX + CELL_SIZE/2, playerY + CELL_SIZE/2, CELL_SIZE/2 - 5, 0, Math.PI * 2);
            ctx.fill();
            
            // Draw AI
            const aiX = gameState.ai_x * CELL_SIZE;
            const aiY = gameState.ai_y * CELL_SIZE;
            ctx.fillStyle = '#ffd700';
            ctx.fillRect(aiX + 5, aiY + 5, CELL_SIZE - 10, CELL_SIZE - 10);
        }
        
        // Use token function
        async function useToken(tokenType, x = null, y = null) {
            if (!gameState.player_turn || gameState.game_over) return;
            if (gameState.player_tokens <= 0) {
                messageArea.textContent = "No tokens left!";
                return;
            }
            
            let url = `/api/token/${tokenType}`;
            if (x !== null && y !== null) {
                url = `/api/token/${tokenType}?x=${x}&y=${y}`;
            }
            
            try {
                const response = await fetch(url);
                const result = await response.json();
                
                messageArea.textContent = result.message;
                
                if (result.success) {
                    gameState = result.state;
                    updateUI();
                    drawMaze();
                    checkGameOver();
                    
                    // Exit special modes
                    exitSpecialModes();
                }
            } catch (error) {
                console.error(`Error using token (${tokenType}):`, error);
            }
        }
        
        // Exit special modes (teleport, wall placement)
        function exitSpecialModes() {
            isTeleportMode = false;
            isWallMode = false;
            teleportMode.style.display = 'none';
            wallMode.style.display = 'none';
        }
        
        // Canvas click handler
        canvas.addEventListener('click', (event) => {
            if (!gameState.player_turn || gameState.game_over) return;
            
            // Get grid coordinates from click position
            const rect = canvas.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const clickY = event.clientY - rect.top;
            
            const gridX = Math.floor(clickX / CELL_SIZE);
            const gridY = Math.floor(clickY / CELL_SIZE);
            
            // Handle special modes
            if (isTeleportMode) {
                useToken('teleport', gridX, gridY);
            } else if (isWallMode) {
                useToken('wall', gridX, gridY);
            }
        });
        
        // Event listeners
        upBtn.addEventListener('click', () => movePlayer('up'));
        downBtn.addEventListener('click', () => movePlayer('down'));
        leftBtn.addEventListener('click', () => movePlayer('left'));
        rightBtn.addEventListener('click', () => movePlayer('right'));
        resetBtn.addEventListener('click', resetGame);
        playAgainBtn.addEventListener('click', resetGame);
        
        // Token button event listeners
        wallBtn.addEventListener('click', () => {
            if (gameState.player_tokens <= 0) {
                messageArea.textContent = "No tokens left!";
                return;
            }
            isWallMode = true;
            isTeleportMode = false;
            wallMode.style.display = 'block';
            teleportMode.style.display = 'none';
            messageArea.textContent = "Click an empty cell to place a wall.";
        });
        
        trapBtn.addEventListener('click', () => {
            useToken('remove_trap');
        });
        
        teleportBtn.addEventListener('click', () => {
            if (gameState.player_tokens <= 0) {
                messageArea.textContent = "No tokens left!";
                return;
            }
            isTeleportMode = true;
            isWallMode = false;
            teleportMode.style.display = 'block';
            wallMode.style.display = 'none';
            messageArea.textContent = "Click a visited cell to teleport.";
        });
        
        // Keyboard controls
        document.addEventListener('keydown', (event) => {
            if (!gameState.player_turn || gameState.game_over) return;
            
            switch(event.key) {
                case 'ArrowUp':
                    movePlayer('up');
                    break;
                case 'ArrowDown':
                    movePlayer('down');
                    break;
                case 'ArrowLeft':
                    movePlayer('left');
                    break;
                case 'ArrowRight':
                    movePlayer('right');
                    break;
                case '1':
                    wallBtn.click();
                    break;
                case '2':
                    trapBtn.click();
                    break;
                case '3':
                    teleportBtn.click();
                    break;
                case 'Escape':
                    exitSpecialModes();
                    messageArea.textContent = "";
                    break;
                case 'r':
                    resetGame();
                    break;
            }
        });
        
        // Initialize game
        fetchGameState();
        
        // Refresh game state periodically
        setInterval(fetchGameState, 2000);
    </script>
</body>
</html>""")
    
    # Initialize the game
    SimpleMazeGame.initialize_game()
    
    # Run the server
    run_server()
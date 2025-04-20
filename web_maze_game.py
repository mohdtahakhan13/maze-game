#!/usr/bin/env python3
"""
Web-based Maze Game server
"""

import os
import json
import random
import numpy as np
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Constants (matching the original game)
GRID_SIZE = 10
GEM_COUNT = 15
TRAP_COUNT = 10
WALL_COUNT = 20
ROUNDS = 20
INITIAL_TOKENS = 3

# Cell types
CELL_EMPTY = 0
CELL_WALL = 1
CELL_GEM = 2
CELL_TRAP = 3

# Game state
game_state = {
    "maze": None,
    "player_x": 0,
    "player_y": 0,
    "ai_x": GRID_SIZE - 1,
    "ai_y": GRID_SIZE - 1,
    "player_score": 0,
    "ai_score": 0,
    "player_gems": 0,
    "ai_gems": 0,
    "player_tokens": INITIAL_TOKENS,
    "ai_tokens": INITIAL_TOKENS,
    "current_round": 1,
    "player_turn": True,
    "game_over": False,
    "visited_player": None,
    "visited_ai": None,
    "gem_locations": []
}

class MazeGame:
    """Web-based maze game logic"""
    
    @staticmethod
    def initialize_game():
        """Initialize a new game"""
        # Create empty maze
        maze = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        
        # Create visited arrays
        visited_player = np.zeros((GRID_SIZE, GRID_SIZE), dtype=bool)
        visited_ai = np.zeros((GRID_SIZE, GRID_SIZE), dtype=bool)
        
        # Mark starting positions
        visited_player[0, 0] = True
        visited_ai[GRID_SIZE - 1, GRID_SIZE - 1] = True
        
        # Generate walls
        wall_count = 0
        while wall_count < WALL_COUNT:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if (x, y) != (0, 0) and (x, y) != (GRID_SIZE - 1, GRID_SIZE - 1) and maze[x, y] == CELL_EMPTY:
                maze[x, y] = CELL_WALL
                wall_count += 1
        
        # Generate gems
        gem_locations = []
        gem_count = 0
        while gem_count < GEM_COUNT:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if maze[x, y] == CELL_EMPTY and (x, y) != (0, 0) and (x, y) != (GRID_SIZE - 1, GRID_SIZE - 1):
                maze[x, y] = CELL_GEM
                gem_locations.append([x, y])
                gem_count += 1
        
        # Generate traps
        trap_count = 0
        while trap_count < TRAP_COUNT:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if maze[x, y] == CELL_EMPTY and (x, y) != (0, 0) and (x, y) != (GRID_SIZE - 1, GRID_SIZE - 1):
                maze[x, y] = CELL_TRAP
                trap_count += 1
        
        # Update game state
        game_state["maze"] = maze.tolist()
        game_state["player_x"] = 0
        game_state["player_y"] = 0
        game_state["ai_x"] = GRID_SIZE - 1
        game_state["ai_y"] = GRID_SIZE - 1
        game_state["player_score"] = 0
        game_state["ai_score"] = 0
        game_state["player_gems"] = 0
        game_state["ai_gems"] = 0
        game_state["player_tokens"] = INITIAL_TOKENS
        game_state["ai_tokens"] = INITIAL_TOKENS
        game_state["current_round"] = 1
        game_state["player_turn"] = True
        game_state["game_over"] = False
        game_state["visited_player"] = visited_player.tolist()
        game_state["visited_ai"] = visited_ai.tolist()
        game_state["gem_locations"] = gem_locations
        
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
            
            # Remove from gem locations
            for i, (gem_x, gem_y) in enumerate(game_state["gem_locations"]):
                if gem_x == x and gem_y == y:
                    game_state["gem_locations"].pop(i)
                    break
            
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
    def remove_trap(x, y, is_player):
        """Remove a trap at position (x, y) if present"""
        if game_state["maze"][x][y] == CELL_TRAP:
            game_state["maze"][x][y] = CELL_EMPTY
            
            # Use a token
            if is_player:
                game_state["player_tokens"] -= 1
            else:
                game_state["ai_tokens"] -= 1
                
            return True
        return False
    
    @staticmethod
    def place_wall(x, y, is_player):
        """Place a wall at position (x, y) if empty"""
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and game_state["maze"][x][y] == CELL_EMPTY:
            game_state["maze"][x][y] = CELL_WALL
            
            # Use a token
            if is_player:
                game_state["player_tokens"] -= 1
            else:
                game_state["ai_tokens"] -= 1
                
            return True
        return False
    
    @staticmethod
    def teleport(x, y, is_player):
        """Teleport to a previously visited position"""
        # Check if position has been visited
        visited = game_state["visited_player"] if is_player else game_state["visited_ai"]
        if not visited[x][y]:
            return False
            
        # Execute teleportation
        if is_player:
            game_state["player_x"] = x
            game_state["player_y"] = y
            game_state["player_tokens"] -= 1
        else:
            game_state["ai_x"] = x
            game_state["ai_y"] = y
            game_state["ai_tokens"] -= 1
            
        return True
    
    @staticmethod
    def player_move(dx, dy):
        """Move the player"""
        if not game_state["player_turn"] or game_state["game_over"]:
            return {"success": False, "message": "Not player's turn or game over"}
        
        new_x = game_state["player_x"] + dx
        new_y = game_state["player_y"] + dy
        
        # Check if move is valid
        if not MazeGame.is_valid_move(new_x, new_y):
            return {"success": False, "message": "Invalid move"}
        
        # Execute the move
        game_state["player_x"] = new_x
        game_state["player_y"] = new_y
        
        # Mark as visited
        game_state["visited_player"][new_x][new_y] = True
        
        # Check for gem collection
        MazeGame.collect_gem(new_x, new_y, True)
        
        # Check for trap
        if MazeGame.check_trap(new_x, new_y):
            game_state["player_score"] -= 5
        
        # Switch to AI's turn
        game_state["player_turn"] = False
        
        # Let AI make its move
        MazeGame.ai_make_move()
        
        # Check if round is complete
        if game_state["current_round"] >= ROUNDS:
            game_state["game_over"] = True
        else:
            game_state["current_round"] += 1
            game_state["player_turn"] = True
        
        return {"success": True, "state": game_state}
    
    @staticmethod
    def player_use_token(action_type, target_x=None, target_y=None):
        """Player uses a token for special action"""
        if not game_state["player_turn"] or game_state["game_over"]:
            return {"success": False, "message": "Not player's turn or game over"}
        
        if game_state["player_tokens"] <= 0:
            return {"success": False, "message": "No tokens left"}
        
        success = False
        
        if action_type == "wall" and target_x is not None and target_y is not None:
            # Place wall
            success = MazeGame.place_wall(target_x, target_y, True)
        
        elif action_type == "remove_trap":
            # Remove trap at current position
            success = MazeGame.remove_trap(game_state["player_x"], game_state["player_y"], True)
        
        elif action_type == "teleport" and target_x is not None and target_y is not None:
            # Teleport to specified position
            success = MazeGame.teleport(target_x, target_y, True)
        
        if success:
            # Switch to AI's turn
            game_state["player_turn"] = False
            
            # Let AI make its move
            MazeGame.ai_make_move()
            
            # Check if round is complete
            if game_state["current_round"] >= ROUNDS:
                game_state["game_over"] = True
            else:
                game_state["current_round"] += 1
                game_state["player_turn"] = True
                
        return {"success": success, "state": game_state}
        
    @staticmethod
    def ai_make_move():
        """AI makes a move using simple strategy"""
        # Simple strategy: 
        # 1. If next to a gem, move to it
        # 2. Otherwise, try to move toward the nearest gem
        # 3. If trapped, use a token to remove trap or teleport
        
        # Check surrounding cells for gems
        x, y = game_state["ai_x"], game_state["ai_y"]
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if MazeGame.is_valid_move(new_x, new_y) and game_state["maze"][new_x][new_y] == CELL_GEM:
                # Found a gem, move to it
                game_state["ai_x"], game_state["ai_y"] = new_x, new_y
                game_state["visited_ai"][new_x][new_y] = True
                MazeGame.collect_gem(new_x, new_y, False)
                return
        
        # If on a trap and has tokens, remove it
        if MazeGame.check_trap(x, y) and game_state["ai_tokens"] > 0:
            MazeGame.remove_trap(x, y, False)
            return
        
        # Find nearest gem
        nearest_gem = None
        min_distance = float('inf')
        
        for gem_x, gem_y in game_state["gem_locations"]:
            distance = abs(gem_x - x) + abs(gem_y - y)  # Manhattan distance
            if distance < min_distance:
                min_distance = distance
                nearest_gem = (gem_x, gem_y)
        
        # If no gems left, just make a random valid move
        if nearest_gem is None:
            valid_moves = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if MazeGame.is_valid_move(new_x, new_y):
                    valid_moves.append((new_x, new_y))
            
            if valid_moves:
                new_x, new_y = random.choice(valid_moves)
                game_state["ai_x"], game_state["ai_y"] = new_x, new_y
                game_state["visited_ai"][new_x][new_y] = True
                
                # Check for gem/trap
                MazeGame.collect_gem(new_x, new_y, False)
                if MazeGame.check_trap(new_x, new_y):
                    game_state["ai_score"] -= 5
            return
        
        # Try to move towards the nearest gem
        gem_x, gem_y = nearest_gem
        
        # Determine best direction
        best_dx, best_dy = 0, 0
        if gem_x > x:
            best_dx = 1
        elif gem_x < x:
            best_dx = -1
            
        if gem_y > y:
            best_dy = 1
        elif gem_y < y:
            best_dy = -1
        
        # Try primary direction first
        if abs(gem_x - x) > abs(gem_y - y):
            # Try x direction first
            if MazeGame.is_valid_move(x + best_dx, y):
                game_state["ai_x"] = x + best_dx
                game_state["ai_y"] = y
            elif MazeGame.is_valid_move(x, y + best_dy):
                game_state["ai_x"] = x
                game_state["ai_y"] = y + best_dy
        else:
            # Try y direction first
            if MazeGame.is_valid_move(x, y + best_dy):
                game_state["ai_x"] = x
                game_state["ai_y"] = y + best_dy
            elif MazeGame.is_valid_move(x + best_dx, y):
                game_state["ai_x"] = x + best_dx
                game_state["ai_y"] = y
        
        # If no good moves, try any valid move
        if game_state["ai_x"] == x and game_state["ai_y"] == y:
            valid_moves = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if MazeGame.is_valid_move(new_x, new_y):
                    valid_moves.append((new_x, new_y))
            
            if valid_moves:
                new_x, new_y = random.choice(valid_moves)
                game_state["ai_x"], game_state["ai_y"] = new_x, new_y
            else:
                # No valid moves and on trap - use token to teleport if available
                if game_state["ai_tokens"] > 0:
                    # Find a visited position to teleport to
                    teleport_options = []
                    for tx in range(GRID_SIZE):
                        for ty in range(GRID_SIZE):
                            if game_state["visited_ai"][tx][ty] and (tx != x or ty != y):
                                teleport_options.append((tx, ty))
                    
                    if teleport_options:
                        new_x, new_y = random.choice(teleport_options)
                        game_state["ai_tokens"] -= 1
                        game_state["ai_x"], game_state["ai_y"] = new_x, new_y
        
        # Mark new position as visited
        new_x, new_y = game_state["ai_x"], game_state["ai_y"]
        game_state["visited_ai"][new_x][new_y] = True
        
        # Check for gem/trap
        MazeGame.collect_gem(new_x, new_y, False)
        if MazeGame.check_trap(new_x, new_y):
            game_state["ai_score"] -= 5

    @staticmethod
    def reset_game():
        """Reset the game"""
        return MazeGame.initialize_game()


class MazeGameHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for the maze game"""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve static files
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Send HTML content
            with open('web_maze_game.html', 'rb') as file:
                self.wfile.write(file.read())
                
        elif self.path == '/api/state':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Initialize game if not already
            if game_state["maze"] is None:
                MazeGame.initialize_game()
                
            self.wfile.write(json.dumps(game_state).encode())
            
        elif self.path.startswith('/api/move'):
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            try:
                dx = int(query_params.get('dx', [0])[0])
                dy = int(query_params.get('dy', [0])[0])
                
                result = MazeGame.player_move(dx, dy)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except (ValueError, KeyError) as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
                
        elif self.path.startswith('/api/token'):
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            try:
                action = query_params.get('action', [''])[0]
                target_x = int(query_params.get('x', [None])[0]) if 'x' in query_params else None
                target_y = int(query_params.get('y', [None])[0]) if 'y' in query_params else None
                
                result = MazeGame.player_use_token(action, target_x, target_y)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except (ValueError, KeyError) as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
                
        elif self.path == '/api/reset':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            result = MazeGame.reset_game()
            self.wfile.write(json.dumps({"success": True, "state": result}).encode())
            
        else:
            # Serve static files
            super().do_GET()


def run_server(port=5001):
    """Run the web server"""
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, MazeGameHandler)
    print(f"Server running at http://0.0.0.0:{port}/")
    httpd.serve_forever()


if __name__ == "__main__":
    # Initialize the game
    MazeGame.initialize_game()
    
    # Create HTML file
    with open('web_maze_game.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maze Game: Player vs AI</title>
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
            max-width: 1200px;
            gap: 20px;
        }
        .maze-container {
            position: relative;
        }
        canvas {
            background-color: #2d2d2d;
            border-radius: 10px;
        }
        .ui-container {
            width: 300px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .panel {
            background-color: #2d2d2d;
            border-radius: 10px;
            padding: 20px;
        }
        h1, h2 {
            color: #40e0d0;
            margin-top: 0;
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
        .controls {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            grid-template-rows: repeat(3, 1fr);
            gap: 5px;
            margin: 20px 0;
        }
        .control-btn {
            padding: 10px;
            background-color: #3a3a3a;
            border: none;
            color: white;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .control-btn:hover {
            background-color: #4a4a4a;
        }
        .control-btn:active {
            background-color: #5a5a5a;
        }
        .action-btn {
            background-color: #7061db;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
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
        .btn-start {
            background-color: #00bfff;
        }
        .game-status {
            font-weight: bold;
            margin-top: 10px;
        }
        .token-count {
            font-weight: bold;
            color: #7061db;
        }
        .token-btn-disabled {
            background-color: #3a3a3a;
            opacity: 0.5;
            cursor: not-allowed;
        }
        .legend {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }
        .teleport-mode {
            position: absolute;
            top: 10px;
            left: 10px;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            pointer-events: none;
        }
        .instructions {
            margin-top: 20px;
            line-height: 1.4;
        }
        .game-over {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-radius: 10px;
        }
        .winner {
            font-size: 24px;
            margin-bottom: 20px;
        }
        .placed-wall-mode {
            position: absolute;
            top: 10px;
            left: 10px;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            pointer-events: none;
        }
        @media (max-width: 900px) {
            .game-container {
                flex-direction: column;
            }
            .ui-container {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="maze-container">
            <canvas id="mazeCanvas" width="500" height="500"></canvas>
            <div id="teleportMode" class="teleport-mode" style="display: none;">Teleport Mode: Click a visited cell</div>
            <div id="placeWallMode" class="placed-wall-mode" style="display: none;">Wall Mode: Click an empty cell</div>
            <div id="gameOver" class="game-over" style="display: none;">
                <div id="winnerText" class="winner"></div>
                <button id="restartBtn" class="btn btn-start">Play Again</button>
            </div>
        </div>
        
        <div class="ui-container">
            <div class="panel">
                <h1>Maze Game</h1>
                <p>A 10x10 maze where you compete with an AI to collect the most gems!</p>
                <div class="score-display">
                    <div>Round: <span id="roundDisplay">1</span>/<span id="totalRounds">20</span></div>
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
                <div class="token-count">Tokens: <span id="playerTokens">3</span></div>
            </div>
            
            <div class="panel">
                <h2>Controls</h2>
                <div class="controls">
                    <div></div>
                    <button id="upBtn" class="control-btn">↑</button>
                    <div></div>
                    <button id="leftBtn" class="control-btn">←</button>
                    <div></div>
                    <button id="rightBtn" class="control-btn">→</button>
                    <div></div>
                    <button id="downBtn" class="control-btn">↓</button>
                    <div></div>
                </div>
                
                <button id="wallBtn" class="btn action-btn">Place Wall <span>(1 token)</span></button>
                <button id="trapBtn" class="btn action-btn">Remove Trap <span>(1 token)</span></button>
                <button id="teleportBtn" class="btn action-btn">Teleport <span>(1 token)</span></button>
                
                <button id="resetGameBtn" class="btn">New Game</button>
            </div>
            
            <div class="panel">
                <h2>Legend</h2>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #00bfff;"></div>
                        <div>Player</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #ffd700;"></div>
                        <div>AI Agent</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #40e0d0;"></div>
                        <div>Gem (+10 points)</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #ff4500;"></div>
                        <div>Trap (-5 points)</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: #646464;"></div>
                        <div>Wall</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="border: 1px solid #00bfff; background-color: transparent;"></div>
                        <div>Player's path</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="border: 1px solid #ffd700; background-color: transparent;"></div>
                        <div>AI's path</div>
                    </div>
                </div>
                
                <div class="instructions">
                    <p>Collect gems to earn points. Use your tokens strategically to gain an advantage over the AI. The game ends after 20 rounds, and the player with the most gems wins!</p>
                </div>
            </div>
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
        
        // Initialize variables
        let gameState = null;
        let teleportMode = false;
        let placeWallMode = false;
        
        // Canvas and context
        const canvas = document.getElementById('mazeCanvas');
        const ctx = canvas.getContext('2d');
        
        // UI elements
        const teleportModeUI = document.getElementById('teleportMode');
        const placeWallModeUI = document.getElementById('placeWallMode');
        const gameOverUI = document.getElementById('gameOver');
        const winnerTextUI = document.getElementById('winnerText');
        const restartBtn = document.getElementById('restartBtn');
        const resetGameBtn = document.getElementById('resetGameBtn');
        
        // Game stats display
        const roundDisplay = document.getElementById('roundDisplay');
        const turnDisplay = document.getElementById('turnDisplay');
        const playerScoreDisplay = document.getElementById('playerScore');
        const aiScoreDisplay = document.getElementById('aiScore');
        const playerGemsDisplay = document.getElementById('playerGems');
        const aiGemsDisplay = document.getElementById('aiGems');
        const playerTokensDisplay = document.getElementById('playerTokens');
        
        // Control buttons
        const upBtn = document.getElementById('upBtn');
        const downBtn = document.getElementById('downBtn');
        const leftBtn = document.getElementById('leftBtn');
        const rightBtn = document.getElementById('rightBtn');
        const wallBtn = document.getElementById('wallBtn');
        const trapBtn = document.getElementById('trapBtn');
        const teleportBtn = document.getElementById('teleportBtn');
        
        // Fetch game state
        async function fetchGameState() {
            const response = await fetch('/api/state');
            gameState = await response.json();
            updateUI();
            drawMaze();
        }
        
        // Move player
        async function movePlayer(dx, dy) {
            if (!gameState.player_turn || gameState.game_over) return;
            
            const response = await fetch(`/api/move?dx=${dx}&dy=${dy}`);
            const result = await response.json();
            
            if (result.success) {
                gameState = result.state;
                updateUI();
                drawMaze();
                checkGameOver();
            }
        }
        
        // Use token
        async function useToken(action, x = null, y = null) {
            if (!gameState.player_turn || gameState.game_over) return;
            if (gameState.player_tokens <= 0) return;
            
            let url = `/api/token?action=${action}`;
            if (x !== null && y !== null) {
                url += `&x=${x}&y=${y}`;
            }
            
            const response = await fetch(url);
            const result = await response.json();
            
            if (result.success) {
                gameState = result.state;
                updateUI();
                drawMaze();
                checkGameOver();
            }
            
            // Exit special modes
            teleportMode = false;
            placeWallMode = false;
            teleportModeUI.style.display = 'none';
            placeWallModeUI.style.display = 'none';
        }
        
        // Reset game
        async function resetGame() {
            const response = await fetch('/api/reset');
            const result = await response.json();
            
            if (result.success) {
                gameState = result.state;
                updateUI();
                drawMaze();
                
                // Hide game over screen
                gameOverUI.style.display = 'none';
                
                // Exit special modes
                teleportMode = false;
                placeWallMode = false;
                teleportModeUI.style.display = 'none';
                placeWallModeUI.style.display = 'none';
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
            
            // Update token buttons based on available tokens
            if (gameState.player_tokens <= 0) {
                wallBtn.classList.add('token-btn-disabled');
                trapBtn.classList.add('token-btn-disabled');
                teleportBtn.classList.add('token-btn-disabled');
            } else {
                wallBtn.classList.remove('token-btn-disabled');
                trapBtn.classList.remove('token-btn-disabled');
                teleportBtn.classList.remove('token-btn-disabled');
            }
        }
        
        // Check if game is over
        function checkGameOver() {
            if (gameState.game_over) {
                gameOverUI.style.display = 'flex';
                
                const playerGems = gameState.player_gems;
                const aiGems = gameState.ai_gems;
                
                if (playerGems > aiGems) {
                    winnerTextUI.textContent = `You Win! (${playerGems} vs ${aiGems} gems)`;
                    winnerTextUI.style.color = '#00bfff';
                } else if (aiGems > playerGems) {
                    winnerTextUI.textContent = `AI Wins! (${aiGems} vs ${playerGems} gems)`;
                    winnerTextUI.style.color = '#ffd700';
                } else {
                    winnerTextUI.textContent = `It's a Tie! (${playerGems} gems each)`;
                    winnerTextUI.style.color = '#ffffff';
                }
            }
        }
        
        // Draw the maze
        function drawMaze() {
            if (!gameState) return;
            
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
                        
                        // Wall pattern
                        ctx.fillStyle = '#5a5a5a';
                        ctx.fillRect(cellX, cellY, CELL_SIZE/2, CELL_SIZE/2);
                        ctx.fillRect(cellX + CELL_SIZE/2, cellY + CELL_SIZE/2, CELL_SIZE/2, CELL_SIZE/2);
                        
                        ctx.strokeStyle = '#707070';
                        ctx.beginPath();
                        ctx.moveTo(cellX, cellY);
                        ctx.lineTo(cellX + CELL_SIZE, cellY + CELL_SIZE);
                        ctx.moveTo(cellX + CELL_SIZE, cellY);
                        ctx.lineTo(cellX, cellY + CELL_SIZE);
                        ctx.stroke();
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
                        
                        // Sparkle
                        ctx.strokeStyle = '#ffffff';
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        ctx.moveTo(cellX + CELL_SIZE/2, cellY + 10);
                        ctx.lineTo(cellX + CELL_SIZE/2, cellY + CELL_SIZE - 10);
                        ctx.moveTo(cellX + 10, cellY + CELL_SIZE/2);
                        ctx.lineTo(cellX + CELL_SIZE - 10, cellY + CELL_SIZE/2);
                        ctx.stroke();
                    } else if (cellType === CELL_TRAP) {
                        // Trap
                        ctx.fillStyle = '#ff4500';
                        ctx.beginPath();
                        ctx.moveTo(cellX + 5, cellY + CELL_SIZE - 5);
                        ctx.lineTo(cellX + CELL_SIZE - 5, cellY + CELL_SIZE - 5);
                        ctx.lineTo(cellX + CELL_SIZE/2, cellY + 5);
                        ctx.closePath();
                        ctx.fill();
                        
                        // Warning mark
                        ctx.fillStyle = '#ffffff';
                        ctx.font = '20px Arial';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText('!', cellX + CELL_SIZE/2, cellY + CELL_SIZE/2 + 5);
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
            
            // Player face
            ctx.fillStyle = '#87cefa';
            ctx.beginPath();
            ctx.arc(playerX + CELL_SIZE/2, playerY + CELL_SIZE/2, CELL_SIZE/2 - 10, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(playerX + CELL_SIZE/2 - 5, playerY + CELL_SIZE/2 - 5, 3, 0, Math.PI * 2);
            ctx.arc(playerX + CELL_SIZE/2 + 5, playerY + CELL_SIZE/2 - 5, 3, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(playerX + CELL_SIZE/2, playerY + CELL_SIZE/2 + 5, 5, 0, Math.PI);
            ctx.stroke();
            
            // Draw AI
            const aiX = gameState.ai_x * CELL_SIZE;
            const aiY = gameState.ai_y * CELL_SIZE;
            ctx.fillStyle = '#ffd700';
            ctx.fillRect(aiX + 5, aiY + 5, CELL_SIZE - 10, CELL_SIZE - 10);
            
            ctx.fillStyle = '#ffec8b';
            ctx.fillRect(aiX + 10, aiY + 10, CELL_SIZE - 20, CELL_SIZE - 20);
            
            ctx.fillStyle = '#000000';
            ctx.beginPath();
            ctx.arc(aiX + CELL_SIZE/2 - 5, aiY + CELL_SIZE/2 - 5, 3, 0, Math.PI * 2);
            ctx.arc(aiX + CELL_SIZE/2 + 5, aiY + CELL_SIZE/2 - 5, 3, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(aiX + CELL_SIZE/2 - 5, aiY + CELL_SIZE/2 + 5);
            ctx.quadraticCurveTo(aiX + CELL_SIZE/2, aiY + CELL_SIZE/2, aiX + CELL_SIZE/2 + 5, aiY + CELL_SIZE/2 + 5);
            ctx.stroke();
        }
        
        // Canvas click handler for teleport and wall placement
        canvas.addEventListener('click', (event) => {
            if (!gameState.player_turn || gameState.game_over) return;
            
            const rect = canvas.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const clickY = event.clientY - rect.top;
            
            const gridX = Math.floor(clickX / CELL_SIZE);
            const gridY = Math.floor(clickY / CELL_SIZE);
            
            if (teleportMode) {
                // Ensure clicked position has been visited
                if (gameState.visited_player[gridX][gridY]) {
                    useToken('teleport', gridX, gridY);
                }
            } else if (placeWallMode) {
                // Ensure clicked position is empty
                if (gameState.maze[gridX][gridY] === CELL_EMPTY) {
                    useToken('wall', gridX, gridY);
                }
            }
        });
        
        // Event listeners for controls
        upBtn.addEventListener('click', () => movePlayer(0, -1));
        downBtn.addEventListener('click', () => movePlayer(0, 1));
        leftBtn.addEventListener('click', () => movePlayer(-1, 0));
        rightBtn.addEventListener('click', () => movePlayer(1, 0));
        
        // Token action buttons
        wallBtn.addEventListener('click', () => {
            if (gameState.player_tokens <= 0) return;
            placeWallMode = true;
            teleportMode = false;
            placeWallModeUI.style.display = 'block';
            teleportModeUI.style.display = 'none';
        });
        
        trapBtn.addEventListener('click', () => {
            useToken('remove_trap');
        });
        
        teleportBtn.addEventListener('click', () => {
            if (gameState.player_tokens <= 0) return;
            teleportMode = true;
            placeWallMode = false;
            teleportModeUI.style.display = 'block';
            placeWallModeUI.style.display = 'none';
        });
        
        // Reset and restart buttons
        resetGameBtn.addEventListener('click', resetGame);
        restartBtn.addEventListener('click', resetGame);
        
        // Keyboard controls
        document.addEventListener('keydown', (event) => {
            // Only process if it's player's turn
            if (!gameState.player_turn || gameState.game_over) return;
            
            switch(event.key) {
                case 'ArrowUp':
                    movePlayer(0, -1);
                    break;
                case 'ArrowDown':
                    movePlayer(0, 1);
                    break;
                case 'ArrowLeft':
                    movePlayer(-1, 0);
                    break;
                case 'ArrowRight':
                    movePlayer(1, 0);
                    break;
                case '1':
                    if (gameState.player_tokens <= 0) return;
                    placeWallMode = true;
                    teleportMode = false;
                    placeWallModeUI.style.display = 'block';
                    teleportModeUI.style.display = 'none';
                    break;
                case '2':
                    useToken('remove_trap');
                    break;
                case '3':
                    if (gameState.player_tokens <= 0) return;
                    teleportMode = true;
                    placeWallMode = false;
                    teleportModeUI.style.display = 'block';
                    placeWallModeUI.style.display = 'none';
                    break;
                case 'r':
                    resetGame();
                    break;
                case 'Escape':
                    // Cancel special modes
                    teleportMode = false;
                    placeWallMode = false;
                    teleportModeUI.style.display = 'none';
                    placeWallModeUI.style.display = 'none';
                    break;
            }
        });
        
        // Initialize game
        fetchGameState();
    </script>
</body>
</html>""")
    
    # Run the server
    run_server()
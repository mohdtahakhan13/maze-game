#!/usr/bin/env python3
"""
Web server for the maze game that allows playing through a web interface.
"""

import os
import sys
import json
import time
import threading
import subprocess
import http.server
import socketserver
from http import HTTPStatus

# Game state variables
game_process = None
game_running = False
last_command = None

def start_game():
    """Start the game in a separate process"""
    global game_process, game_running
    if game_process is None or game_process.poll() is not None:
        # Kill any existing python processes
        os.system("pkill -f 'python main.py'")
        time.sleep(1)
        # Start the game
        game_process = subprocess.Popen(["python", "main.py"], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
        game_running = True
        return True
    return False

def send_key_command(key):
    """Send a key command to the game"""
    global last_command
    if not game_running:
        return False
    
    last_command = key
    # Use xdotool to send keypress to the game window
    key_mapping = {
        "up": "Up",
        "down": "Down", 
        "left": "Left",
        "right": "Right",
        "1": "1",
        "2": "2",
        "3": "3",
        "r": "r"
    }
    
    if key in key_mapping:
        os.system(f"xdotool key {key_mapping[key]}")
        return True
    return False

class GameHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for the game web interface."""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve static files
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Send HTML content
            with open('web_interface.html', 'rb') as file:
                self.wfile.write(file.read())
        
        elif self.path == '/start':
            success = start_game()
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": success}).encode())
        
        elif self.path.startswith('/key/'):
            key = self.path.split('/')[-1]
            success = send_key_command(key)
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "key": key}).encode())
        
        elif self.path == '/status':
            status = {
                "game_running": game_running,
                "last_command": last_command
            }
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        
        else:
            # Serve static files
            super().do_GET()

def run_server():
    """Run the web server on port 5000"""
    handler = GameHandler
    with socketserver.TCPServer(("0.0.0.0", 5000), handler) as httpd:
        print(f"Server running at http://0.0.0.0:5000/")
        httpd.serve_forever()

if __name__ == "__main__":
    # Create the web interface HTML file if it doesn't exist
    if not os.path.exists('web_interface.html'):
        with open('web_interface.html', 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maze Game - Player vs AI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1e1e1e;
            color: white;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #40e0d0;
        }
        .game-info {
            background-color: #2d2d2d;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .controls {
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #2d2d2d;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .d-pad {
            display: grid;
            grid-template-columns: repeat(3, 60px);
            grid-template-rows: repeat(3, 60px);
            gap: 5px;
            margin: 20px 0;
        }
        .btn {
            background-color: #3a3a3a;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 15px 20px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background-color: #4a4a4a;
        }
        .btn:active {
            background-color: #5a5a5a;
        }
        .d-btn {
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 24px;
        }
        .token-btns {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .token-btn {
            background-color: #7061db;
        }
        #startBtn {
            background-color: #00bfff;
            margin-bottom: 20px;
        }
        #resetBtn {
            background-color: #ff4500;
        }
        .instructions {
            background-color: #2d2d2d;
            border-radius: 10px;
            padding: 20px;
            text-align: left;
        }
        .instructions h2 {
            text-align: center;
            color: #40e0d0;
        }
        .instructions ul {
            margin-left: 20px;
        }
        .status {
            margin-top: 20px;
            font-style: italic;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Maze Game: Player vs AI</h1>
        
        <div class="game-info">
            <p>A 10x10 maze game where you compete against an AI agent to collect the most gems!</p>
            <button id="startBtn" class="btn">Start Game</button>
        </div>
        
        <div class="controls">
            <h2>Game Controls</h2>
            
            <div class="d-pad">
                <div></div>
                <button class="btn d-btn" id="upBtn">↑</button>
                <div></div>
                <button class="btn d-btn" id="leftBtn">←</button>
                <div></div>
                <button class="btn d-btn" id="rightBtn">→</button>
                <div></div>
                <button class="btn d-btn" id="downBtn">↓</button>
                <div></div>
            </div>
            
            <div class="token-btns">
                <button class="btn token-btn" id="wallBtn">1: Place Wall</button>
                <button class="btn token-btn" id="trapBtn">2: Remove Trap</button>
                <button class="btn token-btn" id="teleportBtn">3: Teleport</button>
            </div>
            
            <button class="btn" id="resetBtn">R: Reset Game</button>
            
            <div class="status" id="status">Game not started</div>
        </div>
        
        <div class="instructions">
            <h2>How to Play</h2>
            <ul>
                <li><strong>Goal:</strong> Collect more gems than the AI agent within the limited number of rounds.</li>
                <li><strong>Movement:</strong> Use the arrow buttons to move your character (blue circle).</li>
                <li><strong>Gems:</strong> Collect turquoise diamond gems to earn 10 points.</li>
                <li><strong>Traps:</strong> Avoid red triangle traps that cost you 5 points.</li>
                <li><strong>Walls:</strong> Navigate around gray walls that block movement.</li>
                <li><strong>Strategic Tokens:</strong> Use your limited tokens wisely!</li>
                <ul>
                    <li><strong>Place Wall (1):</strong> Block the AI's path by placing a wall.</li>
                    <li><strong>Remove Trap (2):</strong> Remove a trap at your current position.</li>
                    <li><strong>Teleport (3):</strong> Teleport to a previously visited position.</li>
                </ul>
                <li><strong>Turns:</strong> Players alternate turns, and the game ends after a set number of rounds.</li>
                <li><strong>Reset:</strong> Press 'R' to restart the game after it ends.</li>
            </ul>
        </div>
    </div>
    
    <script>
        // Game control functions
        const startBtn = document.getElementById('startBtn');
        const upBtn = document.getElementById('upBtn');
        const downBtn = document.getElementById('downBtn');
        const leftBtn = document.getElementById('leftBtn');
        const rightBtn = document.getElementById('rightBtn');
        const wallBtn = document.getElementById('wallBtn');
        const trapBtn = document.getElementById('trapBtn');
        const teleportBtn = document.getElementById('teleportBtn');
        const resetBtn = document.getElementById('resetBtn');
        const statusEl = document.getElementById('status');
        
        // Start the game
        startBtn.addEventListener('click', async () => {
            statusEl.textContent = 'Starting game...';
            try {
                const response = await fetch('/start');
                const data = await response.json();
                if (data.success) {
                    statusEl.textContent = 'Game started! Use the controls to play.';
                    startBtn.textContent = 'Game Running';
                    startBtn.disabled = true;
                } else {
                    statusEl.textContent = 'Game already running.';
                }
            } catch (error) {
                statusEl.textContent = `Error: ${error.message}`;
            }
        });
        
        // Movement controls
        upBtn.addEventListener('click', () => sendKey('up'));
        downBtn.addEventListener('click', () => sendKey('down'));
        leftBtn.addEventListener('click', () => sendKey('left'));
        rightBtn.addEventListener('click', () => sendKey('right'));
        
        // Token controls
        wallBtn.addEventListener('click', () => sendKey('1'));
        trapBtn.addEventListener('click', () => sendKey('2'));
        teleportBtn.addEventListener('click', () => sendKey('3'));
        
        // Reset game
        resetBtn.addEventListener('click', () => sendKey('r'));
        
        // Send key command to game
        async function sendKey(key) {
            statusEl.textContent = `Sending command: ${key}`;
            try {
                const response = await fetch(`/key/${key}`);
                const data = await response.json();
                if (data.success) {
                    statusEl.textContent = `Command sent: ${key}`;
                } else {
                    statusEl.textContent = 'Game not running. Start the game first.';
                }
            } catch (error) {
                statusEl.textContent = `Error: ${error.message}`;
            }
        }
        
        // Keyboard controls
        document.addEventListener('keydown', (event) => {
            switch(event.key) {
                case 'ArrowUp':
                    sendKey('up');
                    break;
                case 'ArrowDown':
                    sendKey('down');
                    break;
                case 'ArrowLeft':
                    sendKey('left');
                    break;
                case 'ArrowRight':
                    sendKey('right');
                    break;
                case '1':
                    sendKey('1');
                    break;
                case '2':
                    sendKey('2');
                    break;
                case '3':
                    sendKey('3');
                    break;
                case 'r':
                    sendKey('r');
                    break;
            }
        });
        
        // Periodically check game status
        setInterval(async () => {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                if (data.game_running) {
                    startBtn.textContent = 'Game Running';
                    startBtn.disabled = true;
                } else {
                    startBtn.textContent = 'Start Game';
                    startBtn.disabled = false;
                }
            } catch (error) {
                console.error('Error checking game status:', error);
            }
        }, 5000);
    </script>
</body>
</html>""")
    
    # Start the server
    run_server()
"""
Constants module for game-wide settings and values
"""

# Grid settings
GRID_SIZE = 10
CELL_SIZE = 50

# Screen settings
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE + 300  # Extra space for UI
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE

# Game settings
FPS = 60
ROUNDS = 20  # Number of rounds before game ends

# Cell types
CELL_TYPES = {
    "EMPTY": 0,
    "WALL": 1,
    "GEM": 2,
    "TRAP": 3,
    "PLAYER": 4,
    "AI": 5
}

# Game element counts
GEM_COUNT = 15
TRAP_COUNT = 10
WALL_COUNT = 20

# Colors (RGB)
COLORS = {
    "BACKGROUND": (30, 30, 30),
    "GRID_LINE": (50, 50, 50),
    "EMPTY": (0, 0, 0, 0),
    "WALL": (100, 100, 100),
    "GEM": (64, 224, 208),  # Turquoise
    "TRAP": (255, 69, 0),   # Red-orange
    "PLAYER": (0, 191, 255),  # Deep sky blue
    "AI": (255, 215, 0),    # Gold
    "TEXT": (255, 255, 255),
    "PLAYER_VISITED": (0, 191, 255, 128),
    "AI_VISITED": (255, 215, 0, 128),
    "UI_BACKGROUND": (40, 40, 40),
    "UI_BORDER": (100, 100, 100),
    "TOKEN": (147, 112, 219)  # Medium purple
}

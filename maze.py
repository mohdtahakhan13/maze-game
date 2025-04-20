"""
Maze module for creating and managing the maze environment
"""

import random
import numpy as np
from constants import GRID_SIZE, CELL_TYPES, GEM_COUNT, TRAP_COUNT, WALL_COUNT

class Maze:
    """
    Represents the 10x10 maze environment with gems, traps, and walls.
    """
    def __init__(self, size):
        """
        Initialize the maze with a given size.
        
        Args:
            size (int): The size of the maze (10x10 default)
        """
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.visited_player = np.zeros((size, size), dtype=bool)
        self.visited_ai = np.zeros((size, size), dtype=bool)
        self.gem_locations = []
        
        # Generate maze elements
        self._generate_maze()
        
    def _generate_maze(self):
        """Generate a random maze with gems, traps, and walls"""
        # Clear corners for player and AI
        self.grid[0, 0] = CELL_TYPES["EMPTY"]  # Top-left for player
        self.grid[self.size-1, self.size-1] = CELL_TYPES["EMPTY"]  # Bottom-right for AI
        
        # Mark starting positions as visited
        self.visited_player[0, 0] = True
        self.visited_ai[self.size-1, self.size-1] = True
        
        # Generate walls
        wall_count = 0
        while wall_count < WALL_COUNT:
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            # Don't place walls in player or AI starting positions
            if (x, y) != (0, 0) and (x, y) != (self.size-1, self.size-1):
                self.grid[x, y] = CELL_TYPES["WALL"]
                wall_count += 1
        
        # Generate gems
        gem_count = 0
        while gem_count < GEM_COUNT:
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            # Don't place gems on walls or in player/AI starting positions
            if self.grid[x, y] == CELL_TYPES["EMPTY"] and (x, y) != (0, 0) and (x, y) != (self.size-1, self.size-1):
                self.grid[x, y] = CELL_TYPES["GEM"]
                self.gem_locations.append((x, y))
                gem_count += 1
        
        # Generate traps
        trap_count = 0
        while trap_count < TRAP_COUNT:
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            # Don't place traps on walls, gems, or in player/AI starting positions
            if self.grid[x, y] == CELL_TYPES["EMPTY"] and (x, y) != (0, 0) and (x, y) != (self.size-1, self.size-1):
                self.grid[x, y] = CELL_TYPES["TRAP"]
                trap_count += 1
    
    def is_valid_move(self, x, y):
        """
        Check if a move to position (x, y) is valid
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            bool: True if move is valid, False otherwise
        """
        # Check if within grid bounds
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False
        
        # Check if position is a wall
        if self.grid[x, y] == CELL_TYPES["WALL"]:
            return False
            
        return True
    
    def collect_gem(self, x, y):
        """
        Collect a gem at position (x, y) if present
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            bool: True if gem was collected, False otherwise
        """
        if self.grid[x, y] == CELL_TYPES["GEM"]:
            self.grid[x, y] = CELL_TYPES["EMPTY"]
            if (x, y) in self.gem_locations:
                self.gem_locations.remove((x, y))
            return True
        return False
    
    def check_trap(self, x, y):
        """
        Check if position (x, y) contains a trap
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            bool: True if trap is present, False otherwise
        """
        return self.grid[x, y] == CELL_TYPES["TRAP"]
    
    def remove_trap(self, x, y):
        """
        Remove a trap at position (x, y) if present
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            bool: True if trap was removed, False otherwise
        """
        if self.grid[x, y] == CELL_TYPES["TRAP"]:
            self.grid[x, y] = CELL_TYPES["EMPTY"]
            return True
        return False
    
    def place_wall(self, x, y):
        """
        Place a wall at position (x, y) if empty
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            bool: True if wall was placed, False otherwise
        """
        if self.grid[x, y] == CELL_TYPES["EMPTY"]:
            self.grid[x, y] = CELL_TYPES["WALL"]
            return True
        return False
    
    def get_state(self):
        """
        Get the current state of the maze
        
        Returns:
            numpy.ndarray: Current grid state
        """
        return self.grid.copy()
    
    def get_valid_moves(self, x, y):
        """
        Get all valid moves from position (x, y)
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            list: List of valid (dx, dy) pairs
        """
        valid_moves = []
        
        # Check all four directions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_move(new_x, new_y):
                valid_moves.append((dx, dy))
                
        return valid_moves

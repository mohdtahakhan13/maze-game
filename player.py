"""
Player module for handling player actions and state
"""

from constants import CELL_TYPES

class Player:
    """
    Represents the player character in the maze game.
    """
    def __init__(self, x, y, maze):
        """
        Initialize the player at position (x, y).
        
        Args:
            x (int): Initial X coordinate
            y (int): Initial Y coordinate
            maze (Maze): Reference to the maze object
        """
        self.x = x
        self.y = y
        self.maze = maze
        self.gems_collected = 0
        self.score = 0
        self.visited_positions = [(x, y)]  # Track visited positions for teleportation
    
    def move(self, dx, dy):
        """
        Move the player by (dx, dy) if valid
        
        Args:
            dx (int): Change in X direction
            dy (int): Change in Y direction
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        new_x, new_y = self.x + dx, self.y + dy
        
        # Check if move is valid
        if not self.maze.is_valid_move(new_x, new_y):
            return False
        
        # Execute the move
        self.x, self.y = new_x, new_y
        
        # Track visited positions for teleportation
        if (self.x, self.y) not in self.visited_positions:
            self.visited_positions.append((self.x, self.y))
        
        # Mark as visited in the maze
        self.maze.visited_player[self.x, self.y] = True
        
        # Check for gem collection
        if self.maze.collect_gem(self.x, self.y):
            self.gems_collected += 1
            self.score += 10
        
        # Check for trap
        if self.maze.check_trap(self.x, self.y):
            self.score -= 5
        
        return True
    
    def teleport(self, x, y):
        """
        Teleport the player to a previously visited position
        
        Args:
            x (int): Target X coordinate
            y (int): Target Y coordinate
            
        Returns:
            bool: True if teleportation was successful, False otherwise
        """
        # Check if position has been visited
        if (x, y) not in self.visited_positions:
            return False
            
        # Execute teleportation
        self.x, self.y = x, y
        
        # Check for gem collection (in case a gem spawned on a visited tile)
        if self.maze.collect_gem(self.x, self.y):
            self.gems_collected += 1
            self.score += 10
        
        # Check for trap
        if self.maze.check_trap(self.x, self.y):
            self.score -= 5
            
        return True
    
    def place_wall(self, dx, dy):
        """
        Place a wall adjacent to the player's position
        
        Args:
            dx (int): X direction from player
            dy (int): Y direction from player
            
        Returns:
            bool: True if wall was placed successfully, False otherwise
        """
        target_x, target_y = self.x + dx, self.y + dy
        
        # Check if position is within bounds
        if target_x < 0 or target_x >= self.maze.size or target_y < 0 or target_y >= self.maze.size:
            return False
            
        # Check if position is empty
        return self.maze.place_wall(target_x, target_y)
    
    def remove_trap(self):
        """
        Remove a trap at the player's current position
        
        Returns:
            bool: True if trap was removed, False otherwise
        """
        return self.maze.remove_trap(self.x, self.y)
    
    def get_position(self):
        """
        Get the player's current position
        
        Returns:
            tuple: (x, y) coordinates
        """
        return (self.x, self.y)
    
    def get_score(self):
        """
        Get the player's current score
        
        Returns:
            int: Player's score
        """
        return self.score
    
    def get_gems_collected(self):
        """
        Get the number of gems collected by the player
        
        Returns:
            int: Number of gems collected
        """
        return self.gems_collected
    
    def get_visited_positions(self):
        """
        Get all positions visited by the player
        
        Returns:
            list: List of (x, y) coordinates
        """
        return self.visited_positions

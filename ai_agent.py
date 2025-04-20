"""
AI Agent module for the maze game
"""

import random
import numpy as np
from constants import CELL_TYPES

class AIAgent:
    """
    Represents the AI agent character in the maze game.
    Uses a simple reinforcement learning approach for decision-making.
    """
    def __init__(self, x, y, maze):
        """
        Initialize the AI agent at position (x, y).
        
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
        self.tokens = 3  # Start with 3 tokens
        self.visited_positions = [(x, y)]  # Track visited positions for teleportation
        
        # Simple Q-learning parameters
        self.q_table = {}  # State-action value function
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 0.2
        
    def make_move(self):
        """
        AI agent makes a move using reinforcement learning.
        
        Returns:
            bool: True if move was successful, False otherwise
        """
        # Get current state
        state = self._get_state()
        
        # Choose action (move or use token)
        if random.random() < self.exploration_rate:
            # Exploration: random action
            action = self._choose_random_action()
        else:
            # Exploitation: choose best action from Q-table
            action = self._choose_best_action(state)
        
        # Execute the action
        reward = self._execute_action(action)
        
        # Update Q-table
        new_state = self._get_state()
        self._update_q_value(state, action, reward, new_state)
        
        # Mark as visited in the maze
        self.maze.visited_ai[self.x, self.y] = True
        
        # Add to visited positions if not already there
        if (self.x, self.y) not in self.visited_positions:
            self.visited_positions.append((self.x, self.y))
            
        return True
    
    def _get_state(self):
        """
        Get the current state representation for the AI agent.
        
        Returns:
            tuple: Simplified state representation
        """
        # Get information about the surrounding cells
        surroundings = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = self.x + dx, self.y + dy
            if 0 <= new_x < self.maze.size and 0 <= new_y < self.maze.size:
                surroundings.append(self.maze.grid[new_x, new_y])
            else:
                surroundings.append(-1)  # Out of bounds
                
        # Nearest gem direction
        nearest_gem_dir = self._find_nearest_gem()
        
        # Convert state to a hashable representation
        return (self.x, self.y, tuple(surroundings), nearest_gem_dir, self.tokens)
    
    def _find_nearest_gem(self):
        """
        Find the direction to the nearest gem.
        
        Returns:
            tuple: (dx, dy) direction to nearest gem, or (0, 0) if none found
        """
        if not self.maze.gem_locations:
            return (0, 0)
            
        # Find the closest gem
        min_distance = float('inf')
        best_direction = (0, 0)
        
        for gem_x, gem_y in self.maze.gem_locations:
            distance = abs(gem_x - self.x) + abs(gem_y - self.y)  # Manhattan distance
            if distance < min_distance:
                min_distance = distance
                
                # Simplify direction to nearest gem
                dx = 0
                dy = 0
                
                if gem_x > self.x:
                    dx = 1
                elif gem_x < self.x:
                    dx = -1
                    
                if gem_y > self.y:
                    dy = 1
                elif gem_y < self.y:
                    dy = -1
                
                best_direction = (dx, dy)
                
        return best_direction
    
    def _choose_random_action(self):
        """
        Choose a random valid action.
        
        Returns:
            tuple: Action representation
        """
        possible_actions = []
        
        # Add movement actions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = self.x + dx, self.y + dy
            if self.maze.is_valid_move(new_x, new_y):
                possible_actions.append(("move", dx, dy))
        
        # Add token actions if tokens available
        if self.tokens > 0:
            # Place wall
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                wall_x, wall_y = self.x + dx, self.y + dy
                if (0 <= wall_x < self.maze.size and 0 <= wall_y < self.maze.size and 
                    self.maze.grid[wall_x, wall_y] == CELL_TYPES["EMPTY"]):
                    possible_actions.append(("wall", dx, dy))
            
            # Remove trap if on trap
            if self.maze.check_trap(self.x, self.y):
                possible_actions.append(("remove_trap", 0, 0))
            
            # Teleport to a previously visited position
            if len(self.visited_positions) > 1:  # More than just the current position
                for vx, vy in self.visited_positions:
                    if (vx, vy) != (self.x, self.y):  # Don't teleport to current position
                        possible_actions.append(("teleport", vx, vy))
        
        # If no valid actions, stay in place
        if not possible_actions:
            return ("stay", 0, 0)
            
        return random.choice(possible_actions)
    
    def _choose_best_action(self, state):
        """
        Choose the best action based on Q-values.
        
        Args:
            state: Current state representation
            
        Returns:
            tuple: Best action representation
        """
        # Get all possible actions
        possible_actions = []
        
        # Add movement actions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = self.x + dx, self.y + dy
            if self.maze.is_valid_move(new_x, new_y):
                possible_actions.append(("move", dx, dy))
        
        # Add token actions if tokens available
        if self.tokens > 0:
            # Place wall
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                wall_x, wall_y = self.x + dx, self.y + dy
                if (0 <= wall_x < self.maze.size and 0 <= wall_y < self.maze.size and 
                    self.maze.grid[wall_x, wall_y] == CELL_TYPES["EMPTY"]):
                    possible_actions.append(("wall", dx, dy))
            
            # Remove trap if on trap
            if self.maze.check_trap(self.x, self.y):
                possible_actions.append(("remove_trap", 0, 0))
            
            # Teleport to a previously visited position
            if len(self.visited_positions) > 1:  # More than just the current position
                for vx, vy in self.visited_positions:
                    if (vx, vy) != (self.x, self.y):  # Don't teleport to current position
                        possible_actions.append(("teleport", vx, vy))
        
        # If no valid actions, stay in place
        if not possible_actions:
            return ("stay", 0, 0)
        
        # Choose the action with the highest Q-value
        best_action = None
        best_value = float('-inf')
        
        for action in possible_actions:
            if (state, action) in self.q_table:
                q_value = self.q_table[(state, action)]
            else:
                # Initialize with a heuristic value
                q_value = self._get_heuristic_value(state, action)
                self.q_table[(state, action)] = q_value
                
            if q_value > best_value:
                best_value = q_value
                best_action = action
                
        return best_action
    
    def _get_heuristic_value(self, state, action):
        """
        Get a heuristic value for an unexplored state-action pair.
        
        Args:
            state: Current state representation
            action: Action to evaluate
            
        Returns:
            float: Heuristic value
        """
        # Extract components from state
        _, _, _, nearest_gem_dir, _ = state
        
        # Extract components from action
        action_type, dx, dy = action
        
        # Base value
        value = 0
        
        if action_type == "move":
            # Prefer moving towards gems
            if (dx, dy) == nearest_gem_dir:
                value += 5
            
            # Avoid revisiting positions if possible
            new_x, new_y = self.x + dx, self.y + dy
            if (new_x, new_y) in self.visited_positions:
                value -= 2
                
            # Check if move leads to a gem
            if 0 <= new_x < self.maze.size and 0 <= new_y < self.maze.size:
                if self.maze.grid[new_x, new_y] == CELL_TYPES["GEM"]:
                    value += 10
                elif self.maze.grid[new_x, new_y] == CELL_TYPES["TRAP"]:
                    value -= 3
        
        elif action_type == "wall":
            # Place walls strategically to block the player
            value -= 1  # Generally conservative with wall placement
            
        elif action_type == "remove_trap":
            # Only valuable if on a trap
            if self.maze.check_trap(self.x, self.y):
                value += 7
                
        elif action_type == "teleport":
            # Teleport to positions near gems
            teleport_x, teleport_y = dx, dy  # For teleport, dx dy are actual coordinates
            for gem_x, gem_y in self.maze.gem_locations:
                distance = abs(gem_x - teleport_x) + abs(gem_y - teleport_y)
                if distance <= 2:  # Close to a gem
                    value += 8 - distance
        
        # Add some randomness to break ties and encourage exploration
        value += random.uniform(0, 0.1)
        
        return value
    
    def _execute_action(self, action):
        """
        Execute the chosen action and return the reward.
        
        Args:
            action: Action to execute
            
        Returns:
            float: Reward for the action
        """
        action_type, param1, param2 = action
        reward = 0
        
        if action_type == "move":
            dx, dy = param1, param2
            new_x, new_y = self.x + dx, self.y + dy
            
            # Execute the move
            self.x, self.y = new_x, new_y
            
            # Check for gem collection
            if self.maze.collect_gem(self.x, self.y):
                self.gems_collected += 1
                self.score += 10
                reward += 10
            
            # Check for trap
            if self.maze.check_trap(self.x, self.y):
                self.score -= 5
                reward -= 5
                
        elif action_type == "wall" and self.tokens > 0:
            dx, dy = param1, param2
            success = self.place_wall(dx, dy)
            if success:
                self.tokens -= 1
                reward += 2  # Small reward for strategic wall placement
                
        elif action_type == "remove_trap" and self.tokens > 0:
            success = self.remove_trap()
            if success:
                self.tokens -= 1
                reward += 5  # Reward for removing a trap
                
        elif action_type == "teleport" and self.tokens > 0:
            teleport_x, teleport_y = param1, param2
            success = self.teleport(teleport_x, teleport_y)
            if success:
                self.tokens -= 1
                
                # Check for gem collection after teleport
                if self.maze.collect_gem(self.x, self.y):
                    self.gems_collected += 1
                    self.score += 10
                    reward += 10
                    
                # Check for trap after teleport
                if self.maze.check_trap(self.x, self.y):
                    self.score -= 5
                    reward -= 5
        
        # Small penalty for each step to encourage efficiency
        reward -= 0.1
        
        return reward
    
    def _update_q_value(self, state, action, reward, new_state):
        """
        Update the Q-value for the state-action pair.
        
        Args:
            state: Previous state
            action: Action taken
            reward: Reward received
            new_state: New state after action
        """
        # If state-action pair not in Q-table, initialize it
        if (state, action) not in self.q_table:
            self.q_table[(state, action)] = 0
            
        # Get the best Q-value for the new state
        best_next_action = self._choose_best_action(new_state)
        if (new_state, best_next_action) not in self.q_table:
            self.q_table[(new_state, best_next_action)] = self._get_heuristic_value(new_state, best_next_action)
            
        best_next_q = self.q_table[(new_state, best_next_action)]
        
        # Update Q-value using the Q-learning update rule
        current_q = self.q_table[(state, action)]
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * best_next_q - current_q)
        self.q_table[(state, action)] = new_q
    
    def place_wall(self, dx, dy):
        """
        Place a wall adjacent to the AI's position
        
        Args:
            dx (int): X direction from AI
            dy (int): Y direction from AI
            
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
        Remove a trap at the AI's current position
        
        Returns:
            bool: True if trap was removed, False otherwise
        """
        return self.maze.remove_trap(self.x, self.y)
    
    def teleport(self, x, y):
        """
        Teleport the AI to a previously visited position
        
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
        return True
    
    def get_position(self):
        """
        Get the AI's current position
        
        Returns:
            tuple: (x, y) coordinates
        """
        return (self.x, self.y)
    
    def get_score(self):
        """
        Get the AI's current score
        
        Returns:
            int: AI's score
        """
        return self.score
    
    def get_gems_collected(self):
        """
        Get the number of gems collected by the AI
        
        Returns:
            int: Number of gems collected
        """
        return self.gems_collected
    
    def get_tokens_left(self):
        """
        Get the number of tokens the AI has left
        
        Returns:
            int: Number of tokens left
        """
        return self.tokens

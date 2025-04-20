"""
Token System module for managing strategic tokens in the maze game
"""

import pygame
import random

class TokenSystem:
    """
    Manages strategic tokens that can be used by players and AI
    for special actions like placing walls, removing traps, or teleporting.
    """
    def __init__(self, initial_tokens=3):
        """
        Initialize the token system with a set number of tokens.
        
        Args:
            initial_tokens (int): Number of tokens to start with
        """
        self.player_tokens = initial_tokens
        self.ai_tokens = initial_tokens
        self.teleport_selection_active = False
        self.selected_teleport_pos = None
    
    def use_token(self, entity, action_type, target_pos=None):
        """
        Use a token for a specific action.
        
        Args:
            entity: Entity using the token (player or AI)
            action_type (str): Type of action ("wall", "remove_trap", "teleport")
            target_pos (tuple, optional): Target position for certain actions
            
        Returns:
            bool: True if token was used successfully, False otherwise
        """
        # Check if it's a player or AI
        is_player = hasattr(entity, 'maze')  # Simplistic check
        
        # Check if tokens are available
        tokens_available = self.player_tokens if is_player else entity.tokens
        if tokens_available <= 0:
            return False
        
        success = False
        
        if action_type == "wall":
            # For simplicity, place wall in a random adjacent empty cell
            x, y = entity.get_position()
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                success = entity.place_wall(dx, dy)
                if success:
                    break
        
        elif action_type == "remove_trap":
            # Remove trap at current position
            success = entity.remove_trap()
        
        elif action_type == "teleport":
            if target_pos:
                # Teleport to specified position
                success = entity.teleport(target_pos[0], target_pos[1])
            else:
                # For player, activate teleport selection mode
                self.teleport_selection_active = True
                success = True  # Token will be consumed when teleport is executed
                
        # Consume token if action was successful
        if success:
            if is_player:
                self.player_tokens -= 1
            else:
                entity.tokens -= 1
                
        return success
    
    def execute_teleport(self, entity, target_pos):
        """
        Execute a teleport action to a specific position.
        
        Args:
            entity: Entity to teleport
            target_pos (tuple): Target position (x, y)
            
        Returns:
            bool: True if teleport was successful, False otherwise
        """
        success = entity.teleport(target_pos[0], target_pos[1])
        
        if success:
            self.teleport_selection_active = False
            self.selected_teleport_pos = None
            
        return success
    
    def cancel_teleport(self):
        """
        Cancel an active teleport selection.
        
        Returns:
            bool: Always True
        """
        if self.teleport_selection_active:
            self.teleport_selection_active = False
            self.selected_teleport_pos = None
            self.player_tokens += 1  # Refund the token
        
        return True
    
    def select_teleport_position(self, pos):
        """
        Select a position for teleportation.
        
        Args:
            pos (tuple): Position (x, y) to select
            
        Returns:
            bool: True if position was selected, False otherwise
        """
        if self.teleport_selection_active:
            self.selected_teleport_pos = pos
            return True
        return False
    
    def is_teleport_active(self):
        """
        Check if teleport selection is active.
        
        Returns:
            bool: True if teleport selection is active, False otherwise
        """
        return self.teleport_selection_active
    
    def get_selected_teleport_position(self):
        """
        Get the currently selected teleport position.
        
        Returns:
            tuple: Selected position (x, y) or None if none selected
        """
        return self.selected_teleport_pos
    
    def get_player_tokens(self):
        """
        Get the number of tokens the player has.
        
        Returns:
            int: Number of player tokens
        """
        return self.player_tokens
    
    def get_ai_tokens(self):
        """
        Get the number of tokens the AI has.
        
        Returns:
            int: Number of AI tokens
        """
        return self.ai_tokens

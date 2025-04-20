"""
Training module for the AI agent using reinforcement learning
"""

import pygame
import numpy as np
import random
import time
from maze import Maze
from player import Player
from ai_agent import AIAgent
from token_system import TokenSystem
from constants import GRID_SIZE, ROUNDS

class TrainingEnvironment:
    """
    Environment for training the AI agent through simulated games.
    """
    def __init__(self, num_episodes=100):
        """
        Initialize the training environment.
        
        Args:
            num_episodes (int): Number of episodes to train for
        """
        self.num_episodes = num_episodes
        self.maze = None
        self.player = None
        self.ai_agent = None
        self.token_system = None
        
    def train(self):
        """
        Train the AI agent through multiple episodes.
        """
        # Training statistics
        wins = 0
        losses = 0
        ties = 0
        
        print("Starting AI agent training...")
        
        for episode in range(self.num_episodes):
            # Initialize new game components for each episode
            self.maze = Maze(GRID_SIZE)
            self.player = RandomPlayer(0, 0, self.maze)  # Use a random player for training
            self.ai_agent = AIAgent(GRID_SIZE - 1, GRID_SIZE - 1, self.maze)
            self.token_system = TokenSystem(3)
            
            # Play a complete game
            player_turn = True
            current_round = 1
            
            while current_round <= ROUNDS:
                if player_turn:
                    # Random player's turn
                    self.player.make_random_move()
                    player_turn = False
                else:
                    # AI agent's turn
                    self.ai_agent.make_move()
                    player_turn = True
                    current_round += 1
            
            # Determine winner
            player_gems = self.player.get_gems_collected()
            ai_gems = self.ai_agent.get_gems_collected()
            
            if player_gems > ai_gems:
                result = "Loss"
                losses += 1
            elif ai_gems > player_gems:
                result = "Win"
                wins += 1
            else:
                result = "Tie"
                ties += 1
                
            # Print progress
            if (episode + 1) % 10 == 0 or episode == 0:
                print(f"Episode {episode + 1}/{self.num_episodes}, Result: {result}, " 
                      f"AI Score: {self.ai_agent.get_score()}, "
                      f"Player Score: {self.player.get_score()}")
                
        # Print final training statistics
        print("\nTraining Complete!")
        print(f"Episodes: {self.num_episodes}")
        print(f"Wins: {wins} ({wins/self.num_episodes*100:.1f}%)")
        print(f"Losses: {losses} ({losses/self.num_episodes*100:.1f}%)")
        print(f"Ties: {ties} ({ties/self.num_episodes*100:.1f}%)")
        
        # Return the trained AI agent
        return self.ai_agent

class RandomPlayer(Player):
    """
    A random player class for training the AI agent.
    Inherits from Player but makes random moves.
    """
    def make_random_move(self):
        """
        Make a random valid move.
        
        Returns:
            bool: True if move was made, False otherwise
        """
        # Get valid moves
        valid_moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = self.x + dx, self.y + dy
            if self.maze.is_valid_move(new_x, new_y):
                valid_moves.append((dx, dy))
        
        # If no valid moves, try to use a token
        if not valid_moves and random.random() < 0.5:
            # 50% chance to try using a token
            token_actions = ["wall", "remove_trap", "teleport"]
            chosen_action = random.choice(token_actions)
            
            if chosen_action == "wall":
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    if self.place_wall(dx, dy):
                        return True
            
            elif chosen_action == "remove_trap":
                if self.remove_trap():
                    return True
            
            elif chosen_action == "teleport" and len(self.visited_positions) > 1:
                teleport_pos = random.choice(self.visited_positions)
                if teleport_pos != (self.x, self.y):
                    if self.teleport(teleport_pos[0], teleport_pos[1]):
                        return True
        
        # Make a random move if possible
        if valid_moves:
            dx, dy = random.choice(valid_moves)
            return self.move(dx, dy)
            
        return False

if __name__ == "__main__":
    # Run training if this script is executed directly
    env = TrainingEnvironment(num_episodes=100)
    trained_agent = env.train()
    
    print("Training complete. Run main.py to play against the trained AI.")

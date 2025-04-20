#!/usr/bin/env python3
"""
Maze Game: Player vs AI
A 10x10 maze game where a player competes against an AI agent to collect gems.
"""

import os
import pygame
import numpy as np
from maze import Maze
from player import Player
from ai_agent import AIAgent
from token_system import TokenSystem
from ui import UI
from constants import GRID_SIZE, CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, ROUNDS

def main():
    """Main function to start the game"""
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Game: Player vs AI")
    clock = pygame.time.Clock()
    
    # Initialize game components
    maze = Maze(GRID_SIZE)
    player = Player(0, 0, maze)  # Player starts at top-left
    ai_agent = AIAgent(GRID_SIZE - 1, GRID_SIZE - 1, maze)  # AI starts at bottom-right
    token_system = TokenSystem(3)  # Start with 3 tokens
    ui = UI(screen, maze, player, ai_agent, token_system)
    
    # Game state variables
    current_round = 1
    player_turn = True
    game_over = False
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game_over:
                if player_turn:
                    # Handle player movements and actions
                    if event.type == pygame.KEYDOWN:
                        moved = False
                        
                        # Movement controls
                        if event.key == pygame.K_UP:
                            moved = player.move(0, -1)
                        elif event.key == pygame.K_DOWN:
                            moved = player.move(0, 1)
                        elif event.key == pygame.K_LEFT:
                            moved = player.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            moved = player.move(1, 0)
                        
                        # Token usage controls
                        elif event.key == pygame.K_1:  # Place wall
                            if token_system.use_token(player, "wall"):
                                moved = True
                        elif event.key == pygame.K_2:  # Remove trap
                            if token_system.use_token(player, "remove_trap"):
                                moved = True
                        elif event.key == pygame.K_3:  # Teleport
                            if token_system.use_token(player, "teleport"):
                                moved = True
                        
                        # If player moved, switch to AI's turn
                        if moved:
                            player_turn = False
            else:
                # Game over state - restart game on key press
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    # Reset game
                    maze = Maze(GRID_SIZE)
                    player = Player(0, 0, maze)
                    ai_agent = AIAgent(GRID_SIZE - 1, GRID_SIZE - 1, maze)
                    token_system = TokenSystem(3)
                    ui = UI(screen, maze, player, ai_agent, token_system)
                    current_round = 1
                    player_turn = True
                    game_over = False
        
        # AI's turn
        if not player_turn and not game_over:
            ai_agent.make_move()
            player_turn = True
            
            # Check if round is complete (both player and AI have moved)
            if current_round >= ROUNDS:
                game_over = True
            else:
                current_round += 1
        
        # Render game
        screen.fill((0, 0, 0))
        ui.draw(current_round, player_turn, game_over)
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()

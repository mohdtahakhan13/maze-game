"""
UI module for rendering the maze game
"""

import pygame
import os
from constants import CELL_SIZE, GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, CELL_TYPES, COLORS

class UI:
    """
    Handles rendering of the maze game.
    """
    def __init__(self, screen, maze, player, ai_agent, token_system):
        """
        Initialize the UI with game components.
        
        Args:
            screen (pygame.Surface): Pygame screen to render onto
            maze (Maze): Maze object
            player (Player): Player object
            ai_agent (AIAgent): AI agent object
            token_system (TokenSystem): Token system object
        """
        self.screen = screen
        self.maze = maze
        self.player = player
        self.ai_agent = ai_agent
        self.token_system = token_system
        
        # Font initialization
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Load SVG assets using pygame drawing
        self.assets = {
            "wall": self._create_wall_surface(),
            "gem": self._create_gem_surface(),
            "trap": self._create_trap_surface(),
            "player": self._create_player_surface(),
            "agent": self._create_agent_surface()
        }
    
    def _create_wall_surface(self):
        """Create a surface for wall cell"""
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surface.fill(COLORS["WALL"])
        return surface
    
    def _create_gem_surface(self):
        """Create a surface for gem cell"""
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Draw a diamond shape for gem
        points = [
            (CELL_SIZE // 2, 5),
            (CELL_SIZE - 5, CELL_SIZE // 2),
            (CELL_SIZE // 2, CELL_SIZE - 5),
            (5, CELL_SIZE // 2)
        ]
        pygame.draw.polygon(surface, COLORS["GEM"], points)
        # Add some sparkle
        pygame.draw.line(surface, (255, 255, 255), 
                         (CELL_SIZE // 2, 10), 
                         (CELL_SIZE // 2, CELL_SIZE - 10), 2)
        pygame.draw.line(surface, (255, 255, 255), 
                         (10, CELL_SIZE // 2), 
                         (CELL_SIZE - 10, CELL_SIZE // 2), 2)
        return surface
    
    def _create_trap_surface(self):
        """Create a surface for trap cell"""
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Draw a triangle shape for trap
        points = [
            (5, CELL_SIZE - 5),
            (CELL_SIZE - 5, CELL_SIZE - 5),
            (CELL_SIZE // 2, 5)
        ]
        pygame.draw.polygon(surface, COLORS["TRAP"], points)
        return surface
    
    def _create_player_surface(self):
        """Create a surface for player"""
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Draw a circle for player
        pygame.draw.circle(surface, COLORS["PLAYER"], 
                          (CELL_SIZE // 2, CELL_SIZE // 2), 
                          CELL_SIZE // 2 - 5)
        return surface
    
    def _create_agent_surface(self):
        """Create a surface for AI agent"""
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Draw a square for agent
        pygame.draw.rect(surface, COLORS["AI"], 
                        (5, 5, CELL_SIZE - 10, CELL_SIZE - 10))
        return surface
    
    def draw(self, current_round, player_turn, game_over):
        """
        Draw the game state.
        
        Args:
            current_round (int): Current round number
            player_turn (bool): True if it's player's turn, False if AI's turn
            game_over (bool): True if the game is over
        """
        # Clear the screen
        self.screen.fill(COLORS["BACKGROUND"])
        
        # Draw the maze grid
        self._draw_maze()
        
        # Draw player and AI
        self._draw_entities()
        
        # Draw UI elements (scoreboard, tokens, etc.)
        self._draw_ui(current_round, player_turn, game_over)
    
    def _draw_maze(self):
        """Draw the maze grid with all cells"""
        grid = self.maze.get_state()
        
        for x in range(self.maze.size):
            for y in range(self.maze.size):
                # Calculate pixel position
                pos_x = x * CELL_SIZE
                pos_y = y * CELL_SIZE
                
                # Draw cell background
                pygame.draw.rect(self.screen, COLORS["GRID_LINE"], 
                                (pos_x, pos_y, CELL_SIZE, CELL_SIZE), 1)
                
                # Draw cell contents based on type
                cell_type = grid[x, y]
                
                if cell_type == CELL_TYPES["WALL"]:
                    self.screen.blit(self.assets["wall"], (pos_x, pos_y))
                elif cell_type == CELL_TYPES["GEM"]:
                    self.screen.blit(self.assets["gem"], (pos_x, pos_y))
                elif cell_type == CELL_TYPES["TRAP"]:
                    self.screen.blit(self.assets["trap"], (pos_x, pos_y))
                
                # Mark visited cells
                if self.maze.visited_player[x, y]:
                    pygame.draw.rect(self.screen, COLORS["PLAYER_VISITED"], 
                                    (pos_x + 2, pos_y + 2, CELL_SIZE - 4, CELL_SIZE - 4), 1)
                if self.maze.visited_ai[x, y]:
                    pygame.draw.rect(self.screen, COLORS["AI_VISITED"], 
                                    (pos_x + 4, pos_y + 4, CELL_SIZE - 8, CELL_SIZE - 8), 1)
    
    def _draw_entities(self):
        """Draw the player and AI agent"""
        # Draw player
        player_x, player_y = self.player.get_position()
        player_pos_x = player_x * CELL_SIZE
        player_pos_y = player_y * CELL_SIZE
        self.screen.blit(self.assets["player"], (player_pos_x, player_pos_y))
        
        # Draw AI agent
        ai_x, ai_y = self.ai_agent.get_position()
        ai_pos_x = ai_x * CELL_SIZE
        ai_pos_y = ai_y * CELL_SIZE
        self.screen.blit(self.assets["agent"], (ai_pos_x, ai_pos_y))
    
    def _draw_ui(self, current_round, player_turn, game_over):
        """Draw UI elements like scoreboard and turn indicator"""
        # Game area boundary
        pygame.draw.rect(self.screen, COLORS["UI_BORDER"], 
                        (0, 0, GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE), 2)
        
        # Scoreboard background
        scoreboard_rect = pygame.Rect(GRID_SIZE * CELL_SIZE + 10, 10, 
                                     SCREEN_WIDTH - (GRID_SIZE * CELL_SIZE + 20), 
                                     SCREEN_HEIGHT - 20)
        pygame.draw.rect(self.screen, COLORS["UI_BACKGROUND"], scoreboard_rect)
        pygame.draw.rect(self.screen, COLORS["UI_BORDER"], scoreboard_rect, 2)
        
        # Round info
        round_text = self.font.render(f"Round: {current_round}", True, COLORS["TEXT"])
        self.screen.blit(round_text, (scoreboard_rect.left + 10, scoreboard_rect.top + 10))
        
        # Turn indicator
        turn_color = COLORS["PLAYER"] if player_turn else COLORS["AI"]
        turn_text = self.font.render(f"Turn: {'Player' if player_turn else 'AI'}", 
                                   True, turn_color)
        self.screen.blit(turn_text, (scoreboard_rect.left + 10, scoreboard_rect.top + 50))
        
        # Scores
        player_score_text = self.font.render(f"Player Score: {self.player.get_score()}", 
                                           True, COLORS["PLAYER"])
        self.screen.blit(player_score_text, 
                       (scoreboard_rect.left + 10, scoreboard_rect.top + 90))
        
        ai_score_text = self.font.render(f"AI Score: {self.ai_agent.get_score()}", 
                                       True, COLORS["AI"])
        self.screen.blit(ai_score_text, 
                       (scoreboard_rect.left + 10, scoreboard_rect.top + 130))
        
        # Gems collected
        player_gems_text = self.font.render(f"Player Gems: {self.player.get_gems_collected()}", 
                                          True, COLORS["GEM"])
        self.screen.blit(player_gems_text, 
                       (scoreboard_rect.left + 10, scoreboard_rect.top + 170))
        
        ai_gems_text = self.font.render(f"AI Gems: {self.ai_agent.get_gems_collected()}", 
                                      True, COLORS["GEM"])
        self.screen.blit(ai_gems_text, 
                       (scoreboard_rect.left + 10, scoreboard_rect.top + 210))
        
        # Tokens
        player_tokens_text = self.font.render(f"Player Tokens: {self.token_system.get_player_tokens()}", 
                                            True, COLORS["TOKEN"])
        self.screen.blit(player_tokens_text, 
                       (scoreboard_rect.left + 10, scoreboard_rect.top + 250))
        
        ai_tokens_text = self.font.render(f"AI Tokens: {self.ai_agent.get_tokens_left()}", 
                                        True, COLORS["TOKEN"])
        self.screen.blit(ai_tokens_text, 
                       (scoreboard_rect.left + 10, scoreboard_rect.top + 290))
        
        # Controls help
        help_y = scoreboard_rect.top + 330
        controls_title = self.small_font.render("Controls:", True, COLORS["TEXT"])
        self.screen.blit(controls_title, (scoreboard_rect.left + 10, help_y))
        
        controls = [
            "Arrow Keys: Move",
            "1: Place Wall",
            "2: Remove Trap",
            "3: Teleport",
            "R: Restart (after game over)"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, COLORS["TEXT"])
            self.screen.blit(control_text, 
                           (scoreboard_rect.left + 20, help_y + 30 + i * 25))
        
        # Game over screen
        if game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Black with alpha
            self.screen.blit(overlay, (0, 0))
            
            # Game over text
            game_over_text = self.font.render("GAME OVER", True, COLORS["TEXT"])
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            # Winner announcement
            player_gems = self.player.get_gems_collected()
            ai_gems = self.ai_agent.get_gems_collected()
            
            if player_gems > ai_gems:
                winner_text = self.font.render("Player Wins!", True, COLORS["PLAYER"])
            elif ai_gems > player_gems:
                winner_text = self.font.render("AI Wins!", True, COLORS["AI"])
            else:
                winner_text = self.font.render("It's a Tie!", True, COLORS["TEXT"])
                
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(winner_text, winner_rect)
            
            # Restart prompt
            restart_text = self.font.render("Press R to Restart", True, COLORS["TEXT"])
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)

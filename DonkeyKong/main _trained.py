import pygame
import sys

import os
import torch

from environment import Environment

from human_agent import HumanAgent

from character import Character

from AI_agent import DQN_Agent

import config


def main():
    num = 1
    pygame.init()

    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Donkey Kong PyGame Recreation")
   

    # Create environment
    env = Environment(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

    # Create player character
    player_x = config.SCREEN_WIDTH - config.PLAYER_SPAWN_X_OFFSET
    player_y = config.SCREEN_HEIGHT - config.PLAYER_SPAWN_Y_OFFSET
    character = Character(player_x, player_y)
    env.add_player(character)

    # --- SELECT AGENT HERE ---
    #player_agent = HumanAgent()
    # --- SELECT MODE ---
    MODE = "AI"   # "human" or "ai"

    if MODE == "human":
        player_agent = HumanAgent()
    else:
        player_agent = DQN_Agent()
        
        if os.path.exists(f"Data/dqn_model_{num}.pth"):
            player_agent.model.load_state_dict(torch.load(f"Data/dqn_model_{num}.pth"))
            player_agent.target_model.load_state_dict(torch.load(f"Data/dqn_target_model_{num}.pth"))
            player_agent.epsilon = 0   # Disable exploration
            player_agent.model.eval()  # Set evaluation mode
            print("Loaded trained model!")

    
    clock = pygame.time.Clock()

    running = True

    while running:

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # --- LOGIC UPDATE ---

        current_state = env.state_to_tensor(env.get_state())

        action = player_agent.get_action(events=events, state=current_state)

        next_state, reward, done = env.step(action)

        # --- RENDERING ---
        screen.fill((0, 0, 0))
        env.render(screen)
        

        font = pygame.font.SysFont('Arial', 25)

        score_text = font.render(f'Score: {env.score}', True, (255, 255, 255))
        lives_text = font.render(f'Lives: {env.lives}', True, (255, 255, 255))

        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))

        # --- GAME OVER / RESTART ---
        if done:

            game_over_font = pygame.font.SysFont('Arial', 50)
            game_over_text = game_over_font.render('GAME OVER', True, (255, 0, 0))
            screen.blit(game_over_text, (config.SCREEN_WIDTH // 2 - 150, config.SCREEN_HEIGHT // 2 - 25))

            restart_font = pygame.font.SysFont('Arial', 25)
            restart_text = restart_font.render('Press R to Restart', True, (255, 255, 255))
            screen.blit(restart_text, (config.SCREEN_WIDTH // 2 - 100, config.SCREEN_HEIGHT // 2 + 30))

            pygame.display.flip()

            waiting_for_restart = True

            while waiting_for_restart:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting_for_restart = False

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:

                        env = Environment(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
                        character = Character(config.SCREEN_WIDTH - config.PLAYER_SPAWN_X_OFFSET, config.SCREEN_HEIGHT - config.PLAYER_SPAWN_Y_OFFSET)
                        env.add_player(character)

                        waiting_for_restart = False

        pygame.display.flip()

       
        clock.tick(60)

    

    pygame.quit()
    sys.exit() 

if __name__ == "__main__":
    main()

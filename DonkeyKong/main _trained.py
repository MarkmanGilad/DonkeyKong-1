import pygame
import sys

import os
import torch

from environment import Environment

from human_agent import HumanAgent

from character import Character

from AI_agent import DQN_Agent
  


def main():
    num = 1
    pygame.init()

    screen_width = 1500
    screen_height = 820
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Donkey Kong PyGame Recreation")
   

    # Create environment
    env = Environment(screen_width, screen_height)

    # Create player character
    character = Character(50, screen_height - 60)
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
            screen.blit(game_over_text, (screen_width // 2 - 150, screen_height // 2 - 25))

            restart_font = pygame.font.SysFont('Arial', 25)
            restart_text = restart_font.render('Press R to Restart', True, (255, 255, 255))
            screen.blit(restart_text, (screen_width // 2 - 100, screen_height // 2 + 30))

            pygame.display.flip()

            waiting_for_restart = True

            while waiting_for_restart:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting_for_restart = False

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:

                        env = Environment(screen_width, screen_height)
                        character = Character(50, screen_height - 60)
                        env.add_player(character)

                        waiting_for_restart = False

        pygame.display.flip()

       
        clock.tick(60)

    

    pygame.quit()
    sys.exit() 

if __name__ == "__main__":
    main()
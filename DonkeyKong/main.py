import wandb
import pygame
import sys

import os
import torch

from environment import Environment

from human_agent import HumanAgent

from character import Character

from AI_agent import DQN_Agent
  


def main():

    pygame.init()

    num = 2
    screen_width = 1500
    screen_height = 820
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Donkey Kong PyGame Recreation")

    # --- STATS VARIABLES ---
    episode_count = 0
    episode_reward = 0
    reward_history = []
    win_history = []

    # Create environment
    env = Environment(screen_width, screen_height)

    # Create player character
    character = Character(50, screen_height - 60)
    env.add_player(character)

    # --- SELECT AGENT HERE ---
    player_agent = HumanAgent()

    # --- W&B INIT ---
    wandb.init(
        project="donkey-kong-dqn",
        id=f'donkey-kong {num}',
        config={
            "name": f'donkey-kong {num}',
            "screen_width": screen_width,
            "screen_height": screen_height,
            "model_loaded": os.path.exists("dqn_model.pth"),
            "initial_epsilon": player_agent.epsilon if hasattr(player_agent, "epsilon") else None,
            "Model": str(player_agent.model) if hasattr(player_agent, "model") else None
        }
    )

    # --- LOAD SAVED MODEL IF EXISTS ---
    if os.path.exists("dqn_model.pth"):
        player_agent.model.load_state_dict(torch.load("dqn_model.pth"))
        player_agent.target_model.load_state_dict(torch.load("dqn_target_model.pth"))

        if os.path.exists("epsilon.pth"):
            player_agent.epsilon = torch.load("epsilon.pth")

        print("✅ Loaded saved model!")
    else:
        print("🆕 No saved model found, starting fresh.")

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

        episode_reward += reward

        # --- EPISODE END ---
        if done:
            episode_count += 1
            reward_history.append(episode_reward)
            win_history.append(1 if env.score > 900 else 0)

            # --- Log metrics to wandb ---
            win_rate = (sum(win_history) / len(win_history)) * 100 if len(win_history) > 0 else 0
            avg_reward = sum(reward_history) / len(reward_history) if len(reward_history) > 0 else 0

            wandb.log({
                "episode_reward": episode_reward,
                "win_rate": win_rate,
                "avg_reward": avg_reward,
                "score": env.score
            })

            # --- SAVE MODEL EVERY 10 EPISODES ---
            if episode_count % 10 == 0:
                torch.save(player_agent.model.state_dict(), "dqn_model.pth")
                torch.save(player_agent.target_model.state_dict(), "dqn_target_model.pth")
                torch.save(player_agent.epsilon, "epsilon.pth")
                print("✅ Model saved!")

            # Reset trackers
            episode_reward = 0
            reward_history = []
            win_history = []

        # --- TRAINING ---
        if isinstance(player_agent, DQN_Agent):
            player_agent.remember(current_state, action, reward, next_state, done)
            player_agent.train()

        # --- RENDERING ---
        screen.fill((0, 0, 0))
        env.render(screen)

        font = pygame.font.SysFont('Arial', 25)

        score_text = font.render(f'Score: {env.score}', True, (255, 255, 255))
        lives_text = font.render(f'Lives: {env.lives}', True, (255, 255, 255))

        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))

        # --- GAME OVER / RESTART ---
        if env.game_over:

            if isinstance(player_agent, DQN_Agent):

                print(f"Game Over. Score: {env.score}. Restarting...")

                env = Environment(screen_width, screen_height)
                character = Character(50, screen_height - 60)
                env.add_player(character)

            else:

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

        if isinstance(player_agent, DQN_Agent):
            clock.tick(0)
        else:
            clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
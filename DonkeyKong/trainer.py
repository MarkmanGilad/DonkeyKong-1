import pygame
import torch
import os
import wandb

from environment import Environment
from character import Character
from AI_agent import DQN_Agent
from config import *


def main():
    num = 22
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"Donkey Kong Trainer #{num}")

    agent = DQN_Agent()

    best_score = 0

    wandb.init(
        project=WANDB_PROJECT,
        name=f"{WANDB_PROJECT}_{num}",
        id=f"{WANDB_PROJECT}_{num}",
        config={
            "learning_rate": agent.learning_rate,
            "gamma": agent.gamma,
            "batch_size": agent.batch_size,
            "epsilon_decay_steps": EPSILON_DECAY_STEPS
        }
    )

    # ✅ Buffers for 100-episode averaging
    reward_buffer = []
    score_buffer = []
    platform_buffer = []

    for episode in range(EPISODES):

        env = Environment(SCREEN_WIDTH, SCREEN_HEIGHT)
        player_x = SCREEN_WIDTH - PLAYER_SPAWN_X_OFFSET
        player_y = SCREEN_HEIGHT - PLAYER_SPAWN_Y_OFFSET
        character = Character(player_x, player_y)
        env.add_player(character)

        state = env.state_to_tensor(env.get_state())
        total_reward = 0
        done = False
        step = 0
        episode_losses = []
        while not done:
            step += 1
            print(step, end="\r")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            action = agent.get_action(events=[], state=state)
            next_state, reward, done = env.step(action)

            agent.remember(state, action, reward, next_state, done)
            loss = agent.train()
            if loss is not None:
                episode_losses.append(loss)

            state = next_state
            total_reward += reward
            agent.epsilon = max(EPSILON_MIN, EPSILON_START - (agent.train_step_counter * (EPSILON_START - EPSILON_MIN) / EPSILON_DECAY_STEPS))
            if step > MAX_STEPS_PER_EPISODE:
                done = True
                agent.remember(state, action, reward, next_state, done)
                break
            screen.fill((0, 0, 0))
            env.render(screen)
            pygame.display.flip()

        best_score = max(best_score, env.score)

        print(f"#{num} Ep {episode} | Steps: {step} | Platform: {env.player.current_platform_number} | Score: {env.score} | Reward: {total_reward:.1f} | Epsilon: {agent.epsilon:.4f} | Best: {best_score}")

        avg_loss = sum(episode_losses) / len(episode_losses) if episode_losses else 0

        wandb.log({
            "reward": total_reward,
            "score": env.score,
            "loss": avg_loss,
        })

        if env.score >= best_score:
            best_score = env.score
            torch.save(agent.model.state_dict(), f"Data/best_dqn_model_{num}.pth")
            torch.save(agent.target_model.state_dict(), f"Data/best_dqn_target_model_{num}.pth")
            torch.save(agent.epsilon, f"Data/best_epsilon_{num}.pth")
            print("New Best Model Saved")

    pygame.quit()


if __name__ == "__main__":
    main()

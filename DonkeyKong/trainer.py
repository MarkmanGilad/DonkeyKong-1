import pygame
import torch
import os
import wandb

from environment import Environment
from character import Character
from AI_agent import DQN_Agent
from config import *


def main():
    num = 100
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"Donkey Kong Trainer #{num}")

    agent = DQN_Agent()

    best_score = float('-inf')

    wandb.init(
        project=WANDB_PROJECT,
        name=f"{WANDB_PROJECT}_{num}",
        id=f"{WANDB_PROJECT}_{num}",
        config={
            # Network
            "state_dim": STATE_DIM,
            "action_dim": ACTION_DIM,
            "hidden_layer_1": HIDDEN_LAYER_1,
            "hidden_layer_2": HIDDEN_LAYER_2,
            # Training
            "learning_rate": agent.learning_rate,
            "lr_milestones": LR_MILESTONES,
            "lr_gamma": LR_GAMMA,
            "gamma": agent.gamma,
            "batch_size": agent.batch_size,
            "memory_size": MEMORY_SIZE,
            "target_update_freq": TARGET_UPDATE_FREQ,
            # Exploration
            "epsilon_start": EPSILON_START,
            "epsilon_mid": EPSILON_MID,
            "epsilon_min": EPSILON_MIN,
            "epsilon_decay_steps_1": EPSILON_DECAY_STEPS_1,
            "epsilon_decay_steps_2": EPSILON_DECAY_STEPS_2,
            # Trainer
            "episodes": EPISODES,
            "max_steps_per_episode": MAX_STEPS_PER_EPISODE,
            # Physics
            "player_speed": PLAYER_SPEED,
            "player_climb_speed": PLAYER_CLIMB_SPEED,
            "barrel_speed": BARREL_SPEED,
            "barrel_interval_min": BARREL_INTERVAL_MIN,
            "barrel_interval_max": BARREL_INTERVAL_MAX,
            "barrels_enabled": BARRELS_ENABLED,
            "gravity": GRAVITY,
            "player_gravity": PLAYER_GRAVITY,
            "jump_power": PLAYER_JUMP_POWER,
            "max_fall_speed": MAX_FALL_SPEED,
            # Rewards
            "reward_climb_up": REWARD_CLIMB_UP_MULTIPLIER,
            "reward_toward_ladder": REWARD_TOWARD_LADDER,
            "reward_away_ladder": REWARD_AWAY_LADDER,
            "reward_toward_princess": REWARD_TOWARD_PRINCESS,
            "reward_away_princess": REWARD_AWAY_PRINCESS,
            "reward_jump_close": REWARD_JUMP_CLOSE,
            "reward_jump_irrelevant": REWARD_JUMP_IRRELEVANT,
            "reward_jump_close_threshold": REWARD_JUMP_CLOSE_THRESHOLD,
            "reward_death": REWARD_DEATH,
            "reward_barrel_hit": REWARD_BARREL_HIT,
            "reward_win": REWARD_WIN,
            "reward_exit_ladder": REWARD_EXIT_LADDER,
            "reward_fall_penalty": REWARD_FALL_PENALTY,
            # Game
            "initial_lives": INITIAL_LIVES,
            "max_barrel_hits": MAX_BARREL_HITS,
            "barrel_hit_score_penalty": BARREL_HIT_SCORE_PENALTY,
            "win_score": WIN_SCORE,
            "platform_score": PLATFORM_SCORE,
        }
    )

    player_x = SCREEN_WIDTH - PLAYER_SPAWN_X_OFFSET
    player_y = SCREEN_HEIGHT - PLAYER_SPAWN_Y_OFFSET
    character = Character(player_x, player_y)

    for episode in range(EPISODES):

        env = Environment(SCREEN_WIDTH, SCREEN_HEIGHT)
        character.reset(player_x, player_y)
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
            # Two-phase linear epsilon decay
            s = agent.train_step_counter
            if s <= EPSILON_DECAY_STEPS_1:
                agent.epsilon = EPSILON_START - s * (EPSILON_START - EPSILON_MID) / EPSILON_DECAY_STEPS_1
            else:
                agent.epsilon = max(EPSILON_MIN, EPSILON_MID - (s - EPSILON_DECAY_STEPS_1) * (EPSILON_MID - EPSILON_MIN) / EPSILON_DECAY_STEPS_2)
            if step > MAX_STEPS_PER_EPISODE:
                done = True
                agent.remember(state, action, reward, next_state, done)
                break
            screen.fill((0, 0, 0))
            env.render(screen, episode=episode, epsilon=agent.epsilon, best_score=best_score, total_reward=total_reward, steps=step)
            pygame.display.flip()

        print(f"#{num} Ep {episode} | Steps: {step} | Platforms: {env.total_platforms_reached} | Score: {env.score} | Reward: {total_reward:.1f} | Epsilon: {agent.epsilon:.4f} | Best Score: {best_score}")

        avg_loss = sum(episode_losses) / len(episode_losses) if episode_losses else 0

        wandb.log({
            "reward": total_reward,
            "score": env.score,
            "loss": avg_loss,
            "epsilon": agent.epsilon,
            "learning_rate": agent.scheduler.get_last_lr()[0],
            "survival_steps": step,
            "platforms_reached": env.total_platforms_reached,
            "hit_rate": (env.barrel_hits / step) * 1000 if step > 0 else 0,
        })

        if env.score > best_score:
            best_score = env.score
            torch.save(agent.model.state_dict(), f"Data/best_dqn_model_{num}.pth")
            torch.save(agent.target_model.state_dict(), f"Data/best_dqn_target_model_{num}.pth")
            torch.save(agent.epsilon, f"Data/best_epsilon_{num}.pth")
            print("New Best Model Saved")

    pygame.quit()


if __name__ == "__main__":
    main()

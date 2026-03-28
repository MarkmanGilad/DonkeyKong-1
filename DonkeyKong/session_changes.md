# Session Changes Summary (March 28, 2026)

## Bug Fixes

### 1. Double Normalization
- **File:** `AI_agent.py`, `environment.py`
- **Problem:** `state_to_tensor()` normalized indices [1,5,6,7,9,10] by `screen_width`, then `train()` normalized the same indices again by `NORM_DIVISOR` (1500.0). Training saw double-normalized values but action selection saw single-normalized values.
- **Fix:** Removed normalization from `train()`. All normalization now happens once in `state_to_tensor()`.
- **Cleanup:** Removed `NORM_INDICES` and `NORM_DIVISOR` from `config.py`.

### 2. REWARD_AWAY_LADDER Sign Bug
- **File:** `config.py`
- **Problem:** `REWARD_AWAY_LADDER = -3.0` used with `reward -= (-3.0)` = `reward += 3.0`. Moving away from ladder was rewarded instead of penalized.
- **Fix:** Changed to positive value (`3.0`) so `reward -= 3.0` correctly penalizes.
- **Impact:** Agent was stuck on platform 1 because both directions gave +3 reward for ladder distance.

### 3. REWARD_JUMP_IRRELEVANT / REWARD_JUMP_DISTANT Sign Bug
- **File:** `config.py`
- **Problem:** Same double-negative issue. `-1.0` and `-0.5` used with `reward -=` gave positive rewards for bad jumps.
- **Fix:** Changed to positive values (`1.0`, `0.5`).

### 4. barrel_dx Default Value
- **File:** `environment.py`
- **Problem:** Default `barrel_dx = 9999` normalized to ~6.67 (far outside [-1, 1] range), distorting the network.
- **Fix:** Changed default to `0`.

### 5. Jump Reward Without Barrels
- **File:** `environment.py`
- **Problem:** With `barrel_dx = 0` (no barrel), every jump hit the "close barrel" branch and got +0.5 reward for dodging nothing.
- **Fix:** Barrel jump reward logic skipped entirely when `barrel_dx == 0`.

### 6. Timeout Episodes: done=False
- **File:** `trainer.py`
- **Problem:** When `MAX_STEPS_PER_EPISODE` was reached, the loop broke without setting `done=True`. Last transition stored with `done=False`, causing DQN to incorrectly add future Q-values.
- **Fix:** Set `done=True` and re-store the final transition before breaking.

### 7. Princess Reward on Wrong Platform
- **File:** `environment.py`
- **Problem:** Distance-to-princess reward applied on every platform, conflicting with ladder direction on lower platforms.
- **Fix:** Gated with `same_platform_princess == 1`.

## Features Added

### 8. Barrels Toggle
- **File:** `config.py`, `environment.py`
- Added `BARRELS_ENABLED = True/False` constant to disable barrel spawning for isolated climbing training.

### 9. Platform Score
- **File:** `config.py`, `environment.py`
- Added `PLATFORM_SCORE = 100` — player gets 100 points per new platform reached.
- `highest_platform` tracker resets on princess collision.

### 10. Loss Logging to wandb
- **File:** `AI_agent.py`, `trainer.py`
- `train()` now returns `loss.item()` (or `None`).
- Trainer accumulates per-episode average loss and logs to wandb.

### 11. Epsilon Decay Per Step → Linear Decay
- **File:** `config.py`, `trainer.py`, `AI_agent.py`
- Moved epsilon decay from per-episode to per-step inside the training loop.
- Changed from exponential decay (`epsilon *= 0.9999`) to **linear decay** over `EPSILON_DECAY_STEPS = 10000` steps.
- Formula: `epsilon = EPSILON_START - (step × (EPSILON_START - EPSILON_MIN) / EPSILON_DECAY_STEPS)`
- Removed `self.epsilon_decay` attribute from `DQN_Agent`.
- Uses config constants (`EPSILON_MIN`, `EPSILON_START`, `EPSILON_DECAY_STEPS`) directly.

### 12. Improved Training Print
- **File:** `trainer.py`
- Print now shows: `#{num} Ep {episode} | Steps: {step} | Platform: {plat} | Score: {score} | Reward: {reward} | Epsilon: {eps} | Best: {best}`

## Refactoring

### 13. Reward Values Scaled Down
- **File:** `config.py`
- All reward values reduced by ~10x to lower loss magnitude. Relative proportions preserved.

### 14. Trainer Import Style
- **File:** `trainer.py`
- Changed from `import config` / `config.X` to `from config import *` with direct constant names.

### 15. Wandb Logging Simplified
- **File:** `trainer.py`
- Removed rolling average buffers (`avg_reward`, `avg_score`, `avg_platform`).
- Wandb logs only: `reward`, `score`, `loss`.

### 16. Jump Thresholds Adjusted to Match Physics
- **File:** `config.py`
- **Problem:** Old thresholds (close ≤ 80px, distant ≤ 200px) didn't match actual jump physics. At barrel_speed=2 px/frame, 80px = 40 frames to arrive but jump only lasts ~25 frames — player would land and get hit.
- **Fix:** `REWARD_JUMP_CLOSE_THRESHOLD`: 80 → **50** (barrel arrives in 25 frames = jump duration). `REWARD_JUMP_DISTANT_THRESHOLD`: 200 → **100** (barrel arrives in 50 frames — too early to jump).

### 17. Upgraded DQN → DDQN (Double DQN)
- **File:** `AI_agent.py`
- **Problem:** Standard DQN overestimates Q-values because same network selects and evaluates actions.
- **Fix:** Main network selects best action (`argmax`), target network evaluates Q-value at that action.
- Code: `best_actions = self.model(next_state_batch).argmax(1)` → `self.target_model(...).gather(1, best_actions.unsqueeze(1))`

### 18. Training Number in Window Caption
- **File:** `trainer.py`
- Screen caption now shows `"Donkey Kong Trainer #N"` where N is the training run number.
- Non-training modes (`main.py`, `main _trained.py`) keep the generic caption.

### 19. barrel_dx Platform-Aware Filtering
- **File:** `environment.py`
- **Problem:** `barrel_dx` picked the closest barrel facing the player from ANY platform. Agent reacted to barrels on completely different levels.
- **Fix (not on ladder):** Only barrels on the **same platform** as the player AND facing the player are considered.
- **Fix (on ladder):** Only barrels on the **platform above** (the one being climbed to) AND heading toward the **ladder top** are considered. Uses `get_ladder_under_center()` to find the ladder's x position.

### 20. Single Life — Death Ends Episode
- **File:** `config.py`, `environment.py`
- **Problem:** With 3 lives, the agent respawned after dying and kept accumulating reward. Death penalty (−10) was negligible vs ~2800 total reward, so the agent had no incentive to dodge barrels.
- **Fix:** `INITIAL_LIVES = 1`. Any death (barrel collision or fall-off) immediately sets `game_over = True`. Removed respawn logic from death handlers.
- **Impact:** Death penalty now terminates the episode, making barrel avoidance critical for earning further rewards.

### 21. Epsilon Decay Steps Increased
- **File:** `config.py`
- **Problem:** `EPSILON_DECAY_STEPS = 10000` caused epsilon to hit minimum after ~4 episodes (~2500 steps each).
- **Fix:** Increased to `100000` — epsilon decays linearly over ~40 episodes.

## Documentation Created
- `state_action_reference.md` — State dictionary, tensor normalization, and action space reference.
- `reward_reference.md` — Complete reward breakdown with config values and flow.
- `session_changes.md` — This file.

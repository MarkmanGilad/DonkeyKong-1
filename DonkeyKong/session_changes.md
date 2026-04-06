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

## Session: April 6, 2026

### 10. PLAYER_JUMP_POWER: 10 → 14
- **File:** `config.py`
- **Problem:** With jump power 10, max height = 63px, giving only 19 "safe frames" above the barrel. A barrel (20px wide at 2px/frame) takes 25 frames to cross the player's hitbox. Since 19 < 25, **standing jumps could never clear a barrel** — the player always got clipped at the edge. The agent learned that jumping near barrels is bad (+5 jump − 10 hit = −5 net).
- **Fix:** Increased `PLAYER_JUMP_POWER` to 14. Max height = 122px, giving 31 safe frames > 25 crossing frames (margin of +6). Still safe for platforms (122px < 140px gap between platforms).
- **Impact:** Standing jumps (action 5) and directional jumps (actions 6/7) can now clear barrels. Existing reward signals (+5 close jump, −10 hit) are sufficient to teach dodging.

### 11. Jump Reward Thresholds Aligned to Physics
- **File:** `config.py`
- **Problem:** `REWARD_JUMP_CLOSE_THRESHOLD = 50` and `REWARD_JUMP_DISTANT_THRESHOLD = 100` did not match actual dodge physics. With jump power 14, gravity 0.8, player 30px, barrel 20px at 2px/frame:
  - Standing jump (action 5): player is above barrel (>20px) for frames 2–32 (31 frames). Barrel overlap lasts 25 frames (50px / 2px/frame). The dodge window is |barrel_dx| ∈ [29, 39] — only works within ~40px.
  - At 40–50px (old "close" zone), standing jumps fail — barrel reaches overlap after the player has landed. Agent got +5 for jumping then −10 for the hit, learning to avoid jumping near barrels.
  - Directional jumps (actions 6/7, relative speed 5px/frame) have a wider window up to ~135px, but the reward should focus on the range where jumping is critical.
- **Fix:** `REWARD_JUMP_CLOSE_THRESHOLD`: 50 → 40, `REWARD_JUMP_DISTANT_THRESHOLD`: 100 → 70.
  - **≤ 40px (+5):** Standing jump dodge window — any jump type works here.
  - **40–70px (−0.5):** Mild penalty — only directional jumps work, discourage reflexive jumping.
  - **> 70px (−1.0):** Too far — no jump type is needed.
  - **No-jump penalty (−2/frame):** Also uses the 40px threshold — penalizes only when jumping is actually needed.
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

### 22. No-Jump Penalty When Barrel Is Close
- **File:** `config.py`, `environment.py`
- **Problem:** Agent had no negative signal for standing still while a barrel was about to hit it. The one-time jump reward was too sparse.
- **Fix:** Added `REWARD_NO_JUMP_PENALTY = 0.5`. Every frame the agent is on the ground (not jumping, not in air, not on ladder) with a barrel within 50px, it gets −0.5. Fires continuously, creating mounting pressure to jump.

### 23. Comprehensive wandb Config Logging
- **File:** `trainer.py`
- **Problem:** wandb config only logged 4 parameters (learning_rate, gamma, batch_size, epsilon_decay_steps). Most hyperparameters were untracked.
- **Fix:** Now logs all key parameters: network architecture, training hyperparameters, exploration schedule, physics constants, all reward values/thresholds, and game settings. Makes every run fully reproducible from the wandb dashboard.

### 24. Fixed Ladder Grab/Exit Reward Farming Exploit
- **File:** `environment.py`
- **Problem:** Agent oscillated at ladder top: exit ladder (+4.0) → step back, grab ladder (+1.0) → repeat = +2.5/frame average. This was 8× more rewarding than walking toward the next ladder (+0.3/frame).
- **Fix (EXIT_LADDER):** Now only fires when `current_platform_number > prev_platform` — player must actually reach a higher platform.
- **Fix (GRAB_LADDER):** Tracks `_last_exited_ladder` and won't reward re-grabbing the same ladder just exited.

### 25. Fixed Zero-Gravity Ladder Float Exploit
- **File:** `environment.py`
- **Problem:** When `on_ladder=True`, no gravity applied. If the agent pressed action 3 (climb up) past the ladder top, the condition `if not ladder_under_center and action != 3 and action != 4` kept them in ladder mode. The agent floated upward in zero gravity, skipping platforms.
- **Fix:** Removed the `action != 3 and action != 4` condition. Player now detaches from ladder as soon as `ladder_under_center` is `None`, regardless of action.

### 26. Asymmetric Ladder Distance Rewards
- **File:** `config.py`
- **Problem:** Toward ladder (+0.3) and away from ladder (−0.3) were symmetric. Oscillating left-right near a ladder netted 0, while avoiding the idle penalty — making oscillation free.
- **Fix:** `REWARD_AWAY_LADDER` increased to 0.4. One oscillation cycle now costs −0.1 net.

### 27. Barrel Jump Rewards Increased
- **File:** `config.py`
- **Problem:** `REWARD_JUMP_CLOSE = 0.5` and `REWARD_NO_JUMP_PENALTY = 0.5/frame` were negligible compared to death (−10). Agent had no incentive to learn jumping.
- **Fix:** `REWARD_JUMP_CLOSE`: 0.5 → **5.0** (half of death penalty). `REWARD_NO_JUMP_PENALTY`: 0.5 → **2.0/frame** (over ~25 frames = −50, 5× worse than death). Not jumping when a barrel is close is now treated as catastrophic.

### 28. Penalty for Jumping With No Barrel
- **File:** `environment.py`
- **Problem:** When `barrel_dx == 0` (no threatening barrel), jump reward was skipped entirely — jumping was free. Agent learned to jump constantly.
- **Fix:** Jumping with no barrel now gets `−1.0` (`REWARD_JUMP_IRRELEVANT`), same as jumping when a barrel is far away.

### 29. Barrel Hit Lives System (10 Hits Before Death)
- **Files:** `config.py`, `environment.py`
- **Problem:** With `INITIAL_LIVES = 1`, every barrel hit ended the episode instantly. Agent had very few opportunities to learn jumping.
- **Fix:** Added `MAX_BARREL_HITS = 10`. Barrel collision increments `barrel_hits` counter; `game_over` only when hits reach 10. Player continues from the same position after each hit. `REWARD_DEATH` still applied on every hit for reward shaping. Fall-off-platform death remains instant.

### 30. Score Penalty for Barrel Hits
- **Files:** `config.py`, `environment.py`
- **Problem:** Score didn't reflect barrel avoidance skill — an agent that dodges barrels scored the same as one that gets hit.
- **Fix:** Added `BARREL_HIT_SCORE_PENALTY = 10`. Each barrel hit subtracts 10 from score, making score a better measure of barrel avoidance.

### 31. Moved Donkey Kong to Right Side of Top Platform
- **File:** `environment.py`
- **Change:** Kong position moved from x=500 to x=920 (right side of top platform, which spans x=400–1000).

### 32. Fixed Barrel Direction on Flat Platforms
- **File:** `environment.py`
- **Problem:** After moving Kong to x=920, barrels spawned right of the platform center, causing them to roll right on the flat top platform instead of left.
- **Fix:** On flat platforms (angle=0), barrels now preserve their current horizontal direction instead of rolling toward the nearest edge. Kong throws left, so barrels continue left.

### 33. HUD: Remaining Barrel Hits
- **File:** `environment.py`
- **Change:** Added "Hits left: X" text in white at the top-left corner of the screen showing `MAX_BARREL_HITS - barrel_hits`.

### 34. Increased MAX_STEPS_PER_EPISODE
- **File:** `config.py`
- **Change:** `MAX_STEPS_PER_EPISODE`: 5000 → **50000**. Gives the agent much more time per episode to explore and learn.

### 35. Floaty Jump Physics — Separate Player Gravity
- **Files:** `config.py`, `environment.py`
- **Problem:** With `JUMP_POWER = 14` and `GRAVITY = 0.8`, max jump height was 122px — nearly reaching the platform above (140px gap), causing the player's head to clip into the platform. Head collision code (`change_y = 0`) cut air time short, reducing frames above barrel height to ~15 — not enough to dodge a barrel (needs 25 frames). Reducing power to 12 lowered the peak to 90px (no clip) but only gave 27 frames above barrel, with a dodge window of just 3 pixels.
- **Fix:** Added `PLAYER_GRAVITY = 0.3` (used only for player physics). Kept `GRAVITY = 0.8` for barrels. Reduced `PLAYER_JUMP_POWER` from 12 to 6. With lower gravity, the player jumps lower but hangs in the air much longer:
  - Peak height: 60px (vs 90px before) — 10px below head-clip threshold, no collision
  - Frames above barrel height (20px): 33 frames (vs 27 before)
  - Standing dodge window: |barrel_dx| ∈ [31, 45] = 15px wide (vs 3px before)
  - `REWARD_JUMP_CLOSE_THRESHOLD = 40` fits within [31, 45] — **no threshold changes needed**
- **Impact:** Jump feels floaty/arcade-like. Barrel dodging is much more forgiving. Barrels still fall at normal speed.

### 36. Wandb Logging Improvements
- **File:** `trainer.py`
- **Problem:** Only logged `reward`, `score`, `loss`. Missing key training metrics. Rolling average buffers declared but unused.
- **Fix:** Added `epsilon`, `survival_steps`, `platform`, `barrel_hits` to per-episode wandb log. Added all missing config params to wandb init (`player_speed`, `player_climb_speed`, `max_fall_speed`, `barrel_interval_min/max`, `episodes`, `max_barrel_hits`, `barrel_hit_score_penalty`, `win_score`, `platform_score`, `player_gravity`). Removed unused rolling average buffers.

### 37. Princess Reward — Added Away Penalty
- **Files:** `config.py`, `environment.py`, `trainer.py`
- **Problem:** On platform 5 (top), agent walked away from princess despite low epsilon (~0.01). Princess reward was asymmetric: +0.2 for getting closer, but no penalty for moving away. With no ladder on platform 5, `ladder_dx = 0` and ladder reward never fires — the only directional signal was a weak +0.2 toward princess, insufficient to override learned behavior from lower platforms.
- **Fix:** Added `REWARD_AWAY_PRINCESS = 0.4` (penalty for moving away). Increased `REWARD_TOWARD_PRINCESS`: 0.2 → 0.3. Now mirrors the ladder reward pattern (+0.3 toward / -0.4 away). Added to wandb config.
- **Impact:** Agent gets clear directional signal on platform 5 to walk toward princess.

### 35. Fixed best_score Tracking and Print Format
- **File:** `trainer.py`
- **Problem:** `best_score` initialized to 0, so negative scores (from barrel hit penalties) never updated it. Print showed misleading "Best: 0".
- **Fix:** `best_score` initialized to `float('-inf')`. Print now shows actual `Score` and labeled `Best Score`.

## Documentation Created
- `state_action_reference.md` — State dictionary, tensor normalization, and action space reference.
- `reward_reference.md` — Complete reward breakdown with config values and flow.
- `session_changes.md` — This file.

## Session: April 6, 2026 (continued)

### 36. Wandb Logging Improvements
- **File:** `trainer.py`
- **Changes:** Added `epsilon`, `survival_steps`, `platforms_reached`, `hit_rate` (hits per 1000 steps) to per-episode wandb log. Added all missing config params to wandb init (`player_speed`, `player_climb_speed`, `max_fall_speed`, `barrel_interval_min/max`, `episodes`, `max_barrel_hits`, `barrel_hit_score_penalty`, `win_score`, `platform_score`, `player_gravity`, `lr_milestones`, `lr_gamma`). Removed unused rolling average buffers. Replaced raw `barrel_hits` with `hit_rate` for more meaningful dodge tracking.

### 37. Princess Reward — Added Away Penalty
- **Files:** `config.py`, `environment.py`, `trainer.py`
- **Problem:** On platform 5 (top), agent walked away from princess despite low epsilon (~0.01). Princess reward was asymmetric: +0.2 for getting closer, but no penalty for moving away. With no ladder on platform 5, `ladder_dx = 0` and ladder reward never fires — the only directional signal was a weak +0.2 toward princess.
- **Fix:** Added `REWARD_AWAY_PRINCESS = 0.4`. Increased `REWARD_TOWARD_PRINCESS`: 0.2 → 0.3. Now mirrors the ladder reward pattern (+0.3 toward / -0.4 away). Added to wandb config.

### 38. Learning Rate Decay Schedule
- **Files:** `config.py`, `AI_agent.py`, `trainer.py`
- **Change:** Added `MultiStepLR` scheduler with fixed milestones. LR halves at each checkpoint. Current LR logged to wandb per episode.
- **Config:** `LR_MILESTONES = [200000, 400000, 600000]`, `LR_GAMMA = 0.5`.
- **Schedule:** 0.001 → 0.0005 → 0.00025 → 0.000125.

### 39. Cumulative Platform Tracking
- **Files:** `environment.py`, `trainer.py`
- **Problem:** Logged `current_platform_number` at episode end — after catching princess, player resets to platform 0 and the log shows 0 or -1 instead of the total climb progress.
- **Fix:** Added `total_platforms_reached` counter. Only increments when player climbs to a new higher platform (not on falls). Resets of `highest_platform` on princess collision don't affect it. Logged as `platforms_reached` in wandb and print.

### 40. Climb Reward Exploit — Jump Farming Fix
- **File:** `environment.py`
- **Problem:** Reward section A gave `diff_y * 0.5` for ALL upward movement, including jumps. This exploit existed from the very beginning — every jump gave massive unearned reward through climb reward, regardless of physics settings:
  - Old physics (power=14, gravity=0.8): peak 122px → +61.0 climb reward per jump, -1.0 jump penalty = **+60.0 net**
  - Mid physics (power=12, gravity=0.8): peak 90px → +45.0 per jump = **+44.0 net**
  - Floaty physics (power=6, gravity=0.3): peak 60px → +30.0 per jump = **+29.0 net**
  - At ~100 jumps/episode, the agent earned ~2750–6000 reward from jumping alone, dwarfing all other signals.
  - **Symptom in wandb:** reward kept rising while score dropped — the agent was optimizing for jump farming instead of game progress. Section D's -1.0 penalty for irrelevant jumps was negligible vs the +30–60 climb reward per jump.
- **Fix:** Added `and self.player.on_ladder` condition. Climb reward now only fires when player is on a ladder. Jumping gives 0 from section A, and -1.0 from section D = net **-1.0** per irrelevant jump.
- **Impact:** Eliminates the largest reward exploit across all physics configs. Agent can no longer farm reward by jumping in place.

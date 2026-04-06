# Reward Reference

| Section | What | Value | Purpose |
|---------|------|-------|---------|
| **A** | Climb up (on ladder) | `+Δy × 0.5` | Encourage upward progress |
| **B** | Toward/away ladder (>40px) | +0.3 / −0.4 | Navigate to ladders |
| **C** | Toward/away princess (same plat) | +0.3 / −0.4 | Walk to princess on top |
| **D** | Jump: barrel ≤40px / else | +5.0 / −1.0 | Binary dodge decision |
| **F** | Death / Barrel hit / Win / Fall | −50 / −10 / +50 / −100 | Terminal + anti-exploit |
| **H** | Exit ladder to higher plat | +4.0 | Milestone bonus |

All rewards are calculated in `environment.step()` after the action is executed.
5 active sections: A, B, C, D, F (with F2), H.

## Reward Components

### A. Climb Reward (on ladder only)
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| Moved upward while `on_ladder` | `+Δy × 0.5` | `REWARD_CLIMB_UP_MULTIPLIER` |
| Moved downward or not on ladder | 0 | — |

**Note:** Only fires when `self.player.on_ladder` is true, preventing jump-farming exploits.

### B. Distance to Ladder (off-ladder, > 40 px away)
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| Moved closer to ladder (distance > 40 px) | +0.3 | `REWARD_TOWARD_LADDER` |
| Moved away from ladder (distance > 40 px) | −0.4 | `REWARD_AWAY_LADDER` |
| Within 40 px of ladder | 0 (gated) | — |

**Note:** Asymmetric penalty: one toward+away cycle = +0.3 − 0.4 = −0.1 net. The 40 px gate prevents oscillation farming near ladders.

### C. Distance to Princess (same platform only)
| Condition | Reward | Config Constant |
|-----------|--------|------------------|
| Moved closer to princess | +0.3 | `REWARD_TOWARD_PRINCESS` |
| Moved away from princess | −0.4 | `REWARD_AWAY_PRINCESS` |

**Note:** Only active when `same_platform_princess == 1`. Asymmetric like B.

### D. Jump Reward / Penalty (binary)
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| Jump when barrel ≤ 40 px | +5.0 | `REWARD_JUMP_CLOSE` |
| Jump when barrel > 40 px | −1.0 | `REWARD_JUMP_IRRELEVANT` |
| Jump with no barrel (`barrel_dx == 0`) | −1.0 | `REWARD_JUMP_IRRELEVANT` |

Threshold: `REWARD_JUMP_CLOSE_THRESHOLD = 40`

**Note:** `barrel_dx` is platform-aware. Off-ladder: only barrels on the same platform facing the player. On-ladder: only barrels on the platform above heading toward the ladder top.

### F. Terminal Events (override reward with `=`)
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| Life lost (game over) | −50.0 | `REWARD_DEATH` |
| Barrel hit (survives) | −10.0 | `REWARD_BARREL_HIT` |
| Score increased (reached new platform) | +50.0 | `REWARD_WIN` |

**Note:** Death and barrel hit use `reward =` (not `+=`), replacing accumulated A–D rewards. Life lost checks first (highest priority). `INITIAL_LIVES = 1` (fall = instant game over). Barrel hits: player continues from same position, gets −10 reward, −10 score (`BARREL_HIT_SCORE_PENALTY`). Game over after `MAX_BARREL_HITS = 10` hits.

### F2. Fall Penalty (additive after F)
| Condition | Reward | Config Constant |
|-----------|--------|------------------|
| Landed on a lower platform than before | −100.0 | `REWARD_FALL_PENALTY` |

**Note:** Prevents climb-fall-reclimb cycling exploit. Applied with `−=` so it stacks with death if both happen.

### H. Ladder Exit (higher platform)
| Condition | Reward | Config Constant |
|-----------|--------|------------------|
| Exited ladder AND reached a higher platform | +4.0 | `REWARD_EXIT_LADDER` |

**Note:** Only rewards upward progress; exiting to the same or lower platform gives nothing.

## Reward Flow

1. Start with `reward = 0`
2. Add A (climb on ladder) + B (toward/away ladder) + C (toward/away princess) + D (jump)
3. If death → `reward = −50.0` (replaces all above)
4. Elif barrel hit → `reward = −10.0` (replaces all above)
5. If win → `reward = +50.0` (replaces all above)
6. If fell to lower platform → `reward −= 100.0` (stacks on top of F)
7. Add H (ladder exit) — always additive

## Removed Sections (historical)
- **D2 (No-jump penalty)**: Punished valid walk-away dodges; death penalty already handles failed dodges
- **D middle tier (41–70px)**: Merged into single penalty; binary close/far is cleaner
- **Grab ladder (+1)**: Redundant — B shapes toward ladder, A rewards climbing, H rewards arrival
- **E (Idle)**: Redundant with directional shaping (B/C)
- **G (Alive penalty)**: Negligible at −0.01/step
- **J (Hang penalty)**: Addressed by climb-only reward (A)

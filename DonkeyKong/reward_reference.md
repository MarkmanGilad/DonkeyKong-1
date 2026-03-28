# Reward Reference

All rewards are calculated in `environment.step()` after the action is executed.

## Reward Components

### A. Climbing Up
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| Player moved upward (y decreased) | `+Δy × 0.5` | `REWARD_CLIMB_UP_MULTIPLIER` |

### B. Distance to Ladder (only when NOT on a ladder)
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| Moved closer to ladder | +0.3 | `REWARD_TOWARD_LADDER` |
| Moved away from ladder | −0.3 | `REWARD_AWAY_LADDER` (0.3, applied via `reward -=`) |

### C. Distance to Princess (only on same platform)
| Condition | Reward | Config Constant |
|-----------|--------|------------------|
| Moved closer to princess (same platform only) | +0.2 | `REWARD_TOWARD_PRINCESS` |

### D. Jumping (only when a threatening barrel exists)
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| Jump when barrel > 200 px away | −1.0 | `REWARD_JUMP_IRRELEVANT` (1.0, applied via `reward -=`) |
| Jump when barrel 80–200 px away | −0.5 | `REWARD_JUMP_DISTANT` (0.5, applied via `reward -=`) |
| Jump when barrel ≤ 80 px away | +0.5 | `REWARD_JUMP_CLOSE` |
| No threatening barrel (`barrel_dx == 0`) | — | Skipped entirely |

Thresholds: `REWARD_JUMP_CLOSE_THRESHOLD = 80`, `REWARD_JUMP_DISTANT_THRESHOLD = 200`

### E. Idle Penalty
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| Player x and y unchanged from previous step | −0.2 | `REWARD_IDLE` |

### F. Terminal Events (override accumulated reward)
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| Lost a life (or game over) | −10.0 | `REWARD_DEATH` |
| Score increased (reached princess) | +50.0 | `REWARD_WIN` |

### G. Living Penalty (per step)
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| Every step (encourages speed) | −0.1 | `REWARD_ALIVE` |

### H. Ladder Interaction
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| Grabbed a ladder (was off, now on) | +1.0 | `REWARD_GRAB_LADDER` |
| Exited a ladder (was on, now off) | +4.0 | `REWARD_EXIT_LADDER` |

### I. Hang Penalty (scaled)
| Condition | Reward | Config Constant |
|-----------|--------|-----------------|
| On ladder > 30 frames | `−(frames − 30) × 0.03` per frame | `REWARD_HANG_THRESHOLD`, `REWARD_HANG_PENALTY_PER_FRAME` |

## Reward Flow

1. Start with `reward = 0`
2. Add components A–E (cumulative)
3. If death → `reward = −100` (replaces all above)
4. If win → `reward = +5000` (replaces all above)
5. Add living penalty G (always)
6. Add ladder rewards H (if applicable)
7. Add hang penalty I (if applicable)

**Note:** Death and win rewards (F) use `=` not `+=`, so they override components A–E. However, components G, H, and I are still added on top.

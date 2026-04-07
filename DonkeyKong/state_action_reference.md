# State & Action Reference

## State (Dictionary — before tensor)

| Key                    | Type  | Description                                                        | Range / Example        |
|------------------------|-------|--------------------------------------------------------------------|------------------------|
| `player_platform`      | int   | Platform number the player is on or above                          | -1 to 5               |
| `player_x`             | float | Player's horizontal center position (pixels)                       | 0 – 1500              |
| `player_y`             | float | Player's vertical center position (pixels, not in tensor)          | 0 – 820               |
| `height_from_platform` | float | Vertical distance from player bottom to platform top (pixels)      | 0 when standing        |
| `on_ladder`            | int   | Whether the player is currently on a ladder                        | 0 or 1                |
| `in_air`               | int   | Whether the player is airborne (not on ladder, change_y != 0)      | 0 or 1                |
| `ladder_dx`            | float | Signed horizontal distance to nearest ladder on current platform   | negative = left        |
| `barrel_dx`            | float | Signed horizontal distance to closest threatening barrel           | 0 if none              |
| `princess_dx`          | float | Signed horizontal distance to princess                             | negative = left        |
| `same_platform_princess` | int | Whether princess is on the same platform as the player             | 0 or 1                |
| `platform_left_dx`     | float | Signed distance from player to left edge of current platform       | always ≤ 0             |
| `platform_right_dx`    | float | Signed distance from player to right edge of current platform      | always ≥ 0             |

**`barrel_dx` logic:**
- **Not on ladder:** Closest barrel on the **same platform**, facing the player.
- **On ladder:** Closest barrel on the **platform above**, heading toward the ladder top.

## State Tensor (after normalization — length 11)

| Index | Source Key               | Normalization                    | Resulting Range |
|-------|--------------------------|----------------------------------|-----------------|
| 0     | `player_platform`        | **Zeroed out** (always 0)        | 0              |
| 1     | `player_x`               | ÷ screen_width (1500)            | 0 to 1.0        |
| 2     | `height_from_platform`   | ÷ screen_height (820)            | 0 to ~1.0       |
| 3     | `on_ladder`              | no normalization                 | 0 or 1          |
| 4     | `in_air`                 | no normalization                 | 0 or 1          |
| 5     | `ladder_dx`              | ÷ screen_width (1500)            | -1.0 to 1.0     |
| 6     | `barrel_dx`              | ÷ screen_width (1500)            | -1.0 to 1.0     |
| 7     | `princess_dx`            | ÷ screen_width (1500)            | -1.0 to 1.0     |
| 8     | `same_platform_princess` | no normalization                 | 0 or 1          |
| 9     | `platform_left_dx`       | ÷ screen_width (1500)            | -1.0 to 0       |
| 10    | `platform_right_dx`      | ÷ screen_width (1500)            | 0 to 1.0        |

**Note:** All normalization is done once in `state_to_tensor()` before the tensor enters the network or replay buffer.

## Actions (8 total)

| Action | Description          | Details                                      |
|--------|----------------------|----------------------------------------------|
| 0      | Stay / Idle          | Stop horizontal movement                     |
| 1      | Move Right           | Walk right on platform or ladder             |
| 2      | Move Left            | Walk left on platform or ladder              |
| 3      | Climb Up / Jump      | Climb up ladder; jump if not near ladder     |
| 4      | Climb Down           | Climb down ladder                            |
| 5      | Jump                 | Jump in place (keeps current horizontal)     |
| 6      | Jump + Move Right    | Jump while moving right                      |
| 7      | Jump + Move Left     | Jump while moving left                       |

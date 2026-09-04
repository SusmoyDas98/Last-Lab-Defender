# Last Lab Defender

A 3D top-down/first-person arena shooter built with **PyOpenGL** and **GLUT**. Defend the last bio-substance capsule on Earth against three escalating waves of alien invaders — culminating in a boss fight against the alien commander himself.

## Story

Our protagonist is the last of the guardians assigned to shield a capsule containing a secret bio substance inside a laboratory. Aliens have already made it all the way to this realm in search of it, obliterating every other defense and terminating every guardian except the protagonist — who is now trapped in the room with the capsule, racing against a ticking clock.

The guardian is armed with a gun-like weapon to neutralize the enemies. His suit can automatically extract lifeline-regenerating substances by killing special aliens, distinguishable by their red coloring. After enough kills, his weapon automatically upgrades to a more efficient version.

The aliens aren't foolish — they send in the weak, unarmed swarm first to test the guardian's resolve. If he proves resilient within the timeframe, a more potent armed regiment is deployed, one that not only marches toward the capsule but shoots at the guardian directly. If the guardian remains unwavered even then, the aliens retreat and their final boss takes matters into its own hands: the strongest of them all, wielding both a rapid gun and a cannon that fires slow, high-damage spherical projectiles. These cannonballs can be shattered mid-flight by sustained fire if the guardian is quick enough. Survive, defeat the boss, and protect the capsule — that's the whole job.

## Gameplay & Level Structure

| Level | Enemy type | Behavior | Progression trigger |
|---|---|---|---|
| **1** | Unarmed swarm (teal) | Rushes the capsule; special red enemies drop in periodically | 30 kills **or** time limit (40s) reached |
| **2** | Armed regiment (green) | Rushes the capsule *and* fires ranged bullets at the guardian (volleys, max 3 active shooters at once) | 40 kills **or** time limit (60s) reached |
| **3** | Final Boss (purple) | Sweeps the back wall, fires a rapid gun *and* slow, high-damage cannonballs that can be shot down mid-air | Boss defeated (50 HP) |

Each level transition clears the board, shows a "Level Cleared" banner, and briefly pauses before the next wave begins. The weapon's color and bullet speed automatically upgrade when the kill thresholds for Level 1 and Level 2 are crossed.

### Core systems
- **Capsule HP** (10) and **Player HP** (5) — the run ends if either hits zero.
- **Ammo & reload** — a limited magazine (20 rounds) that must be manually reloaded.
- **Special (red) enemies** — killing one restores a point of player health.
- **Weapon upgrades** — automatic color/speed upgrades tied to level kill milestones (with a distinct "cheat mode" tier).
- **Enemy bullet absorption** — the player's suit tolerates a few hits before actually losing HP.
- **Cannonball combat (Level 3)** — cannonballs take multiple hits to destroy; destroying two in a row grants bonus health.

## Controls

| Input | Action |
|---|---|
| `W` / `S` | Move forward / backward |
| `A` / `D` | Strafe left / right |
| `Q` / `E` | Rotate player left / right |
| Mouse (Left Click) | Fire weapon |
| Mouse (Right Click) | Toggle first-person / third-person camera |
| `R` | Reload magazine |
| `P` | Pause / resume |
| `F` | Restart the game |
| `C` | Toggle cheat mode (infinite ammo, max bullet speed) |
| Arrow keys | Orbit / raise / lower the free camera (third-person mode) |
| `Z` / `X` | Decrease / increase field of view |

## Tech Stack

- **Python 3**
- **PyOpenGL** (`OpenGL.GL`, `OpenGL.GLU`, `OpenGL.GLUT`) for rendering
- Immediate-mode OpenGL (quadrics, cubes, and manual vertex drawing) — no external model/asset files, everything is procedurally drawn

## Requirements

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

> **Note:** GLUT must be available on your system. On Linux, install `freeglut3-dev` (Debian/Ubuntu: `sudo apt install freeglut3-dev`). On Windows/macOS, PyOpenGL typically bundles what's needed, but a system GLUT/FreeGLUT install may be required depending on your setup.

## Running the Game

```bash
python last_lab_defender.py
```

The game opens with a four-stage cinematic intro (camera pans through the lab while the story is narrated on screen), after which control passes to the player in first-person view.

## Project Structure

This is a single-file implementation (`Last_Lab_Defender` class) organized into logical sections:
- Intro/cinematic sequences
- Player rendering & movement
- Bullet systems (player and enemy)
- Enemy spawning, movement, and combat AI (per level)
- Boss-specific logic (patrol sweep, cannonball attacks)
- Collision detection (bullets↔enemies, enemies↔player/capsule, cannonballs↔everything)
- HUD (health bars, ammo, kill count, timer)
- Input handling (keyboard, mouse, special keys)
- Main GLUT render/update loop

## Known Design Notes

- Levels 1 and 2 use a wall-relative spawn system that keeps enemies away from the capsule and each other; Level 3 spawns the boss once, away from the player.
- Time limits only apply to Levels 1 and 2 — Level 3 is boss-health-gated, not time-gated.
- Cheat mode (`C`) is intended for testing/demo purposes and grants infinite ammo plus the top-tier weapon stats regardless of kill progress.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
python main.py
```

Requires Python 3.11.x. Never install packages into the global pip — always use the project's virtual environment.

**Option 1 — launcher scripts (recommended).** Automatically create the venv if missing, install dependencies, and start the game:

```bash
start.bat        # Windows
./start.sh       # Linux / macOS
```

**Option 2 — manual.** Activate the venv first, then install dependencies and run:

```bash
# Windows
venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Linux / macOS
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Dependencies: `pygame==2.1.3`, `PyTMX==3.31`

There are no automated tests in this project.

## Architecture Overview

**dungeons-and-traps** is a top-down 2D maze game. The main entry point is `main.py`, which instantiates `src/game.py:Game` and calls `game.run()`.

### Core Objects and Their Roles

- **`settings.py:Settings`** — single class of static constants: screen dimensions, tile size, FPS, colors, and all custom Pygame event type IDs. Touch this when adding new global settings or events.

- **`src/game_manager.py:GameManager`** — central shared state object passed everywhere. Holds: current game status (`GameStatus` enum), player energy/lives/score, collected items (diamonds, keys), active weapon, lighting status, and the ordered `LEVELS` list. Also owns `SoundManager`. Raises Pygame custom events to trigger cross-system reactions (e.g. `COLLECT_DIAMOND_EVENT` triggers dashboard refresh).

- **`src/game.py:Game`** — the main game loop. Owns the three UI surfaces (header, dashboard, game area), handles all keyboard input via a state-machine driven by `game_manager.game_status`, dispatches custom events to `Level` methods, and manages transitions between screens/dialogs.

- **`src/level.py:Level`** — loads a `.tmx` map file and constructs all sprites from it. Owns five layered `CameraGroup`s (drawn back-to-front for depth) and multiple functional `pygame.sprite.Group`s used for collision detection. Runs the game loop's update/draw cycle each frame.

### Rendering Layers (drawn in order)

| Layer | Class | Contents |
|---|---|---|
| `bottom_background_layer` | `CameraGroup` | Ground tiles, exit point, check point |
| `bottom_sprites_layer` | `CameraGroup` | Collectables, fire flames, teleports |
| `middle_sprites_layer` | `CameraGroupWithYSort` | Player, walls, stones — Y-sorted for 3D effect |
| `top_sprites_layer` | `CameraGroup` | Most enemies |
| `the_highest_sprites_layer` | `CameraGroup` | Boss (Octopus, 3×3 tiles) |

`CameraGroupWithYSort` sorts sprites by `rect.centery` before drawing, which creates the pseudo-3D depth illusion. The camera offset is computed relative to the player position in `CameraGroup.custom_draw()`.

### Event-Driven Communication

Sprites communicate back to the game loop via Pygame custom events defined in `Settings`. For example:
- Collecting all diamonds posts `EXIT_POINT_IS_OPEN_EVENT` or `CREATE_BOSS_OCTOPUS_EVENT` (depending on `LevelDetails.exit_point_enabled`).
- Enemy death posts `ADD_TOMBSTONE_EVENT` with a position dict.
- Level completion triggers a chain: `START_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT` → (1s delay) → `FINISH_TELEPORT_PLAYER_TO_NEXT_LEVEL_EVENT` → `NEXT_LEVEL_EVENT`.

`Game.handle_custom_events()` is the single handler for all of these.

### Map / Level System

Levels are defined in `GameManager.LEVELS` as `LevelDetails` objects with a `.tmx` filename, a flag for whether an exit point opens on diamond collection (`exit_point_enabled`), and an optional secret code for level-select. Maps live in `data/tmx/`, tilesets in `data/tsx/`.

`Level.create_sprites()` iterates named TMX layers. Tile layers (`ground`, `obstacle`, `moving-obstacle`, etc.) and object layers (`spider-enemy`, `ghost-enemy`, etc.) are handled separately. Enemy behavior parameters (speed, motion schedule, etc.) are read from TMX object custom properties via `TmxHelper`.

### Sprite Hierarchy

- Enemies that use pathfinding extend `PathfindingEnemy` (marker interface) — `Level.inform_about_player_tile_position()` calls `set_player_tile_position()` on them each time the player moves to a new tile.
- Enemies that need to refresh their collision map extend `ObstacleMapObserver`.
- `DamageableEnemy` (abstract) handles HP and damage logic.

### Obstacle Map

`ObstacleMap` (`src/obstacle_map.py`) is a 2D grid that merges all blocking layers (walls, moving obstacles, removable walls, doors). Enemies with pathfinding (BFS / Greedy Best-First Search in `src/search_path_algorithms/`) use this map. When stones are pushed or walls demolished, `REFRESH_OBSTACLE_MAP_EVENT` triggers `Level.refresh_obstacle_map()`.

### Sound

`SoundManager` (`src/sound_manager.py`) is a Singleton. It loads all `.wav` files from `sound/sfx/set_01/` keyed by `SoundEffect` enum values on startup. Call `sound_manager.play_sfx(SoundEffect.XYZ)` to play a sound.

### Tile Size Scaling

`Settings.SOURCE_TILE_SIZE = 16` (original art resolution), `Settings.TILE_SIZE = 48` (rendered size). `GameHelper.get_tile_size_ratio()` and `GameHelper.multiply_by_tile_size_ratio()` are used to scale speed and geometry values when the tile size changes.

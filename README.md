# Dungeons and Traps: Willy's First Adventure

Simple maze game with a view - from the top. The hero can move blocks and explore new terrain. He fights with monsters, collects keys and diamonds.
The goal: teaching how to create a simple game, Pygame exploratory, checking features.

### Gameplay

Use **arrow keys** or **WASD** to move the hero through the maze.

| Key | Action |
|---|---|
| Arrow keys / WASD | Move |
| Left Ctrl / Left Shift | Use weapon |
| X / Z | Next / previous weapon |
| Space | Pause |
| Escape | Options |

The hero has limited energy — when it runs out, a life is lost. Collect energy pickups to restore health. The game tracks your score across levels.

Each level requires collecting all diamonds to open the exit. Keys unlock locked doors.

### Features

- Top-down 2D maze exploration across multiple levels
- Push stones to open new paths
- Collect diamonds and keys to unlock exits
- Fight enemies: spiders, bats, goblins and a boss (Octopus)
- Avoid ghosts — you can't fight them, only run
- Avoid fire flames — block them with a stone
- Use different weapons: sword, bow or explosion spell
- Enemies with pathfinding (Breadth-First Search / Greedy Best-First Search)
- Teleports and checkpoints
- Dynamic lighting system
- Level select via secret codes
- Original pixel-art graphics and sound effects

### Requirements

- Python 3.11.x
- [pygame-ce](https://pyga.me/) 2.5.6
- [PyTMX](https://pytmx.readthedocs.io/) 3.32

### How to run the game?
    
**Option 1 — launcher scripts (recommended).** Automatically create the venv if missing, install dependencies, and start the game:

Windows
```cmd
start.bat
```

Linux
```bash
./start.sh
```

**Option 2 — manual.** Activate the venv first, then install dependencies and run:

Windows
```cmd
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Linux
```bash
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Project Structure

```
dungeons-and-traps/
├── main.py                  # Entry point
├── settings.py              # Global constants and Pygame event IDs
├── data/
│   ├── tmx/                 # Level maps (Tiled Map Editor)
│   └── tsx/                 # Tilesets
├── img/                     # Sprite sheets (PNG)
├── sound/sfx/set_01/        # Sound effects (WAV)
├── font/silkscreen/         # Silkscreen font
└── src/
    ├── game.py              # Main game loop and input handling
    ├── game_manager.py      # Shared state (score, lives, weapons, events)
    ├── level.py             # Level loading and sprite management
    ├── obstacle_map.py      # 2D grid used by enemy pathfinding
    ├── sound_manager.py     # Sound playback (Singleton)
    ├── sprites/             # All game objects (player, enemies, items, weapons…)
    ├── effects/             # Visual effects (blast, explosion, particles…)
    ├── panels/              # UI panels (header, dashboard, dialogs)
    ├── search_path_algorithms/  # BFS and Greedy Best-First Search
    ├── abstract_classes/    # Base classes for enemies
    ├── enums/               # Game enums (GameStatus, WeaponType, SoundEffect…)
    └── tile_details/        # TMX object property parsers per sprite type
```

### Credits

- **Tiny Dungeon** tileset by [Kenney](https://kenney.nl/assets/tiny-dungeon) — CC0, used as inspiration for original graphics
- **ChipTone** by [SFBGames](https://sfbgames.itch.io/chiptone) — used to create sound effects
- **Silkscreen** font by Jason Kottke — [SIL Open Font License 1.1](font/silkscreen/OFL.txt)

### License

**Code** (`src/`, `main.py`, `settings.py`) — [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)
> You are free to use, modify and distribute the code, provided that any derivative work is also published under GPL v3 and includes attribution to the original author.

**Graphics and sounds** (`data/`, `img/`, `sound/`) — [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)
> You are free to use and adapt the assets, provided that you credit the original author and publish your modifications under the same license.

**Font** (`font/silkscreen/`) — [SIL Open Font License 1.1](font/silkscreen/OFL.txt)

© Crimson-Jack

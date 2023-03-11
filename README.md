# dungeons-and-traps
Simple maze game with a view - from the top. The hero can move blocks and explore new terrain. He fights with monsters, collects keys and diamonds. 
The goal: teaching how to create a simple game, Pygame exploratory, checking features.

### How to run the game?
Python 3.11.x

The following command may be useful to import all required libraries. The virtual environment is preferred:

```pip install -r requirements.txt```

Run the game:

```python main.py```

### What has been done so far:
* Center camera (adjusted to edge of the map).
* 3D effect using Y-sorting for tiles.
* Main game window divided into game and dashboard surfaces.
  * Performance improvement: The dashboard panel is refreshed only when it is required.
* Scalable game window and tile size using game settings.
* Support for .tmx and .tsx map files.
  * Custom properties for objects and layers, such as: sprite's speed, read from the map.
* Player's collisions with: obstacles, items and enemies.
  * Enemy: Spider with "up/down" path. Movement is configurable: the pause time, when the spider is at the top, can be defined in the motion_schedule tuple, eg. "30, 10, 50" (cycles). (means: wait 30 cycles, move, wait 10 cycle, move, wait 50 cycles, move to the first step).
  * Enemy: Ghost with "wall follower" path.
* Moving obstacles, e.g. stones. Moving obstacles affect enemy movement paths.
* Simple game logic: energy, collectables, win and game over.

#### Inspirations and interesting links:
* https://kenney.nl/
* https://www.youtube.com/c/ClearCode
* https://www.youtube.com/c/CodingWithRuss
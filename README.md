***sn\[AI\]ke*** is a Pygame-powered, side-scrolling twist on Snake. You slither forward through an endless grid, eat apples to grow, dodge obstacles, and launch bombs to clear the path or knock a diving bird out of the sky. The bird taunts you with witty one-liners from the brains of an LLM.


## Highlights

- Smooth, momentum-based snake movement with segment following and eye tracking
- Infinite side-scrolling world with grid-aligned obstacles
- Apples that grow your snake and bomb-apples that explode on contact
- Shoot bombs in your facing direction with juicy explosions and particles
- A taunting bird enemy with stateful behavior: appearing, hovering, charging, taking damage, and falling
- On-screen dialogue box with short quips from Grok
- Clean menu and game-over screens with keyboard/mouse controls

## Controls

- Menu:
  - Start: `Space` or click the Start button
  - Quit: `Q` or click the Quit button
- In-game:
  - Move: `WASD` or Arrow keys
  - Fire bomb: `Space`
- Game Over:
  - Restart: `R` or click “restart”
  - Quit to menu: `Q` or click “quit to menu”

## Gameplay

- Eat apples to grow. More length = more risk of self-collision later.
  - Grace for minor collisions, just don't start doing donuts!
- Bomb-apples explode on contact:
  - Clear nearby obstacles with a big AOE
  - Spawn debris particles
- The bird:
  - Appears periodically, hovers, and occasionally charges
  - On a successful charge, it bites off half your length
  - Can be damaged or stunned by your bombs
  - Shows a health bar and annoys you in a dialogue box at the bottom of the screen

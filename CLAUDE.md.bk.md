# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**8BIT CYBERPUNK — NEON DUNGEON ROGUELIKE** is a single-file browser game. There is no build system, no package manager, and no dependencies beyond a Google Fonts import. To play or test, open either HTML file directly in a browser.

Two files exist:
- `8bit_cyberpunk_FIXED.html` — the current working version
- `8bit_cyberpunk_SAVE.html` — a prior save/checkpoint

All CSS, HTML, and JavaScript are inline in a single file.

## Architecture

The entire game is one `<script>` block. Code is organized into plain objects and two classes, defined in this order:

### Rendering Primitives
- `P = 4` — one "pixel" unit = 4×4 real pixels (all sprites use this scale)
- `pg(ctx, ox, oy, grid, flipX)` — renders a 2D array of color strings as pixel art using `fillRect`
- `glow(ctx, x, y, w, h, col, str)` — draws a neon glow rect
- `SPR` — object containing all sprite drawing functions: `warrior`, `ranger`, `rogue`, `cleric`, `warlock`, `druid`, plus all enemy sprites and `dm` (dungeon master narrator). Each takes `(ctx, ox, oy, flip, t)` where `t` is an animation time counter for pulsing effects.
- `SPRITE_SIZE` — lookup table mapping sprite name to `{w, h}` canvas dimensions

### Data / Configuration
- `CLASSES` — 6 player classes (warrior, ranger, rogue, cleric, warlock, druid), each with base stats and 2 spells. Spells have `effect(p, enemies)` functions.
- `ETYPES` — 8 enemy type definitions including the final boss `quantumBoss`. Each has an `ability` with a `trigger` type (`'turn3'`, `'hp50'`, `'cd5'`, `'onhit'`, `'phase'`) and a `fn`.
- `EQUIP_POOL` — 12 equipment items with stat bonuses
- `QUEST_POOL` — 10 quests tracking combat stats

### Game State & Entities
- `GameState` — singleton holding current screen, floor, player, enemies array, combat interval, and run statistics
- `Player` class — constructed from a class definition + equipment. Manages `buffs`, `debuffs`, `spells` (with cooldowns), action counter (ATB), and stat recalculation.
- `Enemy` class — constructed from an `ETYPES` entry scaled by floor number. Manages buffs/debuffs, turn counting, phase transitions (boss only), and death animation timer.

### Systems
- `Arena` — Canvas 2D battle arena. Owns the `requestAnimationFrame` render loop, entity positioning (`getPlayerPos`, `getEnemyPos`), VFX spawning (`spawnVFX`), hit flash animations, and canvas resize handling.
- `Combat` — Turn resolution. Uses `setInterval` at 120ms ticks. Each tick increments action counters by `spd`; when a counter reaches 100 the entity acts. Handles damage (`deal`), enemy AI, floor-clear detection, and game-over/win conditions.
- `DM` — Dungeon master narrator. Updates the speech bubble text (`DM.say()`).
- `QM` — Quest manager. Tracks stat counters (`QM.track(stat, amount)`) and applies rewards on completion.
- `UI` — DOM update helpers: `show(screenId)`, `updateBars()`, `renderSpells()`, `renderBuffs()`, `renderQuests()`, `dmgNumAt()`, `dmgNumPlayer()`, `toggleQ()`.
- `Rogue` — Floor generation. `getEnemies(floor)` returns 1–3 `Enemy` instances; floor 10 always spawns the `quantumBoss`.
- `City` — Animated pixel-art city skyline drawn on `#cityCV` behind the class select screen.
- `Game` — Top-level controller: `init()`, `buildClassSelect()`, `renderEquip()`, `renderSpells()`, `enterDungeon()`, `enterFloor()`, `restart()`.

### Screens
Screens are `div.scr` elements toggled via `UI.show(id)`:
| ID | Purpose |
|----|---------|
| `sCS` | Class select (starting screen) |
| `sCM` | Combat |
| `sRS` | Floor results + upgrade choice (3 random upgrades drawn from `EQUIP_POOL`) |
| `sGO` | Game over |
| `sWN` | Victory |

### Combat Flow
1. `Game.enterFloor()` — spawns enemies, shows `sCM`, calls `Combat.start()` after 1.4s delay
2. `Combat.start()` — starts `setInterval` tick loop
3. Each 120ms tick: increment action counters, trigger actions when counter >= 100, tick buffs/debuffs, check floor-clear/death
4. On floor clear: show `sRS` upgrade screen; player picks upgrade then `Game.enterFloor()` for next floor
5. Floor 10 clear = win (`sWN`); player death = game over (`sGO`)

### CSS Design Tokens
Defined in `:root` and mirrored as JS constants:
- `--C` / `CY` = `#00FFFF` (cyan — primary UI)
- `--M` / `MG` = `#FF00FF` (magenta)
- `--P` / `PU` = `#8800FF` (purple)
- `--G` / `GR` = `#39FF14` (neon green)
- `--OR` / `OR` = `#FF4500` (orange)
- `--GD` / `GD` = `#FFD700` (gold)
- `--RD` / `RD` = `#FF2244` (red)

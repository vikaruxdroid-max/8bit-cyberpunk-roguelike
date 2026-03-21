# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Skills Directory
Before writing any code, always read the relevant skill files from C:\game\skills\:

| Task | Read This Skill |
|---|---|
| Any UI element, color, border, font | cyberpunk-theme.md |
| Any combat logic, timing, formulas | combat-system.md |
| Any item, loot, inventory change | loot-generator.md |
| Any dialog, NPC, speech bubble | dialog-writer.md |
| Any zone background, canvas effect | zone-background.md |
| Any enemy stats, scaling, economy | balance-rules.md |
| Any save/load, localStorage | save-system.md |
| Any sprite, animation, particle | sprite-animation.md |

## Project Overview
**8BIT CYBERPUNK — NEON DUNGEON ROGUELIKE** is a single-file browser game.
No build system, no package manager, no dependencies beyond Google Fonts.
To play or test, open 8bit_cyberpunk_FIXED.html directly in a browser.

## File Structure
- `8bit_cyberpunk_FIXED.html` — the only working game file, all code lives here
- `references/` — UI reference images for screen layouts
- `CLAUDE.md` — this file

## Architecture Rules
- Never introduce external dependencies or CDN imports
- All game state lives in the central STATE object — never create parallel state
- CSS variables only for colors — never hardcode hex values inline
- All new screens must follow the existing show/hide pattern used by other screens
- All new features must hook into the existing game loop and STATE object
- Do not duplicate existing functions — always check if one exists before creating

## Code Style
- Vanilla JavaScript only, no frameworks
- All functions named in camelCase
- CSS classes named in kebab-case
- Comments required on any function longer than 20 lines

## Game Systems Already Built
- Character select screen with 6 classes
- Synthwave animated main menu background
- Combat system with skills, cooldowns, and status effects
- Loot drop system with rarity tiers (common, rare, legendary)
- Victory screen with paperdoll equipment panel
- Inventory and equipment slot system
- Minimap
- Netrunner enemy with hacking abilities
- Level up screen with stat choices
- Post-fight loot screen with TAKE/DISCARD/CONTINUE

## Generative Content Rules
- Dialog must fit within existing dialog box dimensions
- Dungeon rooms must use the existing room template structure
- Enemy stats must scale using the existing floor depth scaling formula
- All generated content reads from external JSON files via fetch()

## Reference Images
- `references/1.png` — loot screen and paperdoll layout reference

## Color Tokens
- Primary neon: cyan #00ffff
- Secondary neon: magenta #ff00ff
- Accent: neon green #00ff41
- Warning: neon orange #ff6600
- Danger: neon red #ff0040
- Background: deep navy #0a0a1a
- Panel: dark #0d0d2b

## Testing
- Open HTML file directly in Chrome or Edge — no server needed
- Test every new screen at 1920x1080 and 1280x720
- Check browser console for JS errors after every change
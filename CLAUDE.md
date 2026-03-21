# CLAUDE.md

## Token Efficiency Rules
- NEVER re-read files already in context — use line numbers from prior reads
- Use targeted reads with offset/limit — never read the full 5700-line file
- Use Grep/Glob before Read — find the exact line first, then read only that section
- Delegate research to subagents (Agent tool) to keep main context clean
- Use plan mode for complex features — one plan, one execution pass, no back-and-forth
- Skip summaries of what was changed — the diff speaks for itself
- Only read the skill files relevant to the current task, not all 17
- Parallel tool calls whenever possible — don't serialize independent operations

## What This Is
Single-file browser roguelike (8bit_cyberpunk_FIXED.html). No build system, no dependencies. Open in browser to test.

## Skills — ALWAYS Read Before Coding
Before writing any code, read the relevant skill file(s) from `skills/`:

**Core Systems:**
| Task | Skill File |
|---|---|
| UI, colors, borders, fonts | cyberpunk-theme.md |
| Combat logic, timing, formulas | combat-system.md |
| Items, loot, inventory | loot-generator.md |
| Dialog, NPCs, speech bubbles | dialog-writer.md |
| Zone backgrounds, canvas effects | zone-background.md |
| Enemy stats, scaling, economy | balance-rules.md |
| Save/load, localStorage | save-system.md |
| Sprites, animation, particles | sprite-animation.md |

**Design & Content:**
| Task | Skill File |
|---|---|
| Room types, events, traps, dungeon flow | dungeon-design.md |
| Boss phases, mechanics, encounters | boss-design.md |
| Zone lore, NPC identity, narrative | world-lore.md |
| Enemy creation, AI behavior, abilities | enemy-design.md |
| Player classes, spells, synergies | class-design.md |
| Shop mechanics, pricing, stock | merchant-system.md |
| Screen layouts, transitions, HUD | screen-design.md |
| Quest objectives, tracking, rewards | quest-design.md |
| Web Audio API, SFX, procedural music | sound-design.md |

## Architecture Rules
- IMPORTANT: All code lives in `8bit_cyberpunk_FIXED.html` — never create separate JS/CSS files
- All game state lives in the central `GameState` object — never create parallel state
- CSS variables for colors — never hardcode hex values inline
- Always check if a function already exists before creating a new one

## Common Mistakes — Don't Repeat These
- **Canvas state leaks**: Every `ctx.save()` MUST have a matching `ctx.restore()`. After any drawing helper function, verify globalAlpha=1, filter='none', shadowBlur=0
- **Invalid color strings**: When building rgba() strings dynamically, always verify the string is complete (e.g. `'rgba(136,0,255,0.5)'` not `'rgba(136,0,255,'`)
- **P=4 sizing**: Sprite pixel size is `const P = 4`. Sprites are 14 columns = 56px wide. Don't use P for font sizes — use explicit px values
- **Screen check**: `Arena.render()` exits early if `GameState.currentScreen !== 'sCM'` — backgrounds draw on all screens, sprites only on combat
- **Null enemies**: Always default `GameState.enemies` to `[]` when accessing in render loops
- **Resize timing**: Canvas buffer (cv.width/height) must match container dimensions. Call `Arena.resize()` after showing combat screen

## Color Tokens
Primary: cyan `#00ffff` | Secondary: magenta `#ff00ff` | Accent: green `#00ff41`
Warning: orange `#ff6600` | Danger: red `#ff0040` | BG: navy `#0a0a1a` | Panel: `#0d0d2b`

## Testing
- Open HTML file directly in Chrome or Edge
- Check browser console (F12) for JS errors after every change
- Test at 1920x1080 and 1280x720

## Slash Commands
- `/add-feature` — plan and implement a new feature
- `/fix-bug` — diagnose and fix a bug
- `/add-enemy` — add a new enemy with sprite, stats, and zone placement
- `/add-zone` — add a new world map zone with background and enemies
- `/audit` — scan code for common issues (canvas leaks, null checks, etc.)

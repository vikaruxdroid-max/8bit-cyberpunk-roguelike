SKILL: screen-design defines UI screen structure, layout patterns, transitions, and HUD rules.

## Screen Architecture
All screens are `<div class="scr" id="sXX">` with `position:absolute;inset:0;display:none;flex-direction:column`.
Active screen gets `.on` class → `display:flex`.
Switch via `UI.show('sXX')` which sets `GameState.currentScreen`.

## Existing Screen IDs
- sCS: Character Select (class pick + equipment)
- sCM: Combat (arena + HUD + inventory sidebar)
- sVIC: Victory (loot cards + paperdoll + upgrades)
- sLV: Level Up (stat choice picker)
- sGO: Game Over (death stats + restart)
- sFC: Floor Complete (zone clear summary)
- sWN: Win (final victory)
- sWM: World Map (zone navigator)

## Screen Transition
Scanline wipe effect via `#screenWipe`:
```javascript
const wipe = document.getElementById('screenWipe');
wipe.classList.remove('active');
void wipe.offsetHeight; // force reflow
wipe.classList.add('active');
```
Always call before switching screens. 200ms duration.

## New Screen Template
```html
<div class="scr" id="sNEW">
  <!-- Header -->
  <div style="flex-shrink:0; padding:8px 16px; border-bottom:2px solid var(--C);
    background:linear-gradient(90deg,rgba(0,0,10,.98),rgba(4,0,24,.98));">
    <div style="font-size:clamp(10px,1.2vw,18px); color:var(--C);
      text-align:center; letter-spacing:4px;">SCREEN TITLE</div>
  </div>

  <!-- Main content (flex:1 for scrollable area) -->
  <div style="flex:1; overflow-y:auto; padding:16px; min-height:0;">
    <!-- content here -->
  </div>

  <!-- Footer with action button -->
  <div style="flex-shrink:0; padding:8px 16px; border-top:2px solid var(--C);
    text-align:center;">
    <button class="entbtn" onclick="UI.show('sCM')">CONTINUE</button>
  </div>
</div>
```

## Layout Patterns

**Full-screen overlay** (Game Over, Win): Dark background, centered content, large text
```css
background: rgba(2,2,18,.97);
display:flex; align-items:center; justify-content:center; flex-direction:column;
```

**Split panel** (Victory Screen): Grid with multiple columns
```css
display:grid; grid-template-columns: 3fr 1fr 1fr; min-height:0; overflow:hidden;
```

**Combat layout** (sCM): Column with sidebar
```css
.cmain { flex:1; display:flex; overflow:hidden; min-height:0; }
.arena-col { flex:1; display:flex; flex-direction:column; }
#invPanel { width:clamp(158px,15vw,222px); flex-shrink:0; }
```

## HUD Element Rules
- All HUD text: `font-family:'Press Start 2P',monospace`
- Stat labels: `clamp(7px,0.8vw,11px)` — tiny but readable
- Values: `clamp(9px,1vw,14px)` — slightly larger
- Bars (HP/MP): `height:clamp(8px,1vh,14px)` with gradient fill
- Buttons: `clamp(8px,0.9vw,13px)` font, `padding:clamp(6px,0.8vh,12px)`
- All sizes use clamp() for responsive scaling — never fixed px

## Z-Index Hierarchy (global)
```
0   — background layers (#bg1, #bg2)
10  — screen content (.scr)
20  — canvas overlays (#dmgOv)
30  — effects
40  — UI panels (#invPanel)
45  — speech bubbles
50  — dialog box (#dlgBox)
60  — modals/overlays (room exits, merchant)
70  — screen wipe transition
80  — pause menu
```

## Responsive Design Rules
- Never use fixed widths — always clamp() or percentage
- Test at 1920x1080 (desktop) and 1280x720 (laptop)
- `100vw × 100vh` root, no scrolling on any screen
- Inventory sidebar collapses gracefully at narrow widths
- Arena canvas auto-resizes via Arena.resize()

## Animation Patterns
- Screen enter: `@keyframes fadeIn { from{opacity:0;transform:translateY(6px)} to{opacity:1} }` 350ms
- Button hover: `transition:all .15s; background:var(--C); color:#020210;`
- Glow pulse: `box-shadow:0 0 Xpx rgba(color,.Y)` with animation
- Scanline overlay: `background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,0,0,.07) 4px)`

## Modal/Overlay Pattern
For in-screen overlays (merchant shop, room choices):
```javascript
const overlay = document.getElementById('overlayId');
overlay.innerHTML = ''; // clear previous
overlay.style.display = 'flex';
// Build content...
// Add close button that sets overlay.style.display = 'none'
```
Always position:absolute inside parent container, never create new screen for temporary UI.

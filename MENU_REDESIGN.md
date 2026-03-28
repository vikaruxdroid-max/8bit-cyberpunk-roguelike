# NEON DUNGEON — INSTRUCTION BLOCK: MAIN MENU REDESIGN
### Claude Chat Architect Layer · 2026-03-26

---

> **SCOPE**: Redesign the main menu HTML/CSS for better visual hierarchy,
> cyberpunk aesthetics, and usability. No game logic changes.
> All existing button functionality (onclick handlers) must be preserved exactly.
> Only the layout, styling, and presentation change.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. The main menu screen HTML element — its ID and current inner structure
2. All button IDs and their current onclick handlers on the main menu
3. Where the main menu CSS is defined — inline `<style>` block or per-element
4. Whether the matrix rain / background animation is canvas or CSS
5. The current font imports — confirm "Press Start 2P" and "Share Tech Mono" are loaded

Report all five before writing any code.

---

## REDESIGN SPECIFICATION

### Layout Structure (replace current button layout with this hierarchy):

```
┌─────────────────────────────────────┐
│  [top-right corner: ⚙ gear icon]    │
│                                     │
│     8-BIT CYBERPUNK  (existing)     │
│     NEON DUNGEON ROGUELIKE (sub)    │
│                                     │
│     [rotating tagline]              │
│                                     │
│     ┌─────────────────────────┐     │
│     │    ◈  CONNECT  ◈        │     │  ← primary, glowing cyan border
│     └─────────────────────────┘     │
│                                     │
│     ┌─────────────────────────┐     │
│     │       CONTINUE          │     │  ← secondary, dimmer
│     └─────────────────────────┘     │
│                                     │
│     ★ DAILY CHALLENGE               │  ← daily entry inline, gold
│     [modifier 1] + [modifier 2]     │
│                                     │
│  ┌──────────┬──────────┬─────────┐  │
│  │ RUN LOG  │ RECORDS  │ ACHIEV. │  │  ← tertiary row, small
│  └──────────┴──────────┴─────────┘  │
│                                     │
│  NEON DUNGEON v1.0 // GRID ONLINE   │  ← footer, tiny terminal text
└─────────────────────────────────────┘
```

---

## STEP 1 — CSS ADDITIONS

Add to the existing `<style>` block. Do not remove any existing styles — only add:

```css
/* ── MAIN MENU REDESIGN ─────────────────────────────── */

#sMenu {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0;
    padding: 20px;
    position: relative;
}

/* Settings gear — top right corner */
#menuSettingsBtn {
    position: absolute;
    top: 16px;
    right: 20px;
    background: none;
    border: 1px solid #1a1a3a;
    color: #555577;
    font-size: 18px;
    cursor: pointer;
    padding: 6px 10px;
    border-radius: 4px;
    transition: color 0.2s, border-color 0.2s;
    font-family: inherit;
    line-height: 1;
}
#menuSettingsBtn:hover {
    color: #00ffff;
    border-color: #00ffff;
}

/* Rotating tagline */
#menuTagline {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #444466;
    text-align: center;
    margin: 4px 0 20px 0;
    min-height: 16px;
    letter-spacing: 2px;
}

/* Primary button — CONNECT */
#menuConnectBtn {
    width: 340px;
    padding: 16px 0;
    font-family: 'Press Start 2P', monospace;
    font-size: 14px;
    color: #00ffff;
    background: rgba(0, 255, 255, 0.04);
    border: 2px solid #00ffff;
    cursor: pointer;
    letter-spacing: 4px;
    position: relative;
    transition: background 0.2s, box-shadow 0.2s;
    animation: connectPulse 2.5s ease-in-out infinite;
    margin-bottom: 10px;
}
#menuConnectBtn:hover {
    background: rgba(0, 255, 255, 0.12);
    box-shadow: 0 0 24px rgba(0,255,255,0.4), inset 0 0 12px rgba(0,255,255,0.08);
    animation: none;
}
@keyframes connectPulse {
    0%, 100% { box-shadow: 0 0 8px rgba(0,255,255,0.2); }
    50%       { box-shadow: 0 0 20px rgba(0,255,255,0.5), inset 0 0 8px rgba(0,255,255,0.06); }
}

/* Secondary button — CONTINUE */
#menuContinueBtn {
    width: 340px;
    padding: 12px 0;
    font-family: 'Press Start 2P', monospace;
    font-size: 11px;
    color: #556677;
    background: rgba(255,255,255,0.02);
    border: 1px solid #1e2a3a;
    cursor: pointer;
    letter-spacing: 3px;
    transition: color 0.2s, border-color 0.2s;
    margin-bottom: 20px;
}
#menuContinueBtn:hover {
    color: #aaccdd;
    border-color: #334455;
}
#menuContinueBtn:disabled,
#menuContinueBtn.hidden {
    opacity: 0.25;
    cursor: default;
    pointer-events: none;
}

/* Daily challenge strip */
#menuDailyStrip {
    width: 340px;
    padding: 10px 14px;
    border: 1px solid #332200;
    background: rgba(255, 200, 0, 0.03);
    cursor: pointer;
    margin-bottom: 16px;
    transition: background 0.2s, border-color 0.2s;
    text-align: left;
}
#menuDailyStrip:hover {
    background: rgba(255, 200, 0, 0.08);
    border-color: #ffd700;
}
#menuDailyStrip .daily-label {
    font-family: 'Press Start 2P', monospace;
    font-size: 8px;
    color: #ffd700;
    letter-spacing: 2px;
    display: block;
    margin-bottom: 4px;
}
#menuDailyStrip .daily-mods {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #887744;
    letter-spacing: 1px;
}
#menuDailyStrip .daily-complete {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #445544;
}
#menuDailyStrip .daily-streak {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #333344;
    float: right;
    margin-top: -18px;
}

/* Tertiary button row */
#menuTertiaryRow {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
}
.menu-tertiary-btn {
    padding: 8px 14px;
    font-family: 'Press Start 2P', monospace;
    font-size: 6px;
    color: #334455;
    background: none;
    border: 1px solid #1a1a2e;
    cursor: pointer;
    letter-spacing: 1px;
    transition: color 0.2s, border-color 0.2s;
}
.menu-tertiary-btn:hover {
    color: #aaaacc;
    border-color: #334466;
}

/* Footer */
#menuFooter {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #1a1a2e;
    letter-spacing: 3px;
    text-align: center;
    position: absolute;
    bottom: 14px;
    left: 0;
    right: 0;
}

/* ── END MAIN MENU REDESIGN ─────────────────────────── */
```

---

## STEP 2 — HTML RESTRUCTURE

Find the main menu screen HTML element (from pre-scan). Replace its inner content with:

```html
<!-- Settings gear — top right -->
<button id="menuSettingsBtn" title="Settings">⚙</button>

<!-- Tagline — rotated by JS -->
<div id="menuTagline"></div>

<!-- Primary: New Game -->
<button id="menuConnectBtn">◈ &nbsp; CONNECT &nbsp; ◈</button>

<!-- Secondary: Continue -->
<button id="menuContinueBtn">CONTINUE</button>

<!-- Daily Challenge strip -->
<div id="menuDailyStrip">
    <span class="daily-label">★ DAILY CHALLENGE</span>
    <span class="daily-mods" id="menuDailyMods">LOADING...</span>
    <span class="daily-streak" id="menuDailyStreak"></span>
</div>

<!-- Tertiary row -->
<div id="menuTertiaryRow">
    <button class="menu-tertiary-btn" id="menuRunLogBtn">RUN LOG</button>
    <button class="menu-tertiary-btn" id="menuRecordsBtn">RECORDS</button>
    <button class="menu-tertiary-btn" id="menuAchBtn">ACHIEVEMENTS</button>
</div>

<!-- Footer -->
<div id="menuFooter">NEON DUNGEON v1.0 &nbsp;//&nbsp; GRID ONLINE</div>
```

---

## STEP 3 — WIRE BUTTON HANDLERS

After the HTML restructure, find where the existing button event listeners are attached
(the lines that were previously attaching onclick to the old button IDs).

Remap them to the new IDs. Preserve all existing handler functions exactly:

```javascript
// New button ID → existing handler (adapt function names to actual code):
document.getElementById('menuConnectBtn')?.addEventListener('click', () => {
    // same as old CONNECT / new game handler
    UI.show('sCC'); // or whatever the character creation screen is
});

document.getElementById('menuContinueBtn')?.addEventListener('click', () => {
    // same as old CONTINUE handler
});

document.getElementById('menuSettingsBtn')?.addEventListener('click', () => {
    // same as old SETTINGS handler
});

document.getElementById('menuRunLogBtn')?.addEventListener('click', () => {
    RunHistoryScreen.open(); // confirmed from Block 5.1
});

document.getElementById('menuRecordsBtn')?.addEventListener('click', () => {
    // same as old RECORDS handler
});

document.getElementById('menuAchBtn')?.addEventListener('click', () => {
    UI.show('sACH'); // confirmed from Block 5.3
});

document.getElementById('menuDailyStrip')?.addEventListener('click', () => {
    if (!hasDailyBeenPlayed()) startDailyChallenge();
});
```

---

## STEP 4 — ROTATING TAGLINE JS

Add to the JS section (near menu initialization code):

```javascript
const MENU_TAGLINES = [
    'THE GRID REMEMBERS EVERYTHING.',
    'JACK IN. JACK OUT. REPEAT UNTIL DEAD.',
    'CORPORATE SECURITY IS SOMEONE ELSE\'S PROBLEM.',
    'NO GODS. NO MODS. NO MERCY.',
    'EVERY RUN IS YOUR LAST RUN.',
    'THE DUNGEON DOES NOT NEGOTIATE.',
    'SURVIVE LONG ENOUGH TO REGRET IT.',
    'YOUR FIREWALL IS A SUGGESTION.',
    'PAIN IS A FEATURE. SO IS PERMADEATH.',
    'THE CORE AWAITS. IT IS NOT PATIENT.'
];

let _menuTaglineIndex = Math.floor(Math.random() * MENU_TAGLINES.length);

function updateMenuTagline() {
    const el = document.getElementById('menuTagline');
    if (!el) return;
    el.textContent = MENU_TAGLINES[_menuTaglineIndex];
    _menuTaglineIndex = (_menuTaglineIndex + 1) % MENU_TAGLINES.length;
}

// Rotate every 4 seconds when on menu screen
let _menuTaglineInterval = null;

function startMenuTaglineRotation() {
    updateMenuTagline();
    _menuTaglineInterval = setInterval(updateMenuTagline, 4000);
}

function stopMenuTaglineRotation() {
    if (_menuTaglineInterval) {
        clearInterval(_menuTaglineInterval);
        _menuTaglineInterval = null;
    }
}
```

Call `startMenuTaglineRotation()` when the menu screen opens.
Call `stopMenuTaglineRotation()` when navigating away from the menu.
Hook into `UI.show()` or `_applyShow()` — when `id === 'sMenu'` start, otherwise stop.

---

## STEP 5 — DAILY STRIP POPULATION

Find where the menu is initialized or where `renderDailyMenuEntry()` was previously called.
Replace with DOM population:

```javascript
function populateMenuDailyStrip() {
    const modsEl   = document.getElementById('menuDailyMods');
    const streakEl = document.getElementById('menuDailyStreak');
    const strip    = document.getElementById('menuDailyStrip');
    if (!modsEl || !strip) return;

    const played = hasDailyBeenPlayed();
    const streak = getDailyStreak();
    const seed   = getDailySeed();
    const mods   = getDailyModifiers(seed);

    if (played) {
        modsEl.className   = 'daily-complete';
        modsEl.textContent = 'COMPLETED TODAY';
        strip.style.cursor = 'default';
        strip.style.opacity = '0.5';
    } else {
        modsEl.className   = 'daily-mods';
        modsEl.textContent = `${mods[0].name} + ${mods[1].name}`;
    }

    if (streakEl) {
        streakEl.textContent = streak > 0 ? `${streak}d streak` : '';
    }
}
```

Call `populateMenuDailyStrip()` when the menu screen opens (same place as `startMenuTaglineRotation()`).

---

## STEP 6 — CONTINUE BUTTON STATE

The CONTINUE button should be dimmed/disabled if there is no active save to continue.
Find how the existing CONTINUE button determines if a save exists.
Apply the same logic to add/remove the `hidden` class or `disabled` attribute:

```javascript
function updateContinueButtonState() {
    const btn = document.getElementById('menuContinueBtn');
    if (!btn) return;
    const hasSave = /* existing save detection logic */ false;
    btn.disabled = !hasSave;
    btn.classList.toggle('hidden', !hasSave);
}
```

Call alongside `populateMenuDailyStrip()` on menu open.

---

## COMPLETION REPORT

1. Confirm all 6 original button handlers (connect, continue, settings, run log, records, achievements) are wired to new IDs
2. Confirm DAILY strip populates with today's modifiers or "COMPLETED TODAY"
3. Confirm tagline rotates every 4s on menu screen and stops when navigating away
4. Confirm gear icon (⚙) in top-right opens settings
5. Confirm CONNECT button pulses on idle, stops pulsing on hover
6. Confirm CONTINUE is dimmed when no save exists
7. Confirm footer text renders at bottom
8. Confirm no existing game functionality is broken
9. Confirm game loads and runs without errors

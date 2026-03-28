# NEON DUNGEON — INSTRUCTION BLOCK: COMBAT-UI-1
## COMBAT SCREEN OVERHAUL — PART 1
## Remove Clutter, Fix Sprites, Redesign HUD
### Claude Chat Architect Layer · 2026-03-26

---

> **SCOPE**: Part 1 of 2 combat UI overhaul.
> Remove the "appears!" popup, fix the solid-block enemy sprite bug,
> scale up sprites, and redesign the top HUD.
> No combat logic changes. Visual/layout only.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. The "NETRUNNER appears!" popup — what renders it, what triggers it, what dismisses it (the bottom bar shown in the screenshot)
2. The solid cyan rectangle enemy — which enemy type renders as a solid block, why (missing sprite? fallback draw?)
3. Where sprite scale is defined — the multiplier that controls sprite render size (currently 4×)
4. The top HUD render function — what renders NEON NEXUS | ROOM 2/10 | KILLS | DMG | DPS | CR | AUTO OFF | MAP
5. Where `DPS` is calculated and rendered
6. Where the `AUTO OFF` button is rendered and what it toggles
7. Where zone lore text ("Beware the shadows...") is rendered during combat

Report all seven before writing any code.

---

## FIX 1 — REMOVE "APPEARS!" POPUP

Find the encounter popup bar (the bottom-spanning banner showing "NETRUNNER appears!").
This is superseded by the Block 3.3 entrance glitch animation.

1. Delete the render call for this popup entirely
2. Delete the trigger that shows it when enemies enter a room
3. Delete the dismiss/timer logic
4. Keep `DM.say()` log entries for enemy encounters — only remove the visual popup bar
5. Confirm: entrance glitch animation from Block 3.3 still plays (it's separate)

---

## FIX 2 — FIX SOLID-BLOCK ENEMY SPRITE

Find the enemy rendering that produces the solid cyan rectangle.
This is a fallback render when `SPR[key]` is undefined for an enemy type.

Find the fallback render path in the enemy draw function:
```javascript
// Current fallback is likely something like:
ctx.fillStyle = enemy.color || '#00ffff';
ctx.fillRect(x, y, spriteW, spriteH);
```

Replace the fallback with a proper placeholder that looks intentional:
```javascript
// Improved fallback — renders a glitchy placeholder instead of solid block:
function drawEnemyFallback(ctx, enemy, x, y, w, h) {
    const c = enemy.color || '#00ffff';
    
    // Dark background
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(x, y, w, h);
    
    // Glitch lines
    ctx.strokeStyle = c;
    ctx.lineWidth = 1;
    for (let i = 0; i < 6; i++) {
        const ly = y + Math.random() * h;
        ctx.beginPath();
        ctx.moveTo(x, ly);
        ctx.lineTo(x + w * (0.3 + Math.random() * 0.7), ly);
        ctx.stroke();
    }
    
    // Border
    ctx.strokeStyle = c;
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, w, h);
    
    // "?" in center
    ctx.font = '10px "Press Start 2P"';
    ctx.fillStyle = c;
    ctx.textAlign = 'center';
    ctx.fillText('?', x + w/2, y + h/2 + 4);
    ctx.textAlign = 'left';
}
```

Also: identify WHICH enemy type causes the solid block and add its sprite definition
if it's missing from the `SPR` object. Report which enemy it is in the completion report.

---

## FIX 3 — SCALE UP SPRITES

Find the sprite scale multiplier (currently rendering at 4×, producing 56×104px sprites).

**Change from 4× to 6×** — this makes sprites 84×156px, significantly more visible.

This affects:
- Player sprite render size
- Enemy sprite render sizes
- Sprite positioning (x/y offsets need to account for larger size)
- HP bar position above enemies (must move up to clear larger sprites)
- Hitbox/click areas if any exist

Update all sprite render calls to use the new scale.
Update all position calculations that depend on sprite dimensions.

If 6× causes sprites to overflow the arena bounds at 1280×720, fall back to 5× (70×130px).
Report which scale was used in the completion report.

---

## FIX 4 — REDESIGN TOP HUD

**Current**: 9 items in one cramped line
**New**: 5 items, larger text, better spacing

```
LEFT SIDE:                    CENTER:              RIGHT SIDE:
[ZONE NAME] [ROOM X/Y]        [HP BAR]             [⚡ CR]  [MAP]
```

**Remove from HUD entirely:**
- `DMG: 0` — raw damage number (meaningless mid-combat)
- `DPS: 54` — not actionable during fights
- `AUTO OFF` button — move to pause menu (see Fix 5)
- `KILLS: 0` — move to end-of-combat summary only
- Zone lore text during combat — remove entirely from combat screen (keep on world map only)

**Keep and resize:**
- Zone name — `"Press Start 2P"` 8px, left
- Room X/Y — `"Share Tech Mono"` 9px, left, next to zone
- HP bar — make it 200px wide, 12px tall, with numeric value inside
- MP bar — 120px wide, 8px tall, below HP
- Credits — keep with ⚡ icon, right side
- MAP button — keep top-right, slightly larger

**New HUD layout render:**

```javascript
function renderCombatHUD(ctx, player, cw) {
    const hudH = 44;
    
    // HUD background strip
    ctx.fillStyle = 'rgba(0,0,5,0.85)';
    ctx.fillRect(0, 0, cw, hudH);
    ctx.strokeStyle = '#00ffff';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, hudH);
    ctx.lineTo(cw, hudH);
    ctx.stroke();
    
    // LEFT: Zone name
    ctx.font = '8px "Press Start 2P"';
    ctx.fillStyle = '#00ffff';
    ctx.fillText(GameState.currentZone || 'ZONE', 12, 16);
    
    // LEFT: Room counter
    ctx.font = '8px "Share Tech Mono"';
    ctx.fillStyle = '#556677';
    ctx.fillText(`ROOM ${GameState.roomNum || 1}/${GameState.totalRooms || 10}`, 12, 32);
    
    // CENTER: HP bar (large)
    const hpBarX = cw/2 - 120;
    const hpBarY = 8;
    const hpBarW = 240;
    const hpBarH = 14;
    const hpPct  = Math.max(0, player.hp / player.maxHp);
    const hpColor = hpPct > 0.5 ? '#00ff41' : hpPct > 0.25 ? '#ffaa00' : '#ff4444';
    
    ctx.fillStyle = '#0a0a1a';
    ctx.fillRect(hpBarX, hpBarY, hpBarW, hpBarH);
    ctx.fillStyle = hpColor;
    ctx.fillRect(hpBarX, hpBarY, Math.floor(hpBarW * hpPct), hpBarH);
    ctx.strokeStyle = '#334455';
    ctx.lineWidth = 1;
    ctx.strokeRect(hpBarX, hpBarY, hpBarW, hpBarH);
    
    // HP text inside bar
    ctx.font = '7px "Press Start 2P"';
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    ctx.fillText(`${player.hp}/${player.maxHp}`, hpBarX + hpBarW/2, hpBarY + hpBarH - 2);
    ctx.textAlign = 'left';
    
    // CENTER: MP bar (smaller, below HP)
    const mpBarX = hpBarX + 30;
    const mpBarY = hpBarY + hpBarH + 4;
    const mpBarW = hpBarW - 60;
    const mpBarH = 6;
    const mpPct  = Math.max(0, player.mp / player.maxMp);
    
    ctx.fillStyle = '#0a0a1a';
    ctx.fillRect(mpBarX, mpBarY, mpBarW, mpBarH);
    ctx.fillStyle = '#4488ff';
    ctx.fillRect(mpBarX, mpBarY, Math.floor(mpBarW * mpPct), mpBarH);
    ctx.strokeStyle = '#223344';
    ctx.lineWidth = 1;
    ctx.strokeRect(mpBarX, mpBarY, mpBarW, mpBarH);
    
    // MP label
    ctx.font = '5px "Share Tech Mono"';
    ctx.fillStyle = '#4488ff';
    ctx.fillText(`MP ${player.mp}/${player.maxMp}`, mpBarX - 28, mpBarY + 5);
    
    // RIGHT: Credits
    ctx.font = '8px "Press Start 2P"';
    ctx.fillStyle = '#ffd700';
    ctx.textAlign = 'right';
    ctx.fillText(`⚡ ${player.gold || 0} CR`, cw - 70, 20);
    ctx.textAlign = 'left';
}
```

Replace the existing HUD render function with this. Adapt variable names
(`GameState.roomNum`, `GameState.totalRooms`, `player.gold`) to actual names found in source.

---

## FIX 5 — MOVE AUTO OFF TO PAUSE

Find the AUTO OFF button and what it toggles (auto-battle mode).

1. Remove the AUTO OFF button from the combat HUD entirely
2. Find if a pause menu exists during combat. If yes, add AUTO-BATTLE toggle there.
3. If no pause menu exists, add a small `[P]` pause button to the top-right of the HUD
   that opens a minimal overlay with: AUTO-BATTLE toggle + QUIT RUN button

---

## COMPLETION REPORT FOR COMBAT-UI-1

1. Confirm "appears!" popup removed — entrance glitch still plays
2. Identify which enemy caused the solid-block bug and confirm it's fixed
3. Confirm sprite scale used (5× or 6×) and any layout adjustments made
4. Confirm HUD now shows: Zone, Room, HP bar (large), MP bar, Credits, MAP only
5. Confirm DPS, DMG, KILLS, AUTO OFF removed from HUD
6. Confirm zone lore text removed from combat screen
7. Confirm AUTO OFF toggle relocated (where?)
8. Confirm game loads and runs without errors

---

*COMBAT-UI-1 — Claude Chat Architect Layer · 2026-03-26*
*Execute COMBAT-UI-1 fully before starting COMBAT-UI-2.*

---
---

# NEON DUNGEON — INSTRUCTION BLOCK: COMBAT-UI-2
## COMBAT SCREEN OVERHAUL — PART 2
## Spell Bar, Enemy HP Bars, AI Battle Integration
### Claude Chat Architect Layer · 2026-03-26
### Depends on: COMBAT-UI-1 complete

---

> **SCOPE**: Part 2 of 2 combat UI overhaul.
> Redesign spell buttons (larger, more readable).
> Redesign enemy HP bars (thicker, named).
> Add 3 AI-powered battle enhancements.
> No combat logic changes.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. The spell button render function — current size, font, layout of the 4 spell slots
2. Enemy HP bar render — current thickness, position relative to sprite
3. Where the combo counter is currently displayed
4. Where `DM.say()` output is rendered during combat — the text area at the bottom

---

## REDESIGN 1 — SPELL BAR (larger, more readable)

**Current**: ~50px squares with 7px font, cramped
**New**: 90px × 72px buttons, spell name 8px, MP/CD clearly readable

The spell bar sits at the bottom. 4 spell slots side by side centered.

```javascript
function renderSpellBar(ctx, spells, cw, ch) {
    const slotW = 90;
    const slotH = 72;
    const gap   = 10;
    const totalW = 4 * slotW + 3 * gap;
    const startX = cw/2 - totalW/2;
    const startY = ch - slotH - 8;

    spells.forEach((spell, i) => {
        if (!spell) return;
        const x = startX + i * (slotW + gap);
        const y = startY;
        const onCD = spell.currentCooldown > 0;
        const isEX = spell.evolved;

        // Slot background
        ctx.fillStyle = onCD ? 'rgba(10,5,5,0.9)' : 'rgba(5,5,20,0.92)';
        ctx.fillRect(x, y, slotW, slotH);

        // Border — color by type
        const borderColor = onCD ? '#221122' :
            isEX ? '#ffd700' :
            spell.type === 'attack'  ? '#ff4444' :
            spell.type === 'defense' ? '#00aaff' :
            spell.type === 'potion'  ? '#00ff41' : '#555577';

        ctx.strokeStyle = borderColor;
        ctx.lineWidth = isEX ? 2 : 1;
        ctx.strokeRect(x, y, slotW, slotH);

        // EX glow
        if (isEX) {
            ctx.shadowColor = '#ffd700';
            ctx.shadowBlur = 8;
            ctx.strokeRect(x, y, slotW, slotH);
            ctx.shadowBlur = 0;
        }

        // Spell name — truncate if needed
        const name = (spell.name || '').toUpperCase();
        const maxChars = 10;
        const displayName = name.length > maxChars ? name.substring(0, maxChars - 1) + '.' : name;
        ctx.font = '7px "Press Start 2P"';
        ctx.fillStyle = onCD ? '#333344' : '#ffffff';
        ctx.textAlign = 'center';
        ctx.fillText(displayName, x + slotW/2, y + 18);

        // MP cost
        ctx.font = '7px "Share Tech Mono"';
        ctx.fillStyle = onCD ? '#223' : '#4488ff';
        ctx.fillText(`MP:${spell.mpCost || spell.mp || 0}`, x + slotW/2, y + 34);

        // Cooldown display
        if (onCD) {
            ctx.font = '14px "Press Start 2P"';
            ctx.fillStyle = '#ff4444';
            ctx.fillText(spell.currentCooldown, x + slotW/2, y + slotH/2 + 6);
        } else {
            // CD info when ready
            ctx.font = '6px "Share Tech Mono"';
            ctx.fillStyle = '#334455';
            ctx.fillText(`CD:${spell.cooldown || 0}`, x + slotW/2, y + 50);
        }

        // Key hint (1-4)
        ctx.font = '5px "Share Tech Mono"';
        ctx.fillStyle = '#222233';
        ctx.fillText(`[${i+1}]`, x + 4, y + slotH - 4);

        // EX badge
        if (isEX) {
            ctx.font = '6px "Press Start 2P"';
            ctx.fillStyle = '#ffd700';
            ctx.fillText('EX', x + slotW - 18, y + 10);
        }

        ctx.textAlign = 'left';
    });
}
```

Replace the existing spell button render with this function.
Update the click detection hitboxes to match new slot positions and dimensions:
```javascript
// Spell slot hit test — update to new coordinates:
function getSpellSlotAt(mouseX, mouseY, cw, ch) {
    const slotW = 90, slotH = 72, gap = 10;
    const totalW = 4 * slotW + 3 * gap;
    const startX = cw/2 - totalW/2;
    const startY = ch - slotH - 8;
    for (let i = 0; i < 4; i++) {
        const x = startX + i * (slotW + gap);
        if (mouseX >= x && mouseX <= x + slotW &&
            mouseY >= startY && mouseY <= startY + slotH) {
            return i;
        }
    }
    return -1;
}
```

---

## REDESIGN 2 — ENEMY HP BARS (thicker, named)

**Current**: 1–2px line above sprite
**New**: 10px bar with name label, positioned clearly above sprite

```javascript
function renderEnemyHPBar(ctx, enemy, spriteX, spriteY, spriteW) {
    const barW  = Math.max(spriteW, 80);
    const barH  = 10;
    const barX  = spriteX + spriteW/2 - barW/2;
    const barY  = spriteY - 22;
    const pct   = Math.max(0, enemy.hp / enemy.maxHp);
    const color = pct > 0.6 ? '#00ff41' : pct > 0.3 ? '#ffaa00' : '#ff4444';

    // Background
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.fillRect(barX - 1, barY - 1, barW + 2, barH + 2);

    // Fill
    ctx.fillStyle = color;
    ctx.fillRect(barX, barY, Math.floor(barW * pct), barH);

    // Border
    ctx.strokeStyle = '#334455';
    ctx.lineWidth = 1;
    ctx.strokeRect(barX, barY, barW, barH);

    // Enemy name above bar
    ctx.font = '6px "Press Start 2P"';
    ctx.fillStyle = '#aaaaaa';
    ctx.textAlign = 'center';
    ctx.fillText(enemy.name || '???', spriteX + spriteW/2, barY - 4);
    ctx.textAlign = 'left';

    // Shield phase indicator
    if (enemy.shieldActive && enemy.shieldHp > 0) {
        const shieldPct = enemy.shieldHp / (enemy.maxHp * 0.15);
        ctx.fillStyle = '#00aaff';
        ctx.fillRect(barX, barY, Math.floor(barW * shieldPct), barH);
        ctx.font = '5px "Share Tech Mono"';
        ctx.fillStyle = '#00aaff';
        ctx.textAlign = 'center';
        ctx.fillText('SHIELD', spriteX + spriteW/2, barY + barH + 8);
        ctx.textAlign = 'left';
    }

    // Boss phase indicator
    if (enemy.isBoss && enemy.currentPhase > 1) {
        ctx.font = '5px "Share Tech Mono"';
        ctx.fillStyle = enemy.currentPhase === 3 ? '#ff4444' : '#ff8800';
        ctx.textAlign = 'right';
        ctx.fillText(`PH${enemy.currentPhase}`, barX + barW, barY - 4);
        ctx.textAlign = 'left';
    }
}
```

Replace existing enemy HP bar renders with this function.
Call it for each active enemy after drawing their sprite.

---

## REDESIGN 3 — COMBO COUNTER (more visible)

Find the current combo counter display. Make it more prominent:

```javascript
function renderComboCounter(ctx, comboCount, cw, ch) {
    if (!comboCount || comboCount < 2) return;

    const pulse = 0.85 + Math.sin(Date.now() / 150) * 0.15;
    ctx.save();
    ctx.globalAlpha = pulse;

    ctx.font = '10px "Press Start 2P"';
    ctx.fillStyle = comboCount >= 10 ? '#ffd700' : '#ff00ff';
    ctx.shadowColor = comboCount >= 10 ? '#ffd700' : '#ff00ff';
    ctx.shadowBlur = 12;
    ctx.textAlign = 'right';
    ctx.fillText(`${comboCount}x COMBO`, cw - 12, ch - 90);

    ctx.shadowBlur = 0;
    ctx.textAlign = 'left';
    ctx.restore();
}
```

Position: right side, above spell bar.

---

## AI INTEGRATION 1 — TACTICAL HINT AFTER 3 CONSECUTIVE DIRECT HITS

Track consecutive direct hits in combat state:

```javascript
// In resolveReactionPhase(), when grade === 'direct_hit':
GameState.combatStats = GameState.combatStats || {};
GameState.combatStats.consecutiveDirectHits =
    (GameState.combatStats.consecutiveDirectHits || 0) + 1;

if (GameState.combatStats.consecutiveDirectHits >= 3) {
    GameState.combatStats.consecutiveDirectHits = 0;
    fetchCombatTacticalHint();
}

// Reset on any non-direct-hit outcome:
// In resolveReactionPhase(), for any other grade:
GameState.combatStats = GameState.combatStats || {};
GameState.combatStats.consecutiveDirectHits = 0;
```

Fetch the hint non-blocking:
```javascript
async function fetchCombatTacticalHint() {
    const player = GameState.player;
    const spells = (player.spells || []).map(s => s.name).filter(Boolean);

    // Use existing AIService from Phase 4
    const hint = await AIService.call('spell_commentary', { spells })
        || 'ADJUST YOUR STRATEGY. YOU ARE LOSING.';

    // Display in DM area — brief, then clear
    DM.say(`TACTICAL: ${hint}`, 'warning');
}
```

---

## AI INTEGRATION 2 — KILL CALLOUT POOL (no API, static)

After any enemy is killed, display a random kill callout from a pre-written pool.
No API call — pure static pool for performance.

```javascript
const KILL_CALLOUTS = [
    'TARGET ELIMINATED.',
    'SYSTEM OFFLINE.',
    'THREAT NEUTRALIZED.',
    'PROCESS TERMINATED.',
    'DELETED.',
    'SIGNAL LOST.',
    'FLATLINED.',
    'NULL POINTER.',
    'STACK OVERFLOW: ENEMY.EXE',
    'GARBAGE COLLECTED.',
    'FATAL EXCEPTION.',
    'CONNECTION CLOSED.',
    'CORE DUMP COMPLETE.',
    'ACCESS REVOKED.',
    'UNSUBSCRIBED FROM LIFE.',
    'MEMORY FREED.',
    'TASK KILLED.',
    'SEGMENTATION FAULT.',
    '404: ENEMY NOT FOUND.',
    'EXIT CODE: 0 (DEAD)',
];

function getKillCallout() {
    return KILL_CALLOUTS[Math.floor(Math.random() * KILL_CALLOUTS.length)];
}
```

In the kill resolution (where `killEnemy()` fires), add:
```javascript
Arena.spawnText(getKillCallout(), enemy, '#00ff41');
```

---

## AI INTEGRATION 3 — ENEMY DAMAGE REACTION TAUNTS

When an enemy takes heavy damage (>30% of their max HP in one hit), they react.
Use the existing enemy taunt pools from Block 1.4 (ENEMY_TAUNTS object).

```javascript
// In damage application to enemy (deal() function):
function checkEnemyDamageReaction(enemy, damage) {
    if (damage < enemy.maxHp * 0.30) return;
    if (enemy.hp <= 0) return; // dead, no reaction
    if (Math.random() > 0.40) return; // 40% chance to react

    const taunts = [
        'THAT... ACTUALLY HURT.',
        'IMPRESSIVE. IRRELEVANT.',
        'YOU GOT LUCKY.',
        'SYSTEMS DAMAGED. ANGER RISING.',
        'THIS CHANGES NOTHING.',
        'NOTED. RETALIATION QUEUED.',
        '... FINE. YOU HAVE MY ATTENTION.'
    ];

    // Boss uses AI taunt pool, regular enemies use static
    if (enemy.isBoss && enemy.tauntPool) {
        const taunt = enemy.tauntPool[Math.floor(Math.random() * enemy.tauntPool.length)];
        DM.say(`${enemy.name}: ${taunt}`, 'enemy');
    } else {
        const taunt = taunts[Math.floor(Math.random() * taunts.length)];
        DM.say(`${enemy.name}: ${taunt}`, 'enemy');
    }
}
```

Call `checkEnemyDamageReaction(enemy, damage)` in the damage application function,
after applying damage but before checking for death.

---

## COMPLETION REPORT FOR COMBAT-UI-2

1. Confirm spell bar renders at 90×72px slots — list actual positions
2. Confirm spell slot hit detection updated to new coordinates
3. Confirm EX spells show gold border and EX badge
4. Confirm on-cooldown slots show countdown number prominently
5. Confirm enemy HP bars are 10px tall with name label above
6. Confirm boss phase indicator shows on boss HP bars
7. Confirm shield HP bar overlays correctly during shield phase
8. Confirm combo counter visible and pulses above 10 combo
9. Confirm kill callouts spawn as floating text on kill
10. Confirm tactical hint fires after 3 consecutive direct hits (test this)
11. Confirm enemy damage reaction taunts appear in DM area on heavy hits
12. Confirm game loads and runs without errors

---

*COMBAT-UI-2 — Claude Chat Architect Layer · 2026-03-26*
*After both parts complete, commit with:*
*`feat: combat UI overhaul — sprites scaled, HUD decluttered, spell bar redesigned, AI battle integration`*

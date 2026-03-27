# NEON DUNGEON — INSTRUCTION BLOCK 1.4-FIX
## Phase 1 Verification Failure Remediation
### Claude Chat Architect Layer · 2026-03-26
### Fixes items 3, 6, 7, 8, 9, 11, 12, 13 from Phase 1 Final Verification

---

> **SCOPE**: Fix only the 8 failing items listed below. Do not touch anything else.
> All Phase 1.3 dodge window failures are INTENTIONAL — Block 1.4 replaced that system.
> Do not re-implement any dodge window code.

---

## PRE-IMPLEMENTATION SCAN

Locate and report the exact names/locations of:

1. The `checkPhase()` function (boss phase threshold logic)
2. The `hpBar()` function (enemy HP bar rendering)
3. The `deal()` function (damage application to enemies)
4. The `arcShield` buff definition and where it is applied to `theArchitect`
5. The combat state variable that pauses/resumes the combat loop (e.g. a `paused` flag, a state machine string, etc.)
6. The `renderReactionPhase()` function — specifically the threat color / bubble border section

Report all six before writing any code.

---

## FIX 1 — Boss phase thresholds (Items 6 & 7)

Find `checkPhase()`. Replace the threshold expression with the correct values:

**Current (wrong):**
```javascript
pct > .67 ? 1 : pct > .34 ? 2 : 3
```

**Replace with:**
```javascript
pct > .60 ? 1 : pct > .25 ? 2 : 3
```

Phase 2 must trigger at ≤ 60% HP. Phase 3 must trigger at ≤ 25% HP.
Verify the expression reads as: "if HP percent is above 60%, phase 1. If above 25%, phase 2. Otherwise phase 3."

---

## FIX 2 — Combat pause and banner during phase transition (Item 8)

Find `checkPhase()`. Currently it calls `ability.fn()` and `DM.say()` with no pause.

Replace the phase transition call with the following pattern. Use the actual pause/resume mechanism
found in the pre-scan — do not invent a new one, use what already exists:

```javascript
// When a phase transition is detected (new phase !== current phase):

// 1. Pause combat using existing pause mechanism
// (use whatever flag/state variable controls combat ticking — e.g. combat.paused = true)
setPauseCombat(true); // REPLACE with actual pause call

// 2. Display phase transition banner for 2500ms
showPhaseBanner(newPhaseText, () => {
    // 3. Resume combat after banner
    setPauseCombat(false); // REPLACE with actual resume call
});
```

Add the `showPhaseBanner` function if it does not already exist:

```javascript
function showPhaseBanner(text, onComplete) {
    // Create or reuse a full-width overlay element
    // If the game uses canvas-only rendering, draw it in the render loop for 2500ms
    // If the game uses HTML overlays, create a temporary DOM element

    // --- CANVAS VERSION (use if game is canvas-only) ---
    let elapsed = 0;
    const duration = 2500;
    const prevTick = combat.tick; // store existing tick if needed

    function bannerFrame(dt) {
        elapsed += dt;

        // Draw dark overlay
        ctx.save(); // use actual ctx variable
        ctx.fillStyle = 'rgba(10,10,26,0.92)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Banner box
        const bx = 40;
        const by = canvas.height / 2 - 35;
        const bw = canvas.width - 80;
        const bh = 70;
        ctx.fillStyle = '#0a0a1a';
        ctx.fillRect(bx, by, bw, bh);
        ctx.strokeStyle = '#ff4444';
        ctx.lineWidth = 2;
        ctx.strokeRect(bx, by, bw, bh);

        // Phase transition text
        ctx.font = '10px "Press Start 2P"';
        ctx.fillStyle = '#ff4444';
        ctx.textAlign = 'center';
        ctx.fillText(text, canvas.width / 2, canvas.height / 2 + 4);
        ctx.textAlign = 'left';
        ctx.restore();

        if (elapsed >= duration) {
            if (onComplete) onComplete();
        }
    }

    // Register bannerFrame to run each tick during the pause period
    // Use the existing animation/tick registration mechanism
    // ADAPT to match how the game schedules per-frame draw calls
    combat._bannerFrame = bannerFrame; // placeholder — adapt to actual pattern
}
```

**Important:** If the game already has a pause mechanism that stops `requestAnimationFrame` entirely,
the banner must be drawn in its own `requestAnimationFrame` loop during the pause. If the game has
a render loop that continues while paused (just skipping combat logic), hook into that instead.
Use whichever approach matches the existing architecture — do not introduce a second render loop.

---

## FIX 3 — Boss HP bar color by phase (Item 9)

Find `hpBar()`. Locate where the HP bar fill color is set.

Currently it uses generic HP%-based colors. Add a phase-aware override BEFORE the generic logic:

```javascript
// Add BEFORE the existing color logic in hpBar():
if (enemy.isBoss && enemy.phase) {
    if (enemy.phase === 3) {
        // Phase 3: pulsing red
        const pulse = 0.7 + Math.sin(Date.now() / 200) * 0.3;
        ctx.globalAlpha = pulse; // use actual ctx variable
        barColor = '#ff4444';
    } else if (enemy.phase === 2) {
        barColor = '#ff8800';
    } else {
        barColor = '#00ffff'; // phase 1 default cyan
    }
    // Apply barColor to the HP bar fill
    // Then reset ctx.globalAlpha = 1.0 after drawing the bar if phase 3 pulse was applied
}
// existing generic HP%-based color logic continues below for non-boss enemies
```

Replace `barColor` with whatever variable name the existing `hpBar()` function uses for the fill color.
Reset `ctx.globalAlpha = 1.0` immediately after drawing the phase 3 bar.

---

## FIX 4 — Shield phase as HP pool, not DEF buff (Items 11, 12, 13)

This is the largest fix. Three parts.

### Part A — Redefine arcShield on theArchitect

Find where `arcShield` is defined and applied to `theArchitect`.

Currently: `addBuff('arcShield', { def: 8, turns: 99 })`

Replace with a shield HP pool on the enemy object directly (not a buff):

```javascript
// When theArchitect activates shield phase, instead of addBuff:
enemy.shieldHp = Math.floor(enemy.maxHp * 0.15); // 15% of max HP as shield pool
enemy.shieldActive = true;
DM.say(`${enemy.name} ACTIVATES ENERGY BARRIER! ARMOR-PIERCE REQUIRED.`, 'warning');
// Remove the arcShield DEF buff application entirely
```

If `arcShield` is defined in a buffs data table rather than inline, update that definition to be
a no-op (empty object `{}`) so it no longer grants DEF — the shield behavior is now handled by
`shieldHp` / `shieldActive` on the enemy object directly.

Also add `shieldHp: 0, shieldActive: false` as default properties on enemy initialization
(same place `telegraph: null` was added in Block 1.1).

### Part B — Add piercing interception in deal()

Find the `deal()` function (damage application to enemies). At the START of the function,
before any damage is applied to enemy HP, add:

```javascript
// --- SHIELD PHASE INTERCEPTION ---
if (enemy.shieldActive && enemy.shieldHp > 0) {
    const hasArmorPierce = spell && spell.tags && spell.tags.includes('armor_pierce');

    if (hasArmorPierce) {
        // Piercing spell damages the shield pool
        enemy.shieldHp -= damage;
        Arena.spawnText(`SHIELD -${damage}`, enemy, '#00ffff');

        if (enemy.shieldHp <= 0) {
            // Shield broken
            enemy.shieldHp = 0;
            enemy.shieldActive = false;
            // Stun the boss for 1 turn
            addDebuff(enemy, 'stun', { turns: 1 }); // use actual debuff application function
            DM.say('BARRIER SHATTERED — SYSTEMS EXPOSED', 'success');
            Arena.spawnText('SHIELD BROKEN!', enemy, '#ffd700');
        }
        return; // damage absorbed by shield — do NOT reduce enemy HP
    } else {
        // Non-piercing spell: blocked entirely
        Arena.spawnText('BLOCKED', enemy, '#888888');
        return; // damage blocked — do NOT reduce enemy HP
    }
}
// --- END SHIELD INTERCEPTION ---
// existing damage application continues below
```

**Note:** `spell` must be the spell object currently being applied. If `deal()` does not currently
receive the spell as a parameter, add it as an optional parameter: `function deal(enemy, damage, spell = null)`.
Update all existing `deal()` call sites to pass the spell where available, and pass `null` where
the source is auto-attack or environmental (no spell object).

### Part C — Add armor_pierce tags to qualifying spells

Scan existing attack spell definitions. Add `tags: [...existing, 'armor_pierce']` to spells that
thematically fit piercing/penetration. Apply to **3–5 spells** using this criteria:

- Heavy energy weapons / overload-type attacks: YES
- Tech/hack attacks that bypass defenses: YES
- Standard physical slashes or shots: NO
- AoE area spells: NO (too powerful against shield)
- Execute/finisher spells: YES if single-target

Report which spells received `armor_pierce` in the completion report.

---

## FIX 5 — LETHAL blink on reaction bubble (Item 3)

Find `renderReactionPhase()`. Locate where `threatColor` is applied to the bubble border
(the `_drawMangaBubble` call and/or `ctx.shadowColor`).

Add blink logic for LETHAL tier:

```javascript
// Before calling _drawMangaBubble and applying shadow:
const isLethal = rp.telegraph.threatLevel === 'LETHAL';
const blinkVisible = isLethal ? Math.floor(Date.now() / 500) % 2 === 0 : true;

if (!blinkVisible) {
    // On blink-off frames: draw bubble with dim/no border instead of skipping entirely
    // This keeps the bubble visible but removes the threatening glow
    ctx.shadowBlur = 0;
    _drawMangaBubble(ctx, bubbleX, bubbleY, bubbleW, bubbleH, 'rgba(100,100,100,0.3)');
} else {
    ctx.shadowColor = threatColor;
    ctx.shadowBlur = 18;
    _drawMangaBubble(ctx, bubbleX, bubbleY, bubbleW, bubbleH, threatColor);
    ctx.shadowBlur = 0;
}
```

The bubble text content (attack name, taunt, threat badge) renders every frame regardless of blink.
Only the border color and glow pulse on/off. This gives a threatening flash effect without
the bubble disappearing entirely.

---

## COMPLETION REPORT FOR BLOCK 1.4-FIX

When done, report each item:

1. **Fix 1 (thresholds):** Confirm new expression: phase 2 triggers at ≤60%, phase 3 at ≤25%
2. **Fix 2 (banner):** Describe how combat pause was implemented — what variable/mechanism was used
3. **Fix 3 (HP bar):** Confirm boss HP bar color now reflects `enemy.phase` — cyan / orange / pulsing red
4. **Fix 4A (arcShield):** Confirm `arcShield` DEF buff removed; `shieldHp`/`shieldActive` added to enemy
5. **Fix 4B (deal()):** Confirm shield interception added; confirm `deal()` signature change if made
6. **Fix 4C (armor_pierce):** List exact spell names that received `armor_pierce` tag
7. **Fix 5 (blink):** Confirm LETHAL bubble border blinks at ~1Hz
8. Any part that could NOT be implemented and why
9. Confirm game loads and runs without errors after all fixes

---

## RE-VERIFICATION TARGETS

After this fix block is complete, re-run ONLY these checklist items:

```
[ ] Item 3  — LETHAL warnings blink at ~1Hz on reaction bubble border
[ ] Item 6  — Phase 2 triggers at exactly 60% boss HP
[ ] Item 7  — Phase 3 triggers at exactly 25% boss HP
[ ] Item 8  — Phase transition pauses combat and shows banner for 2500ms
[ ] Item 9  — Boss HP bar shows cyan (phase 1) / orange (phase 2) / pulsing red (phase 3)
[ ] Item 11 — Shield phase blocks damage from non-piercing spells
[ ] Item 12 — Armor-pierce spells damage shield HP pool correctly
[ ] Item 13 — Shield break stuns boss for 1 turn
```

All 8 must pass. Report results. If all pass, Phase 1 is complete.

---

*Block 1.4-FIX generated by Claude Chat Architect Layer · 2026-03-26*
*Execute in Claude Code. Report back when all 8 re-verification items pass.*

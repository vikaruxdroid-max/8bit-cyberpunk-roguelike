# NEON DUNGEON — INSTRUCTION BLOCK 4.1
## AI DUNGEON MASTER NARRATION
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Phase 3 complete (commit 205d862), Worker live at https://neon-dungeon-ai.neondungeon.workers.dev

---

> **HARD RULES — READ BEFORE IMPLEMENTING ANYTHING:**
> 1. The game must run FULLY with zero AI calls. All AI is progressive enhancement.
> 2. If the worker is unreachable or times out, fall back to static content SILENTLY. No error shown to player.
> 3. NEVER call AI mid-combat. Only at: boss intro, room transition, post-run summary, zone hover.
> 4. No API key in the game HTML file. Ever. The worker holds the key.
> 5. Timeout: 3000ms. If no response in 3s, use fallback immediately.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. Where boss combat is initiated — the moment just before combat starts against a boss enemy
2. Where room transitions occur — specifically the moment after a room is cleared and before the next room loads (distinct from the screen transition glitch added in Block 3.4)
3. Where the run summary / death screen is rendered — the screen shown after the player wins or dies
4. The world map rendering — specifically where zone hover/selection is handled
5. Any existing narration or flavor text display system — where DM.say() output is rendered, or any text box currently used for in-game messages

Report all five before writing any code.

---

## STEP 1 — AI SERVICE MODULE

Add this as a self-contained section in the game JS. This is the only place the worker URL lives:

```javascript
// ============================================================
// AI SERVICE — Phase 4.1
// Worker: https://neon-dungeon-ai.neondungeon.workers.dev
// ============================================================

const AIService = {
    WORKER_URL: 'https://neon-dungeon-ai.neondungeon.workers.dev',
    TIMEOUT_MS: 3000,
    enabled: true,   // set false if worker is unreachable — disables for session

    async call(feature, payload) {
        if (!this.enabled) return null;

        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), this.TIMEOUT_MS);

        try {
            const response = await fetch(this.WORKER_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feature, payload }),
                signal: controller.signal
            });

            clearTimeout(timeout);

            if (!response.ok) throw new Error(`Worker error: ${response.status}`);

            const data = await response.json();
            return data.result || null;

        } catch (err) {
            clearTimeout(timeout);
            if (err.name === 'AbortError') {
                console.warn('[AI] Timeout — using fallback');
            } else {
                console.warn('[AI] Unreachable — disabling for session:', err.message);
                this.enabled = false;
            }
            return null;
        }
    }
};
```

---

## STEP 2 — STATIC FALLBACK CONTENT

These are used when AIService returns null. Never shown as errors — just seamless fallbacks.

```javascript
const AI_FALLBACKS = {
    boss_narration: {
        'quantumBoss':          'The Quantum Boss materializes from fragmented data. Only those who understand the pattern survive.',
        'theArchitect':         'The Architect regards you as an anomaly to be corrected. Correct it first.',
        'secret_the_archivist': 'The Archivist has catalogued every way you can die. It intends to demonstrate.',
        'secret_phantom_executive': 'The Phantom Executive has already filed the paperwork for your termination.',
        'secret_null_prophet':  'The Null Prophet sees nothing in your future. It plans to make that literal.',
        'secret_chrome_duchess':'The Chrome Duchess finds your resistance aesthetically displeasing.',
        'secret_overclocked_priest': 'The Overclocked Priest moves faster than prayer. Faster than you.',
        'secret_binary_witch':  'The Binary Witch has already computed the outcome. It does not favor you.',
        '_default':             'Something ancient and hostile turns its attention toward you. Move carefully.'
    },
    zone_lore: {
        'neonNexus':        'Neon Nexus: where corporate light hides corporate rot, and every alley sells something illegal.',
        'voidSector':       'Void Sector: corrupted data made manifest, a place where reality has given up trying.',
        'corporateStrip':   'Corporate Strip: profit margins maintained in blood, quarterly reports filed over graves.',
        'rustMarket':       'Rust Market: everything here is broken, including the people selling it.',
        'theUndernet':      'The Undernet: the internet\'s basement, dark and cold and full of things that crawl.',
        'ghostDistrict':    'Ghost District: populated by signals and echoes of those who ran out of luck here.',
        'dataHighway':      'Data Highway: information moves fast here. So do the things hunting it.',
        'theCore':          'The Core: where the machine dreams. It does not dream of you surviving.',
        '_default':         'Another zone. Another set of things trying to kill you. Nothing changes.'
    },
    run_coaching: '▸ Missed counter opportunities were your primary damage amplifier.\n▸ Adapt your spell loadout to the zone ahead — not the zone behind.\n▸ Boss phases telegraph. Watch HP thresholds at 60% and 25%.',
    spell_commentary: 'Loadout is functional. Whether you are is another question.'
};

function getAIFallback(feature, key) {
    const pool = AI_FALLBACKS[feature];
    if (!pool) return null;
    if (typeof pool === 'string') return pool;
    return pool[key] || pool['_default'] || null;
}
```

---

## STEP 3 — NARRATION DISPLAY SYSTEM

A typewriter-style text box rendered on canvas. Used for boss intros and zone lore.

```javascript
const NarrationBox = {
    active: false,
    text: '',
    displayed: '',   // characters revealed so far
    charIndex: 0,
    charTimer: 0,
    charInterval: 35,  // ms per character
    displayTimer: 0,
    displayDuration: 4000,  // ms to show full text before auto-dismiss
    onComplete: null,
    style: 'dm',     // 'dm' (dungeon master) | 'lore' (zone lore)

    show(text, style, onComplete) {
        this.active = true;
        this.text = text || '';
        this.displayed = '';
        this.charIndex = 0;
        this.charTimer = 0;
        this.displayTimer = 0;
        this.style = style || 'dm';
        this.onComplete = onComplete || null;
    },

    update(dt) {
        if (!this.active) return;

        // Typewriter reveal
        if (this.charIndex < this.text.length) {
            this.charTimer += dt;
            while (this.charTimer >= this.charInterval && this.charIndex < this.text.length) {
                this.displayed += this.text[this.charIndex];
                this.charIndex++;
                this.charTimer -= this.charInterval;
            }
            return;
        }

        // Full text shown — start display timer
        this.displayTimer += dt;
        if (this.displayTimer >= this.displayDuration) {
            this.active = false;
            if (this.onComplete) this.onComplete();
        }
    },

    // Skip typewriter on click — show full text immediately
    skip() {
        if (!this.active) return false;
        if (this.charIndex < this.text.length) {
            this.displayed = this.text;
            this.charIndex = this.text.length;
            return true;
        }
        // If already fully shown, dismiss
        this.active = false;
        if (this.onComplete) this.onComplete();
        return true;
    },

    render(ctx, cw, ch) {
        if (!this.active || !this.displayed) return;

        const isDM = this.style === 'dm';
        const boxH = 80;
        const boxY = isDM ? 20 : ch - boxH - 20;
        const padding = 16;

        ctx.save();

        // Background
        ctx.fillStyle = 'rgba(5, 5, 20, 0.92)';
        ctx.fillRect(0, boxY, cw, boxH);

        // Border
        ctx.strokeStyle = isDM ? '#ff00ff' : '#00ffff';
        ctx.lineWidth = 1;
        ctx.strokeRect(0, boxY, cw, boxH);

        // Prefix label
        ctx.font = '7px "Press Start 2P"';
        ctx.fillStyle = isDM ? '#ff00ff' : '#00ffff';
        ctx.fillText(isDM ? '> DM:' : '> LORE:', padding, boxY + 18);

        // Narration text — wrap at canvas width
        ctx.font = '8px "Share Tech Mono"';
        ctx.fillStyle = isDM ? '#ffffff' : '#00ffff';
        const maxWidth = cw - padding * 2 - 60;
        const words = this.displayed.split(' ');
        let line = '';
        let lineY = boxY + 36;

        words.forEach(word => {
            const test = line + word + ' ';
            if (ctx.measureText(test).width > maxWidth && line !== '') {
                ctx.fillText(line, padding + 60, lineY);
                line = word + ' ';
                lineY += 16;
            } else {
                line = test;
            }
        });
        if (line) ctx.fillText(line, padding + 60, lineY);

        // Blinking cursor while typing
        if (this.charIndex < this.text.length) {
            const cursorVisible = Math.floor(Date.now() / 400) % 2 === 0;
            if (cursorVisible) {
                ctx.fillText('_', padding + 60 + ctx.measureText(line).width, lineY);
            }
        }

        // Skip hint (only after full text shown)
        if (this.charIndex >= this.text.length) {
            ctx.font = '6px "Press Start 2P"';
            ctx.fillStyle = '#555577';
            ctx.textAlign = 'right';
            ctx.fillText('[CLICK TO DISMISS]', cw - padding, boxY + boxH - 8);
            ctx.textAlign = 'left';
        }

        ctx.restore();
    }
};
```

---

## STEP 4 — BOSS INTRO NARRATION

Find the boss combat initiation point (pre-scan item 1). Before combat starts, fetch narration
and display it. Combat should be paused during display.

```javascript
async function showBossIntroNarration(boss, onComplete) {
    // Pause combat — use existing pause mechanism (GameState._phaseBanner.active or equivalent)
    setPauseCombat(true); // replace with actual pause call

    // Build payload
    const player = GameState.player; // use actual accessor
    const payload = {
        bossName:    boss.name,
        zoneName:    GameState.currentZone, // use actual zone accessor
        playerClass: player.class || player.type || 'Runner',
        playerSpells: (player.spells || []).map(s => s.name).filter(Boolean)
    };

    // Fetch AI narration (3s timeout, falls back silently)
    const narration = await AIService.call('boss_narration', payload)
        || getAIFallback('boss_narration', boss.id);

    if (!narration) {
        setPauseCombat(false);
        if (onComplete) onComplete();
        return;
    }

    // Display narration — resume combat when dismissed
    NarrationBox.show(narration, 'dm', () => {
        setPauseCombat(false);
        if (onComplete) onComplete();
    });
}
```

Hook this into the boss combat initiation. Call `showBossIntroNarration(boss, startCombat)` 
instead of starting combat directly. The `onComplete` callback starts combat after narration dismisses.

Replace `setPauseCombat` with the actual pause/resume mechanism confirmed in Block 1.4-FIX.

---

## STEP 5 — ZONE LORE ON WORLD MAP

Find where the world map renders zone hover/selection (pre-scan item 4).

```javascript
// Zone lore cache — fetch once per session per zone, not on every hover
const _zoneLoreCache = {};

async function fetchZoneLore(zoneId) {
    if (_zoneLoreCache[zoneId]) return; // already fetched

    const zoneName = ZONE_DISPLAY_NAMES[zoneId] || zoneId;
    // Add zone display name mapping — adapt to actual zone name strings:
    const lore = await AIService.call('zone_lore', { zoneName })
        || getAIFallback('zone_lore', zoneId);

    _zoneLoreCache[zoneId] = lore || '';
}

// Call this when player hovers over or selects a zone on the world map:
// fetchZoneLore(zoneId); — fire and forget, result cached for render

// In world map render, display cached lore below the zone name:
function renderZoneLore(ctx, zoneId, x, y) {
    const lore = _zoneLoreCache[zoneId];
    if (!lore) return;

    ctx.save();
    ctx.font = '7px "Share Tech Mono"';
    ctx.fillStyle = '#557755';
    ctx.globalAlpha = 0.85;

    // Simple single-line truncation for world map context
    const maxLen = 60;
    const display = lore.length > maxLen ? lore.substring(0, maxLen - 2) + '..' : lore;
    ctx.fillText(display, x, y);
    ctx.restore();
}
```

Add zone display names mapping:
```javascript
const ZONE_DISPLAY_NAMES = {
    neonNexus:      'Neon Nexus',
    voidSector:     'Void Sector',
    corporateStrip: 'Corporate Strip',
    rustMarket:     'Rust Market',
    theUndernet:    'The Undernet',
    ghostDistrict:  'Ghost District',
    dataHighway:    'Data Highway',
    theCore:        'The Core'
};
```

---

## STEP 6 — SPELL COMMENTARY ON SWAP SCREEN

Find the spell swap screen (shown after each room victory). After the player's current loadout
is displayed but before they make a swap decision, fetch a one-liner commentary:

```javascript
async function fetchSpellCommentary(spells) {
    const spellNames = (spells || []).map(s => s.name).filter(Boolean);
    if (spellNames.length === 0) return null;

    return await AIService.call('spell_commentary', { spells: spellNames })
        || getAIFallback('spell_commentary', null);
}
```

Display the result in the spell swap UI as a small flavor line below the loadout display.
Fetch it once when the swap screen opens — do not re-fetch on each swap.

---

## STEP 7 — HOOK NARRATIONBOX INTO RENDER AND UPDATE LOOPS

Update loop:
```javascript
NarrationBox.update(deltaTime);
```

Render loop — AFTER all game elements, BEFORE GlitchTransition:
```javascript
NarrationBox.render(ctx, canvas.width, canvas.height);
```

Hook click-to-skip into the input handler — at the top, before other handlers:
```javascript
if (NarrationBox.active) {
    NarrationBox.skip();
    return;
}
```

---

## STEP 8 — WIRE INTO UI.show() INTERCEPT

The GlitchTransition from Block 3.4 already intercepts all screen changes via `UI.show()`.
Narration does NOT need to intercept screen changes — it overlays the current screen.
No changes needed to the screen transition system.

---

## COMPLETION REPORT FOR BLOCK 4.1

1. Confirm `AIService` module added with correct worker URL
2. Confirm boss intro narration fires before combat starts — combat pauses during display
3. Confirm zone lore appears on world map for at least 3 zones (test by hovering)
4. Confirm spell commentary appears on spell swap screen
5. Confirm fallbacks work — temporarily set `AIService.enabled = false` and verify game still runs normally
6. Confirm timeout works — the game does not hang if worker is slow
7. Actual function names used for pause/resume (replacing setPauseCombat)
8. Confirm NarrationBox click-to-skip works
9. Confirm typewriter effect renders correctly with Share Tech Mono font
10. Confirm game loads and runs without errors

---

*Block 4.1 — Claude Chat Architect Layer · 2026-03-26*
*Worker URL: https://neon-dungeon-ai.neondungeon.workers.dev*
*Model: claude-haiku-4-5*
*Block 4.2 (post-run coaching) depends on 4.1 AIService module being present.*

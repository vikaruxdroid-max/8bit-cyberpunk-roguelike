# NEON DUNGEON — INSTRUCTION BLOCK 4.2
## POST-RUN AI COACHING
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Block 4.1 complete (AIService module must exist)

---

> **SCOPE**: Show 3 AI-generated coaching bullet points on the run summary/death screen.
> Fires ONCE after run ends. Non-blocking — game shows summary immediately, coaching
> appears when it arrives (or fallback if it doesn't).

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. The run summary / death screen render function
2. Where run statistics are tracked — damage dealt, damage taken, deaths, zones cleared, missed counters
3. Whether missed counter opportunities are currently tracked — if not, add a counter

---

## STEP 1 — TRACK MISSED COUNTER OPPORTUNITIES

In the reaction phase resolution (Block 1.4), when `resolveReactionPhase(null)` is called
(timer expired, no player action), increment a missed counter stat:

```javascript
// In resolveReactionPhase(), when spell is null (no action):
GameState.runStats = GameState.runStats || {};
GameState.runStats.missedCounters = (GameState.runStats.missedCounters || 0) + 1;
```

Also initialize `runStats` at run start:
```javascript
GameState.runStats = {
    missedCounters: 0,
    damageDealt: 0,
    damageTaken: 0,
    zonesCleared: 0,
    outcome: 'defeat'  // set to 'victory' on win
};
```

Hook `damageDealt` and `damageTaken` into the relevant combat functions if not already tracked.

---

## STEP 2 — COACHING STATE

Add to game state:

```javascript
GameState.aiCoaching = {
    text: null,       // null = not yet fetched, string = result or fallback
    loading: false,   // true while fetch is in flight
    dots: 0,          // animation counter for loading indicator
    dotsTimer: 0
};
```

---

## STEP 3 — FETCH COACHING ON RUN END

Find where the run ends (win or death). After updating final stats, fire the coaching fetch:

```javascript
async function fetchRunCoaching() {
    const stats = GameState.runStats;
    GameState.aiCoaching.loading = true;
    GameState.aiCoaching.text = null;

    const payload = {
        outcome:        stats.outcome || 'defeat',
        zonesCleared:   stats.zonesCleared || 0,
        missedCounters: stats.missedCounters || 0,
        damageRatio:    stats.damageTaken > 0
            ? (stats.damageDealt / stats.damageTaken).toFixed(2)
            : 'N/A'
    };

    const result = await AIService.call('run_coaching', payload)
        || AI_FALLBACKS.run_coaching;

    GameState.aiCoaching.text = result;
    GameState.aiCoaching.loading = false;
}
```

Call `fetchRunCoaching()` immediately when the run ends — do NOT await it. Fire and forget:
```javascript
fetchRunCoaching(); // non-blocking — result arrives asynchronously
```

---

## STEP 4 — RENDER COACHING ON SUMMARY SCREEN

In the run summary render function, add a coaching section:

```javascript
function renderAICoaching(ctx, x, y, maxWidth) {
    const coaching = GameState.aiCoaching;

    ctx.save();

    // Section header
    ctx.font = '7px "Press Start 2P"';
    ctx.fillStyle = '#ff00ff';
    ctx.fillText('> AI DEBRIEF:', x, y);
    y += 18;

    if (coaching.loading) {
        // Animated loading dots
        coaching.dotsTimer += 16; // approximate dt
        if (coaching.dotsTimer > 400) {
            coaching.dots = (coaching.dots + 1) % 4;
            coaching.dotsTimer = 0;
        }
        ctx.font = '7px "Share Tech Mono"';
        ctx.fillStyle = '#555577';
        ctx.fillText('ANALYZING RUN DATA' + '.'.repeat(coaching.dots), x, y);

    } else if (coaching.text) {
        // Render bullet points
        const lines = coaching.text.split('\n').filter(l => l.trim());
        ctx.font = '7px "Share Tech Mono"';
        lines.forEach(line => {
            ctx.fillStyle = line.startsWith('▸') ? '#00ffff' : '#aaaaaa';
            // Wrap long lines
            const words = line.split(' ');
            let current = '';
            words.forEach(word => {
                const test = current + word + ' ';
                if (ctx.measureText(test).width > maxWidth && current !== '') {
                    ctx.fillText(current, x, y);
                    current = '    ' + word + ' '; // indent continuation
                    y += 13;
                } else {
                    current = test;
                }
            });
            if (current.trim()) { ctx.fillText(current, x, y); y += 13; }
            y += 4; // gap between bullets
        });
    }

    ctx.restore();
}
```

Call `renderAICoaching(ctx, x, y, maxWidth)` in the run summary render function.
Position it below the run statistics block. Adapt `x`, `y`, `maxWidth` to fit the
existing summary layout.

---

## COMPLETION REPORT FOR BLOCK 4.2

1. Confirm `runStats` initializes at run start
2. Confirm missed counter increments correctly when reaction window expires
3. Confirm coaching fetch fires on run end (both win and death)
4. Confirm loading dots animate while fetch is in flight
5. Confirm coaching text renders on summary screen after arrival
6. Confirm fallback text renders if AI unavailable
7. Confirm game loads and runs without errors

---

---

# NEON DUNGEON — INSTRUCTION BLOCK 4.3
## AI DIFFICULTY TUNING
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Block 4.2 complete

---

> **SCOPE**: Silently adjust enemy stats for the next zone based on player performance.
> Player never sees this. No UI. Pure background adaptation.
> If AI returns no result: preset difficulty curve unchanged.
> Tuning applies ONLY to the next zone — not retroactively.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. Where zone boss defeat is processed — the moment after the boss dies and before the next zone loads
2. Where enemy stats are applied when a room loads — specifically where enemy HP/ATK values are set from definitions
3. Whether a per-run difficulty multiplier already exists anywhere

---

## STEP 1 — PERFORMANCE METRICS TRACKING

Add to `GameState.runStats` (initialized in Block 4.2):

```javascript
GameState.runStats.bossPerformance = []; // one entry per boss defeated
```

After each boss fight ends, record performance:

```javascript
function recordBossPerformance(boss, turnsToKill, hpOnEntry) {
    GameState.runStats.bossPerformance.push({
        bossId:          boss.id,
        zone:            GameState.currentZone,
        hpPct:           Math.round((hpOnEntry / GameState.player.maxHp) * 100),
        bossTurns:       turnsToKill,
        counterMissRate: calculateCounterMissRate() // see below
    });
}

function calculateCounterMissRate() {
    const stats = GameState.runStats;
    const total = (stats.missedCounters || 0) + (stats.successfulCounters || 0);
    if (total === 0) return 0;
    return Math.round((stats.missedCounters / total) * 100);
}
```

Also track `successfulCounters` — increment in `resolveReactionPhase()` when grade is
`nullify`, `silence`, or `absorb`.

---

## STEP 2 — DIFFICULTY MODIFIER STATE

```javascript
GameState.difficultyMod = {
    enemyStatMultiplier: 1.0,
    abilityProbability: 1.0,
    lastReasoning: null  // for debug only — never shown to player
};
```

---

## STEP 3 — FETCH TUNING BETWEEN ZONES

Call this after zone boss defeat, before next zone loads:

```javascript
async function fetchDifficultyTuning(bossPerf) {
    if (!bossPerf) return;

    const payload = {
        hpPct:           bossPerf.hpPct,
        bossTurns:       bossPerf.bossTurns,
        counterMissRate: bossPerf.counterMissRate
    };

    const result = await AIService.call('difficulty_tuning', payload);

    if (!result) return; // no AI response — keep current multiplier

    try {
        // Result should be JSON string
        const tuning = typeof result === 'string' ? JSON.parse(result) : result;

        // Validate and clamp — never trust raw AI output without bounds check
        const statMult = Math.max(0.7, Math.min(1.5, parseFloat(tuning.enemyStatMultiplier) || 1.0));
        const abilProb = Math.max(0.7, Math.min(1.5, parseFloat(tuning.abilityProbability) || 1.0));

        GameState.difficultyMod.enemyStatMultiplier = statMult;
        GameState.difficultyMod.abilityProbability  = abilProb;
        GameState.difficultyMod.lastReasoning       = tuning.reasoning || '';

        console.log('[AI Difficulty]', statMult, abilProb, tuning.reasoning);
    } catch (e) {
        console.warn('[AI Difficulty] Failed to parse tuning response:', e.message);
        // Keep current multiplier — no change
    }
}
```

Call `fetchDifficultyTuning()` after boss death — fire and forget (non-blocking):
```javascript
const lastPerf = GameState.runStats.bossPerformance.slice(-1)[0];
fetchDifficultyTuning(lastPerf); // non-blocking
```

---

## STEP 4 — APPLY MULTIPLIER TO ENEMY STATS

Find where enemy HP and ATK are set when a room loads (pre-scan item 2).
Apply the difficulty multiplier:

```javascript
// When instantiating enemies for a room, after copying from definition:
function applyDifficultyMod(enemy) {
    const mod = GameState.difficultyMod;
    if (!mod || mod.enemyStatMultiplier === 1.0) return;

    enemy.maxHp = Math.round(enemy.maxHp * mod.enemyStatMultiplier);
    enemy.hp    = enemy.maxHp;
    enemy.atk   = Math.round(enemy.atk  * mod.enemyStatMultiplier);
    // Do NOT modify DEF or SPD — only HP and ATK scale
    // Do NOT apply to secret bosses or the final boss
}
```

Call `applyDifficultyMod(enemy)` on each enemy when the room loads, AFTER copying from
the definition but BEFORE adding to the active enemies list.

Skip application for:
- `enemy.isSecretBoss === true`
- `enemy.id === 'quantumBoss'` or `enemy.id === 'theArchitect'`

---

## COMPLETION REPORT FOR BLOCK 4.3

1. Confirm `bossPerformance` array records data after each boss fight
2. Confirm `difficultyMod` updates silently after boss defeat
3. Confirm enemy HP and ATK scale correctly in next zone
4. Confirm secret bosses and final boss are exempt from scaling
5. Confirm multiplier is clamped to 0.7–1.5 range regardless of AI output
6. Test: complete a zone very easily — confirm next zone enemies are slightly harder
7. Confirm game loads and runs without errors

---

---

# NEON DUNGEON — INSTRUCTION BLOCK 4.4
## ZONE LORE POLISH + PHASE 4 FINAL VERIFICATION
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Block 4.3 complete

---

> **SCOPE**: Final polish pass on AI integration. Ensure all AI features degrade
> gracefully. Add a subtle AI indicator so players know when AI content is live.
> Run full Phase 4 verification checklist.

---

## STEP 1 — AI STATUS INDICATOR

Add a subtle indicator in the game UI that shows when AI content is active.
This is a small dot in the corner — not obtrusive:

```javascript
function renderAIStatusDot(ctx, cw, ch) {
    if (!AIService.enabled) return;

    const dotColor = '#00ff41';
    const x = cw - 12;
    const y = 12;

    ctx.save();
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    ctx.fillStyle = dotColor;
    ctx.shadowColor = dotColor;
    ctx.shadowBlur = 6;
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.restore();
}
```

Call this in the main render pass. When `AIService.enabled` is false (worker unreachable),
the dot is absent — player never knows AI was attempted.

---

## STEP 2 — GRACEFUL DEGRADATION TEST

Add a test mode toggle (debug only — remove before final ship):

```javascript
// Debug toggle — set via browser console: AIService.enabled = false
// Verify game runs identically without AI
```

This is not a UI feature — just a note for testing. No code needed.

---

## STEP 3 — RATE LIMIT GUARD

Prevent excessive API calls if the player rapidly enters/exits the world map:

```javascript
const _aiCallTimestamps = {};

function canCallAI(feature, cooldownMs) {
    const now = Date.now();
    const last = _aiCallTimestamps[feature] || 0;
    if (now - last < cooldownMs) return false;
    _aiCallTimestamps[feature] = now;
    return true;
}
```

Apply cooldowns:
```javascript
// Before zone lore fetch:
if (!canCallAI('zone_lore_' + zoneId, 30000)) return; // 30s cooldown per zone

// Boss narration has no cooldown — only fires once per boss encounter

// Spell commentary:
if (!canCallAI('spell_commentary', 5000)) return; // 5s cooldown
```

---

## PHASE 4 FINAL VERIFICATION CHECKLIST

Run after all blocks (4.1–4.4) are complete.

```
AI SERVICE (4.1)
[ ] AIService module present with correct worker URL
[ ] Worker URL: https://neon-dungeon-ai.neondungeon.workers.dev
[ ] Timeout fires at 3000ms — game does not hang
[ ] AIService.enabled = false disables all AI calls silently
[ ] Game runs fully with AIService.enabled = false (fallbacks only)

BOSS NARRATION (4.1)
[ ] Narration box appears before boss combat starts
[ ] Combat pauses during narration display
[ ] Typewriter effect reveals text character by character
[ ] Click-to-skip works — shows full text immediately or dismisses
[ ] Auto-dismisses after 4000ms
[ ] Combat resumes after dismissal
[ ] Fallback fires when AI unavailable — no error shown

ZONE LORE (4.1)
[ ] Lore text appears on world map for hovered/selected zones
[ ] Fetched once per zone per session — not on every hover
[ ] 30s cooldown prevents rapid re-fetching
[ ] Fallback lore renders when AI unavailable

SPELL COMMENTARY (4.1)
[ ] One-liner appears on spell swap screen
[ ] Fetched once when swap screen opens — not per swap
[ ] Fallback renders when AI unavailable

POST-RUN COACHING (4.2)
[ ] Coaching section appears on run summary screen
[ ] Loading dots animate while fetch is in flight
[ ] 3 bullet points render after AI responds
[ ] Fallback bullets render if AI unavailable
[ ] missedCounters tracks correctly

DIFFICULTY TUNING (4.3)
[ ] bossPerformance recorded after each boss fight
[ ] difficultyMod updates silently — no player-visible indication
[ ] Enemy HP/ATK scale in next zone after easy boss fight
[ ] Secret bosses exempt from scaling
[ ] Multiplier clamped to 0.7x–1.5x regardless of AI output

GENERAL
[ ] AI status dot visible in corner when AIService.enabled = true
[ ] No console errors related to AI system during normal play
[ ] No performance impact — AI calls are all async/non-blocking
[ ] Worker URL in AIService is the only place it appears in the game file
```

When all items pass: commit with message:
`feat: Phase 4 complete — AI narration, coaching, difficulty tuning, zone lore`

Then tell Claude Chat: "Phase 4 complete and verified."

---

*Blocks 4.2, 4.3, 4.4 — Claude Chat Architect Layer · 2026-03-26*
*Worker: https://neon-dungeon-ai.neondungeon.workers.dev*
*Model: claude-haiku-4-5*
*Execute in order: 4.2 → 4.3 → 4.4 → Final Verification*
*Do not begin Phase 5 until Phase 4 final verification passes.*

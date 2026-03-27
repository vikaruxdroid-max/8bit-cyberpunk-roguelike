# NEON DUNGEON — INSTRUCTION BLOCK 3.3
## ENEMY ENTRANCE & DEATH ANIMATIONS
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Block 3.2 complete

---

> **SCOPE**: Glitch-in entrance animation when enemies appear in a room.
> Enhanced death animation: desaturation + pixel scatter.
> Elite/boss deaths add screen flash before scatter.
> All animations canvas-rendered, no DOM manipulation.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. Where enemies are rendered each frame — the function that draws enemy sprites to canvas
2. When enemies are first introduced to a room — the moment enemy objects are added to combat state
3. The existing kill cam implementation — what it currently does and where it runs
4. How enemy sprite images are stored and drawn (drawImage calls, sprite sheets, etc.)
5. Whether enemies have a `renderX` / `renderY` or similar position property used for drawing

Report all five before writing any code.

---

## STEP 1 — ENTRANCE ANIMATION STATE

Add to each enemy object when it is created for a room:

```javascript
// Add to enemy initialization (same place telegraph: null was added in Block 1.1):
enemy.entranceAnim = {
    active: true,
    frame: 0,
    totalFrames: 12,
    complete: false
};
```

---

## STEP 2 — ENTRANCE GLITCH RENDER

In the enemy render function, check `entranceAnim.active`. If true, apply horizontal
displacement that decays over 12 frames:

```javascript
function renderEnemy(ctx, enemy) {
    const ea = enemy.entranceAnim;

    if (ea && ea.active && !ea.complete) {
        const progress = ea.frame / ea.totalFrames;
        const maxOffset = 20 * (1 - progress);
        const offsetX = (Math.random() - 0.5) * maxOffset * 2;

        // Ghost copy on early frames (scanline tear)
        if (ea.frame < 6) {
            ctx.save();
            ctx.globalAlpha = 0.3 * (1 - progress);
            drawEnemySprite(ctx, enemy, enemy.renderX + offsetX * 1.5, enemy.renderY - 8);
            ctx.restore();
        }

        // Main sprite fading in with displacement
        ctx.save();
        ctx.globalAlpha = 0.4 + progress * 0.6;
        drawEnemySprite(ctx, enemy, enemy.renderX + offsetX, enemy.renderY);
        ctx.restore();

        ea.frame++;
        if (ea.frame >= ea.totalFrames) {
            ea.active = false;
            ea.complete = true;
        }
        return;
    }

    // Normal render
    drawEnemySprite(ctx, enemy, enemy.renderX, enemy.renderY);
}
```

`drawEnemySprite(ctx, enemy, x, y)` wraps the existing sprite draw call.
Also trigger a short static audio cue on `ea.frame === 0` using the existing Web Audio system.

---

## STEP 3 — DEATH ANIMATION: DESATURATION + PIXEL SCATTER

```javascript
const DeathAnimations = [];

function spawnDeathAnimation(enemy) {
    const isElite = enemy.tier === 'advanced' || enemy.tier === 'boss';

    DeathAnimations.push({
        x: enemy.renderX,
        y: enemy.renderY,
        spriteKey: enemy.sprite,
        frame: 0,
        totalFrames: 12,
        isElite: isElite,
        chunks: generateDeathChunks(enemy.renderX, enemy.renderY)
    });

    if (isElite) {
        ScreenShake.trigger(8, 3); // use ScreenShake from Block 3.2
    }
}

function generateDeathChunks(x, y) {
    const chunks = [];
    const cols = 6, rows = 6;
    const spriteW = 56, spriteH = 104;
    const chunkW = spriteW / cols;
    const chunkH = spriteH / rows;

    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = 1 + Math.random() * 4;
            chunks.push({
                srcX: col * chunkW, srcY: row * chunkH,
                w: chunkW, h: chunkH,
                x: x + col * chunkW, y: y + row * chunkH,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 2,
                rotation: 0, alpha: 1
            });
        }
    }
    return chunks;
}

function updateDeathAnimations(dt) {
    for (let i = DeathAnimations.length - 1; i >= 0; i--) {
        const da = DeathAnimations[i];
        da.frame++;
        if (da.frame >= da.totalFrames) { DeathAnimations.splice(i, 1); continue; }

        if (da.frame >= 6) {
            da.chunks.forEach(chunk => {
                chunk.x  += chunk.vx * (dt / 16);
                chunk.y  += chunk.vy * (dt / 16);
                chunk.vy += 0.2;
                chunk.alpha = 1 - ((da.frame - 6) / 6);
                chunk.rotation += 0.05;
            });
        }
    }
}

function renderDeathAnimations(ctx) {
    DeathAnimations.forEach(da => {
        // Elite flash on frame 0
        if (da.isElite && da.frame === 0) {
            ctx.save();
            ctx.fillStyle = 'rgba(255,255,255,0.6)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.restore();
        }

        if (da.frame < 6) {
            // Phase A: desaturation
            ctx.save();
            ctx.globalAlpha = 1 - (da.frame / 12);
            ctx.filter = `saturate(${(1 - da.frame / 5) * 100}%)`;
            drawSpriteByKey(ctx, da.spriteKey, da.x, da.y);
            ctx.filter = 'none';
            ctx.restore();
        } else {
            // Phase B: scatter chunks
            da.chunks.forEach(chunk => {
                if (chunk.alpha <= 0) return;
                ctx.save();
                ctx.globalAlpha = chunk.alpha;
                ctx.translate(chunk.x + chunk.w / 2, chunk.y + chunk.h / 2);
                ctx.rotate(chunk.rotation * (da.frame - 6));
                ctx.translate(-(chunk.x + chunk.w / 2), -(chunk.y + chunk.h / 2));
                drawSpriteChunk(ctx, da.spriteKey, chunk.srcX, chunk.srcY, chunk.w, chunk.h, chunk.x, chunk.y);
                ctx.restore();
            });
        }
    });
}
```

**If sprites are Image objects in a cache:**
```javascript
function drawSpriteByKey(ctx, key, x, y) {
    const img = SpriteCache[key]; // use actual sprite cache variable
    if (img) ctx.drawImage(img, x, y, 56, 104);
}
function drawSpriteChunk(ctx, key, sx, sy, sw, sh, dx, dy) {
    const img = SpriteCache[key];
    if (img) ctx.drawImage(img, sx, sy, sw, sh, dx, dy, sw, sh);
}
```

**If sprites are procedurally drawn (no image files):** emit 36 colored square particles
from the enemy bounding box using the `Particle` class from Block 3.1 instead of scatter
chunks. Use the enemy's primary accent color as the particle color.

---

## STEP 4 — HOOK TO KILL EVENT

```javascript
// In kill/death resolution, BEFORE removing enemy:
if (enemy.hp <= 0) {
    spawnDeathAnimation(enemy);
    // existing kill logic continues...
}
```

---

## STEP 5 — HOOK UPDATE/RENDER

Update loop: `updateDeathAnimations(deltaTime);`
Render loop (after sprites, before UI): `renderDeathAnimations(ctx);`

---

## COMPLETION REPORT FOR BLOCK 3.3

1. Confirm entrance glitch plays on all enemies at room start, resolves in 12 frames
2. Confirm death desaturation on frames 0–5, scatter on frames 6–11
3. Confirm elite/boss deaths: white flash + heavier shake
4. Confirm existing kill cam still functions or confirm it was integrated
5. Note: image-based or procedural sprites — which path was taken
6. Confirm game loads and runs without errors

---
---

# NEON DUNGEON — INSTRUCTION BLOCK 3.4
## SCREEN TRANSITION GLITCH EFFECTS
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Block 3.3 complete

---

> **SCOPE**: Glitch transition effect between all major screen changes.
> Duration: ~250ms (15 frames at 60fps).
> Screen switch happens at midpoint. Input blocked during transition.
> Must not break existing screen state machine.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. How screens are currently changed — exact function or pattern (e.g. `GameState.screen = 'combat'`, `showScreen('worldmap')`)
2. The screen state variable name and all possible values
3. Whether screen changes happen instantly or already have transition logic
4. The main render function — confirm it checks screen state to decide what to draw

Report all four before writing any code.

---

## STEP 1 — GLITCH TRANSITION STATE

```javascript
// ============================================================
// SCREEN TRANSITION SYSTEM — Phase 3.4
// ============================================================

const GlitchTransition = {
    active: false,
    frame: 0,
    totalFrames: 15,
    pendingScreen: null,
    pendingCallback: null,
    phase: 'out',

    trigger(targetScreen, callback) {
        if (this.active) return;
        this.active = true;
        this.frame = 0;
        this.phase = 'out';
        this.pendingScreen = targetScreen;
        this.pendingCallback = callback || null;
    },

    update(stateRef) {
        if (!this.active) return;
        this.frame++;

        if (this.phase === 'out' && this.frame >= Math.floor(this.totalFrames / 2)) {
            this.phase = 'in';
            if (this.pendingScreen) {
                stateRef.screen = this.pendingScreen; // use actual screen state setter
            }
            if (this.pendingCallback) this.pendingCallback();
        }

        if (this.frame >= this.totalFrames) {
            this.active = false;
            this.frame = 0;
            this.pendingScreen = null;
            this.pendingCallback = null;
        }
    },

    render(ctx, cw, ch) {
        if (!this.active) return;

        const halfFrames = this.totalFrames / 2;
        const intensity = this.phase === 'out'
            ? this.frame / halfFrames
            : 1 - ((this.frame - halfFrames) / halfFrames);

        // Horizontal noise bands
        const bandCount = 6 + Math.floor(intensity * 6);
        for (let i = 0; i < bandCount; i++) {
            const bandY = Math.random() * ch;
            const bandH = 4 + Math.random() * 20;
            const offsetX = (Math.random() - 0.5) * 60 * intensity;
            ctx.save();
            ctx.globalAlpha = 0.3 + Math.random() * 0.4;
            ctx.drawImage(ctx.canvas, 0, bandY, cw, bandH, offsetX, bandY, cw, bandH);
            ctx.restore();
        }

        // RGB channel split at peak
        if (intensity > 0.6) {
            const split = intensity * 8;
            ctx.save();
            ctx.globalAlpha = 0.2 * intensity;
            ctx.globalCompositeOperation = 'screen';
            ctx.fillStyle = 'rgba(255,0,0,0.15)';
            ctx.fillRect(split, 0, cw, ch);
            ctx.fillStyle = 'rgba(0,0,255,0.15)';
            ctx.fillRect(-split, 0, cw, ch);
            ctx.globalCompositeOperation = 'source-over';
            ctx.restore();
        }

        // Cyan flash at midpoint
        if (this.phase === 'in' && this.frame === Math.floor(halfFrames)) {
            ctx.save();
            ctx.fillStyle = 'rgba(0,255,255,0.12)';
            ctx.fillRect(0, 0, cw, ch);
            ctx.restore();
        }

        // Dark vignette at peak
        if (intensity > 0.7) {
            ctx.save();
            ctx.fillStyle = `rgba(0,0,0,${(intensity - 0.7) * 1.5})`;
            ctx.fillRect(0, 0, cw, ch);
            ctx.restore();
        }
    }
};
```

If `ctx.drawImage(ctx.canvas, ...)` causes artifacts, replace with a snapshot canvas:
```javascript
// At start of render(), before band loop:
const snap = document.createElement('canvas');
snap.width = cw; snap.height = ch;
snap.getContext('2d').drawImage(ctx.canvas, 0, 0);
// Then use snap instead of ctx.canvas in drawImage calls
```

---

## STEP 2 — INTERCEPT ALL SCREEN CHANGES

Find every direct screen state assignment in the codebase. Replace with `GlitchTransition.trigger()`.

```javascript
// BEFORE: GameState.screen = 'combat';
// AFTER:  GlitchTransition.trigger('combat');

// BEFORE: GameState.screen = 'victory'; loadVictoryData();
// AFTER:  GlitchTransition.trigger('victory', () => loadVictoryData());
```

**Must intercept:**
- World map → Zone entry
- Zone entry → Combat start
- Combat → Victory screen
- Combat → Death/game over
- Victory → World map
- All main menu navigation

**Do NOT intercept:**
- Mini-game intro (has its own, Block 2.1)
- Phase transition banners (has its own, Block 1.2)
- Reaction phase overlay (not a screen change)

---

## STEP 3 — HOOKS

Update loop: `GlitchTransition.update(GameState);`
Render loop (very last call, on top of everything): `GlitchTransition.render(ctx, canvas.width, canvas.height);`

---

## STEP 4 — BLOCK INPUT DURING TRANSITION

At the top of ALL input handlers (click, keydown, etc.):

```javascript
if (GlitchTransition.active) return;
```

---

## COMPLETION REPORT FOR BLOCK 3.4

1. List all screen transitions found and confirm each now uses `GlitchTransition.trigger()`
2. Confirm transition is ~250ms and screen switches at midpoint
3. Confirm input is blocked during active transition
4. Confirm glitch bands and RGB split visible at peak
5. Confirm no transition fires during mini-game or phase banner
6. Any screen change that could NOT be intercepted and why
7. Confirm game loads and runs without errors

---

## PHASE 3 FINAL VERIFICATION CHECKLIST

Run after all 4 blocks (3.1–3.4) are complete.

```
PARTICLES (3.1)
[ ] All 8 zones have unique visible particle effects
[ ] Particles render behind sprites, above background image
[ ] Active particle count never exceeds 200
[ ] Particle system activates on zone entry, deactivates on zone exit
[ ] No frame rate drop below 30fps with particles active

SPELL ANIMATIONS (3.2)
[ ] Screen shake fires on heavy and execute spells, resolves in 2 frames
[ ] Slow-motion fires on execute spells — deltaTime ~30% for 8 frames
[ ] AoE ripple ring expands and fades correctly
[ ] Hex shield renders 6 rotating hexagons around player on shield cast
[ ] Heal particles rise from player and fade
[ ] EX spell gold border flash appears when EX spell fires
[ ] No animation persists beyond its intended duration

ENEMY ANIMATIONS (3.3)
[ ] Entrance glitch plays on all enemies at room start, resolves in 12 frames
[ ] Death desaturation frames 0–5, scatter frames 6–11
[ ] Elite/boss deaths: white flash + heavier shake
[ ] Existing kill cam still works or confirmed integrated

TRANSITIONS (3.4)
[ ] All major screen changes use GlitchTransition.trigger()
[ ] Transition visible ~250ms, screen switches at midpoint
[ ] Input blocked during transition
[ ] Glitch bands and RGB split visible at peak intensity
[ ] No transition fires during mini-game intros or phase banners
```

When all items pass: commit with message `feat: Phase 3 complete — particles, spell FX, enemy animations, transitions`
Then tell Claude Chat: "Phase 3 complete and verified."

---

*Blocks 3.3 and 3.4 — Claude Chat Architect Layer · 2026-03-26*
*Execute in order: 3.3 → 3.4 → Final Verification*
*Do not begin Phase 4 until Phase 3 final verification passes.*

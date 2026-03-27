# NEON DUNGEON — INSTRUCTION BLOCK 3.2
## ENHANCED SPELL CAST ANIMATIONS
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Block 3.1 complete

---

> **SCOPE**: Extend existing VFX for each spell category with new animation layers.
> Do NOT replace existing VFX — extend with additional effects on top.
> Screen shake: canvas translate offset, self-correcting within 2 frames.
> All animations driven by the existing requestAnimationFrame loop.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. The existing VFX system — the function(s) that handle explode, slash, spark, ring, kill cam, spell flash
2. Where spell type/category is determined at cast time (how the game knows a spell is heavy_attack vs execute vs aoe etc.)
3. The main canvas draw call — specifically the `ctx.drawImage` or equivalent that draws the scene each frame, to confirm where canvas translate can be injected
4. Whether spells have a `subtype` property (confirmed in Phase 1 work) — confirm the exact subtype strings in use
5. The player sprite render position — x/y coordinates used when drawing the player character

Report all five before writing any code.

---

## STEP 1 — SCREEN SHAKE SYSTEM

Add to game state (or as module-level variables near the VFX section):

```javascript
// ============================================================
// ENHANCED SPELL ANIMATIONS — Phase 3.2
// ============================================================

const ScreenShake = {
    x: 0,
    y: 0,
    intensity: 0,
    framesLeft: 0,

    trigger(intensity, frames) {
        this.intensity = intensity;
        this.framesLeft = frames;
    },

    update() {
        if (this.framesLeft <= 0) {
            this.x = 0;
            this.y = 0;
            return;
        }
        const decay = this.framesLeft / (this.framesLeft + 1);
        this.x = (Math.random() - 0.5) * this.intensity * 2 * decay;
        this.y = (Math.random() - 0.5) * this.intensity * 2 * decay;
        this.framesLeft--;
    },

    apply(ctx) {
        if (this.framesLeft > 0 || this.x !== 0 || this.y !== 0) {
            ctx.translate(this.x, this.y);
        }
    }
};
```

Hook into the main render loop — apply shake BEFORE drawing everything, reset AFTER:

```javascript
// At the START of the main render function (before any draw calls):
ctx.save();
ScreenShake.update();
ScreenShake.apply(ctx);

// At the END of the main render function (after all draw calls):
ctx.restore();
```

---

## STEP 2 — SLOW-MOTION SYSTEM

Add a time-scale modifier that slows `deltaTime` for a specified duration:

```javascript
const SlowMo = {
    active: false,
    scale: 1.0,
    framesLeft: 0,

    trigger(scale, frames) {
        this.scale = scale;
        this.framesLeft = frames;
        this.active = true;
    },

    apply(dt) {
        if (!this.active) return dt;
        this.framesLeft--;
        if (this.framesLeft <= 0) {
            this.active = false;
            this.scale = 1.0;
        }
        return dt * this.scale;
    }
};
```

In the game update loop, wrap `deltaTime` before passing to combat/animation update:

```javascript
const effectiveDt = SlowMo.apply(deltaTime);
// Use effectiveDt for all game logic updates this frame
// (particle systems, animation timers, combat tick)
// Do NOT apply to ScreenShake.update() — shake runs at real speed
```

---

## STEP 3 — RIPPLE RING EFFECT

A ring that expands outward from a point and fades. Used for AoE spells.

```javascript
const RippleEffects = [];

function spawnRipple(x, y, color, maxRadius, duration) {
    RippleEffects.push({
        x, y, color,
        radius: 0,
        maxRadius,
        duration,
        elapsed: 0
    });
}

function updateRipples(dt) {
    for (let i = RippleEffects.length - 1; i >= 0; i--) {
        const r = RippleEffects[i];
        r.elapsed += dt;
        r.radius = (r.elapsed / r.duration) * r.maxRadius;
        if (r.elapsed >= r.duration) RippleEffects.splice(i, 1);
    }
}

function renderRipples(ctx) {
    RippleEffects.forEach(r => {
        const alpha = 1 - (r.elapsed / r.duration);
        ctx.save();
        ctx.beginPath();
        ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2);
        ctx.strokeStyle = r.color;
        ctx.lineWidth = 2;
        ctx.globalAlpha = alpha * 0.8;
        ctx.shadowColor = r.color;
        ctx.shadowBlur = 8;
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.restore();
    });
}
```

Hook `updateRipples(effectiveDt)` into the game update loop.
Hook `renderRipples(ctx)` into the render loop AFTER sprites (so rings appear in front).

---

## STEP 4 — HEX SHIELD PATTERN

A hexagonal shield that appears around the player sprite when a shield spell is cast.

```javascript
const HexShield = {
    active: false,
    duration: 0,
    maxDuration: 800,  // ms
    rotation: 0,
    color: '#00ffff',

    trigger(color) {
        this.active = true;
        this.duration = this.maxDuration;
        this.rotation = 0;
        this.color = color || '#00ffff';
    },

    update(dt) {
        if (!this.active) return;
        this.duration -= dt;
        this.rotation += 0.04;
        if (this.duration <= 0) {
            this.active = false;
        }
    },

    render(ctx, playerX, playerY) {
        if (!this.active) return;
        const alpha = Math.min(1, this.duration / 200);
        const radius = 44;

        ctx.save();
        ctx.translate(playerX, playerY);
        ctx.rotate(this.rotation);
        ctx.globalAlpha = alpha * 0.7;
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 1.5;
        ctx.shadowColor = this.color;
        ctx.shadowBlur = 10;

        // Draw 6 hexagons at equal angles
        for (let i = 0; i < 6; i++) {
            const angle = (i / 6) * Math.PI * 2;
            const hx = Math.cos(angle) * radius;
            const hy = Math.sin(angle) * radius;
            this._drawHex(ctx, hx, hy, 12);
        }
        ctx.restore();
    },

    _drawHex(ctx, cx, cy, size) {
        ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            const a = (i / 6) * Math.PI * 2;
            const x = cx + Math.cos(a) * size;
            const y = cy + Math.sin(a) * size;
            i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.stroke();
    }
};
```

Hook `HexShield.update(effectiveDt)` into the game update loop.
Hook `HexShield.render(ctx, playerX, playerY)` into the render loop AFTER the player sprite.

---

## STEP 5 — HEAL PARTICLE BURST

Rising green particles from the player when a heal spell fires.

```javascript
function spawnHealParticles(playerX, playerY) {
    for (let i = 0; i < 12; i++) {
        const angle = -Math.PI / 2 + (Math.random() - 0.5) * Math.PI;
        const speed = 1 + Math.random() * 2;
        // Reuse the Particle class from Block 3.1
        if (typeof Particle !== 'undefined' && _activeAtmosphere !== undefined) {
            // Add directly to a dedicated heal particle array
            _healParticles.push(new Particle(
                playerX + (Math.random() - 0.5) * 20,
                playerY,
                Math.cos(angle) * speed,
                Math.sin(angle) * speed - 1,
                600 + Math.random() * 400,
                1000,
                2 + Math.random() * 2,
                '#00ff41',
                'dot'
            ));
        }
    }
}

const _healParticles = [];

function updateHealParticles(dt) {
    for (let i = _healParticles.length - 1; i >= 0; i--) {
        _healParticles[i].update(dt);
        if (_healParticles[i].isDead()) _healParticles.splice(i, 1);
    }
}

function renderHealParticles(ctx) {
    _healParticles.forEach(p => p.render(ctx));
}
```

If Block 3.1 `Particle` class is not available (not yet implemented), replace with inline
drawing: for each heal particle, draw a small green circle that rises and fades. Same visual,
no class dependency.

Hook `updateHealParticles(effectiveDt)` and `renderHealParticles(ctx)` into update/render loops.

---

## STEP 6 — EX SPELL GOLD OUTLINE

When an EX-tier spell is cast, render a gold border flash around the spell name in the combat log
AND briefly around the spell button that was clicked.

```javascript
const ExSpellFlash = {
    active: false,
    timer: 0,
    duration: 500,
    spellName: '',

    trigger(spellName) {
        this.active = true;
        this.timer = this.duration;
        this.spellName = spellName;
    },

    update(dt) {
        if (!this.active) return;
        this.timer -= dt;
        if (this.timer <= 0) this.active = false;
    },

    render(ctx, canvasW, canvasH) {
        if (!this.active) return;
        const alpha = this.timer / this.duration;

        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.strokeStyle = '#ffd700';
        ctx.lineWidth = 2;
        ctx.shadowColor = '#ffd700';
        ctx.shadowBlur = 16;

        // Gold border flash along the bottom of the canvas (near spell buttons)
        ctx.strokeRect(4, canvasH - 84, canvasW - 8, 80);

        // EX label centered
        ctx.font = '8px "Press Start 2P"';
        ctx.fillStyle = '#ffd700';
        ctx.textAlign = 'center';
        ctx.fillText(`EX: ${this.spellName}`, canvasW / 2, canvasH - 90);
        ctx.textAlign = 'left';
        ctx.shadowBlur = 0;
        ctx.restore();
    }
};
```

Hook `ExSpellFlash.update(dt)` and `ExSpellFlash.render(ctx, canvas.width, canvas.height)`
into update/render loops.

---

## STEP 7 — WIRE TRIGGERS TO SPELL CAST EVENTS

Find where each spell type resolves. After the spell's core effect fires, trigger the
appropriate animation:

```javascript
// In spell cast resolution (adapt to actual spell dispatch function):
function onSpellCast(spell, targets) {
    const subtype = spell.subtype || spell.type;

    // Screen shake — heavy and execute spells
    if (['heavy_physical', 'heavy_magical', 'execute'].includes(subtype)) {
        ScreenShake.trigger(6, 2); // 6px intensity, 2 frames
    }

    // Slow motion — execute spells only
    if (subtype === 'execute') {
        SlowMo.trigger(0.3, 8); // 30% speed for 8 frames
    }

    // Ripple ring — AoE spells
    if (subtype === 'aoe') {
        const centerX = canvas.width * 0.6; // adapt to actual enemy group render center
        const centerY = canvas.height * 0.4;
        spawnRipple(centerX, centerY, '#ff00ff', 120, 600);
    }

    // Hex shield — any shield/defense spell
    if (spell.tags && (spell.tags.includes('shield') || spell.tags.includes('defense'))) {
        HexShield.trigger('#00ffff');
    }

    // Reflect spells: magenta hex shield
    if (spell.tags && spell.tags.includes('reflect')) {
        HexShield.trigger('#ff00ff');
    }

    // Heal particles — any heal spell
    if (spell.tags && spell.tags.includes('heal')) {
        const player = GameState.player; // use actual
        spawnHealParticles(player.renderX || canvas.width * 0.25, player.renderY || canvas.height * 0.5);
    }

    // EX flash — EX-tier spells
    if (spell.isEX) {
        ExSpellFlash.trigger(spell.name);
    }
}
```

This function should be called from wherever spell effects are dispatched. If a single
central spell dispatch function already exists, add these calls there. If spell effects
are scattered, add calls at each branch for the relevant subtypes.

---

## STEP 8 — ADD ALL UPDATE/RENDER HOOKS TOGETHER

For clarity, add a single aggregator function to avoid missing hooks:

```javascript
// Call this once per frame in the UPDATE loop:
function updateSpellAnimations(dt) {
    ScreenShake.update();      // uses real dt, not effectiveDt
    HexShield.update(dt);
    ExSpellFlash.update(dt);
    updateRipples(dt);
    updateHealParticles(dt);
}

// Call this once per frame in the RENDER loop (after sprites, before UI):
function renderSpellAnimations(ctx) {
    renderRipples(ctx);
    HexShield.render(ctx, getPlayerRenderX(), getPlayerRenderY());
    ExSpellFlash.render(ctx, canvas.width, canvas.height);
    renderHealParticles(ctx);
}
```

Replace `getPlayerRenderX()` / `getPlayerRenderY()` with the actual player position
values from the source (pre-scan item 5).

---

## COMPLETION REPORT FOR BLOCK 3.2

1. Confirm ScreenShake fires on heavy and execute spells — self-corrects in 2 frames
2. Confirm SlowMo reduces deltaTime to 30% for 8 frames on execute spells
3. Confirm AoE ripple ring expands and fades correctly
4. Confirm HexShield renders 6 hexagons rotating around player on shield spell cast
5. Confirm heal particles rise and fade from player position
6. Confirm EX flash renders gold border when an EX spell fires
7. Any animation that could NOT be implemented and why
8. Confirm no frame rate degradation with all animations running simultaneously
9. Confirm game loads and runs without errors

---

*Block 3.2 — Claude Chat Architect Layer · 2026-03-26*
*Block 3.3 (enemy entrance/death) does not depend on 3.2 — but execute in order.*

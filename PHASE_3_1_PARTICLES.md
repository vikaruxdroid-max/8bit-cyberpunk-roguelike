# NEON DUNGEON — INSTRUCTION BLOCK 3.1
## ZONE ATMOSPHERE PARTICLE SYSTEM
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Phase 2 complete (commit c96bf1b)

---

> **SCOPE**: Add a unique ambient particle system for each of the 8 zones.
> Particles render BEHIND sprites but ABOVE the background image.
> Hard performance cap: 200 active particles maximum per system.
> Canvas-only — no DOM, no CSS animations.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. The main combat/arena render order — specifically where background image is drawn vs where sprites are drawn, to confirm layer insertion point
2. The current zone identifier on game state — the variable that holds which zone the player is in (e.g. `GameState.zone`, `GameState.currentZone`, a zone ID string, etc.)
3. Where the game loop's `deltaTime` is available
4. Whether a zone transition event exists — a moment when the current zone changes that can be hooked to swap particle systems
5. Canvas width and height variables used in rendering

Report all five before writing any code.

---

## STEP 1 — PARTICLE CLASS

Insert as a new named section in the JS:

```javascript
// ============================================================
// ATMOSPHERE PARTICLE SYSTEM — Phase 3.1
// ============================================================

class Particle {
    constructor(x, y, vx, vy, life, maxLife, size, color, type) {
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.life = life;
        this.maxLife = maxLife;
        this.size = size;
        this.color = color;
        this.type = type;  // 'dot' | 'line' | 'spark' | 'flicker'
        this.alpha = 1;
    }

    update(dt) {
        this.x += this.vx * (dt / 16);
        this.y += this.vy * (dt / 16);
        this.life -= dt;
        this.alpha = Math.max(0, this.life / this.maxLife);
    }

    isDead() { return this.life <= 0; }

    render(ctx) {
        if (this.alpha <= 0) return;
        ctx.save();
        ctx.globalAlpha = this.alpha * 0.7;

        switch (this.type) {
            case 'dot':
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                break;
            case 'line':
                ctx.strokeStyle = this.color;
                ctx.lineWidth = this.size;
                ctx.beginPath();
                ctx.moveTo(this.x, this.y);
                ctx.lineTo(this.x + this.vx * 3, this.y + this.vy * 3);
                ctx.stroke();
                break;
            case 'spark':
                ctx.strokeStyle = this.color;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(this.x, this.y);
                ctx.lineTo(this.x - this.vx * 2, this.y - this.vy * 2);
                ctx.stroke();
                break;
            case 'flicker':
                if (Math.random() > 0.3) {
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size * (0.5 + Math.random() * 0.5), 0, Math.PI * 2);
                    ctx.fillStyle = this.color;
                    ctx.fill();
                }
                break;
        }
        ctx.restore();
    }
}
```

---

## STEP 2 — PARTICLE SYSTEM CLASS

```javascript
class ParticleSystem {
    constructor(config) {
        this.config = config;
        this.particles = [];
        this.spawnTimer = 0;
        this.active = false;
    }

    activate() { this.active = true; this.particles = []; this.spawnTimer = 0; }
    deactivate() { this.active = false; this.particles = []; }

    update(dt, canvasW, canvasH) {
        if (!this.active) return;

        // Spawn new particles
        this.spawnTimer -= dt;
        const spawnInterval = 1000 / this.config.spawnRate;
        while (this.spawnTimer <= 0 && this.particles.length < 200) {
            this.particles.push(this._spawn(canvasW, canvasH));
            this.spawnTimer += spawnInterval;
        }

        // Update existing
        this.particles = this.particles.filter(p => {
            p.update(dt);
            return !p.isDead();
        });
    }

    render(ctx) {
        if (!this.active || this.particles.length === 0) return;
        this.particles.forEach(p => p.render(ctx));
    }

    _spawn(cw, ch) {
        const c = this.config;
        return c.spawnFn(cw, ch);
    }
}
```

---

## STEP 3 — ZONE ATMOSPHERE CONFIGURATIONS

```javascript
const ZONE_ATMOSPHERES = {

    // Zone 1 — Neon Nexus: cyan rain falling vertically
    'neon_nexus': new ParticleSystem({
        spawnRate: 18,  // particles per second
        spawnFn: (cw, ch) => new Particle(
            Math.random() * cw,
            -10,
            (Math.random() - 0.5) * 0.5,
            2.5 + Math.random() * 2,
            1500 + Math.random() * 1000,
            2500,
            1 + Math.random(),
            '#00ffff',
            'line'
        )
    }),

    // Zone 2 — Data Vaults: green code characters drifting down
    'data_vaults': new ParticleSystem({
        spawnRate: 12,
        spawnFn: (cw, ch) => new Particle(
            Math.random() * cw,
            -10,
            0,
            1.5 + Math.random() * 1.5,
            2000 + Math.random() * 1500,
            3500,
            1.5,
            '#00ff41',
            'line'
        )
    }),

    // Zone 3 — Chrome Wastes: gray ash drifting diagonally
    'chrome_wastes': new ParticleSystem({
        spawnRate: 10,
        spawnFn: (cw, ch) => new Particle(
            Math.random() * cw,
            -5,
            0.3 + Math.random() * 0.5,
            0.8 + Math.random() * 0.8,
            3000 + Math.random() * 2000,
            5000,
            1 + Math.random() * 1.5,
            `hsl(0,0%,${40 + Math.floor(Math.random() * 30)}%)`,
            'dot'
        )
    }),

    // Zone 4 — Virus Lanes: magenta corruption particles, dense and chaotic
    'virus_lanes': new ParticleSystem({
        spawnRate: 25,
        spawnFn: (cw, ch) => new Particle(
            Math.random() * cw,
            Math.random() * ch,
            (Math.random() - 0.5) * 3,
            (Math.random() - 0.5) * 3,
            500 + Math.random() * 800,
            1300,
            1 + Math.random() * 2,
            '#ff00ff',
            'flicker'
        )
    }),

    // Zone 5 — Core Approach: white energy arcs shooting upward
    'core_approach': new ParticleSystem({
        spawnRate: 15,
        spawnFn: (cw, ch) => new Particle(
            Math.random() * cw,
            ch + 5,
            (Math.random() - 0.5) * 1.5,
            -(2 + Math.random() * 3),
            1000 + Math.random() * 1000,
            2000,
            1,
            '#ffffff',
            'spark'
        )
    }),

    // Zone 6 — Ghost Sector: blue-tinted static fog, slow drift
    'ghost_sector': new ParticleSystem({
        spawnRate: 8,
        spawnFn: (cw, ch) => new Particle(
            Math.random() * cw,
            Math.random() * ch,
            (Math.random() - 0.5) * 0.4,
            (Math.random() - 0.5) * 0.4,
            4000 + Math.random() * 3000,
            7000,
            2 + Math.random() * 3,
            'rgba(80,80,255,0.4)',
            'dot'
        )
    }),

    // Zone 7 — Black Ice: pale blue ice crystals drifting slowly downward
    'black_ice': new ParticleSystem({
        spawnRate: 10,
        spawnFn: (cw, ch) => new Particle(
            Math.random() * cw,
            -8,
            (Math.random() - 0.5) * 0.5,
            0.6 + Math.random() * 0.8,
            4000 + Math.random() * 2000,
            6000,
            1.5 + Math.random() * 2,
            '#aaddff',
            'dot'
        )
    }),

    // Zone 8 — The Core: deep red reality-tear particles, intense and omnidirectional
    'the_core': new ParticleSystem({
        spawnRate: 30,
        spawnFn: (cw, ch) => {
            const angle = Math.random() * Math.PI * 2;
            const speed = 1 + Math.random() * 4;
            return new Particle(
                cw / 2 + (Math.random() - 0.5) * cw,
                ch / 2 + (Math.random() - 0.5) * ch,
                Math.cos(angle) * speed,
                Math.sin(angle) * speed,
                600 + Math.random() * 600,
                1200,
                1 + Math.random() * 2,
                `hsl(${10 + Math.floor(Math.random() * 20)},100%,${50 + Math.floor(Math.random()*20)}%)`,
                'spark'
            );
        }
    })
};

// Active system reference
let _activeAtmosphere = null;

function setZoneAtmosphere(zoneId) {
    // Deactivate previous
    if (_activeAtmosphere) _activeAtmosphere.deactivate();

    // Map zone ID to atmosphere key — adapt zone ID format to match actual game state values
    const key = zoneId ? zoneId.toLowerCase().replace(/\s+/g, '_') : null;
    _activeAtmosphere = ZONE_ATMOSPHERES[key] || null;

    if (_activeAtmosphere) _activeAtmosphere.activate();
}
```

---

## STEP 4 — HOOK INTO ZONE TRANSITION

Find the zone transition event/function (pre-scan item 4). Call `setZoneAtmosphere()` when
the zone changes, passing the new zone ID:

```javascript
// When zone changes (adapt to actual zone ID format):
setZoneAtmosphere(GameState.currentZone); // use actual zone identifier
```

Also call it on game init / when a run starts to set the initial zone atmosphere.

---

## STEP 5 — HOOK INTO RENDER LOOP

In the main render function, find where the background image is drawn and where sprites are drawn.
Insert atmosphere rendering AFTER background but BEFORE sprites:

```javascript
// After: draw background image
// Before: draw enemy/player sprites

if (_activeAtmosphere) {
    _activeAtmosphere.render(ctx);
}
```

Also add the update call in the game loop where `deltaTime` is available:

```javascript
if (_activeAtmosphere) {
    _activeAtmosphere.update(deltaTime, canvas.width, canvas.height);
}
```

---

## STEP 6 — ZONE ID MAPPING

The `ZONE_ATMOSPHERES` keys must match the actual zone identifiers used in the game.
After adding the system, verify the zone IDs by checking how zones are currently stored
in `GameState`. If the IDs differ from the keys above (e.g. numeric IDs like `zone1`
instead of `neon_nexus`), add a mapping table:

```javascript
const ZONE_ATMOSPHERE_MAP = {
    // Map actual game zone IDs to atmosphere keys
    // Fill these in based on actual zone IDs found in source:
    'zone1': 'neon_nexus',
    'zone2': 'data_vaults',
    'zone3': 'chrome_wastes',
    'zone4': 'virus_lanes',
    'zone5': 'core_approach',
    'zone6': 'ghost_sector',
    'zone7': 'black_ice',
    'zone8': 'the_core',
    // Add string name variants if zones use names:
    'Neon Nexus':    'neon_nexus',
    'Data Vaults':   'data_vaults',
    'Chrome Wastes': 'chrome_wastes',
    'Virus Lanes':   'virus_lanes',
    'Core Approach': 'core_approach',
    'Ghost Sector':  'ghost_sector',
    'Black Ice':     'black_ice',
    'The Core':      'the_core'
};

function setZoneAtmosphere(zoneId) {
    if (_activeAtmosphere) _activeAtmosphere.deactivate();
    const key = ZONE_ATMOSPHERE_MAP[zoneId]
        || (zoneId ? zoneId.toLowerCase().replace(/\s+/g, '_') : null);
    _activeAtmosphere = ZONE_ATMOSPHERES[key] || null;
    if (_activeAtmosphere) _activeAtmosphere.activate();
}
```

---

## STEP 7 — PERFORMANCE GUARD

Add a global safety cap in the update loop to catch any configuration that produces too many
particles:

```javascript
// In ParticleSystem.update(), the spawn loop already checks particles.length < 200.
// Additionally, after update, hard-trim if somehow exceeded:
if (this.particles.length > 200) {
    this.particles = this.particles.slice(this.particles.length - 200);
}
```

If frame rate drops below 30fps during testing with particles active, reduce `spawnRate`
on the offending zone config. The_core (spawnRate: 30) is most likely to need trimming.

---

## COMPLETION REPORT FOR BLOCK 3.1

1. Confirm `Particle` and `ParticleSystem` classes added
2. List the actual zone IDs found in the source and confirm mapping to atmosphere keys
3. Confirm particles render between background and sprites (not on top of everything)
4. Confirm particle cap of 200 is enforced
5. Test each zone: confirm unique particle behavior visible per zone
6. Report frame rate impact — is it stable at 30fps+ with particles active?
7. Any zone that had to have its spawnRate reduced for performance
8. Confirm game loads and runs without errors

---

*Block 3.1 — Claude Chat Architect Layer · 2026-03-26*
*Block 3.2 (spell animations) does not depend on 3.1 — but execute in order.*

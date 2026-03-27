# NEON DUNGEON — CLAUDE CODE EXECUTION SPECIFICATION
## Living Technical Document · Version 1.1 · 2026-03-26

---

> **DIRECTIVE FOR CLAUDE CODE**: This document is the single source of truth for all development on Neon Dungeon. You are operating mid-development on an active codebase — read this document fully before executing any instruction block. Every section is load-bearing. Do not infer, guess, or improvise outside what is specified here or in the active instruction block you have been given. When ambiguity exists, stop and report it. Preserve all existing functionality unless a section explicitly authorizes modification.

---

## HOW THIS PROJECT IS RUN — READ FIRST

This project uses a **two-tier development workflow**:

```
Developer intent
      ↓
[Claude Chat — Architect Layer]
  • Receives plain-language requests from the developer
  • Translates intent into precise, Claude Code-ready instruction blocks
  • Maintains and updates this specification document
  • Reviews output and prepares next instruction
      ↓
[Claude Code — Execution Layer]  ← YOU ARE HERE
  • Receives instruction blocks copied from Claude Chat
  • Reads this spec document before executing
  • Implements exactly what the instruction block specifies
  • Reports back what was done, what was skipped, and any blockers
      ↓
Developer reviews → feeds back to Claude Chat → next instruction block
```

**Claude Code operating rules:**
1. An instruction block from Claude Chat always takes precedence over your own interpretation
2. This spec document defines constraints, patterns, and architecture — instruction blocks define what to do right now
3. After completing an instruction block, output a brief summary: what was implemented, what file(s) changed, and any decisions you had to make that weren't specified
4. If something in the instruction block conflicts with this spec, stop and report the conflict — do not resolve it silently
5. Never refactor, rename, or restructure code that is not mentioned in the instruction block

---

## TABLE OF CONTENTS

1. [Project Identity & Hard Constraints](#1-project-identity--hard-constraints)
2. [Repository & File Structure](#2-repository--file-structure)
3. [Current State Inventory](#3-current-state-inventory)
4. [Code Conventions & Patterns](#4-code-conventions--patterns)
5. [Phase 1 — Combat Polish (CURRENT PRIORITY)](#5-phase-1--combat-polish)
6. [Phase 2 — Content & Variety](#6-phase-2--content--variety)
7. [Phase 3 — Visual & Audio Polish](#7-phase-3--visual--audio-polish)
8. [Phase 4 — AI Integration Architecture](#8-phase-4--ai-integration-architecture)
9. [Phase 5 — Endgame & Competitive](#9-phase-5--endgame--competitive)
10. [AI Payload Schemas & Prompt Templates](#10-ai-payload-schemas--prompt-templates)
11. [Cloudflare Worker Proxy Specification](#11-cloudflare-worker-proxy-specification)
12. [Testing & Acceptance Criteria](#12-testing--acceptance-criteria)
13. [Do Not Touch List](#13-do-not-touch-list)
14. [Change Log](#14-change-log)

---

## 1. PROJECT IDENTITY & HARD CONSTRAINTS

### 1.1 What This Game Is

**Neon Dungeon** is a browser-based roguelike with cyberpunk/grimdark aesthetics. The player builds a spell loadout across a procedurally structured dungeon run, fighting through 8 zones to reach a final boss. The core differentiator is the **spell swap decision** after every room — the build evolves through the run, not at creation.

### 1.2 Non-Negotiable Technical Constraints

These constraints are **permanent** unless the developer explicitly instructs otherwise in writing. Do not propose workarounds that violate them.

| Constraint | Rule |
|---|---|
| **Single HTML file** | All game code, CSS, and markup lives in one `.html` file. No imports from local files. No build step. No bundler. |
| **No backend (game itself)** | The game file has zero server dependencies. The AI proxy (Cloudflare Worker) is a separate artifact and is NOT part of the game file. |
| **No npm / no Node for the game** | Vanilla JS only. No frameworks (React, Vue, Svelte, etc.) in the game file. |
| **No external JS libraries** | No lodash, no jQuery, no game engines. Canvas 2D API and Web Audio API only. |
| **External assets allowed** | 6 PNG sprites, 2 background images, 2 JSON data files, 2 Google Fonts (Press Start 2P, Share Tech Mono). These load at runtime via URL. |
| **localStorage only** | No IndexedDB, no sessionStorage for save data. Run state is ephemeral (permadeath). Meta-progression (unlocks, history) uses localStorage. |
| **Target browsers** | Chrome and Edge, latest stable. Minimum viewport: 1280×720. Designed for 1920×1080. No mobile support required. |
| **Canvas rendering** | All game visuals render to an HTML5 Canvas element via 2D context. No WebGL. No DOM-based game objects. UI overlays (menus, tooltips) may use positioned HTML/CSS over the canvas. |

### 1.3 Aesthetic Constraints

| Element | Specification |
|---|---|
| Background base | `#0a0a1a` (dark navy) |
| Primary accent | `#00ffff` (cyan) |
| Secondary accent | `#ff00ff` (magenta) |
| Tertiary accent | `#00ff41` (matrix green) |
| Warning/danger | `#ff4444` (red) |
| Gold/rare | `#ffd700` (gold) |
| Primary font | `"Press Start 2P"` — all game UI, headers, combat text |
| Secondary font | `"Share Tech Mono"` — lore text, narration, terminal output |
| Sprite size | 14×26 pixels at 4× scale = 56×104 rendered |
| Visual tone | CRT scanlines, matrix rain, neon glow, vaporwave. **Never clean/modern/flat.** |

---

## 2. REPOSITORY & FILE STRUCTURE

```
github.com/vikaruxdroid-max/8bit-cyberpunk-roguelike
│
├── 8bit_cyberpunk_FIXED.html          ← PRIMARY GAME FILE (the only file that matters for the game)
├── NEON_DUNGEON_CLAUDE_CODE_SPEC.md   ← THIS DOCUMENT (keep updated)
├── GAME_DESIGN_BRIEF.md               ← Original design brief (reference only)
│
├── /data/                             ← JSON data files loaded at runtime
│   ├── spells.json                    ← Spell definitions (if externalized)
│   └── enemies.json                   ← Enemy definitions (if externalized)
│
├── /assets/                           ← PNG sprites and background images
│   ├── sprites/                       ← 6 character/enemy sprites
│   └── backgrounds/                   ← 2 background images
│
└── /worker/                           ← Cloudflare Worker proxy (Phase 4, separate deployment)
    ├── worker.js                      ← Main worker script
    └── wrangler.toml                  ← Cloudflare deployment config
```

**Active development notes for Claude Code:**
- You are operating on a live, in-progress codebase — the game already runs. Do not treat this as a blank slate.
- Only edit `8bit_cyberpunk_FIXED.html` for game changes. The `/worker/` directory is a separate deployment artifact.
- Before any implementation, scan the existing source to locate the relevant functions/objects mentioned in your instruction block. Do not add duplicate implementations.
- Verify exact variable and function names in the source before referencing them in new code — names in this spec are targets, not guarantees of exact current naming.
- Commit messages should describe the feature implemented, e.g. `feat: add enemy telegraph system with counter bonuses`

---

## 3. CURRENT STATE INVENTORY

This is what currently EXISTS and WORKS. Do not reimplement these systems — extend them.

### 3.1 Systems That Are Complete

| System | Status | Notes |
|---|---|---|
| Character creation | ✅ Complete | 3×2 grid, pick 1 of 2 per category, 6 categories |
| Apple II boot screen | ✅ Complete | Green phosphor terminal, asset preloading |
| World map | ✅ Complete | 8 zones, linear unlock, final boss at The Core |
| Zone/room progression | ✅ Complete | 5–12 rooms per zone (combat, loot, rest, merchant) |
| Combat engine | ✅ Complete (needs polish) | Speed-based turns, auto-attack, 4 manual spells |
| Spell system | ✅ Complete | 30 attack + 30 defensive + 30 potions |
| Spell swap | ✅ Complete | After each room, swap 1 of 4 spells for new random offering |
| Spell evolution | ✅ Complete | 10 casts → EX version, -1 cooldown |
| Weapon system | ✅ Complete | 30 weapons, 7 equipment slots |
| Passive skills | ✅ Complete (5 of 30) | Crit, lifesteal, dodge, block DR, CD reduction |
| Quest system | ✅ Complete | 15 in pool, 5 active per run |
| Level-up system | ✅ Complete | 10 stat/ability upgrade choices |
| VFX system | ✅ Complete | explode, slash, spark, ring, kill cam, spell flash |
| Procedural audio | ✅ Complete | 8 SFX via Web Audio API |
| Buff/debuff system | ✅ Complete | Timed effects: ATK up, DEF up, dodge, stun, bleed, poison, reflect |
| Combo system | ✅ Complete | Consecutive hits → combo counter → bonus damage |
| Block mechanic | ✅ Complete | Manual block with cooldown, blockDR% reduction |
| localStorage save | ✅ Complete | Persists meta-progression |
| 5 playable classes | ✅ Complete | Man, Woman, Sage, Cyber, Shadow |
| 14 enemy types | ✅ Complete | 9 base + 5 advanced/bosses |
| Relic system | ⚠️ UI skeleton only | Data structure and rendering exist; no actual relic data/effects |

### 3.2 Known Architecture Patterns (Preserve These)

- **Game state object**: All runtime state lives in a single `gameState` object. Do not create parallel state stores.
- **Render loop**: `requestAnimationFrame` drives canvas redraws. Do not add `setInterval`-based rendering.
- **Event system**: Input handled via `addEventListener` on `document` and canvas. Do not add framework-style event buses.
- **Data files**: Spells, enemies, and items are defined as JavaScript objects/arrays within the HTML file OR loaded from `/data/` JSON files. Maintain whichever pattern currently exists — do not mix.
- **Screen management**: Screens are toggled via CSS `display` and canvas redraw. There is a screen state variable (verify exact name in source before modifying).

---

## 4. CODE CONVENTIONS & PATTERNS

Claude Code must follow these conventions in all new code. Read the existing source to confirm current patterns before adding anything.

### 4.1 JavaScript Style

```javascript
// Variable naming: camelCase for variables, PascalCase for classes/constructors
let playerHealth = 100;
class SpellEffect { }

// Constants: SCREAMING_SNAKE_CASE
const MAX_SPELL_SLOTS = 4;
const BASE_CRIT_CHANCE = 0.05;

// Functions: camelCase, verb-first
function castSpell(spellId, targetId) { }
function renderCombatUI(ctx, state) { }
function applyBuff(entityId, buffType, duration) { }

// No arrow functions in top-level definitions (use for callbacks/inline only)
// CORRECT:
function updateCombat(deltaTime) { }
// ACCEPTABLE for callbacks:
enemies.forEach(enemy => enemy.update(deltaTime));

// Comments: explain WHY, not WHAT
// BAD: // increment combo counter
comboCount++;
// GOOD: // Each consecutive non-blocked hit adds 1 to combo; resets on miss or enemy turn
comboCount++;
```

### 4.2 Canvas Drawing Pattern

```javascript
// Always save/restore context state when drawing sub-systems
function drawSpellEffect(ctx, effect) {
    ctx.save();
    // ... drawing code ...
    ctx.restore();
}

// Color usage: always use CSS variable equivalents as constants
const COLORS = {
    cyan: '#00ffff',
    magenta: '#ff00ff',
    green: '#00ff41',
    red: '#ff4444',
    gold: '#ffd700',
    bg: '#0a0a1a',
    bgLight: '#0d0d2b'
};

// Glow effect pattern (used throughout):
function drawGlow(ctx, color, blur = 15) {
    ctx.shadowColor = color;
    ctx.shadowBlur = blur;
}
```

### 4.3 Data Structure Patterns

```javascript
// Spell object structure (match existing exactly):
{
    id: 'spell_neon_slash',
    name: 'Neon Slash',
    type: 'attack',          // 'attack' | 'defense' | 'potion'
    subtype: 'single',       // 'single' | 'aoe' | 'execute' | 'multi' | 'special'
    mpCost: 20,
    cooldown: 2,             // turns
    currentCooldown: 0,      // runtime state
    castCount: 0,            // for EX evolution tracking
    isEX: false,
    damage: { base: 45, scaling: 'ATK', multiplier: 1.2 },
    effect: null,            // or buff/debuff object
    description: 'A razor-edged slice of pure neon energy.',
    flavorText: 'The grid bleeds cyan.'
}

// Enemy object structure (match existing exactly):
{
    id: 'enemy_chrome_samurai',
    name: 'Chrome Samurai',
    tier: 'advanced',        // 'base' | 'advanced' | 'boss'
    hp: 0, maxHp: 280,
    atk: 55, def: 30, spd: 70, mpAtk: 0,
    actionCounter: 0,        // fills by spd each tick; acts at >= 100
    buffs: [],
    debuffs: [],
    aiPattern: 'aggressive', // 'aggressive' | 'defensive' | 'tactical' | 'boss'
    abilities: [],           // special attack definitions
    loot: { gold: [20,40], spellDrop: 0.15 },
    sprite: 'enemy_advanced_01.png',
    // Phase 1 addition:
    telegraph: null          // populated when enemy is charging (see Phase 1)
}
```

---

## 5. PHASE 1 — COMBAT POLISH

**STATUS: CURRENT PRIORITY. Implement in order. Do not begin Phase 2 until all Phase 1 items are complete and tested.**

### 5.1 Enemy Telegraphing System

**Problem**: Combat is reactive rather than strategic. Players have no reason to time defensive spells.

**Implementation Specification**:

#### 5.1.1 Telegraph Data Structure

Add a `telegraph` property to every enemy object at runtime (not in static data):

```javascript
// Telegraph object — attached to enemy when they begin charging
enemy.telegraph = {
    active: true,
    attackName: 'Mega Pulse Cannon',      // Display name
    attackType: 'heavy_physical',          // Determines correct counter
    turnsRemaining: 1,                     // Counts down; fires at 0
    counterType: 'shield',                 // What the player SHOULD use: 'shield' | 'stun' | 'dodge' | 'reflect'
    warningText: '⚡ CHARGING MEGA BLAST', // Displayed in combat log
    damage: calculatedDamage,             // Pre-calculated so player can see threat level
    threatLevel: 'HIGH'                   // 'LOW' | 'MEDIUM' | 'HIGH' | 'LETHAL'
}
```

#### 5.1.2 Telegraph Trigger Rules

Not every attack is telegraphed. Apply these rules:

| Condition | Telegraph |
|---|---|
| Enemy attack damage > 40% of player current HP | Always telegraph |
| Enemy special ability (AoE, execute, multi-hit) | Always telegraph |
| Normal attack, damage ≤ 20% player HP | Never telegraph |
| Normal attack, damage 20–40% player HP | 50% chance to telegraph |
| Boss attacks | Always telegraph, 2 turns warning (not 1) |

#### 5.1.3 Telegraph UI Rendering

Render telegraph warnings in the combat log area. Specifications:

- **Warning color**: `#ff4444` (red) for LETHAL, `#ff8800` (orange) for HIGH, `#ffff00` (yellow) for MEDIUM
- **Font**: `"Press Start 2P"` at 9px
- **Animation**: Pulse/blink at 1Hz for LETHAL threats
- **Icon**: `⚡` prefix for physical, `💀` for execute/lethal, `🔮` for magical
- **Counter hint**: After warning text, on new line in `#00ffff`: `→ Counter: [SHIELD/STUN/DODGE]`
- **Position**: Top of combat log, pinned above normal log entries

```javascript
// Render function to add to combat UI:
function renderTelegraphWarning(ctx, telegraph, x, y) {
    if (!telegraph || !telegraph.active) return;
    
    const color = {
        'LETHAL': '#ff4444',
        'HIGH': '#ff8800',
        'MEDIUM': '#ffff00',
        'LOW': '#aaaaaa'
    }[telegraph.threatLevel];
    
    // Blinking logic for LETHAL
    const blink = telegraph.threatLevel === 'LETHAL' 
        ? Math.floor(Date.now() / 500) % 2 === 0 
        : true;
    
    if (blink) {
        ctx.font = '9px "Press Start 2P"';
        ctx.fillStyle = color;
        ctx.fillText(`${telegraph.warningText} [${telegraph.turnsRemaining}T]`, x, y);
        ctx.fillStyle = '#00ffff';
        ctx.fillText(`→ COUNTER: ${telegraph.counterType.toUpperCase()}`, x, y + 16);
    }
}
```

#### 5.1.4 Counter-Attack Bonus System

When a player uses the correct counter type against a telegraphed attack:

| Player Action | Correct Counter For | Bonus Effect |
|---|---|---|
| Any SHIELD spell | `heavy_physical`, `aoe_physical` | Negate 100% damage + deal 20% of negated damage back |
| Any STUN spell | `heavy_magical`, `execute` | Cancel attack entirely, enemy skips turn |
| DODGE (active) | `multi_hit`, `sweep` | Full evasion + 1.5× damage on next player attack |
| REFLECT spell | `magical`, `beam` | Return 150% damage to enemy |

Counter bonuses display as floating combat text: `PERFECT COUNTER! +[bonus]` in gold.

#### 5.1.5 Telegraph Integration Points

```javascript
// In the enemy action resolution function (find existing function, add before attack execution):
function resolveEnemyAction(enemy, player) {
    const incomingDamage = calculateDamage(enemy, player);
    const shouldTelegraph = determineTelegraph(enemy, incomingDamage, player);
    
    if (shouldTelegraph && !enemy.telegraph) {
        // Set up telegraph for NEXT turn
        enemy.telegraph = buildTelegraph(enemy, incomingDamage);
        logCombatEvent(enemy.telegraph.warningText, 'warning');
        return; // Enemy spends this turn charging, not attacking
    }
    
    if (enemy.telegraph && enemy.telegraph.active) {
        // This is the telegraphed attack — check for player counter
        const counterResult = checkPlayerCounter(enemy.telegraph, player.lastAction);
        executeAttack(enemy, player, counterResult);
        enemy.telegraph = null;
        return;
    }
    
    // Normal attack — no telegraph
    executeAttack(enemy, player, null);
}
```

---

### 5.2 Boss Phase Mechanics

**Specification**: Each boss has 3 phases triggered by HP thresholds. Phases change AI pattern, abilities, and visual state.

#### 5.2.1 Boss Phase Data Structure

Add to boss enemy definitions:

```javascript
boss.phases = [
    {
        phase: 1,
        hpThreshold: 1.0,      // 100% HP — initial state
        aiPattern: 'aggressive',
        abilities: ['basic_attack', 'power_shot'],
        buffs: [],
        visualState: 'normal',
        phaseTransitionText: null
    },
    {
        phase: 2,
        hpThreshold: 0.6,      // Triggers at 60% HP
        aiPattern: 'tactical',
        abilities: ['basic_attack', 'power_shot', 'shield_phase', 'emp_burst'],
        buffs: [{ type: 'atk_up', value: 0.3, duration: -1 }], // -1 = permanent for phase
        visualState: 'enraged',  // Sprite tint changes
        phaseTransitionText: 'CORE SYSTEMS OVERCLOCKING... DANGER LEVEL: CRITICAL'
    },
    {
        phase: 3,
        hpThreshold: 0.25,     // Triggers at 25% HP
        aiPattern: 'desperate',
        abilities: ['basic_attack', 'execute_protocol', 'reality_tear', 'full_barrage'],
        buffs: [{ type: 'spd_up', value: 0.5, duration: -1 }, { type: 'atk_up', value: 0.5, duration: -1 }],
        visualState: 'overloaded', // Glitch/distortion effect on sprite
        phaseTransitionText: 'EMERGENCY PROTOCOLS ENGAGED. EXTERMINATION MODE ACTIVE.'
    }
]
```

#### 5.2.2 Phase Transition Sequence

When HP crosses a threshold:
1. **Pause combat** (set `combatState = 'phase_transition'`)
2. **Screen flash**: White flash 3 frames, then return to normal
3. **Boss sprite effect**: Apply `visualState` tint/distortion (see Phase 3 visual specs)
4. **Display transition text**: Full-width banner in `"Press Start 2P"` 10px, red, center of canvas, 2.5 seconds
5. **Boss HP bar changes color**: Phase 2 → orange (`#ff8800`), Phase 3 → red (`#ff4444`) with pulse
6. **Apply phase buffs** permanently for the remainder of the fight
7. **Resume combat**

#### 5.2.3 Shield Phase Mechanic (Special Mechanic for Select Bosses)

Certain boss abilities trigger a `SHIELD_PHASE`:

```javascript
// When boss activates SHIELD_PHASE:
boss.shieldPhase = {
    active: true,
    type: 'energy_barrier',         // 'energy_barrier' | 'armor_plating' | 'ghost_form'
    requiredCounter: 'armor_pierce', // Spell tag that penetrates
    turnsRemaining: 3,
    hpImmune: true,                  // No HP damage until shield broken
    shieldHp: 200,                   // Separate shield HP pool
    breakText: 'BARRIER SHATTERED — SYSTEMS EXPOSED'
}
```

If player uses a spell tagged `armor_pierce` (add this tag to relevant spells): deal damage to `shieldHp`. When `shieldHp <= 0`, shield breaks, boss is stunned for 1 turn.

If player does NOT break shield within 3 turns: boss executes a full-damage `reality_tear` that cannot be blocked.

---

### 5.3 Active Dodge / Counter-Attack Timing

**Specification**: Replace passive dodge chance with an active click mechanic during combat.

#### 5.3.1 Dodge Window UI

```
When an enemy attacks (non-telegraphed, or during telegraphed attack resolution):
1. A DODGE BAR appears on screen (bottom of combat area)
2. A cursor/indicator slides across the bar at speed proportional to enemy SPD
3. A green "safe zone" is highlighted on the bar (width proportional to player AGI/DEX stat)
4. Player must click within the safe zone before indicator passes it
5. Success = full evasion; Failure = take full damage
```

**Dodge bar specifications**:
- Width: 300px, Height: 20px
- Background: `#1a1a3a`
- Border: 1px `#00ffff`
- Safe zone color: `#00ff41` (green), width scales: `(player.agi / 100) * 80 + 20` pixels minimum 20px max 100px
- Indicator: 4px wide, color `#ff00ff`, moves left to right
- Speed: `(enemy.spd / 100) * 2 + 0.5` seconds to cross full bar (faster enemies = harder dodge)
- Label above: `"DODGE WINDOW"` in `"Press Start 2P"` 7px cyan

#### 5.3.2 Dodge Passive Skill Interaction

The existing passive dodge skill now modifies the active dodge window rather than granting passive chance:
- Dodge passive level 1: Safe zone width +20px
- Dodge passive level 2: Safe zone width +40px, indicator speed -10%
- Dodge passive level 3: Safe zone width +60px, indicator speed -20%

#### 5.3.3 Auto-resolve for AFK / Accessibility

Add a `combatMode` setting (accessible from settings menu):
- `'active'`: Full active dodge window (default)
- `'passive'`: Reverts to old passive dodge % (for accessibility or AFK play)

---

## 6. PHASE 2 — CONTENT & VARIETY

**Do not begin until Phase 1 is complete and committed.**

### 6.1 Mini-Games Between Stages

**Architecture Rule**: Mini-games are rendered on the Canvas like combat. They are NOT HTML/CSS overlays. They must follow the same draw loop pattern as everything else.

#### 6.1.1 Mini-Game Trigger Logic

```javascript
// After a non-boss combat room resolves, before rendering next room:
function checkMiniGameTrigger(roomsCleared, zone) {
    // Mini-game appears with 25% base chance after every 3rd room cleared
    // Increases to 40% after zone boss is defeated
    // Cannot trigger twice in a row
    // Cannot trigger in the final room before a boss
    const chance = (roomsCleared % 3 === 0) 
        ? (zone.bossDefeated ? 0.40 : 0.25) 
        : 0;
    return Math.random() < chance && !state.lastRoomWasMiniGame;
}
```

#### 6.1.2 Mini-Game 1: Hacking (Pattern Match)

```
Screen: A 4×4 grid of 8 different symbols (pairs of each)
Timer: 30 seconds
Mechanic: Click to reveal symbol, click second tile to match
Success condition: All 8 pairs matched before timer expires
Reward tier: Pairs matched in < 15s = GOLD, 15-25s = SILVER, >25s = BRONZE
Failure: Timer expires — no secret room this interval
```

**Symbols**: Use Unicode/ASCII cyberpunk symbols: `⌘ ⟁ ⬡ ◈ ⊛ ⌬ ⊕ ⋈`

**Visual**: Grid cells as cyan-bordered boxes `56×56px`. Revealed cells show magenta symbol. Matched cells stay revealed and pulse green.

#### 6.1.3 Mini-Game 2: Lockpicking (Timing)

```
Screen: A circular dial (radius 120px)
Mechanic: A highlight arc sweeps the dial continuously
Safe zone: A 15-degree arc in a random position (shown in green)
Player must click when the sweep overlaps the safe zone
3 tumblers required (3 successful clicks)
Each tumbler: safe zone shrinks by 3 degrees
Time limit: 20 seconds per tumbler
```

**Feedback**: On success: `CLICK` sound + tumbler locks (visual tick). On fail: resets that tumbler, -3 seconds from timer.

#### 6.1.4 Mini-Game 3: Code Breaker (Wordle-Style)

```
Screen: A 4-digit code must be guessed
Each digit: 0–9
Player input: Number buttons rendered as grid
Feedback per guess:
  - Green: Correct digit, correct position
  - Yellow: Correct digit, wrong position
  - Gray: Digit not in code
Max attempts: 6
Time limit: None (pure logic)
```

#### 6.1.5 Mini-Game 4: Neural Reflex (Reaction Time)

```
Screen: 5 random prompts flash in sequence
Each prompt: Arrow direction (↑↓←→) OR button (A/B/X/Y rendered on screen)
Display time: 800ms each, 400ms gap
Player must click the correct on-screen button
Score: Correct within 600ms = perfect, 600-800ms = good, miss = fail
```

#### 6.1.6 Mini-Game 5: Market Hustle (Shell Game)

```
Screen: 3 cups shuffled visually
Credit bet: Player bets 10/25/50 credits
Shuffle: 5-8 random cup swaps (animated, speed scales with zone difficulty)
Player clicks cup they believe hides the prize
Win: 2× credits bet
Lose: Credits lost
```

#### 6.1.7 Mini-Game 6: Data Corruption (Memory Sequence)

```
Screen: A sequence of 4–7 symbols flashes (0.5s each, with 0.2s gaps)
Sequence length: 4 in early zones, +1 per 2 zones
Player must click the symbols in the correct order from a displayed grid
Time to reproduce: 10 seconds after sequence ends
```

#### 6.1.8 Secret Room Structure

```javascript
const SECRET_ROOM_TIERS = {
    GOLD: {
        bossHpMultiplier: 1.5,
        rewardPool: 'legendary',
        relicGuaranteed: true,
        goldReward: [80, 120]
    },
    SILVER: {
        bossHpMultiplier: 1.2,
        rewardPool: 'rare',
        relicGuaranteed: false,
        relicChance: 0.5,
        goldReward: [40, 70]
    },
    BRONZE: {
        bossHpMultiplier: 1.0,
        rewardPool: 'uncommon',
        relicGuaranteed: false,
        relicChance: 0.2,
        goldReward: [20, 40]
    }
}
```

Secret room bosses are a separate pool of 6 unique enemies not found in normal zones. Each has a distinct name, dialogue line, and exclusive relic drop.

---

### 6.2 Relic System (Complete Implementation)

**Current state**: UI skeleton only. This completes the system.

#### 6.2.1 Relic Data Structure

```javascript
const RELICS = [
    {
        id: 'relic_ghost_chip',
        name: 'Ghost Chip',
        rarity: 'uncommon',
        description: 'Phase through attacks once per room.',
        flavorText: 'Salvaged from a dead netrunner. Still warm.',
        effect: {
            type: 'proc',
            trigger: 'on_hit_received',
            condition: 'once_per_room',
            action: 'negate_damage',
            params: {}
        },
        sprite: null  // Rendered as text icon for now
    }
    // ... minimum 20 relics required for system to feel meaningful
]
```

#### 6.2.2 Relic Effect Types

| Type | Description |
|---|---|
| `passive_stat` | Flat stat bonus applied permanently |
| `passive_percent` | Percentage stat modifier |
| `proc` | Triggers on specific game event |
| `on_spell_cast` | Triggers when player casts a specific spell type |
| `on_kill` | Triggers when player kills an enemy |
| `on_low_hp` | Triggers when player HP drops below threshold |
| `room_start` | Applies effect at the start of each room |
| `boss_modifier` | Only active during boss fights |

#### 6.2.3 Relic Stacking Rules

- Maximum 5 relics held simultaneously
- Multiple copies of same relic: stack effects (no cap unless specified)
- Relics persist for the entire run (no removal)
- Relics display in a dedicated HUD row during combat

---

### 6.3 Expand Passive Skills (5 → 30)

**Current passives** (preserve, do not modify): Crit, Lifesteal, Dodge, Block DR, CD Reduction.

**25 new passives to add**:

```javascript
// New passive skill definitions — add to existing passive pool:
[
    { id: 'passive_execution', name: 'Executioner', effect: 'Deal +50% damage to enemies below 25% HP', stat: 'execute_bonus', value: 0.5 },
    { id: 'passive_momentum', name: 'Momentum', effect: '+5% ATK per combo stack (max +50%)', stat: 'combo_atk_bonus', value: 0.05 },
    { id: 'passive_spellweave', name: 'Spellweave', effect: 'Every 3rd spell cast costs 0 MP', stat: 'free_cast_interval', value: 3 },
    { id: 'passive_overclock', name: 'Overclock', effect: '+15% SPD when below 50% HP', stat: 'low_hp_spd_bonus', value: 0.15 },
    { id: 'passive_vampiric', name: 'Vampiric Aura', effect: 'AoE spells drain 5% HP from all hit enemies', stat: 'aoe_drain', value: 0.05 },
    { id: 'passive_ironwall', name: 'Iron Wall', effect: 'Block absorbs 15% more damage per cast', stat: 'block_dr_per_cast', value: 0.15 },
    { id: 'passive_ghost', name: 'Ghost Protocol', effect: 'First hit in combat always misses (ghost)', stat: 'first_hit_immune', value: 1 },
    { id: 'passive_resonance', name: 'Spell Resonance', effect: 'EX spells deal +25% bonus damage', stat: 'ex_spell_bonus', value: 0.25 },
    { id: 'passive_shrapnel', name: 'Shrapnel', effect: 'Killing a mob deals 10% of their max HP to adjacent enemies', stat: 'kill_splash', value: 0.10 },
    { id: 'passive_meditate', name: 'Meditate', effect: 'Resting rooms restore +30% additional HP', stat: 'rest_bonus', value: 0.30 },
    { id: 'passive_blackmarket', name: 'Black Market', effect: 'Merchant prices reduced by 20%', stat: 'merchant_discount', value: 0.20 },
    { id: 'passive_doubledown', name: 'Double Down', effect: '10% chance any spell fires twice', stat: 'double_cast_chance', value: 0.10 },
    { id: 'passive_voltaic', name: 'Voltaic', effect: 'Crits apply 2-turn shock (deals 8 damage/turn)', stat: 'crit_shock', value: 8 },
    { id: 'passive_feedback', name: 'Feedback Loop', effect: 'Taking damage charges next attack (+1% per 10 damage taken)', stat: 'damage_charge', value: 0.001 },
    { id: 'passive_overclock2', name: 'Neural Lace', effect: 'MP regenerates +2 per turn', stat: 'mp_regen', value: 2 },
    { id: 'passive_hardened', name: 'Hardened', effect: '+5 flat DEF per zone cleared', stat: 'zone_def_bonus', value: 5 },
    { id: 'passive_berserk', name: 'Berserk', effect: '+2% ATK for each HP lost (max +60%)', stat: 'hp_loss_atk', value: 0.02 },
    { id: 'passive_opportunist', name: 'Opportunist', effect: '+30% damage against stunned/debuffed enemies', stat: 'debuff_bonus', value: 0.30 },
    { id: 'passive_spell_echo', name: 'Spell Echo', effect: 'Last cast spell has 15% chance to auto-repeat', stat: 'echo_chance', value: 0.15 },
    { id: 'passive_warlord', name: 'Warlord', effect: '+5% all damage per elite enemy killed this run', stat: 'elite_kill_bonus', value: 0.05 },
    { id: 'passive_phase', name: 'Phase Shift', effect: 'Teleport (dodge) cooldown reduced by 1 turn', stat: 'dodge_cd_reduction', value: 1 },
    { id: 'passive_scavenger', name: 'Scavenger', effect: 'Enemies drop +25% gold', stat: 'gold_bonus', value: 0.25 },
    { id: 'passive_fortify', name: 'Fortify', effect: '+10 max HP per room cleared (up to +100)', stat: 'room_hp_bonus', value: 10, cap: 100 },
    { id: 'passive_chain', name: 'Chain Lightning', effect: 'Single-target spells have 20% chance to jump to a second enemy at 50% damage', stat: 'chain_chance', value: 0.20 },
    { id: 'passive_predator', name: 'Predator', effect: '+15% damage against enemies with higher max HP than player current HP', stat: 'predator_bonus', value: 0.15 }
]
```

---

### 6.4 Weapon Abilities (Proc Effects)

Add a `procEffect` property to each of the 30 weapons. Format:

```javascript
{
    id: 'weapon_plasma_katana',
    name: 'Plasma Katana',
    // ... existing properties ...
    passive: 'ATK +18, +5% crit chance',
    procEffect: {
        trigger: 'on_hit',
        chance: 0.10,
        action: 'cast_free',
        spell: 'neon_slash',        // Must reference an existing spell ID
        description: '10% chance to cast free Neon Slash on hit'
    }
}
```

Proc effects fire AFTER the triggering attack resolves. Display as floating text: `[WEAPON NAME] PROC!` in gold.

---

### 6.5 Spell Synergy Indicators

When the player's active loadout contains complementary spell combinations, display a `SYNERGY` indicator on the combat HUD.

**Synergy Definitions** (minimum 10 pairs to implement):

```javascript
const SYNERGIES = [
    { 
        id: 'stun_execute', 
        spells: ['any_stun', 'any_execute'],
        name: 'KNOCKOUT PROTOCOL',
        bonus: '+40% execute damage on stunned targets',
        color: '#ffd700'
    },
    {
        id: 'bleed_multi',
        spells: ['any_bleed_applier', 'any_multi_hit'],
        name: 'HEMORRHAGE',
        bonus: 'Multi-hit triggers bleed stacks individually',
        color: '#ff4444'
    },
    {
        id: 'shield_reflect',
        spells: ['any_shield', 'any_reflect'],
        name: 'MIRROR PROTOCOL',
        bonus: 'Shield absorb triggers reflect at 50% value',
        color: '#00ffff'
    },
    {
        id: 'aoe_combo',
        spells: ['any_aoe', 'any_combo_builder'],
        name: 'CHAIN REACTION',
        bonus: 'AoE hits count for combo counter individually',
        color: '#ff00ff'
    },
    {
        id: 'heal_lifesteal',
        spells: ['any_heal', 'lifesteal_passive'],
        name: 'VAMPIRE LORD',
        bonus: 'Healing spells also trigger lifesteal calculation',
        color: '#00ff41'
    }
    // Add 5 more based on common spell combinations found in the pool
]
```

**UI**: A compact synergy display appears in the spell loadout panel. Synergy name in appropriate color, 8px `"Press Start 2P"`. Tooltip on hover showing the bonus.

---

## 7. PHASE 3 — VISUAL & AUDIO POLISH

**Do not begin until Phase 2 is complete and committed.**

### 7.1 Weather & Atmosphere Per Zone

Each of the 8 zones gets a unique particle/atmosphere effect rendered as a Canvas overlay layer.

```javascript
const ZONE_ATMOSPHERES = {
    'neon_nexus':     { type: 'neon_rain',    color: '#00ffff', density: 0.7 },
    'data_vaults':    { type: 'code_stream',  color: '#00ff41', density: 0.5 },
    'chrome_wastes':  { type: 'ash_fall',     color: '#888888', density: 0.4 },
    'virus_lanes':    { type: 'corruption',   color: '#ff00ff', density: 0.9 },
    'core_approach':  { type: 'energy_arcs',  color: '#ffffff', density: 0.6 },
    'ghost_sector':   { type: 'static_fog',   color: '#4444ff', density: 0.3 },
    'black_ice':      { type: 'ice_crystals', color: '#aaddff', density: 0.5 },
    'the_core':       { type: 'reality_tear', color: '#ff4400', density: 1.0 }
}
```

**Particle system** (new, generic, reusable):

```javascript
class ParticleSystem {
    constructor(type, color, density, canvasWidth, canvasHeight) { }
    update(deltaTime) { }
    render(ctx) { }
    // Particle types: rain (vertical fall), stream (horizontal drift), 
    //                 float (upward drift), static (random flicker), arc (curved paths)
}
```

Particles render BEHIND sprites but ABOVE background image. Performance cap: max 200 active particles per system.

### 7.2 Enhanced Spell Cast Animations

For each spell category, extend existing VFX with:

| Category | Enhancement |
|---|---|
| Heavy attack spells | 2-frame screen shake (±4px canvas offset, then snap back) |
| Execute spells | Slow-motion effect: `deltaTime * 0.3` for 8 frames, then snap |
| AoE spells | Ripple ring expanding from center of enemy group |
| Shield spells | Player sprite surrounded by hex-grid shield pattern (6 hexagons, rotated) |
| Heal spells | Green particles rising from player sprite |
| EX spells | Same as base + gold outline on spell name in combat log |

Screen shake implementation:
```javascript
// Add to render loop:
let screenShake = { x: 0, y: 0, duration: 0 };

function applyScreenShake(intensity, duration) {
    screenShake = { 
        x: (Math.random() - 0.5) * intensity * 2, 
        y: (Math.random() - 0.5) * intensity * 2, 
        duration 
    };
}

// In render loop, before drawing:
if (screenShake.duration > 0) {
    ctx.translate(screenShake.x, screenShake.y);
    screenShake.duration--;
    if (screenShake.duration <= 0) { screenShake.x = 0; screenShake.y = 0; }
}
```

### 7.3 Enemy Entrance & Death Animations

**Entrance** (play when enemy appears in room):
- Glitch-in effect: render enemy sprite with horizontal displacement that decays over 12 frames
- Each frame: random X offset (-8 to +8px), decreasing magnitude
- Accompanied by static/noise audio cue (Web Audio, short)

**Death**:
- Current kill cam: enhance by adding color desaturation over 6 frames, then pixel scatter (sprite breaks into 6×6 pixel chunks that fly outward)
- Elite/boss deaths: Add screen flash (white, 2 frames) before scatter

### 7.4 Screen Transition Effects

Between screens (world map → zone, zone → combat, etc.):

```javascript
// Glitch transition (add to all screen state changes):
function glitchTransition(duration, callback) {
    let frame = 0;
    const totalFrames = duration; // e.g., 15
    
    function step() {
        if (frame < totalFrames) {
            // Draw horizontal noise bands across full canvas
            drawGlitchBands(ctx, frame / totalFrames);
            frame++;
            requestAnimationFrame(step);
        } else {
            callback(); // Execute screen change
        }
    }
    step();
}

function drawGlitchBands(ctx, progress) {
    const bandCount = 8;
    for (let i = 0; i < bandCount; i++) {
        const y = Math.random() * canvas.height;
        const h = Math.random() * 20 + 5;
        const xOffset = (Math.random() - 0.5) * 40 * (1 - progress);
        ctx.drawImage(canvas, xOffset, y, canvas.width, h, xOffset, y, canvas.width, h);
    }
}
```

---

## 8. PHASE 4 — AI INTEGRATION ARCHITECTURE

**Do not begin until Phase 3 is complete. Phase 4 requires the Cloudflare Worker to be deployed first (see Section 11).**

### 8.1 Core Architecture Decision

**Selected**: Option C (Hybrid) — Pre-generated base content + optional live AI enhancement.

**Non-negotiable rule**: The game must run fully and completely with ZERO AI calls. All AI features are progressive enhancement only. If the AI proxy is unreachable, the game falls back to pre-generated content silently.

### 8.2 AI Feature Priority (Ordered)

| Priority | Feature | Call Timing | Latency Budget | Fallback |
|---|---|---|---|---|
| 1 | Dungeon Master narration | Boss intro, room transition | 2000ms | Static lore snippets from JSON |
| 2 | Post-run AI coaching | Run summary screen | 3000ms | Static performance message |
| 3 | AI difficulty tuning | Between zones (invisible) | 3000ms | Preset difficulty curve |
| 4 | Zone lore generation | World map zone hover | 1500ms | Pre-written zone descriptions |
| 5 | Spell swap commentary | Spell swap screen | 1500ms | Generic loadout description |

### 8.3 AI Call Architecture

```javascript
// AI service module (add to game file as self-contained section):
const AIService = {
    WORKER_URL: 'https://neon-dungeon-ai.YOUR_SUBDOMAIN.workers.dev',
    TIMEOUT_MS: 3000,
    enabled: true,  // Toggled off if worker unreachable
    
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
            return data.result;
            
        } catch (err) {
            clearTimeout(timeout);
            if (err.name === 'AbortError') {
                console.warn('[AI] Timeout — using fallback content');
            } else {
                console.warn('[AI] Unreachable — disabling for session');
                this.enabled = false;
            }
            return null;
        }
    }
};
```

### 8.4 Feature 1: Dungeon Master Narration

**Trigger points and payload schemas** (see Section 10 for full prompt templates):

```javascript
// On boss intro (before combat begins):
async function getBossNarration(boss, player, zone) {
    const payload = {
        bossName: boss.name,
        bossPhase: 1,
        playerClass: player.class,
        playerLevel: player.level,
        playerHp: player.hp,
        playerSpells: player.spells.map(s => s.name),
        zoneName: zone.name,
        runDepth: state.zonesCleared  // How far into the run
    };
    
    const narration = await AIService.call('boss_narration', payload);
    return narration || FALLBACK_BOSS_NARRATIONS[boss.id] || DEFAULT_BOSS_NARRATION;
}

// Render narration in terminal-style text box:
function renderNarrationBox(ctx, text, x, y, width) {
    // Typewriter effect: reveal 2 characters per frame
    // Font: "Share Tech Mono" 10px, color: #00ff41 (matrix green)
    // Background: semi-transparent #0a0a1a with cyan border
    // Prefix: "> DM: " in magenta
}
```

### 8.5 Feature 2: Post-Run AI Coaching

```javascript
// On run end (win or death), before showing run summary:
async function getRunCoaching(runData) {
    const payload = {
        outcome: runData.outcome,          // 'victory' | 'defeat'
        deathCause: runData.deathCause,    // null or enemy/spell name
        zonesCleared: runData.zonesCleared,
        spellsUsed: runData.spellCastLog,  // Array of {spellId, castCount}
        swapHistory: runData.swapHistory,  // Array of {offered, kept, swapped}
        passivesEquipped: runData.passives,
        totalDamageDealt: runData.stats.damageDealt,
        totalDamageTaken: runData.stats.damageTaken,
        missedCounters: runData.stats.missedCounterOpportunities,
        miniGamesPlayed: runData.miniGames
    };
    
    const coaching = await AIService.call('run_coaching', payload);
    return coaching || generateLocalCoaching(runData);
}
```

### 8.6 Feature 3: AI Difficulty Tuning

**This runs silently between zones. Player never sees it directly.**

```javascript
// Called after zone boss is defeated, before loading next zone:
async function tuneNextZoneDifficulty(performanceMetrics) {
    const payload = {
        currentZone: state.currentZone,
        nextZone: state.nextZone,
        hpPercentageEnteringBoss: performanceMetrics.bossEntryHpPct,
        turnsToKillBoss: performanceMetrics.bossTurns,
        missedCounterRate: performanceMetrics.counterMissRate,
        deathsThisRun: performanceMetrics.deaths,
        spellEfficacy: performanceMetrics.spellHitRate
    };
    
    const tuning = await AIService.call('difficulty_tuning', payload);
    
    if (tuning) {
        // Apply tuning modifiers to next zone enemy definitions
        applyDifficultyModifiers(tuning.enemyStatMultiplier, tuning.abilityProbability);
    }
    // If no tuning returned: use preset difficulty curve (no change)
}
```

---

## 9. PHASE 5 — ENDGAME & COMPETITIVE

**Do not begin until Phase 4 is complete.**

### 9.1 Run History (localStorage)

```javascript
// Run record structure stored in localStorage['neonDungeon_runHistory']:
const RUN_RECORD = {
    id: Date.now(),
    date: new Date().toISOString(),
    playerClass: '',
    outcome: 'victory' | 'defeat',
    zonesCleared: 0,
    finalZone: '',
    deathCause: null,
    duration: 0,            // seconds
    spellsDiscovered: [],   // spell IDs seen during run
    finalLoadout: [],       // 4 spell IDs at run end
    stats: {
        damageDealt: 0,
        damageTaken: 0,
        healingDone: 0,
        enemiesKilled: 0,
        bossesKilled: 0,
        critCount: 0,
        perfectCounters: 0,
        miniGamesCompleted: 0,
        goldEarned: 0
    }
}
// Maximum stored: 50 runs (FIFO, drop oldest)
```

### 9.2 Daily Challenge Runs

```javascript
// Seed generation (deterministic from date):
function getDailySeed() {
    const date = new Date();
    const dateStr = `${date.getFullYear()}${date.getMonth()}${date.getDate()}`;
    return parseInt(dateStr) * 31337; // Arbitrary prime multiplier for seed variation
}

// Seeded RNG (LCG algorithm — replaces Math.random() for all roguelike decisions during seeded run):
function createSeededRNG(seed) {
    let s = seed;
    return function() {
        s = (s * 1664525 + 1013904223) & 0xffffffff;
        return (s >>> 0) / 0xffffffff;
    };
}
```

Daily challenge modifiers (pick 2 randomly from this pool, seeded by date):

```javascript
const CHALLENGE_MODIFIERS = [
    { id: 'glass_cannon', name: 'GLASS CANNON', desc: '+50% ATK, -50% DEF' },
    { id: 'spell_locked', name: 'SPELL LOCKED', desc: 'No spell swaps allowed this run' },
    { id: 'cursed_gold', name: 'CURSED GOLD', desc: 'Enemies have 2× HP; 2× gold drops' },
    { id: 'overclock', name: 'OVERCLOCK', desc: 'All SPD doubled — for everyone' },
    { id: 'one_spell', name: 'MONO-CASTER', desc: 'Only 1 spell slot (the others are locked)' },
    { id: 'no_potions', name: 'DRY RUN', desc: 'No potions allowed' },
    { id: 'elite_only', name: 'ELITE GAUNTLET', desc: 'All standard enemies replaced with advanced tier' },
    { id: 'permastun', name: 'UNSTABLE GRID', desc: 'Both player and enemies have 20% chance to self-stun' }
]
```

### 9.3 Achievement System

```javascript
// Achievements stored in localStorage['neonDungeon_achievements']:
const ACHIEVEMENTS = [
    { id: 'first_clear', name: 'Jack In', desc: 'Complete your first run', condition: 'runs_won >= 1', reward: 'unlock_portrait_neon' },
    { id: 'speed_run', name: 'Speed Daemon', desc: 'Clear any zone in under 3 minutes', condition: 'zone_clear_time < 180', reward: null },
    { id: 'no_damage_boss', name: 'Ghost Protocol', desc: 'Defeat any boss without taking damage', condition: 'boss_no_damage', reward: 'unlock_spell_ghost_strike' },
    { id: 'all_minigames', name: 'Side Hustle', desc: 'Complete all 6 mini-game types in one run', condition: 'minigames_completed_types >= 6', reward: null },
    { id: 'perfect_counter_10', name: 'Reflex God', desc: 'Land 10 perfect counters in one run', condition: 'perfect_counters >= 10', reward: null },
    { id: 'evolve_all', name: 'EX Machine', desc: 'Evolve all 4 spells to EX in one run', condition: 'ex_spells_at_end >= 4', reward: 'unlock_class_ex_variant' },
    { id: 'no_heal_clear', name: 'Aggro', desc: 'Clear The Core without using any healing spell', condition: 'clear_no_heal', reward: null },
    { id: 'daily_10', name: 'Daily Driver', desc: 'Complete 10 daily challenges', condition: 'daily_completions >= 10', reward: null }
    // Minimum 20 achievements required
]
```

---

## 10. AI PAYLOAD SCHEMAS & PROMPT TEMPLATES

**These are the exact prompts sent to the Cloudflare Worker, which forwards them to the Claude API. They must be followed precisely.**

### 10.1 Boss Narration Prompt

```javascript
const BOSS_NARRATION_PROMPT = (payload) => `
You are the Dungeon Master of Neon Dungeon, a grimdark cyberpunk roguelike set in a neon-soaked dystopia. Your tone is Warhammer 40K grimness blended with Ghost in the Shell philosophical dread.

CURRENT CONTEXT:
- Player class: ${payload.playerClass}
- Player level: ${payload.playerLevel}
- Player HP: ${payload.playerHp}%
- Player's active spells: ${payload.playerSpells.join(', ')}
- Zone: ${payload.zoneName}
- Boss: ${payload.bossName}
- Run depth: Zone ${payload.runDepth} of 8

REQUIREMENTS:
- Write exactly 2 sentences of combat narration for this boss encounter
- First sentence: describe the boss appearing/speaking (menacing, specific to their identity)
- Second sentence: hint at what the player must do to survive (vague but tactically relevant)
- Tone: cold, brutal, no hope
- No emojis, no exclamation points, no hero's journey encouragement
- Maximum 40 words total

Respond with ONLY the narration text. No preamble, no labels, no quotes.
`;
```

### 10.2 Run Coaching Prompt

```javascript
const RUN_COACHING_PROMPT = (payload) => `
You are a cold, data-driven combat analyst reviewing a cyberpunk dungeon run. Provide tactical coaching with zero sentimentality.

RUN DATA:
- Outcome: ${payload.outcome}
${payload.deathCause ? `- Died to: ${payload.deathCause}` : ''}
- Zones cleared: ${payload.zonesCleared}/8
- Most used spell: ${getMostUsed(payload.spellsUsed)}
- Damage dealt/taken ratio: ${(payload.totalDamageDealt / Math.max(1, payload.totalDamageTaken)).toFixed(2)}
- Missed counter opportunities: ${payload.missedCounters}
- Spell swap pattern: ${summarizeSwaps(payload.swapHistory)}

REQUIREMENTS:
- 3 bullet points maximum
- Each point: one specific, actionable coaching tip based on the data
- Be blunt. If they played poorly, say so with data.
- Reference specific spells or mechanics when relevant
- Maximum 15 words per bullet point
- Format: start each bullet with "▸ "

Respond with ONLY the 3 bullet points. No preamble, no score, no encouragement.
`;
```

### 10.3 Difficulty Tuning Prompt

```javascript
const DIFFICULTY_TUNING_PROMPT = (payload) => `
You are a difficulty balancer for a roguelike game. Analyze player performance and return a JSON tuning object.

PERFORMANCE DATA (Zone ${payload.currentZone} → ${payload.nextZone}):
- HP entering boss: ${payload.hpPercentageEnteringBoss}% of max
- Turns to kill boss: ${payload.turnsToKillBoss} (expected: 15-25)
- Counter miss rate: ${payload.counterMissRate}% (healthy: <40%)
- Deaths this run: ${payload.deathsThisRun}

TUNING RULES:
- If player is dominant (boss HP > 70%, turns < 12, miss rate < 20%): increase challenge
- If player is struggling (boss HP < 30%, turns > 30, miss rate > 60%): reduce challenge  
- If player is balanced: minor adjustment only
- Max tuning swing: ±25% stat multiplier, ±15% ability probability
- Never reduce below 0.7× base stats; never exceed 1.5× base stats

Respond with ONLY valid JSON, no markdown, no explanation:
{
  "enemyStatMultiplier": 1.0,
  "abilityProbability": 1.0,
  "reasoning": "one sentence max"
}
`;
```

---

## 11. CLOUDFLARE WORKER PROXY SPECIFICATION

**This is a separate file deployed to Cloudflare — NOT part of the game HTML.**

### 11.1 Worker File: `worker/worker.js`

```javascript
// Neon Dungeon AI Proxy Worker
// Deploy via: wrangler deploy
// Environment variable required: ANTHROPIC_API_KEY (set in Cloudflare dashboard, NOT in code)

const ALLOWED_FEATURES = ['boss_narration', 'run_coaching', 'difficulty_tuning', 'zone_lore', 'spell_commentary'];
const MAX_TOKENS_PER_FEATURE = {
    boss_narration: 80,
    run_coaching: 120,
    difficulty_tuning: 150,
    zone_lore: 100,
    spell_commentary: 80
};

export default {
    async fetch(request, env) {
        // CORS headers
        const corsHeaders = {
            'Access-Control-Allow-Origin': '*',  // Restrict to your domain in production
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        };
        
        if (request.method === 'OPTIONS') {
            return new Response(null, { headers: corsHeaders });
        }
        
        if (request.method !== 'POST') {
            return new Response('Method not allowed', { status: 405 });
        }
        
        let body;
        try {
            body = await request.json();
        } catch {
            return new Response('Invalid JSON', { status: 400 });
        }
        
        const { feature, payload } = body;
        
        // Validate feature type
        if (!ALLOWED_FEATURES.includes(feature)) {
            return new Response('Unknown feature', { status: 400 });
        }
        
        // Build prompt from feature type
        const prompt = buildPrompt(feature, payload);
        if (!prompt) {
            return new Response('Failed to build prompt', { status: 400 });
        }
        
        // Call Claude API
        try {
            const claudeResponse = await fetch('https://api.anthropic.com/v1/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': env.ANTHROPIC_API_KEY,
                    'anthropic-version': '2023-06-01'
                },
                body: JSON.stringify({
                    model: 'claude-haiku-4-5-20251001',  // Haiku for cost efficiency in real-time calls
                    max_tokens: MAX_TOKENS_PER_FEATURE[feature] || 100,
                    messages: [{ role: 'user', content: prompt }]
                })
            });
            
            if (!claudeResponse.ok) {
                throw new Error(`Claude API error: ${claudeResponse.status}`);
            }
            
            const claudeData = await claudeResponse.json();
            const result = claudeData.content[0]?.text || '';
            
            return new Response(
                JSON.stringify({ result }),
                { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            );
            
        } catch (err) {
            console.error('Claude API call failed:', err);
            return new Response(
                JSON.stringify({ result: null, error: 'AI unavailable' }),
                { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
                // Return 200 with null result so game falls back gracefully
            );
        }
    }
};

function buildPrompt(feature, payload) {
    // Implement prompt templates from Section 10 here
    // Each case returns the formatted prompt string
    switch(feature) {
        case 'boss_narration': return buildBossNarrationPrompt(payload);
        case 'run_coaching': return buildRunCoachingPrompt(payload);
        case 'difficulty_tuning': return buildDifficultyTuningPrompt(payload);
        case 'zone_lore': return buildZoneLorePrompt(payload);
        case 'spell_commentary': return buildSpellCommentaryPrompt(payload);
        default: return null;
    }
}
```

### 11.2 Wrangler Configuration: `worker/wrangler.toml`

```toml
name = "neon-dungeon-ai"
main = "worker.js"
compatibility_date = "2024-01-01"

[vars]
# Do NOT put ANTHROPIC_API_KEY here
# Set it via: wrangler secret put ANTHROPIC_API_KEY

[[routes]]
pattern = "neon-dungeon-ai.YOUR_SUBDOMAIN.workers.dev/*"
zone_name = "workers.dev"
```

### 11.3 Deployment Steps (One-Time Setup)

1. `npm install -g wrangler` — Install Cloudflare CLI
2. `wrangler login` — Authenticate with Cloudflare account
3. `cd worker && wrangler deploy` — Deploy the worker
4. `wrangler secret put ANTHROPIC_API_KEY` — Set API key securely (never in code)
5. Update `AIService.WORKER_URL` in game file with the deployed worker URL
6. Test with `curl -X POST https://YOUR_WORKER_URL -H "Content-Type: application/json" -d '{"feature":"boss_narration","payload":{"bossName":"Test"}}'`

---

## 12. TESTING & ACCEPTANCE CRITERIA

### 12.1 Phase 1 Acceptance

- [ ] Enemy telegraphing fires correctly per trigger rules (verify with 50 simulated combats)
- [ ] Counter-attack bonuses apply correctly for all 4 counter types
- [ ] Boss phase transitions trigger at correct HP thresholds (60%, 25%)
- [ ] Phase transition sequence completes without freezing combat loop
- [ ] Shield phase mechanic correctly blocks damage and responds to `armor_pierce` tagged spells
- [ ] Active dodge bar appears and resolves correctly in under 16ms (one frame)
- [ ] Passive mode (`combatMode: 'passive'`) reverts to original dodge % behavior
- [ ] No existing combat functionality is broken (auto-attack, spells, buffs, combos still work)

### 12.2 Phase 2 Acceptance

- [ ] All 6 mini-games render and complete correctly on Canvas
- [ ] Mini-game trigger chance matches specification (25%/40%)
- [ ] Secret room reward tiers deliver correct item pools
- [ ] 20 relics implemented with distinct effects
- [ ] 25 new passives visible in character creation/level-up
- [ ] Weapon proc effects fire at correct probability and display floating text
- [ ] Minimum 5 synergies detect and display correctly

### 12.3 Phase 3 Acceptance

- [ ] Each zone has unique atmosphere particles, max 200 particles, no frame rate drop below 30fps
- [ ] Screen shake fires on heavy/execute spells and self-corrects within 2 frames
- [ ] Enemy entrance glitch animation completes in under 12 frames
- [ ] Glitch transition between screens completes in ~250ms
- [ ] No visual artifacts remaining after transitions

### 12.4 Phase 4 Acceptance

- [ ] Game loads and plays fully with no internet connection (AI features silently absent)
- [ ] AI call with worker URL returns narration within 2000ms on fast connection
- [ ] Timeout (3000ms exceeded) triggers fallback content without error
- [ ] Worker returns 200 with `null` result on Claude API failure; game handles it
- [ ] No API key is visible anywhere in the game HTML file
- [ ] Typewriter narration renders correctly with `"Share Tech Mono"`

---

## 13. DO NOT TOUCH LIST

The following systems are working correctly. **Do not modify them unless a phase above explicitly requires it.** Any modification requires a comment explaining why.

- Apple II boot screen and asset preloading sequence
- Core speed-based turn system (`actionCounter` fill logic)
- Spell evolution system (10 casts → EX, -1 cooldown)
- Existing 30 attack spells, 30 defensive spells, 30 potions — definitions only (proc effects added in Phase 2 are additive)
- Existing 5 passive skills (extend, don't replace)
- `localStorage` save key names (changing these breaks existing saves)
- Web Audio procedural SFX system
- Existing VFX: explode, slash, spark, ring, kill cam, spell flash
- Character creation grid layout
- World map zone unlock progression logic
- Quest system pool and active quest mechanics

---

## 14. CHANGE LOG

| Date | Version | Change | Author |
|---|---|---|---|
| 2026-03-26 | 1.0 | Initial specification created from design brief | NeuroNeko + Claude |
| 2026-03-26 | 1.1 | Added two-tier workflow model; updated repo section for active development context; removed greenfield assumptions; Claude Code operating rules added to header | NeuroNeko + Claude |

---

*This document is authoritative. When in doubt: read this document, ask the developer, then code. In that order.*

*Repository: github.com/vikaruxdroid-max/8bit-cyberpunk-roguelike*
*Last updated: 2026-03-26*

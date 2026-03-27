# NEON DUNGEON — INSTRUCTION BLOCK 1.4
## ACE ATTORNEY REACTION COMBAT SYSTEM
### Claude Chat Architect Layer · 2026-03-26
### Priority: HIGH — This upgrades Phase 1.1 UI and replaces Phase 1.3 dodge window

---

> **WHAT THIS IS**: A full replacement of the Phase 1 combat *presentation layer*. The telegraph data
> structures from Block 1.1 are KEPT and reused. The telegraph UI rendering is REPLACED. The active
> dodge window from Block 1.3 is REMOVED — dodging is now a spell reaction option, not a separate bar.
> The Phase 1.1 counter bonus system becomes the effectiveness grading engine for this new system.
> No core combat logic (damage calc, buffs, debuffs, speed turns) changes.

---

## PRE-IMPLEMENTATION SCAN

Before writing any code, locate and report:

1. The `renderTelegraphWarning()` function added in Block 1.1 — it will be REPLACED
2. The `openDodgeWindow()` / `renderDodgeWindow()` / `handleDodgeWindowClick()` functions from Block 1.3 — they will be REMOVED
3. The `buildTelegraph()` and `checkPlayerCounter()` functions from Block 1.1 — they are KEPT
4. Where player spell buttons are rendered during combat (the 4-slot spell UI)
5. The main combat canvas rendering function name
6. Where combat screen dimming / overlay effects are currently handled (if at all)
7. The game's primary canvas variable name (e.g. `canvas`, `gameCanvas`) and 2D context name

Report all seven. Then proceed.

---

## STEP 1 — REMOVE SUPERSEDED PHASE 1 CODE

1. DELETE the `renderTelegraphWarning()` function entirely
2. DELETE `openDodgeWindow()`, `renderDodgeWindow()`, `updateDodgeWindow()`, `handleDodgeWindowClick()` entirely
3. DELETE the `dodgeWindow` state object from combat state
4. DELETE the dodge window click handler hook from the canvas click handler
5. DELETE the `renderDodgeWindow(ctx)` call from the combat render pass
6. DELETE the `updateDodgeWindow(deltaTime)` call from the game update loop

**Do NOT delete:** `buildTelegraph()`, `determineTelegraph()`, `checkPlayerCounter()`, `applyCounterBonus()`,
the `telegraph` property on enemies, or spell `tags` arrays. Those are all kept.

After deleting, confirm the game still loads without errors before continuing.

---

## STEP 2 — ADD REACTION SYSTEM STATE

Add to the combat state object (wherever `dodgeWindow` used to live):

```javascript
reactionPhase: {
    active: false,
    enemy: null,              // reference to the attacking enemy
    telegraph: null,          // the telegraph object from Block 1.1
    timeLimit: 3000,          // ms — set per attack when opened
    timeRemaining: 3000,      // ms — counts down
    timerStarted: 0,          // Date.now() when window opened
    playerResponded: false,
    responseSpell: null,      // spell object the player clicked
    responseGrade: null,      // 'nullify'|'silence'|'absorb'|'clash'|'resist'|'direct_hit'
    bubbleScale: 0,           // 0→1 animation progress (bubble expand-in)
    bubbleRotation: 0,        // slight tilt angle in radians
    tauntText: '',            // enemy taunt line pulled from pool
    resultText: '',           // player result line shown post-resolution
    resultTimer: 0,           // ms to show result text before clearing
    pendingQueue: []          // named attacks from other enemies waiting their turn
}
```

---

## STEP 3 — ADD COMEDY TEXT POOLS

Insert as a constant block near the top of the JS (outside any function):

```javascript
// ============================================================
// REACTION COMBAT — COMEDY TEXT POOLS
// ============================================================

const ENEMY_TAUNTS = {
    // Generic — used for any enemy without a specific pool
    generic: [
        'THIS WILL HURT.',
        'YOUR FIREWALL IS GARBAGE.',
        'FEEL THE BYTE.',
        'DELETING YOU NOW.',
        'FATAL ERROR: YOU.',
        'INITIATING PAIN PROTOCOL.',
        'NO INSURANCE WHERE YOU\'RE GOING.',
        'SKILL CHECK: FAILED.',
        'YOU ARE NOT PREPARED.',
        'THIS IS GOING ON YOUR PERMANENT RECORD.'
    ],
    // Boss-tier — used when enemy.tier === 'boss'
    boss: [
        'I HAVE BEEN WAITING FOR THIS.',
        'YOUR SUFFERING IS SCHEDULED.',
        'THREAT LEVEL: YOU. RESPONSE: MAXIMUM.',
        'I HAVE KILLED BETTER.',
        'YOU ARE AN ACCEPTABLE CASUALTY.',
        'THIS ZONE BELONGS TO ME. SO DO YOUR HP.',
        'OVERRIDE COMPLETE. YOU\'RE NEXT.',
        'SCANNING... TARGET ACQUIRED. GOODBYE.'
    ],
    // Per-enemy-type — key should match enemy.id prefix or enemy.name keyword
    // Add more as new enemies are defined
    samurai: [
        'HONOR IS FOR THE WEAK. PAIN IS FREE.',
        '404: DODGE NOT FOUND.',
        'MY BLADE COSTS MORE THAN YOUR LIFE.',
        'BUSHIDO.EXE HAS LOADED.',
        'CUT THE THEATRICS. AND THEN YOU.'
    ],
    virus: [
        'I\'VE ALREADY COPIED YOUR SOUL.',
        'CORRUPTION IN PROGRESS...',
        'YOU HAVE 0 ANTIVIRUS.',
        'REPLICATING INTO YOUR HP BAR.',
        'ERROR: CANNOT FIND YOUR WILL TO LIVE.'
    ],
    corporate: [
        'THIS IS CALLED A PERFORMANCE REVIEW.',
        'YOU\'RE FIRED. ALSO DEAD.',
        'SYNERGIZING YOUR DESTRUCTION.',
        'THIS VIOLENCE IS WITHIN BUDGET.',
        'KINDLY ACCEPT THIS TERMINATION PACKAGE.'
    ]
};

const REACTION_RESULT_TEXT = {
    nullify: [
        'ERROR 404: ATTACK NOT FOUND.',
        'FIREWALL ACTIVATED.',
        'NICE TRY, CHROME BREATH.',
        'NOPE.',
        'SYSTEM: DENIED.',
        'REQUEST REJECTED.',
        'BLOCKED AT THE ROUTER.',
        'NOT TODAY.',
        'PATCH APPLIED.',
        'COUNTERPROTOCOL: SUCCESS.'
    ],
    silence: [
        'SIT DOWN.',
        'CANCELLED LIKE YOUR SOCIAL CREDIT.',
        'BUFFERING... ATTACK FAILED.',
        'STUN.EXE HAS ENTERED THE CHAT.',
        'INTERRUPT SIGNAL SENT.',
        'TALK LESS. HURT LESS.',
        'SHUT IT DOWN.',
        'YOUR ATTACK HAS BEEN RESCHEDULED FOR NEVER.'
    ],
    absorb: [
        'SHIELD TOOK THE HIT. MOSTLY.',
        'OW. BUT MANAGEABLE.',
        'ABSORBED. KIND OF.',
        'SOME DAMAGE. ALL DIGNITY.',
        'SHIELD SAYS: RUDE.',
        'LESS THAN EXPECTED. STILL BAD.',
        'THE BARRIER DID ITS JOB. BARELY.'
    ],
    clash: [
        'MUTUAL ASSURED PAIN.',
        'WE BOTH FELT THAT.',
        'EQUAL OPPORTUNITY VIOLENCE.',
        'SIMULTANEOUS REGRET.',
        'NOBODY WINS. EVERYBODY HURTS.',
        'IMPRESSIVE. ALSO OW.',
        'CLASH OF THE IDIOTS.'
    ],
    resist: [
        'DAMAGE REDUCED. DIGNITY INTACT.',
        'PARTIAL HIT. STILL ALIVE. BARELY.',
        'THAT HELPED. A LITTLE.',
        'TANKED IT. SORT OF.',
        'SURVIVED. TECHNICALLY.',
        'LESS DEAD THAN EXPECTED.',
        'RESISTANCE WAS WORTH SOMETHING.'
    ],
    direct_hit: [
        'SKILL ISSUE DETECTED.',
        'FATAL EXCEPTION: PAIN.EXE',
        'HP NOT FOUND.',
        'THAT WAS YOUR FAULT.',
        'NOTED. ALSO OW.',
        'DAMAGE INCOMING. DAMAGE ARRIVED.',
        'MAYBE BLOCK NEXT TIME?',
        'DIRECT HIT. MAXIMUM DISRESPECT.',
        'YOUR SUFFERING IS VALID.',
        'REACTION TIME: UNACCEPTABLE.'
    ],
    // Special interactions — triggered by specific spell types during reaction
    potion_during_attack: [
        'YOU DRANK SOMETHING DURING MY ATTACK??',
        'ARE YOU SERIOUS RIGHT NOW.',
        'I WILL REMEMBER THIS DISRESPECT.',
        'UNBELIEVABLE. ABSOLUTELY UNBELIEVABLE.',
        'POTION SPEEDRUN. RESPECT. ALSO OW.'
    ]
};

// Helper: get a random item from an array
function randomFrom(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

// Helper: get the best taunt for an enemy
function getEnemyTaunt(enemy) {
    const name = (enemy.name || '').toLowerCase();
    if (enemy.tier === 'boss') return randomFrom(ENEMY_TAUNTS.boss);
    if (name.includes('samurai')) return randomFrom(ENEMY_TAUNTS.samurai);
    if (name.includes('virus') || name.includes('corrupt')) return randomFrom(ENEMY_TAUNTS.virus);
    if (name.includes('corp') || name.includes('exec') || name.includes('suit')) return randomFrom(ENEMY_TAUNTS.corporate);
    return randomFrom(ENEMY_TAUNTS.generic);
}
```

---

## STEP 4 — ADD THE REACTION PHASE CORE FUNCTIONS

Insert as a new named section in the JS:

```javascript
// ============================================================
// REACTION COMBAT SYSTEM — Phase 1.4
// ============================================================

// TIME LIMITS per attack tier (ms)
const REACTION_TIME = {
    normal: 2500,
    heavy: 3000,
    boss: 4000,
    execute: 3500
};

// Opens the reaction phase for a named attack
// Called instead of immediately executing the attack
function openReactionPhase(enemy, telegraph) {
    const rp = combat.reactionPhase; // use actual combat state path

    // If a reaction phase is already active, queue this one
    if (rp.active) {
        rp.pendingQueue.push({ enemy, telegraph });
        return;
    }

    const tier = telegraph.attackType || 'normal';
    const timeLimit = REACTION_TIME[tier] || REACTION_TIME.normal;

    // Set boss timer longer
    const finalTime = enemy.tier === 'boss' ? REACTION_TIME.boss : timeLimit;

    rp.active = true;
    rp.enemy = enemy;
    rp.telegraph = telegraph;
    rp.timeLimit = finalTime;
    rp.timeRemaining = finalTime;
    rp.timerStarted = Date.now();
    rp.playerResponded = false;
    rp.responseSpell = null;
    rp.responseGrade = null;
    rp.bubbleScale = 0;       // bubble will animate in
    rp.bubbleRotation = (Math.random() - 0.5) * 0.08; // slight random tilt
    rp.tauntText = getEnemyTaunt(enemy);
    rp.resultText = '';
    rp.resultTimer = 0;
}

// Called each frame during active reaction phase
function updateReactionPhase(deltaTime) {
    const rp = combat.reactionPhase;
    if (!rp.active) return;

    // Animate bubble scale in (ease-out, ~300ms)
    if (rp.bubbleScale < 1) {
        rp.bubbleScale = Math.min(1, rp.bubbleScale + deltaTime / 250);
    }

    // Count down timer
    if (!rp.playerResponded) {
        rp.timeRemaining = Math.max(0, rp.timeLimit - (Date.now() - rp.timerStarted));

        if (rp.timeRemaining <= 0) {
            // Time expired — auto-resolve as direct hit
            resolveReactionPhase(null);
        }
    }

    // Show result text for 1800ms then close and process next in queue
    if (rp.playerResponded && rp.resultTimer > 0) {
        rp.resultTimer -= deltaTime;
        if (rp.resultTimer <= 0) {
            closeReactionPhase();
        }
    }
}

// Player clicked a spell during the reaction window
function handleReactionSpellClick(spell) {
    const rp = combat.reactionPhase;
    if (!rp.active || rp.playerResponded) return false;

    resolveReactionPhase(spell);
    return true; // consumed the click
}

// Grade the player's response and apply effects
function resolveReactionPhase(spell) {
    const rp = combat.reactionPhase;
    rp.playerResponded = true;
    rp.responseSpell = spell;

    const telegraph = rp.telegraph;
    const enemy = rp.enemy;
    const player = getPlayer(); // use actual player accessor

    let grade = 'direct_hit';
    let damageMultiplier = 1.0;

    if (!spell) {
        // No action taken — direct hit
        grade = 'direct_hit';
        damageMultiplier = 1.0;

    } else if (spell.tags && spell.tags.includes('potion')) {
        // Player used a potion — special comedy interaction
        grade = 'resist';                   // partial mitigate (they healed)
        damageMultiplier = 1.0;             // but still take full damage (the potion was for HP, not defense)
        rp.resultText = randomFrom(REACTION_RESULT_TEXT.potion_during_attack);
        // Apply the potion effect normally
        applySpellEffect(spell, player, [enemy]); // use actual spell application function
        // Override the grade result text to the special one
        rp.responseGrade = 'potion_special';
        _finalizeReaction(grade, damageMultiplier, telegraph, enemy, player);
        return;

    } else {
        // Evaluate spell effectiveness against the telegraph
        const counterResult = checkPlayerCounter(telegraph, {
            type: spell.type,
            tags: spell.tags || [],
            name: spell.name
        });

        if (counterResult) {
            // Correct counter — use Phase 1.1 applyCounterBonus logic to determine grade
            switch (counterResult.type) {
                case 'cancel_and_skip':
                    grade = 'silence';
                    damageMultiplier = 0;
                    break;
                case 'negate_and_retaliate':
                    grade = 'nullify';
                    damageMultiplier = 0;
                    break;
                case 'evade_and_empower':
                    grade = 'nullify';
                    damageMultiplier = 0;
                    break;
                case 'reflect_damage':
                    grade = 'nullify';
                    damageMultiplier = 0;
                    break;
            }
            // Apply the counter bonus effects (Phase 1.1 system)
            applyCounterBonus(counterResult, enemy, player);

        } else {
            // No perfect counter — grade by spell category
            const isAttack = spell.type === 'attack' || (spell.tags && spell.tags.includes('attack'));
            const isDefense = spell.type === 'defense' || (spell.tags && (
                spell.tags.includes('shield') ||
                spell.tags.includes('defense') ||
                spell.tags.includes('stun') ||
                spell.tags.includes('dodge')
            ));
            const isPhysicalAttack = telegraph.attackType && telegraph.attackType.includes('physical');

            if (isAttack) {
                // Attack vs attack — clash
                grade = 'clash';
                damageMultiplier = 0.5;
                // Player also deals 50% of their spell's damage back
                const clashDamage = Math.floor(calculateSpellDamage(spell, player) * 0.5);
                enemy.hp -= clashDamage;
                spawnFloatingText(`-${clashDamage}`, enemy.x || 400, enemy.y || 200, '#ff00ff');
                // use actual floating text fn name

            } else if (isDefense && isPhysicalAttack) {
                // Shield vs physical — absorb
                grade = 'absorb';
                damageMultiplier = 0.30;

            } else if (isDefense) {
                // Generic defense vs any attack — resist
                grade = 'resist';
                damageMultiplier = 0.60;

            } else {
                // Irrelevant spell type — direct hit
                grade = 'direct_hit';
                damageMultiplier = 1.0;
            }
        }

        // Apply the spell's own effect regardless of grade (unless it was a perfect nullify)
        if (grade !== 'nullify' && grade !== 'silence') {
            applySpellEffect(spell, player, [enemy]); // use actual spell application function
        }
    }

    rp.responseGrade = grade;
    if (!rp.resultText) {
        rp.resultText = randomFrom(REACTION_RESULT_TEXT[grade] || REACTION_RESULT_TEXT.direct_hit);
    }

    _finalizeReaction(grade, damageMultiplier, telegraph, enemy, player);
}

// Internal — apply damage and set result display timer
function _finalizeReaction(grade, damageMultiplier, telegraph, enemy, player) {
    const rp = combat.reactionPhase;

    // Apply final damage if any
    if (damageMultiplier > 0) {
        const finalDamage = Math.floor(telegraph.damage * damageMultiplier);
        applyDamageToPlayer(finalDamage, enemy); // use actual damage application function
    }

    // Log to combat log
    logCombatEvent(`${rp.resultText}`, 'reaction_' + rp.responseGrade);

    // Hold result display for 1800ms before closing
    rp.resultTimer = 1800;
}

// Close the reaction phase and process next in queue
function closeReactionPhase() {
    const rp = combat.reactionPhase;

    rp.active = false;
    rp.enemy = null;
    rp.telegraph = null;
    rp.playerResponded = false;
    rp.responseSpell = null;
    rp.responseGrade = null;
    rp.resultText = '';
    rp.bubbleScale = 0;

    // Process next queued attack if any
    if (rp.pendingQueue.length > 0) {
        const next = rp.pendingQueue.shift();
        setTimeout(() => openReactionPhase(next.enemy, next.telegraph), 200);
        // Small gap between sequential windows feels better
    }
}

// Get the effectiveness hint for a spell slot (used to color spell buttons)
// Returns: 'nullify'|'absorb'|'clash'|'resist'|'unknown'
function getSpellEffectivenessHint(spell, telegraph) {
    if (!telegraph || !spell) return 'unknown';

    const counterResult = checkPlayerCounter(telegraph, {
        type: spell.type,
        tags: spell.tags || [],
        name: spell.name
    });

    if (counterResult) {
        return counterResult.type === 'cancel_and_skip' ? 'nullify' : 'nullify';
    }

    const isAttack = spell.type === 'attack' || (spell.tags && spell.tags.includes('attack'));
    const isDefense = spell.type === 'defense' || (spell.tags && spell.tags.includes('defense'));
    const isPhysical = telegraph.attackType && telegraph.attackType.includes('physical');

    if (spell.tags && spell.tags.includes('potion')) return 'potion';
    if (isAttack) return 'clash';
    if (isDefense && isPhysical) return 'absorb';
    if (isDefense) return 'resist';
    return 'unknown';
}
```

---

## STEP 5 — THE ANIME SPEECH BUBBLE RENDERER

This is the centerpiece visual. Insert as part of the reaction combat section:

```javascript
// Renders the enemy attack announcement bubble + countdown ring
// Call this from the combat render pass when reactionPhase.active === true
function renderReactionPhase(ctx, rp) {
    if (!rp.active) return;

    const cw = canvas.width;   // use actual canvas variable
    const ch = canvas.height;

    // ── STAGE DIM ─────────────────────────────────────────────
    // Darken everything except the bubble area
    ctx.save();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.55)';
    ctx.fillRect(0, 0, cw, ch);
    ctx.restore();

    if (rp.bubbleScale <= 0) return;

    // ── SPEECH BUBBLE ─────────────────────────────────────────
    // Positioned above the enemy sprite — adapt coordinates to actual enemy render position
    const enemyRenderX = rp.enemy.renderX || rp.enemy.x || cw * 0.65;
    const enemyRenderY = rp.enemy.renderY || rp.enemy.y || ch * 0.35;

    const bubbleW = 280;
    const bubbleH = 80;
    const bubbleX = Math.min(cw - bubbleW - 20, Math.max(20, enemyRenderX - bubbleW / 2));
    const bubbleY = enemyRenderY - bubbleH - 40;

    ctx.save();
    ctx.translate(bubbleX + bubbleW / 2, bubbleY + bubbleH / 2);
    ctx.rotate(rp.bubbleRotation);
    ctx.scale(rp.bubbleScale, rp.bubbleScale);
    ctx.translate(-(bubbleX + bubbleW / 2), -(bubbleY + bubbleH / 2));

    // Bubble border color based on threat level
    const threatColor = {
        'LETHAL': '#ff4444',
        'HIGH':   '#ff8800',
        'MEDIUM': '#ffff00',
        'LOW':    '#00ffff'
    }[rp.telegraph.threatLevel] || '#ff00ff';

    // Outer glow pass
    ctx.shadowColor = threatColor;
    ctx.shadowBlur = 18;

    // Manga-style jagged bubble background
    _drawMangaBubble(ctx, bubbleX, bubbleY, bubbleW, bubbleH, threatColor);

    ctx.shadowBlur = 0;

    // Attack name — "Press Start 2P" large
    ctx.font = '11px "Press Start 2P"';
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    const attackName = rp.telegraph.attackName.toUpperCase();
    // Truncate if too long
    const maxChars = 22;
    const displayName = attackName.length > maxChars
        ? attackName.substring(0, maxChars - 2) + '..'
        : attackName;
    ctx.fillText(displayName, bubbleX + bubbleW / 2, bubbleY + 26);

    // Taunt text — "Share Tech Mono" smaller, cyan
    ctx.font = '7px "Share Tech Mono"';
    ctx.fillStyle = '#00ffff';
    const taunt = rp.tauntText || '';
    const maxTauntChars = 36;
    const displayTaunt = taunt.length > maxTauntChars
        ? taunt.substring(0, maxTauntChars - 2) + '..'
        : taunt;
    ctx.fillText(displayTaunt, bubbleX + bubbleW / 2, bubbleY + 50);

    // Threat level badge
    ctx.font = '7px "Press Start 2P"';
    ctx.fillStyle = threatColor;
    ctx.fillText(`[${rp.telegraph.threatLevel}]`, bubbleX + bubbleW / 2, bubbleY + 68);

    ctx.textAlign = 'left'; // reset
    ctx.restore();

    // ── POINTER / TAIL from bubble to enemy ───────────────────
    ctx.save();
    ctx.scale(rp.bubbleScale, 1);
    const tailX = enemyRenderX;
    const tailY = enemyRenderY - 10;
    const tailBaseX = bubbleX + bubbleW / 2;
    const tailBaseY = bubbleY + bubbleH;
    ctx.beginPath();
    ctx.moveTo(tailBaseX - 10, tailBaseY);
    ctx.lineTo(tailBaseX + 10, tailBaseY);
    ctx.lineTo(tailX, tailY);
    ctx.closePath();
    ctx.fillStyle = '#0a0a2a';
    ctx.strokeStyle = threatColor;
    ctx.lineWidth = 1.5;
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    // ── COUNTDOWN RING ─────────────────────────────────────────
    if (!rp.playerResponded) {
        const ringX = 80;
        const ringY = ch - 80;
        const ringR = 32;
        const progress = rp.timeRemaining / rp.timeLimit;
        const startAngle = -Math.PI / 2;
        const endAngle = startAngle + (Math.PI * 2 * progress);

        // Ring background
        ctx.save();
        ctx.beginPath();
        ctx.arc(ringX, ringY, ringR, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.lineWidth = 6;
        ctx.stroke();

        // Ring fill — color shifts red as time runs out
        const ringColor = progress > 0.5 ? '#00ffff' :
                          progress > 0.25 ? '#ff8800' :
                          '#ff4444';
        ctx.beginPath();
        ctx.arc(ringX, ringY, ringR, startAngle, endAngle);
        ctx.strokeStyle = ringColor;
        ctx.lineWidth = 6;
        ctx.lineCap = 'round';
        ctx.shadowColor = ringColor;
        ctx.shadowBlur = 8;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Time remaining text inside ring
        const secondsLeft = Math.ceil(rp.timeRemaining / 1000);
        ctx.font = '14px "Press Start 2P"';
        ctx.fillStyle = ringColor;
        ctx.textAlign = 'center';
        ctx.fillText(secondsLeft, ringX, ringY + 5);

        // "REACT" label below ring
        ctx.font = '6px "Press Start 2P"';
        ctx.fillStyle = '#aaaaaa';
        ctx.fillText('REACT', ringX, ringY + ringR + 14);
        ctx.textAlign = 'left';
        ctx.restore();
    }

    // ── RESULT TEXT (shown after response) ────────────────────
    if (rp.playerResponded && rp.resultText && rp.resultTimer > 0) {
        const alpha = Math.min(1, rp.resultTimer / 400); // fade out last 400ms
        const resultColor = {
            nullify:     '#00ff41',
            silence:     '#00ffff',
            absorb:      '#00aaff',
            clash:       '#ff00ff',
            resist:      '#ffff00',
            direct_hit:  '#ff4444',
            potion_special: '#ffaa00'
        }[rp.responseGrade] || '#ffffff';

        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.font = '13px "Press Start 2P"';
        ctx.fillStyle = resultColor;
        ctx.shadowColor = resultColor;
        ctx.shadowBlur = 12;
        ctx.textAlign = 'center';
        ctx.fillText(rp.resultText, cw / 2, ch / 2 - 20);
        ctx.shadowBlur = 0;
        ctx.textAlign = 'left';
        ctx.restore();
    }

    // ── SPELL BUTTON EFFECTIVENESS INDICATORS ─────────────────
    // This overlays colored halos on the spell buttons during the reaction window
    // Call AFTER the spell buttons are rendered, so halos appear on top
    if (!rp.playerResponded) {
        renderSpellEffectivenessHalos(ctx, rp.telegraph);
    }
}

// Draw manga-style jagged speech bubble
// Path: rounded rect with spiky border cuts along the edges
function _drawMangaBubble(ctx, x, y, w, h, borderColor) {
    const r = 10; // corner radius
    const spike = 5; // spike protrusion in px
    const freq = 14; // pixels between spikes on long edges

    ctx.beginPath();
    // Build a jagged rect path: start top-left, go clockwise
    // Top edge (jagged)
    ctx.moveTo(x + r, y);
    let px = x + r;
    while (px < x + w - r) {
        const mid = px + freq / 2;
        ctx.lineTo(mid, y - spike);
        ctx.lineTo(Math.min(px + freq, x + w - r), y);
        px += freq;
    }
    // Top-right corner
    ctx.arcTo(x + w, y, x + w, y + r, r);
    // Right edge
    let py = y + r;
    while (py < y + h - r) {
        const mid = py + freq / 2;
        ctx.lineTo(x + w + spike, mid);
        ctx.lineTo(x + w, Math.min(py + freq, y + h - r));
        py += freq;
    }
    // Bottom-right corner
    ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
    // Bottom edge (no jagged — cleaner)
    ctx.lineTo(x + r, y + h);
    // Bottom-left corner
    ctx.arcTo(x, y + h, x, y + h - r, r);
    // Left edge (no jagged)
    ctx.lineTo(x, y + r);
    // Top-left corner
    ctx.arcTo(x, y, x + r, y, r);
    ctx.closePath();

    // Fill dark bg
    ctx.fillStyle = 'rgba(5, 5, 20, 0.95)';
    ctx.fill();

    // Colored border
    ctx.strokeStyle = borderColor;
    ctx.lineWidth = 2;
    ctx.stroke();

    // Inner thin border for depth
    ctx.strokeStyle = 'rgba(255,255,255,0.08)';
    ctx.lineWidth = 1;
    ctx.stroke();
}

// Render glow halos on the spell button slots to indicate effectiveness
// Slot positions: find the actual spell button coordinates in the source
function renderSpellEffectivenessHalos(ctx, telegraph) {
    const playerSpells = getPlayerSpells(); // use actual accessor for player's 4 spells
    // Adapt spellButtonSlots to match the ACTUAL rendered position of each spell button in the game
    // These coordinates MUST be verified against the existing spell button render code
    const spellButtonSlots = [
        { x: 0, y: 0, w: 0, h: 0 },  // REPLACE with actual slot 0 bounding box
        { x: 0, y: 0, w: 0, h: 0 },  // REPLACE with actual slot 1 bounding box
        { x: 0, y: 0, w: 0, h: 0 },  // REPLACE with actual slot 2 bounding box
        { x: 0, y: 0, w: 0, h: 0 }   // REPLACE with actual slot 3 bounding box
    ];

    const haloColors = {
        nullify: '#00ff41',
        absorb:  '#00aaff',
        clash:   '#ff00ff',
        resist:  '#ffff00',
        potion:  '#ffaa00',
        unknown: '#333344'
    };

    playerSpells.forEach((spell, i) => {
        if (!spellButtonSlots[i] || spellButtonSlots[i].w === 0) return;
        const hint = getSpellEffectivenessHint(spell, telegraph);
        const color = haloColors[hint] || haloColors.unknown;
        const slot = spellButtonSlots[i];

        ctx.save();
        ctx.shadowColor = color;
        ctx.shadowBlur = 16;
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.globalAlpha = 0.7 + Math.sin(Date.now() / 300) * 0.3; // pulse
        ctx.strokeRect(slot.x - 3, slot.y - 3, slot.w + 6, slot.h + 6);
        ctx.restore();
    });
}
```

---

## STEP 6 — HOOK INTO ENEMY ACTION RESOLUTION

In the enemy action resolution function (modified in Block 1.1), change the telegraph firing logic.
When a telegraphed attack fires (i.e. `enemy.telegraph.turnsRemaining <= 0`), instead of immediately
applying damage, call `openReactionPhase`:

```javascript
// REPLACE the telegraphed-attack-fires block in enemy action resolution:
if (enemy.telegraph && enemy.telegraph.active) {
    enemy.telegraph.turnsRemaining--;

    if (enemy.telegraph.turnsRemaining > 0) {
        // Still charging (boss 2-turn warning)
        logCombatEvent(
            `${enemy.name}: ${enemy.telegraph.attackName} [${enemy.telegraph.turnsRemaining}T]`,
            'warning'
        );
        return;
    }

    // Attack fires — open reaction window instead of applying damage directly
    openReactionPhase(enemy, enemy.telegraph);
    enemy.telegraph = null;

    // IMPORTANT: return here. Damage is applied inside resolveReactionPhase, not here.
    return;
}
```

Also: for NON-named attacks (no telegraph), these still auto-resolve immediately using the existing
damage application code. The reaction system only intercepts telegraphed attacks.

---

## STEP 7 — HOOK INTO COMBAT RENDER PASS

In the main combat render function, add the reaction phase render call LAST (on top of everything):

```javascript
// At the very end of the combat render pass, after all other elements are drawn:
renderReactionPhase(ctx, combat.reactionPhase);
```

---

## STEP 8 — HOOK INTO COMBAT UPDATE LOOP

In the main game update loop, add:

```javascript
if (combat.reactionPhase && combat.reactionPhase.active) {
    updateReactionPhase(deltaTime);
}
```

---

## STEP 9 — HOOK INTO COMBAT CLICK HANDLER

In the combat canvas click handler, add reaction phase interception at the top:

```javascript
// TOP of combat click handler — BEFORE spell button checks:
if (combat.reactionPhase && combat.reactionPhase.active && !combat.reactionPhase.playerResponded) {
    // Check if click is on any spell button slot
    const clickedSpell = getSpellClickedAt(event, playerSpells);
    // Replace getSpellClickedAt with the actual function/logic that detects spell button clicks
    if (clickedSpell) {
        handleReactionSpellClick(clickedSpell);
        return; // consume the click
    }
    // Click was NOT on a spell button — don't pass through to other handlers
    return; // during reaction phase, only spell buttons are clickable
}
```

---

## STEP 10 — VERIFY SPELL BUTTON SLOT COORDINATES

After implementing, open the game and note the exact rendered pixel positions of all 4 spell button
slots on the combat screen. Update the `spellButtonSlots` array in `renderSpellEffectivenessHalos()`
with the real coordinates. This CANNOT be guessed — it must be read from the existing render code.

---

## STEP 11 — TUNE WHICH ATTACKS ARE NAMED

Review the 14 enemy types currently in the game. For each enemy, ensure their ability definitions
include at least 1–2 abilities that qualify as "named attacks" (those that will trigger the
telegraph system and therefore the reaction window). An ability qualifies as named if:

- It has a non-null `name` property
- OR it has a `subtype` of `aoe`, `execute`, `multi_hit`, `special`, or `heavy_physical`

If an enemy has no qualifying abilities, add at least one named special ability to their definition.
Use the existing ability structure format already in the codebase.

---

## STEP 12 — OPTIONAL PERFORMANCE GUARD

If testing shows frame rate drops when the bubble is rendering (especially the jagged path), add:

```javascript
// Cache the bubble path as an offscreen canvas — regenerate only when bubbleScale changes
// Only implement this if frame rate testing shows it's needed. Skip if performance is fine.
```

---

## COMPLETION REPORT FOR BLOCK 1.4

When done, provide:

1. Confirm Phase 1.3 dodge window code has been fully removed
2. List the actual spell button slot coordinates you found and used in `renderSpellEffectivenessHalos`
3. List which enemies now have named abilities that trigger the reaction window
4. Any comedy text that was NOT used (e.g. if enemy type pools couldn't be matched) and why
5. Any function names substituted (floating text, player accessor, damage application, etc.)
6. Confirm: reaction window appears correctly when an enemy uses a named attack
7. Confirm: all 6 grades (nullify, silence, absorb, clash, resist, direct_hit) produce the correct damage multiplier
8. Confirm: countdown ring depletes visually and auto-resolves as direct_hit when it expires
9. Confirm: comedy result text appears centered on screen after each reaction
10. Confirm: spell button halos appear with appropriate colors during the reaction window
11. Confirm: non-named enemy attacks still auto-resolve without opening a window
12. Confirm: multiple queued reactions process sequentially with a 200ms gap
13. Confirm: game loads and runs without errors

---

## NOTES FOR FUTURE TUNING

The following values are intentionally easy to find and change. Tune these after playtesting:

| Variable | Location | Default | Adjust if... |
|---|---|---|---|
| `REACTION_TIME.normal` | REACTION_TIME const | 2500ms | Feels too fast/slow on normal attacks |
| `REACTION_TIME.boss` | REACTION_TIME const | 4000ms | Boss fights feel too easy/hard |
| `rp.resultTimer` | `_finalizeReaction()` | 1800ms | Result text disappears too fast/slow |
| `bubbleScale` animation speed | `updateReactionPhase()` | 250ms | Bubble expands too fast/slow |
| `spike` in `_drawMangaBubble` | function param | 5px | Spikes too subtle/too aggressive |
| `freq` in `_drawMangaBubble` | function param | 14px | Too many/few spikes |
| Stage dim opacity | `renderReactionPhase()` | 0.55 | Screen too dark/not dark enough |

---

*Instruction Block 1.4 generated by Claude Chat Architect Layer · 2026-03-26*
*Feed to Claude Code only after blocks 1.1, 1.2, and 1.3 are complete and verified.*

# NEON DUNGEON — INSTRUCTION BLOCK PRE-4 FIX
## Audit Remediation — Fix Before Phase 4
### Claude Chat Architect Layer · 2026-03-26
### Must complete before executing any Phase 4 blocks

---

> **SCOPE**: Fix all broken and stub systems identified in the full audit.
> Execute fixes in order. Do not touch dead code (pg, glow, dead DM.* methods,
> dead palette constants) — those are harmless and will be cleaned up later.
> After all fixes, re-execute Phase 2.5 and 2.6 which were confirmed unimplemented.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. `AIDialog` object — exact line, what API key it reads from localStorage, and all functions it exposes
2. `Player.tickBuffs()` — exact line, current buff processing loop
3. `enemyAttack()` — exact line, the section where damage is applied to player
4. `Player.isDodging()` — exact line, what it currently checks
5. `openSecretRoom(tier)` — exact line, confirm it is still a stub
6. Where `GameState.runRelics` is initialized and where the victory/relic screen reads from it
7. `awardRelic()` — confirm whether the Block 2.3 implementation exists or only the stub

Report all seven before writing any code.

---

## FIX 1 — REMOVE AIDialog CLIENT-SIDE API KEY (SECURITY)

Find the `AIDialog` object at approximately line 9045. It makes direct `fetch()` calls to
`api.anthropic.com` using an API key stored in localStorage.

**This must be removed entirely.** It is a security violation — API keys must never be
client-side. The Phase 4 Worker proxy replaces this functionality correctly.

Actions:
1. Delete the entire `AIDialog` object and all its methods
2. Find every call site that invokes `AIDialog.*` anywhere in the file — list them in the completion report
3. Replace each call site with a `DM.say()` fallback using a static string, or remove the call entirely if it was purely cosmetic
4. Remove any localStorage reads/writes for an API key (search for `localStorage` + `api` or `key` or `anthropic`)
5. Confirm: zero references to `api.anthropic.com` remain in the game file after this fix

---

## FIX 2 — STUN SYSTEM (stunTurns vs debuffs array)

**Problem**: 8+ spells increment `enemy.stunTurns` but `Enemy.isStunned()` checks the `debuffs`
array. The two systems are disconnected — stun spells have zero effect.

Find `Enemy.isStunned()`. Determine which system is canonical — `debuffs` array or `stunTurns`.

**Resolution**: Make `stunTurns` the canonical system (simpler). Update `Enemy.isStunned()`:

```javascript
// Replace existing isStunned check with:
Enemy.isStunned = function(enemy) {
    // Check both systems for compatibility
    if (enemy.stunTurns && enemy.stunTurns > 0) return true;
    if (enemy.debuffs && enemy.debuffs.some(d => d.type === 'stun' && d.turns > 0)) return true;
    return false;
};
```

Also add `stunTurns` decrement in the enemy turn tick (wherever enemy turn counters are processed):

```javascript
// In enemy turn processing, after the enemy acts:
if (enemy.stunTurns > 0) {
    enemy.stunTurns--;
}
```

Also initialize `stunTurns: 0` on enemy creation (same place `telegraph: null` was added).

---

## FIX 3 — REGEN BUFF (never applied)

Find `Player.tickBuffs()`. The loop decrements buff turns but never reads `buff.regen`.

Add regen healing inside the buff tick loop:

```javascript
// Inside Player.tickBuffs(), inside the buff processing loop,
// after decrementing turns, add:
if (buff.regen && buff.regen > 0) {
    player.hp = Math.min(player.maxHp, player.hp + buff.regen);
    Arena.spawnText(`+${buff.regen}`, player, '#00ff41');
}
```

---

## FIX 4 — REFLECT BUFF (never checked)

Find `enemyAttack()` — the section where damage is applied to the player.

Before applying damage to player HP, check for reflect buff:

```javascript
// In enemyAttack(), BEFORE applying damage to player:
const reflectBuff = player.buffs && player.buffs.find(b => b.reflect && b.reflect > 0 && b.turns > 0);
if (reflectBuff) {
    const reflectedDmg = Math.floor(rawDamage * reflectBuff.reflect);
    enemy.hp = Math.max(0, enemy.hp - reflectedDmg);
    Arena.spawnText(`REFLECT -${reflectedDmg}`, enemy, '#ff00ff');
    DM.say(`${player.name} reflects ${reflectedDmg} damage back!`, 'system');
    // Do NOT skip the incoming damage — reflect is partial, not a full block
    // (unless the spec says otherwise — check against spec §4B counter bonuses)
}
// Existing damage application continues below
```

---

## FIX 5 — ENEMY POISON AND BLEED (dead properties)

Find where `t.poison` and `t.bleed` are set on enemies (approximately lines 4052, 4092, 4094, 4814).

Add processing in the enemy turn tick (wherever `stunTurns` decrement was added in Fix 2):

```javascript
// In enemy turn processing, after the enemy acts:
if (enemy.poison && enemy.poison > 0) {
    enemy.hp = Math.max(0, enemy.hp - enemy.poison);
    Arena.spawnText(`POISON -${enemy.poison}`, enemy, '#00ff41');
    enemy.poisonTurns = (enemy.poisonTurns || 0) - 1;
    if (enemy.poisonTurns <= 0) { enemy.poison = 0; enemy.poisonTurns = 0; }
}

if (enemy.bleed && enemy.bleed > 0) {
    enemy.hp = Math.max(0, enemy.hp - enemy.bleed);
    Arena.spawnText(`BLEED -${enemy.bleed}`, enemy, '#ff4444');
    enemy.bleedTurns = (enemy.bleedTurns || 0) - 1;
    if (enemy.bleedTurns <= 0) { enemy.bleed = 0; enemy.bleedTurns = 0; }
}
```

When `t.poison` or `t.bleed` is set on an enemy, also set `t.poisonTurns` and `t.bleedTurns`
to a duration (use 3 turns as default). Update the setters at lines 4052, 4092, 4094, 4814:

```javascript
// Example — update each setter:
t.poison = 8;       // damage per turn
t.poisonTurns = 3;  // duration
```

---

## FIX 6 — PHASESHIELD DODGE BUFF (never checked)

Find `Player.isDodging()`. It currently doesn't check the `phaseShield` buff.

Add check:

```javascript
// In Player.isDodging(), add alongside existing dodge checks:
const phaseShieldBuff = player.buffs && player.buffs.find(b => b.dodgeChance && b.dodgeChance > 0 && b.turns > 0);
if (phaseShieldBuff && Math.random() < phaseShieldBuff.dodgeChance) return true;
```

---

## FIX 7 — COMPLETE openSecretRoom() STUB

Find `openSecretRoom(tier)` at approximately line 5908. It currently shows a placeholder DM message.

Replace stub with full implementation using the `SECRET_BOSSES` array and `SECRET_ROOM_TIERS`
that were added in Block 2.2. If those arrays exist in the file, use them. If they don't exist,
add them from the Block 2.2 instruction file before implementing this function.

```javascript
function openSecretRoom(tier) {
    const tierData = SECRET_ROOM_TIERS[tier];
    if (!tierData) {
        DM.say('Secret room unavailable.', 'system');
        return;
    }

    // Pick a random secret boss (deep copy — do not mutate definition)
    const bossDef = SECRET_BOSSES[Math.floor(Math.random() * SECRET_BOSSES.length)];
    const boss = JSON.parse(JSON.stringify(bossDef));

    // Apply tier modifiers
    boss.maxHp = Math.floor(boss.maxHp * tierData.bossHpMult);
    boss.hp    = boss.maxHp;
    boss.atk   = Math.floor(boss.atk  * tierData.bossAtkMult);

    // Store on game state
    GameState.secretRoom = {
        active:   true,
        tier:     tier,
        tierData: tierData,
        boss:     boss
    };
    GameState.pendingSecretRoom = null;

    DM.say(`[${tier}] SECRET ROOM — ${boss.name} AWAITS`, 'warning');

    // Show banner then load combat
    // Use existing phase banner mechanism:
    GameState._phaseBanner = {
        active: true,
        text:   `[${tier}] SECRET ROOM`,
        sub:    boss.name
    };
    setTimeout(() => {
        GameState._phaseBanner.active = false;
        // Start combat with the secret boss using existing combat initiation
        Game._spawnBoss(boss); // adapt to actual boss spawn function name
        UI.show('sCM');        // show combat screen
    }, 2000);
}
```

Also wire `resolveSecretRoom()` into the combat victory handler if not already done
(check Block 2.2 completion — it may have been implemented but not wired).

---

## FIX 8 — RELIC SYSTEM (never pushes to GameState.runRelics)

Find `awardRelic(relicId)`. Check if the Block 2.3 full implementation exists or just the stub.

**If only the stub exists:** Re-implement the full `awardRelic()` from Block 2.3 instruction file.

**If full implementation exists but doesn't push to `GameState.runRelics`:** Add the push:

```javascript
// Inside awardRelic(), after adding to player.relics:
GameState.runRelics = GameState.runRelics || [];
GameState.runRelics.push(relicId);
```

Also check where `GameState.runRelics` is reset at run start — confirm it clears to `[]` on new run.

---

## FIX 9 — BROKEN RING VFX REFERENCE (line 4270)

Find line 4270: `Arena.spawnVFX('ring', ..., 90)` passing a 5th argument.

If `Arena.spawnRing()` exists as a separate function, replace the call:
```javascript
Arena.spawnRing(x, y, color, 90); // use actual spawnRing signature
```

If `Arena.spawnRing()` does not exist, update `spawnVFX` to accept an optional radius param:
```javascript
// In spawnVFX, if type === 'ring', use the 5th param as radius if provided
```

---

## FIX 10 — TACTICAL ENEMY SELF-DEBUFF BUG (line 6662)

Find line 6662: `en.addDebuff('atkDown', ...)` — tactical enemy applying ATK-down to itself.

Change `en` to `p` (the player):
```javascript
// Change:
en.addDebuff('atkDown', ...);
// To:
addDebuff(p, 'atkDown', ...); // use actual addDebuff signature with player as target
```

---

## RE-EXECUTE PHASE 2.5 AND 2.6

After all 10 fixes above are complete and verified, re-execute the unimplemented blocks:

**Block 2.5 — Weapon Proc Effects:**
Read `PHASE_2_3_to_2_6.md` and execute ONLY the Block 2.5 section.
Add `procEffect` to all 30 weapons and implement `checkWeaponProc()`.

**Block 2.6 — Spell Synergy Indicators:**
Read `PHASE_2_3_to_2_6.md` and execute ONLY the Block 2.6 section.
Implement synergy detection, HUD rendering, and swap screen hint.

---

## COMPLETION REPORT FOR PRE-4 FIX

1. Confirm `AIDialog` fully removed — list all call sites that were replaced
2. Confirm zero references to `api.anthropic.com` remain in the game file
3. Confirm zero localStorage API key reads remain
4. Confirm stun spells now correctly stun enemies (test: cast a stun spell)
5. Confirm regen buff heals player each turn
6. Confirm reflect buff sends partial damage back to enemy
7. Confirm poison/bleed tick on enemies per turn
8. Confirm `openSecretRoom()` launches actual combat (not stub message)
9. Confirm relics push to `GameState.runRelics`
10. Confirm ring VFX uses correct radius
11. Confirm tactical enemy ATK-down applies to player not self
12. Confirm Block 2.5 weapon procs implemented (list 5 example weapons and their proc)
13. Confirm Block 2.6 synergy HUD appears with stun + execute in loadout
14. Confirm game loads and runs without errors

---

*Pre-Phase 4 Fix Block — Claude Chat Architect Layer · 2026-03-26*
*Complete ALL items before executing Phase 4 blocks.*
*Especially critical: AIDialog removal (Fix 1) must be confirmed before Phase 4.*

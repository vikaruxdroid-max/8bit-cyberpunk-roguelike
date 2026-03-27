# NEON DUNGEON — INSTRUCTION BLOCK 2.3
## RELIC SYSTEM (Complete Implementation)
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Block 2.2 complete (awardRelic stub must exist to replace)

---

> **SCOPE**: Complete the relic system. UI skeleton already exists in the game.
> Replace the Block 2.2 awardRelic() stub with full implementation.
> Maximum 5 relics held simultaneously. All effects persist for the entire run.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. The existing relic UI skeleton — where relic slots are rendered in the HUD
2. Where player run state is initialized (to add `relics: []` default)
3. Where player stats are calculated — to confirm where passive relic effects apply
4. The buff/debuff system — `addBuff()` / `addDebuff()` function signatures

---

## STEP 1 — RELIC DEFINITIONS

```javascript
// ============================================================
// RELIC SYSTEM — Phase 2.3
// ============================================================

const RELICS = [
    // ── UNCOMMON ──────────────────────────────────────────────
    {
        id: 'relic_ghost_chip',
        name: 'GHOST CHIP',
        rarity: 'uncommon',
        icon: '👻',
        description: 'Negate the first hit received in each room.',
        flavorText: 'Salvaged from a dead netrunner. Still warm.',
        effect: { type: 'proc', trigger: 'first_hit_per_room', action: 'negate_damage' }
    },
    {
        id: 'relic_overcharge_cell',
        name: 'OVERCHARGE CELL',
        rarity: 'uncommon',
        icon: '⚡',
        description: '+8 MP regeneration per turn.',
        flavorText: 'Leaks slightly. Don\'t ask what it\'s leaking.',
        effect: { type: 'passive_stat', stat: 'mpRegen', value: 8 }
    },
    {
        id: 'relic_black_market_chip',
        name: 'BLACK MARKET CHIP',
        rarity: 'uncommon',
        icon: '💰',
        description: 'Merchant prices reduced by 20%.',
        flavorText: 'Don\'t tell anyone where you got this.',
        effect: { type: 'passive_stat', stat: 'merchantDiscount', value: 0.20 }
    },
    {
        id: 'relic_scavenger_lens',
        name: 'SCAVENGER LENS',
        rarity: 'uncommon',
        icon: '🔍',
        description: 'Enemies drop 30% more gold.',
        flavorText: 'Sees value in everything. Even corpses.',
        effect: { type: 'passive_percent', stat: 'goldDropBonus', value: 0.30 }
    },
    {
        id: 'relic_medpack',
        name: 'FIELD MEDPACK',
        rarity: 'uncommon',
        icon: '➕',
        description: 'Restore +25% additional HP at rest rooms.',
        flavorText: 'Expired three zones ago. Still works.',
        effect: { type: 'passive_stat', stat: 'restBonus', value: 0.25 }
    },
    // ── RARE ──────────────────────────────────────────────────
    {
        id: 'relic_archive_shard',
        name: 'ARCHIVE SHARD',
        rarity: 'rare',
        icon: '📼',
        description: 'EX spells deal +30% bonus damage.',
        flavorText: 'Contains the memory of a thousand failed runs.',
        effect: { type: 'passive_percent', stat: 'exSpellBonus', value: 0.30 }
    },
    {
        id: 'relic_golden_badge',
        name: 'GOLDEN BADGE',
        rarity: 'rare',
        icon: '🏅',
        description: '+15% all damage per elite enemy killed this run (max +60%).',
        flavorText: 'Stripped from a VP\'s corpse. He won\'t need it.',
        effect: { type: 'on_kill', trigger: 'elite_kill', stat: 'eliteKillBonus', value: 0.15, cap: 0.60 }
    },
    {
        id: 'relic_null_shard',
        name: 'NULL SHARD',
        rarity: 'rare',
        icon: '⬛',
        description: '+30% damage against debuffed or stunned enemies.',
        flavorText: 'Empty inside. Like its previous owner.',
        effect: { type: 'passive_stat', stat: 'debuffDamageBonus', value: 0.30 }
    },
    {
        id: 'relic_chrome_crown',
        name: 'CHROME CROWN',
        rarity: 'rare',
        icon: '👑',
        description: '+5 flat DEF per zone cleared (max +40).',
        flavorText: 'Weighs exactly as much as a dynasty.',
        effect: { type: 'passive_stat', stat: 'zoneDefBonus', value: 5, cap: 40 }
    },
    {
        id: 'relic_overclocked_coil',
        name: 'OVERCLOCKED COIL',
        rarity: 'rare',
        icon: '🌀',
        description: '+15% SPD when below 50% HP.',
        flavorText: 'Danger activates it. That\'s a feature.',
        effect: { type: 'conditional', condition: 'hp_below_50pct', stat: 'spd', bonus: 0.15 }
    },
    {
        id: 'relic_hex_tome',
        name: 'HEX TOME',
        rarity: 'rare',
        icon: '📖',
        description: 'Every 3rd spell cast costs 0 MP.',
        flavorText: '01001000 01000101 01011000. You\'re welcome.',
        effect: { type: 'proc', trigger: 'spell_cast_count', interval: 3, action: 'free_cast' }
    },
    // ── LEGENDARY ─────────────────────────────────────────────
    {
        id: 'relic_quantum_core',
        name: 'QUANTUM CORE',
        rarity: 'legendary',
        icon: '🔮',
        description: '10% chance any spell fires twice.',
        flavorText: 'Schrödinger\'s damage. It both hits and misses. Until it hits.',
        effect: { type: 'proc', trigger: 'on_spell_cast', chance: 0.10, action: 'double_cast' }
    },
    {
        id: 'relic_void_engine',
        name: 'VOID ENGINE',
        rarity: 'legendary',
        icon: '🕳️',
        description: 'Killing a mob deals 15% of their max HP to all remaining enemies.',
        flavorText: 'The void is efficient.',
        effect: { type: 'on_kill', trigger: 'any_kill', action: 'kill_splash', value: 0.15 }
    },
    {
        id: 'relic_berserker_node',
        name: 'BERSERKER NODE',
        rarity: 'legendary',
        icon: '💀',
        description: '+2% ATK for every HP lost (max +80%).',
        flavorText: 'Pain is a power source. Inefficient but spectacular.',
        effect: { type: 'dynamic', stat: 'atk', per: 'hp_lost', rate: 0.02, cap: 0.80 }
    },
    {
        id: 'relic_resonance_crystal',
        name: 'RESONANCE CRYSTAL',
        rarity: 'legendary',
        icon: '💎',
        description: 'Crits apply 2-turn shock dealing 10 damage/turn.',
        flavorText: 'Cuts through armor. Also through careers.',
        effect: { type: 'proc', trigger: 'on_crit', action: 'apply_shock', value: 10, duration: 2 }
    },
    {
        id: 'relic_chain_protocol',
        name: 'CHAIN PROTOCOL',
        rarity: 'legendary',
        icon: '🔗',
        description: 'Single-target spells have 25% chance to jump to a second enemy at 50% damage.',
        flavorText: 'Why hit one when you can traumatize two?',
        effect: { type: 'proc', trigger: 'single_target_spell', chance: 0.25, action: 'chain_hit', chainMult: 0.50 }
    },
    // Additional uncommon relics to reach 20 total
    {
        id: 'relic_feedback_loop',
        name: 'FEEDBACK LOOP',
        rarity: 'uncommon',
        icon: '🔄',
        description: 'Gain 1% ATK charge per 10 damage taken (max charge applied next hit).',
        flavorText: 'Pain is data. Data is power.',
        effect: { type: 'dynamic', stat: 'atkCharge', per: 'damage_taken', rate: 0.001 }
    },
    {
        id: 'relic_phase_cloak',
        name: 'PHASE CLOAK',
        rarity: 'uncommon',
        icon: '🌫️',
        description: 'Reduce dodge cooldown by 1 turn.',
        flavorText: 'Light bends around it. Attacks do too.',
        effect: { type: 'passive_stat', stat: 'dodgeCooldownReduction', value: 1 }
    },
    {
        id: 'relic_fortify_core',
        name: 'FORTIFY CORE',
        rarity: 'uncommon',
        icon: '🛡️',
        description: '+8 max HP per room cleared (cap +80).',
        flavorText: 'Grows stronger with every room survived.',
        effect: { type: 'on_room_clear', stat: 'maxHp', value: 8, cap: 80 }
    },
    {
        id: 'relic_predator_lens',
        name: 'PREDATOR LENS',
        rarity: 'rare',
        icon: '🎯',
        description: '+20% damage against enemies with more max HP than your current HP.',
        flavorText: 'The odds are against you. The lens takes notes.',
        effect: { type: 'conditional', condition: 'enemy_hp_greater', stat: 'dmg', bonus: 0.20 }
    }
];

// Lookup helper
function getRelicDef(id) {
    return RELICS.find(r => r.id === id) || null;
}
```

---

## STEP 2 — PLAYER RELIC STATE

Add to player run state initialization:

```javascript
player.relics = [];            // array of relic IDs currently held
player.relicState = {};        // runtime state for proc relics (cast counts, room flags, etc.)
```

---

## STEP 3 — REPLACE awardRelic() STUB

Remove the Block 2.2 stub. Replace with:

```javascript
function awardRelic(relicId) {
    const player = GameState.player; // use actual player accessor
    const def = getRelicDef(relicId);
    if (!def) { console.warn('Unknown relic:', relicId); return; }

    if (player.relics.length >= 5) {
        DM.say('RELIC INVENTORY FULL (5/5) — RELIC LOST', 'warning');
        return;
    }

    player.relics.push(relicId);
    DM.say(`RELIC ACQUIRED: ${def.name}`, 'success');
    Arena.spawnText(`+ ${def.name}`, player, '#ffd700'); // use actual player position

    // Initialize relic runtime state
    if (def.effect.type === 'proc') {
        player.relicState[relicId] = { castCount: 0, roomUsed: false };
    } else if (def.effect.type === 'on_room_clear') {
        player.relicState[relicId] = { stacks: 0 };
    } else if (def.effect.type === 'on_kill') {
        player.relicState[relicId] = { stacks: 0 };
    } else if (def.effect.type === 'dynamic') {
        player.relicState[relicId] = { currentBonus: 0 };
    }
}
```

---

## STEP 4 — RELIC EFFECT ENGINE

Add a central relic event dispatcher. Call the appropriate trigger whenever the relevant game event occurs:

```javascript
function triggerRelicEvent(eventType, context) {
    const player = GameState.player;
    if (!player.relics || player.relics.length === 0) return;

    player.relics.forEach(relicId => {
        const def = getRelicDef(relicId);
        if (!def) return;
        const effect = def.effect;
        const state = player.relicState[relicId] || {};

        switch (eventType) {

            case 'room_start':
                // Reset per-room flags
                if (state.roomUsed !== undefined) state.roomUsed = false;
                // GHOST CHIP: re-arm
                if (relicId === 'relic_ghost_chip') state.roomUsed = false;
                // FORTIFY CORE: increment on room clear (called on room_clear event instead)
                break;

            case 'room_clear':
                if (effect.type === 'on_room_clear') {
                    const current = state.stacks || 0;
                    const maxBonus = effect.cap || 999;
                    const totalBonus = Math.min(maxBonus, (current + 1) * effect.value);
                    state.stacks = Math.min(Math.floor(maxBonus / effect.value), current + 1);
                    player[effect.stat] = (player[effect.stat] || 0) + effect.value;
                    if (player[effect.stat] > maxBonus) player[effect.stat] = maxBonus;
                }
                break;

            case 'first_hit_received':
                if (relicId === 'relic_ghost_chip' && !state.roomUsed) {
                    state.roomUsed = true;
                    context.negated = true; // set this flag to prevent damage in caller
                    Arena.spawnText('GHOST CHIP!', player, '#aaaaff');
                }
                break;

            case 'spell_cast':
                // HEX TOME: every 3rd cast free
                if (relicId === 'relic_hex_tome') {
                    state.castCount = (state.castCount || 0) + 1;
                    if (state.castCount % 3 === 0) {
                        context.mpCost = 0;
                        Arena.spawnText('FREE CAST!', player, '#ffd700');
                    }
                }
                // QUANTUM CORE: 10% chance double cast
                if (relicId === 'relic_quantum_core' && Math.random() < 0.10) {
                    context.doubleCast = true;
                    Arena.spawnText('QUANTUM ECHO!', player, '#ff00ff');
                }
                break;

            case 'on_crit':
                // RESONANCE CRYSTAL: apply shock
                if (relicId === 'relic_resonance_crystal') {
                    addDebuff(context.target, 'shock', { damage: 10, turns: 2 });
                    // use actual addDebuff function
                    Arena.spawnText('SHOCK!', context.target, '#ffff00');
                }
                break;

            case 'on_kill':
                // VOID ENGINE: splash
                if (relicId === 'relic_void_engine' && context.killedEnemy) {
                    const splash = Math.floor(context.killedEnemy.maxHp * 0.15);
                    context.remainingEnemies.forEach(e => {
                        e.hp = Math.max(0, e.hp - splash);
                        Arena.spawnText(`VOID -${splash}`, e, '#8800ff');
                    });
                }
                // GOLDEN BADGE: stack elite kill bonus
                if (relicId === 'relic_golden_badge' && context.killedEnemy && context.killedEnemy.tier === 'advanced') {
                    state.stacks = (state.stacks || 0) + 1;
                    const bonus = Math.min(0.60, state.stacks * 0.15);
                    player.relicState[relicId].currentBonus = bonus;
                    DM.say(`GOLDEN BADGE: +${Math.floor(bonus*100)}% DMG`, 'system');
                }
                break;

            case 'damage_taken':
                // BERSERKER NODE: charge on damage
                if (relicId === 'relic_berserker_node') {
                    const hpLost = player.maxHp - player.hp;
                    const bonus = Math.min(0.80, hpLost * 0.02);
                    state.currentBonus = bonus;
                }
                // FEEDBACK LOOP: charge on damage
                if (relicId === 'relic_feedback_loop') {
                    state.currentBonus = Math.min(1.0, (state.currentBonus || 0) + context.damage * 0.001);
                }
                break;

            case 'single_target_spell':
                // CHAIN PROTOCOL: 25% chain
                if (relicId === 'relic_chain_protocol' && Math.random() < 0.25 && context.remainingEnemies && context.remainingEnemies.length > 1) {
                    const chainTarget = context.remainingEnemies.find(e => e !== context.primaryTarget);
                    if (chainTarget) {
                        const chainDmg = Math.floor(context.damage * 0.50);
                        chainTarget.hp = Math.max(0, chainTarget.hp - chainDmg);
                        Arena.spawnText(`CHAIN -${chainDmg}`, chainTarget, '#ff00ff');
                    }
                }
                break;
        }
    });
}
```

---

## STEP 5 — HOOK RELIC EVENTS INTO GAME

Add `triggerRelicEvent()` calls at these points in the existing code:

| Hook point | Call |
|---|---|
| Room starts | `triggerRelicEvent('room_start', {})` |
| Room cleared | `triggerRelicEvent('room_clear', {})` |
| Player receives first hit in room | `triggerRelicEvent('first_hit_received', context)` — check `context.negated` after |
| Player casts any spell | `triggerRelicEvent('spell_cast', context)` — check `context.mpCost` and `context.doubleCast` after |
| Player lands a crit | `triggerRelicEvent('on_crit', { target: enemy })` |
| Enemy dies | `triggerRelicEvent('on_kill', { killedEnemy: enemy, remainingEnemies: [...] })` |
| Player takes damage | `triggerRelicEvent('damage_taken', { damage: amount })` |
| Player casts single-target spell | `triggerRelicEvent('single_target_spell', { primaryTarget: enemy, damage: dmg, remainingEnemies: [...] })` |

---

## STEP 6 — PASSIVE STAT APPLICATION

For relics with `type: 'passive_stat'` or `type: 'passive_percent'`, apply their values when
calculating player stats. Find where player ATK, DEF, SPD are computed:

```javascript
function getPlayerStatWithRelics(stat) {
    const player = GameState.player;
    let value = player[stat] || 0;

    (player.relics || []).forEach(relicId => {
        const def = getRelicDef(relicId);
        if (!def) return;
        const e = def.effect;
        const rs = player.relicState[relicId] || {};

        if (e.type === 'passive_stat' && e.stat === stat) {
            value += e.value;
        }
        if (e.type === 'passive_percent' && e.stat === stat) {
            value = Math.floor(value * (1 + e.value));
        }
        if (e.type === 'conditional') {
            if (e.condition === 'hp_below_50pct' && player.hp < player.maxHp * 0.50) {
                if (e.stat === stat) value = Math.floor(value * (1 + e.bonus));
            }
            if (e.condition === 'enemy_hp_greater' && e.stat === 'dmg') {
                // Applied in damage calculation, not here — handle in deal() or spell damage calc
            }
        }
        if (e.type === 'dynamic' && e.stat === stat && rs.currentBonus) {
            value = Math.floor(value * (1 + rs.currentBonus));
        }
        // GOLDEN BADGE stacked bonus
        if (relicId === 'relic_golden_badge' && stat === 'dmg' && rs.currentBonus) {
            value = Math.floor(value * (1 + rs.currentBonus));
        }
    });

    return value;
}
```

---

## STEP 7 — RELIC HUD RENDERING

Find the existing relic UI skeleton. Replace the placeholder rendering with:

```javascript
function renderRelicHUD(ctx) {
    const player = GameState.player;
    if (!player.relics || player.relics.length === 0) return;

    const slotSize = 28;
    const gap = 6;
    const startX = 10;
    const startY = canvas.height - 44; // bottom-left strip

    player.relics.forEach((relicId, i) => {
        const def = getRelicDef(relicId);
        if (!def) return;
        const x = startX + i * (slotSize + gap);
        const y = startY;

        const rarityColors = { uncommon: '#00aaff', rare: '#aa00ff', legendary: '#ffd700' };
        const borderColor = rarityColors[def.rarity] || '#aaaaaa';

        ctx.save();
        ctx.fillStyle = '#0a0a1a';
        ctx.strokeStyle = borderColor;
        ctx.lineWidth = 1;
        ctx.fillRect(x, y, slotSize, slotSize);
        ctx.strokeRect(x, y, slotSize, slotSize);

        ctx.font = '14px "Share Tech Mono"';
        ctx.textAlign = 'center';
        ctx.fillStyle = '#ffffff';
        ctx.fillText(def.icon || '?', x + slotSize / 2, y + slotSize / 2 + 5);
        ctx.textAlign = 'left';
        ctx.restore();
    });
}
```

Call `renderRelicHUD(ctx)` in the combat and world map render passes.

---

## COMPLETION REPORT FOR BLOCK 2.3

1. Confirm `awardRelic()` stub replaced with full implementation
2. Confirm all 20 relic definitions added
3. List which relic event hooks were added and to which functions
4. Confirm relic HUD renders in combat
5. Test: acquire GHOST CHIP relic, confirm first hit per room is negated
6. Test: acquire HEX TOME relic, confirm every 3rd cast is free
7. Any relic effects that could NOT be implemented and why
8. Confirm game loads and runs without errors

---

---

# NEON DUNGEON — INSTRUCTION BLOCK 2.4
## EXPAND PASSIVE SKILLS (5 → 30)
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Block 2.3 complete

---

> **SCOPE**: Add 25 new passive skills to the existing 5.
> Do NOT modify the existing 5 passives. Only add.
> These appear in level-up choices and character creation.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. Where the existing 5 passive skill definitions are stored
2. How passives are applied to player stats during combat
3. Where level-up passive choices are presented to the player
4. The existing passive skill data structure (exact property names)

---

## STEP 1 — ADD 25 NEW PASSIVE DEFINITIONS

Add to the existing passives array/object, matching the exact structure of existing entries:

```javascript
// Add these to the existing passives definition array:
{ id:'passive_execution',   name:'EXECUTIONER',     description:'+50% damage to enemies below 25% HP.',       effect:{ stat:'executionBonus',    value:0.50 } },
{ id:'passive_momentum',    name:'MOMENTUM',        description:'+5% ATK per combo stack (max +50%).',        effect:{ stat:'comboAtkBonus',     value:0.05, cap:0.50 } },
{ id:'passive_spellweave',  name:'SPELLWEAVE',      description:'Every 3rd spell costs 0 MP.',                effect:{ stat:'freeCastInterval',  value:3 } },
{ id:'passive_overclock',   name:'OVERCLOCK',       description:'+15% SPD when below 50% HP.',                effect:{ stat:'lowHpSpdBonus',     value:0.15 } },
{ id:'passive_vampiric',    name:'VAMPIRIC AURA',   description:'AoE spells drain 5% HP from each hit enemy.',effect:{ stat:'aoeDrain',          value:0.05 } },
{ id:'passive_ironwall',    name:'IRON WALL',       description:'Block absorbs +15% more damage per cast.',   effect:{ stat:'blockDrPerCast',    value:0.15 } },
{ id:'passive_ghost',       name:'GHOST PROTOCOL',  description:'First hit in combat always misses.',         effect:{ stat:'firstHitImmune',    value:1 } },
{ id:'passive_resonance',   name:'SPELL RESONANCE', description:'EX spells deal +25% bonus damage.',          effect:{ stat:'exSpellBonus',      value:0.25 } },
{ id:'passive_shrapnel',    name:'SHRAPNEL',        description:'Killing a mob splashes 10% of their max HP to adjacent enemies.', effect:{ stat:'killSplash', value:0.10 } },
{ id:'passive_meditate',    name:'MEDITATE',        description:'Rest rooms restore +30% additional HP.',     effect:{ stat:'restBonus',         value:0.30 } },
{ id:'passive_blackmarket', name:'BLACK MARKET',    description:'Merchant prices reduced by 20%.',            effect:{ stat:'merchantDiscount',  value:0.20 } },
{ id:'passive_doubledown',  name:'DOUBLE DOWN',     description:'10% chance any spell fires twice.',          effect:{ stat:'doubleCastChance',  value:0.10 } },
{ id:'passive_voltaic',     name:'VOLTAIC',         description:'Crits apply 2-turn shock (10 dmg/turn).',    effect:{ stat:'critShock',         value:10 } },
{ id:'passive_feedback',    name:'FEEDBACK LOOP',   description:'+1% ATK charge per 10 damage taken.',        effect:{ stat:'damageCharge',      value:0.001 } },
{ id:'passive_neurallace',  name:'NEURAL LACE',     description:'+2 MP regeneration per turn.',               effect:{ stat:'mpRegen',           value:2 } },
{ id:'passive_hardened',    name:'HARDENED',        description:'+5 flat DEF per zone cleared.',              effect:{ stat:'zoneDefBonus',      value:5 } },
{ id:'passive_berserk',     name:'BERSERK',         description:'+2% ATK for each HP lost (max +60%).',       effect:{ stat:'hpLossAtk',         value:0.02, cap:0.60 } },
{ id:'passive_opportunist', name:'OPPORTUNIST',     description:'+30% damage against stunned/debuffed enemies.',effect:{ stat:'debuffBonus',    value:0.30 } },
{ id:'passive_spellecho',   name:'SPELL ECHO',      description:'Last cast spell has 15% chance to auto-repeat.', effect:{ stat:'echoChance',   value:0.15 } },
{ id:'passive_warlord',     name:'WARLORD',         description:'+5% all damage per elite killed this run.',  effect:{ stat:'eliteKillBonus',    value:0.05 } },
{ id:'passive_phaseshift',  name:'PHASE SHIFT',     description:'Dodge cooldown reduced by 1 turn.',          effect:{ stat:'dodgeCdReduction',  value:1 } },
{ id:'passive_scavenger',   name:'SCAVENGER',       description:'Enemies drop +25% gold.',                    effect:{ stat:'goldBonus',         value:0.25 } },
{ id:'passive_fortify',     name:'FORTIFY',         description:'+10 max HP per room cleared (cap +100).',    effect:{ stat:'roomHpBonus',       value:10, cap:100 } },
{ id:'passive_chain',       name:'CHAIN LIGHTNING', description:'Single-target spells have 20% chance to jump to a second enemy at 50% damage.', effect:{ stat:'chainChance', value:0.20 } },
{ id:'passive_predator',    name:'PREDATOR',        description:'+15% damage against enemies with more max HP than your current HP.', effect:{ stat:'predatorBonus', value:0.15 } },
```

---

## STEP 2 — WIRE NEW PASSIVE EFFECTS INTO COMBAT

For each new passive, find the correct hook point and add the effect. Use the same pattern
as existing passive implementations. Key hook points:

| Passive | Hook point |
|---|---|
| EXECUTIONER | In `deal()` — check if enemy HP < 25% maxHp, apply +50% |
| MOMENTUM | In combo counter update — multiply ATK by (1 + comboCount * 0.05), cap 0.50 |
| SPELLWEAVE | In spell cast handler — track cast count, zero MP cost every 3rd |
| OVERCLOCK | In SPD calculation — if HP < 50%, apply +15% |
| VAMPIRIC AURA | In AoE spell resolution — after damage, heal player by 5% of damage dealt per target |
| IRON WALL | In block handler — increase blockDR by 0.15 per block cast this room |
| GHOST PROTOCOL | On room start — set `player.firstHitImmune = true`; on first hit, negate and clear flag |
| SPELL RESONANCE | In EX spell damage calculation — multiply final damage by 1.25 |
| SHRAPNEL | In on-kill handler — deal 10% of killed enemy maxHp to remaining enemies |
| MEDITATE | In rest room HP restore — multiply restored amount by 1.30 |
| BLACK MARKET | In merchant price display — multiply prices by 0.80 |
| DOUBLE DOWN | In spell cast handler — roll 10%, if hit cast spell twice |
| VOLTAIC | In crit handler — `addDebuff(enemy, 'shock', { damage:10, turns:2 })` |
| FEEDBACK LOOP | In damage-taken handler — accumulate charge, apply to next hit |
| NEURAL LACE | In MP regeneration per turn — add +2 |
| HARDENED | On zone clear — add +5 to player.def (permanent for run) |
| BERSERK | In ATK calculation — `(1 + (maxHp - hp) * 0.02)`, cap 0.60 |
| OPPORTUNIST | In deal() — if target has any debuff/stun, apply +30% |
| SPELL ECHO | In post-cast handler — roll 15%, if hit re-trigger last spell at no cost |
| WARLORD | In on-kill handler — if elite, increment stack, apply +5% dmg per stack |
| PHASE SHIFT | In dodge ability cooldown calculation — subtract 1 from result |
| SCAVENGER | In gold drop calculation — multiply by 1.25 |
| FORTIFY | On room clear — add +10 to player.maxHp, cap at +100 total |
| CHAIN LIGHTNING | In single-target spell resolution — roll 20%, chain to second enemy at 50% |
| PREDATOR | In deal() — if enemy.maxHp > player.hp, apply +15% |

---

## STEP 3 — UPDATE LEVEL-UP POOL

Confirm the level-up passive selection pool now includes all 30 passives (5 original + 25 new).
If the pool is hardcoded, add the 25 new IDs. If it pulls from the definitions array, no change needed.

---

## COMPLETION REPORT FOR BLOCK 2.4

1. Confirm all 25 new passive definitions added
2. List which passive effects were fully wired and which are definition-only (no hook yet)
3. Confirm level-up pool now shows new passives
4. Test: equip EXECUTIONER, confirm bonus damage at low enemy HP
5. Confirm game loads and runs without errors

---

---

# NEON DUNGEON — INSTRUCTION BLOCK 2.5
## WEAPON PROC EFFECTS
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Block 2.4 complete

---

> **SCOPE**: Add procEffect property to all 30 weapons.
> Procs fire AFTER the triggering attack resolves.
> Display as floating text: "[WEAPON NAME] PROC!" in gold.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. The 30 weapon definitions — exact property names used
2. Where weapon passive bonuses are currently applied
3. Where auto-attack damage is resolved — to hook proc trigger
4. The floating text function (confirmed: `Arena.spawnText()`)

---

## STEP 1 — ADD procEffect TO ALL 30 WEAPONS

Find each weapon definition. Add a `procEffect` property. Use this format:

```javascript
// Format:
procEffect: {
    trigger: 'on_hit',          // 'on_hit' | 'on_crit' | 'on_kill'
    chance: 0.12,               // 0.0–1.0
    action: 'cast_free',        // 'cast_free' | 'apply_buff' | 'apply_debuff' | 'deal_bonus_damage' | 'heal'
    // action-specific params:
    spell: 'spell_id',          // for cast_free
    buffType: 'atk_up',         // for apply_buff
    buffValue: 0.20,
    buffDuration: 2,
    damage: 15,                 // for deal_bonus_damage (flat)
    damageMult: 0.30,           // for deal_bonus_damage (% of weapon ATK)
    healAmount: 20,             // for heal
    description: '12% on hit: cast free Neon Slash'
}
```

Apply these proc effects to the 30 weapons. Assign thematically — blade weapons proc slashes,
pistols proc extra shots, heavy weapons proc stun/knockback, energy weapons proc burns/shocks,
tech weapons proc hacks/debuffs. Example assignments:

```javascript
// BLADES (thematic: bonus slash, lifesteal, bleed)
// Weapon: Plasma Katana
procEffect: { trigger:'on_hit', chance:0.12, action:'cast_free', spell:'neon_slash', description:'12% on hit: free Neon Slash' }

// Weapon: Mono Wire
procEffect: { trigger:'on_hit', chance:0.15, action:'apply_debuff', buffType:'bleed', buffValue:8, buffDuration:3, description:'15% on hit: apply Bleed (8dmg/3t)' }

// Weapon: Vibro Blade
procEffect: { trigger:'on_crit', chance:1.0, action:'deal_bonus_damage', damageMult:0.50, description:'Crits deal +50% bonus damage' }

// PISTOLS (thematic: multi-hit, armor pierce, slow)
// Weapon: Neon Pistol
procEffect: { trigger:'on_hit', chance:0.20, action:'deal_bonus_damage', damage:12, description:'20% on hit: +12 bonus damage' }

// Weapon: Rail Gun
procEffect: { trigger:'on_hit', chance:0.10, action:'apply_debuff', buffType:'armor_break', buffValue:0.20, buffDuration:2, description:'10% on hit: Armor Break (-20% DEF, 2t)' }

// HEAVY (thematic: stun, knockback, shield break)
// Weapon: Crusher
procEffect: { trigger:'on_hit', chance:0.15, action:'apply_debuff', buffType:'stun', buffValue:0, buffDuration:1, description:'15% on hit: Stun (1t)' }

// Weapon: Gravity Maul
procEffect: { trigger:'on_kill', chance:1.0, action:'apply_buff', buffType:'atk_up', buffValue:0.20, buffDuration:3, description:'On kill: ATK +20% for 3 turns' }

// ENERGY (thematic: burn, shock, MP drain)
// Weapon: Arc Caster
procEffect: { trigger:'on_hit', chance:0.18, action:'apply_debuff', buffType:'shock', buffValue:10, buffDuration:2, description:'18% on hit: Shock (10dmg/2t)' }

// Weapon: Plasma Torch
procEffect: { trigger:'on_hit', chance:0.20, action:'apply_debuff', buffType:'burn', buffValue:8, buffDuration:3, description:'20% on hit: Burn (8dmg/3t)' }

// TECH (thematic: hack, stat debuff, free spell)
// Weapon: Neural Jacker
procEffect: { trigger:'on_hit', chance:0.12, action:'apply_debuff', buffType:'atk_down', buffValue:0.20, buffDuration:2, description:'12% on hit: ATK -20% (2t)' }

// Weapon: Data Spike
procEffect: { trigger:'on_crit', chance:1.0, action:'cast_free', spell:'data_splice', description:'Crits: cast free Data Splice' }
```

For the remaining weapons not listed above: assign a thematically appropriate proc from the
available action types. Every weapon must have a `procEffect`. Vary the proc types — do not
assign `cast_free: neon_slash` to every weapon.

---

## STEP 2 — PROC TRIGGER ENGINE

Add to the auto-attack and spell hit resolution:

```javascript
function checkWeaponProc(attackResult) {
    const player = GameState.player; // use actual accessor
    const weapon = player.equippedWeapon; // use actual equipped weapon accessor
    if (!weapon || !weapon.procEffect) return;

    const proc = weapon.procEffect;

    // Check trigger condition
    const triggerMet =
        (proc.trigger === 'on_hit'  && attackResult.hit) ||
        (proc.trigger === 'on_crit' && attackResult.crit) ||
        (proc.trigger === 'on_kill' && attackResult.killed);

    if (!triggerMet) return;
    if (Math.random() >= proc.chance) return;

    // Fire proc
    Arena.spawnText(`${weapon.name} PROC!`, player, '#ffd700');

    switch (proc.action) {
        case 'cast_free':
            const spellDef = getSpellById(proc.spell); // use actual spell lookup
            if (spellDef) applySpellEffect(spellDef, player, attackResult.targets);
            break;
        case 'apply_buff':
            addBuff(player, proc.buffType, { value: proc.buffValue, turns: proc.buffDuration });
            break;
        case 'apply_debuff':
            attackResult.targets.forEach(t => addDebuff(t, proc.buffType, { value: proc.buffValue, turns: proc.buffDuration }));
            break;
        case 'deal_bonus_damage':
            const bonusDmg = proc.damage || Math.floor(weapon.atk * (proc.damageMult || 0));
            attackResult.targets.forEach(t => {
                t.hp = Math.max(0, t.hp - bonusDmg);
                Arena.spawnText(`+${bonusDmg}`, t, '#ff8800');
            });
            break;
        case 'heal':
            player.hp = Math.min(player.maxHp, player.hp + proc.healAmount);
            Arena.spawnText(`+${proc.healAmount}HP`, player, '#00ff41');
            break;
    }
}
```

Hook `checkWeaponProc()` after auto-attack resolution and after single-target spell hit resolution.
Pass an `attackResult` object: `{ hit: bool, crit: bool, killed: bool, targets: [enemy] }`.

---

## COMPLETION REPORT FOR BLOCK 2.5

1. Confirm all 30 weapons have a `procEffect` property
2. List weapon names and their assigned proc actions
3. Confirm proc fires correctly on `on_hit`, `on_crit`, `on_kill` triggers
4. Confirm `[WEAPON NAME] PROC!` floats in gold
5. Confirm procs do not fire on 0% chance weapons (no regression)
6. Confirm game loads and runs without errors

---

---

# NEON DUNGEON — INSTRUCTION BLOCK 2.6
## SPELL SYNERGY INDICATORS
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Block 2.5 complete

---

> **SCOPE**: Detect when the player's active 4-spell loadout contains synergistic combinations.
> Display a compact synergy indicator on the spell loadout panel during combat.
> This is display-only — synergy bonuses are already partially handled by existing counter system.
> New here: detection logic, HUD display, and the bonus effects for non-counter synergies.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. Where the player's 4 active spell slots are stored and rendered
2. The spell HUD position and available rendering space near the spell buttons
3. How spell tags are structured (confirmed in Block 1.1 — `spell.tags` array)

---

## STEP 1 — SYNERGY DEFINITIONS

```javascript
// ============================================================
// SPELL SYNERGY SYSTEM — Phase 2.6
// ============================================================

const SYNERGIES = [
    {
        id: 'stun_execute',
        name: 'KNOCKOUT PROTOCOL',
        requires: ['stun', 'execute'],        // tags that must both be present in loadout
        matchType: 'tags',
        bonus: '+40% execute damage on stunned targets',
        color: '#ffd700',
        effect: { type: 'conditional_damage', condition: 'target_stunned', spellTag: 'execute', bonus: 0.40 }
    },
    {
        id: 'bleed_multi',
        name: 'HEMORRHAGE',
        requires: ['bleed_applier', 'multi_hit'],
        matchType: 'tags',
        bonus: 'Multi-hit triggers bleed stacks individually',
        color: '#ff4444',
        effect: { type: 'hit_modifier', spellTag: 'multi_hit', modifier: 'bleed_per_hit' }
    },
    {
        id: 'shield_reflect',
        name: 'MIRROR PROTOCOL',
        requires: ['shield', 'reflect'],
        matchType: 'tags',
        bonus: 'Shield absorb triggers reflect at 50% value',
        color: '#00ffff',
        effect: { type: 'proc_on_absorb', action: 'reflect_half' }
    },
    {
        id: 'aoe_combo',
        name: 'CHAIN REACTION',
        requires: ['aoe', 'combo_builder'],
        matchType: 'tags',
        bonus: 'AoE hits each count toward combo',
        color: '#ff00ff',
        effect: { type: 'combo_modifier', spellTag: 'aoe', modifier: 'count_all_hits' }
    },
    {
        id: 'heal_lifesteal',
        name: 'VAMPIRE LORD',
        requires: ['heal'],
        requiresPassive: 'passive_lifesteal',
        matchType: 'spell_and_passive',
        bonus: 'Healing spells also trigger lifesteal calc',
        color: '#00ff41',
        effect: { type: 'heal_modifier', spellTag: 'heal', modifier: 'add_lifesteal' }
    },
    {
        id: 'execute_low_hp',
        name: 'DEATH MARK',
        requires: ['execute'],
        requiresPassive: 'passive_execution',
        matchType: 'spell_and_passive',
        bonus: 'Execute passive and execute spell stack: +80% at <25% HP',
        color: '#ff4444',
        effect: { type: 'stacked_bonus', value: 0.80 }
    },
    {
        id: 'shield_block',
        name: 'IRON TRINITY',
        requires: ['shield', 'defense'],
        matchType: 'tags',
        bonus: 'Shields cast while block is active cost 0 MP',
        color: '#00aaff',
        effect: { type: 'cost_modifier', condition: 'block_active', spellTag: 'shield', modifier: 'free' }
    },
    {
        id: 'stun_aoe',
        name: 'CROWD CONTROL',
        requires: ['stun', 'aoe'],
        matchType: 'tags',
        bonus: 'AoE after stun hits all enemies for +20% damage',
        color: '#ffff00',
        effect: { type: 'conditional_damage', condition: 'any_enemy_stunned', spellTag: 'aoe', bonus: 0.20 }
    },
    {
        id: 'full_offense',
        name: 'ALL IN',
        requires: ['attack', 'attack', 'attack'],
        matchType: 'count',
        count: 3,
        tag: 'attack',
        bonus: '3+ attack spells: +15% all attack damage',
        color: '#ff8800',
        effect: { type: 'global_damage_bonus', value: 0.15 }
    },
    {
        id: 'full_defense',
        name: 'BUNKER MODE',
        requires: ['defense', 'defense'],
        matchType: 'count',
        count: 2,
        tag: 'defense',
        bonus: '2+ defense spells: +25% shield effectiveness',
        color: '#0088ff',
        effect: { type: 'shield_modifier', value: 0.25 }
    }
];
```

---

## STEP 2 — SYNERGY DETECTION

```javascript
function detectActiveSynergies(playerSpells, playerPassives) {
    const spellTags = new Set();
    const tagCounts = {};

    // Collect all tags from active spells
    playerSpells.forEach(spell => {
        (spell.tags || []).forEach(tag => {
            spellTags.add(tag);
            tagCounts[tag] = (tagCounts[tag] || 0) + 1;
        });
    });

    const activePassiveIds = (playerPassives || []).map(p => p.id);

    return SYNERGIES.filter(syn => {
        if (syn.matchType === 'tags') {
            return syn.requires.every(tag => spellTags.has(tag));
        }
        if (syn.matchType === 'count') {
            return (tagCounts[syn.tag] || 0) >= syn.count;
        }
        if (syn.matchType === 'spell_and_passive') {
            const hasSpellTags = syn.requires.every(tag => spellTags.has(tag));
            const hasPassive = activePassiveIds.includes(syn.requiresPassive);
            return hasSpellTags && hasPassive;
        }
        return false;
    });
}

// Cache active synergies — recalculate when loadout changes
let _cachedSynergies = [];

function refreshSynergies() {
    const player = GameState.player; // use actual accessor
    _cachedSynergies = detectActiveSynergies(player.spells, player.passives);
}
```

Call `refreshSynergies()` whenever the player's spell loadout changes (after spell swap, after spell evolution).

---

## STEP 3 — SYNERGY HUD RENDERING

Render active synergies as a compact strip below or beside the spell buttons:

```javascript
function renderSynergyHUD(ctx) {
    if (_cachedSynergies.length === 0) return;

    // Position: below spell buttons — adapt x/y to actual spell button layout
    const startX = 10;   // REPLACE with actual x position relative to spell button panel
    const startY = canvas.height - 80; // REPLACE with actual y below spell buttons
    const lineH = 14;

    _cachedSynergies.slice(0, 3).forEach((syn, i) => { // show max 3 at once
        const y = startY + i * lineH;
        const pulse = 0.8 + Math.sin(Date.now() / 600 + i) * 0.2;

        ctx.save();
        ctx.globalAlpha = pulse;
        ctx.font = '6px "Press Start 2P"';
        ctx.fillStyle = syn.color;
        ctx.fillText(`★ ${syn.name}`, startX, y);
        ctx.restore();
    });

    // If more than 3 synergies (rare): show count
    if (_cachedSynergies.length > 3) {
        ctx.save();
        ctx.font = '6px "Press Start 2P"';
        ctx.fillStyle = '#aaaaaa';
        ctx.fillText(`+${_cachedSynergies.length - 3} MORE`, startX, startY + 3 * lineH);
        ctx.restore();
    }
}
```

Call `renderSynergyHUD(ctx)` in the combat render pass, after spell buttons are drawn.

---

## STEP 4 — APPLY SYNERGY EFFECTS IN COMBAT

For each synergy effect type, hook into the correct combat function:

```javascript
function applySynergyEffects(eventType, context) {
    _cachedSynergies.forEach(syn => {
        const e = syn.effect;
        switch (e.type) {
            case 'conditional_damage':
                if (eventType === 'spell_damage' && context.spell.tags.includes(e.spellTag)) {
                    const condMet = e.condition === 'target_stunned'
                        ? context.target.debuffs && context.target.debuffs.some(d => d.type === 'stun')
                        : e.condition === 'any_enemy_stunned'
                        ? context.allEnemies.some(en => en.debuffs && en.debuffs.some(d => d.type === 'stun'))
                        : false;
                    if (condMet) context.damage = Math.floor(context.damage * (1 + e.bonus));
                }
                break;
            case 'global_damage_bonus':
                if (eventType === 'spell_damage' || eventType === 'auto_attack') {
                    context.damage = Math.floor(context.damage * (1 + e.value));
                }
                break;
            case 'cost_modifier':
                if (eventType === 'spell_cast_mp_check' && context.spell.tags.includes(e.spellTag)) {
                    const condMet = e.condition === 'block_active' && GameState.player.blockActive;
                    if (condMet) context.mpCost = 0;
                }
                break;
        }
    });
}
```

Call `applySynergyEffects()` at the appropriate combat event points with a mutable `context` object.

---

## STEP 5 — SPELL SWAP SYNERGY HINT

When the player is on the spell swap screen, show which of the offered spells would create or
break a synergy:

```javascript
function getSwapSynergyDelta(currentSpells, offeredSpell, swapIndex) {
    const hypothetical = [...currentSpells];
    hypothetical[swapIndex] = offeredSpell;
    const player = GameState.player;

    const before = detectActiveSynergies(currentSpells, player.passives).length;
    const after  = detectActiveSynergies(hypothetical,  player.passives).length;

    if (after > before) return { delta: after - before, label: `+${after - before} SYNERGY`, color: '#00ff41' };
    if (after < before) return { delta: after - before, label: `${after - before} SYNERGY`, color: '#ff4444' };
    return null;
}
```

In the spell swap UI render, call `getSwapSynergyDelta()` for the offered spell and display the
label near it if non-null.

---

## COMPLETION REPORT FOR BLOCK 2.6

1. Confirm all 10 synergy definitions added
2. Confirm `refreshSynergies()` is called after spell swap and spell evolution
3. Confirm synergy HUD renders during combat (show screenshot or describe position)
4. Test: equip stun + execute tagged spells, confirm KNOCKOUT PROTOCOL appears
5. Test: spell swap screen shows +SYNERGY hint when offered spell would create a new synergy
6. Any synergy effects that could NOT be wired and why
7. Confirm game loads and runs without errors

---

## PHASE 2 FINAL VERIFICATION CHECKLIST

Run after all 6 blocks (2.1–2.6) are complete.

```
MINI-GAMES (2.1)
[ ] All 6 mini-game types render and complete correctly on Canvas
[ ] Trigger chance: 25% every 3rd room, 40% after zone boss defeated
[ ] lastRoomWasMiniGame prevents back-to-back triggers
[ ] Score tiers (GOLD/SILVER/BRONZE/FAIL) produce correct pendingSecretRoom values
[ ] Result screen shows before transitioning

SECRET ROOMS (2.2)
[ ] All 6 secret bosses have correct stats, abilities, and phase definitions
[ ] Tier modifiers apply: GOLD boss has 1.5× HP
[ ] resolveSecretRoom() fires only after secret boss defeat
[ ] awardRelic() stub replaced (Block 2.3)
[ ] SECRET [TIER] badge visible in combat

RELICS (2.3)
[ ] All 20 relic definitions present
[ ] awardRelic() adds relic to player.relics (max 5)
[ ] GHOST CHIP negates first hit per room
[ ] HEX TOME makes every 3rd cast free
[ ] QUANTUM CORE double-casts at 10% rate
[ ] Relic HUD renders during combat

PASSIVES (2.4)
[ ] 30 total passives in pool (5 original + 25 new)
[ ] New passives appear in level-up choices
[ ] EXECUTIONER applies +50% below 25% enemy HP
[ ] BERSERK scales with HP lost

WEAPON PROCS (2.5)
[ ] All 30 weapons have procEffect defined
[ ] Procs fire at correct trigger and chance
[ ] PROC! floating text appears in gold
[ ] No proc fires when roll fails

SYNERGIES (2.6)
[ ] KNOCKOUT PROTOCOL detected with stun + execute in loadout
[ ] Synergy HUD shows during combat
[ ] Spell swap screen shows synergy delta hint
[ ] refreshSynergies() called after each swap
```

When all items pass: commit, then tell Claude Chat "Phase 2 complete and verified."

---

*Blocks 2.3–2.6 — Claude Chat Architect Layer · 2026-03-26*
*Execute in order: 2.3 → 2.4 → 2.5 → 2.6*
*Do not begin Phase 3 until Phase 2 final verification passes.*

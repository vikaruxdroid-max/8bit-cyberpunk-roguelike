# NEON DUNGEON — INSTRUCTION BLOCK 2.2
## SECRET ROOMS & RARE BOSSES
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Block 2.1 complete (GameState.pendingSecretRoom must exist)

---

> **SCOPE**: Secret rooms triggered by mini-game success. 6 unique secret bosses.
> Reward tiers GOLD/SILVER/BRONZE drive boss difficulty and loot pool.
> Relics dropped here are stubs — full relic data implemented in Block 2.3.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. How normal combat rooms are loaded — the function that sets up enemies, background, and starts combat
2. Where enemy definitions are stored — the array/object holding all 14 enemy types
3. Where the loot/reward screen is rendered after combat
4. How gold is awarded to the player after combat
5. Where `GameState.pendingSecretRoom` is checked after `closeMiniGame()` (set in Block 2.1)

---

## STEP 1 — SECRET BOSS DEFINITIONS

Add 6 new enemy definitions to the enemy data store. These are ONLY encountered in secret rooms — never in normal zone rooms.

```javascript
const SECRET_BOSSES = [
    {
        id: 'secret_the_archivist',
        name: 'THE ARCHIVIST',
        tier: 'boss',
        isSecretBoss: true,
        maxHp: 320, hp: 320,
        atk: 48, def: 22, spd: 60,
        actionCounter: 0,
        telegraph: null, shieldHp: 0, shieldActive: false,
        phase: 1, currentPhase: 1,
        phases: [
            { phase:1, hpThreshold:1.0,  aiPattern:'tactical',  buffs:[], phaseTransitionText: null },
            { phase:2, hpThreshold:0.60, aiPattern:'desperate', buffs:[{type:'atk_up',value:0.25,duration:-1}], phaseTransitionText:'RECORDS CORRUPTED. PURGE PROTOCOL ACTIVE.' },
            { phase:3, hpThreshold:0.25, aiPattern:'boss',      buffs:[{type:'spd_up',value:0.40,duration:-1}], phaseTransitionText:'ARCHIVE SELF-DESTRUCT SEQUENCE INITIATED.' }
        ],
        abilities: [
            { id:'data_surge',    name:'DATA SURGE',    subtype:'aoe',            mpAtk:0, dmgMult:0.9 },
            { id:'record_purge',  name:'RECORD PURGE',  subtype:'execute',        mpAtk:0, dmgMult:1.4 },
            { id:'memory_wipe',   name:'MEMORY WIPE',   subtype:'special',        mpAtk:0, effect:'amnesia' }
        ],
        relicDrop: 'relic_archive_shard',
        tauntPool: [
            'YOUR DATA BELONGS TO ME.',
            'UNAUTHORIZED ACCESS. PUNISHMENT: DEATH.',
            'I HAVE SEEN EVERY RUN YOU\'VE EVER MADE.',
            'DELETING YOUR PROGRESS NOW.',
            'THE RECORDS SHOW YOU LOSE HERE.'
        ],
        loot: { gold: [60, 100] }
    },
    {
        id: 'secret_phantom_executive',
        name: 'PHANTOM EXECUTIVE',
        tier: 'boss',
        isSecretBoss: true,
        maxHp: 280, hp: 280,
        atk: 55, def: 18, spd: 75,
        actionCounter: 0,
        telegraph: null, shieldHp: 0, shieldActive: false,
        phase: 1, currentPhase: 1,
        phases: [
            { phase:1, hpThreshold:1.0,  aiPattern:'aggressive', buffs:[], phaseTransitionText: null },
            { phase:2, hpThreshold:0.60, aiPattern:'tactical',   buffs:[{type:'atk_up',value:0.30,duration:-1}], phaseTransitionText:'HOSTILE TAKEOVER AUTHORIZED.' },
            { phase:3, hpThreshold:0.25, aiPattern:'desperate',  buffs:[{type:'spd_up',value:0.50,duration:-1}], phaseTransitionText:'GOLDEN PARACHUTE DEPLOYED. LETHAL FORCE APPROVED.' }
        ],
        abilities: [
            { id:'pink_slip',       name:'PINK SLIP',       subtype:'execute',        mpAtk:0, dmgMult:1.6 },
            { id:'board_vote',      name:'BOARD VOTE',      subtype:'aoe',            mpAtk:0, dmgMult:0.85 },
            { id:'hostile_bid',     name:'HOSTILE BID',     subtype:'heavy_physical', mpAtk:0, dmgMult:1.2 }
        ],
        relicDrop: 'relic_golden_badge',
        tauntPool: [
            'THIS MEETING COULD HAVE BEEN AN EXECUTION.',
            'YOUR SEVERANCE IS A SHALLOW GRAVE.',
            'I EARN MORE PER SECOND THAN YOUR MAX HP.',
            'RESTRUCTURING. YOU\'RE THE FIRST CUT.',
            'YOU CALL THIS A HOSTILE ENCOUNTER? I CALL IT THURSDAY.'
        ],
        loot: { gold: [70, 110] }
    },
    {
        id: 'secret_null_prophet',
        name: 'NULL PROPHET',
        tier: 'boss',
        isSecretBoss: true,
        maxHp: 350, hp: 350,
        atk: 42, def: 30, spd: 50,
        actionCounter: 0,
        telegraph: null, shieldHp: 0, shieldActive: false,
        phase: 1, currentPhase: 1,
        phases: [
            { phase:1, hpThreshold:1.0,  aiPattern:'defensive', buffs:[], phaseTransitionText: null },
            { phase:2, hpThreshold:0.60, aiPattern:'tactical',  buffs:[{type:'def_up',value:0.30,duration:-1}], phaseTransitionText:'THE VOID SPEAKS. YOU ARE ITS TARGET.' },
            { phase:3, hpThreshold:0.25, aiPattern:'boss',      buffs:[{type:'atk_up',value:0.60,duration:-1},{type:'spd_up',value:0.30,duration:-1}], phaseTransitionText:'NULL SINGULARITY ACHIEVED. ALL RESISTANCE IS MEANINGLESS.' }
        ],
        abilities: [
            { id:'void_sermon',   name:'VOID SERMON',   subtype:'aoe',      mpAtk:0, dmgMult:0.8 },
            { id:'null_strike',   name:'NULL STRIKE',   subtype:'magical',  mpAtk:0, dmgMult:1.1 },
            { id:'entropy_pulse', name:'ENTROPY PULSE', subtype:'special',  mpAtk:0, effect:'defense_down' }
        ],
        relicDrop: 'relic_null_shard',
        tauntPool: [
            'YOUR EXISTENCE IS A ROUNDING ERROR.',
            'THE NULL TAKES ALL THINGS. INCLUDING YOU.',
            'I HAVE PREACHED YOUR DOOM FOR CYCLES.',
            'MEANING IS AN ILLUSION. YOUR HP IS NOT.',
            'THE VOID DOES NOT FORGIVE. NEITHER DO I.'
        ],
        loot: { gold: [50, 90] }
    },
    {
        id: 'secret_chrome_duchess',
        name: 'CHROME DUCHESS',
        tier: 'boss',
        isSecretBoss: true,
        maxHp: 300, hp: 300,
        atk: 50, def: 26, spd: 65,
        actionCounter: 0,
        telegraph: null, shieldHp: 0, shieldActive: false,
        phase: 1, currentPhase: 1,
        phases: [
            { phase:1, hpThreshold:1.0,  aiPattern:'tactical',  buffs:[], phaseTransitionText: null },
            { phase:2, hpThreshold:0.60, aiPattern:'aggressive', buffs:[{type:'atk_up',value:0.20,duration:-1}], phaseTransitionText:'POLITENESS PROTOCOL TERMINATED.' },
            { phase:3, hpThreshold:0.25, aiPattern:'desperate',  buffs:[{type:'atk_up',value:0.40,duration:-1},{type:'spd_up',value:0.40,duration:-1}], phaseTransitionText:'CHROME AND RAGE. MAXIMUM ALLOCATION.' }
        ],
        abilities: [
            { id:'royal_decree',  name:'ROYAL DECREE',  subtype:'heavy_physical', mpAtk:0, dmgMult:1.3 },
            { id:'chrome_waltz',  name:'CHROME WALTZ',  subtype:'multi_hit',      mpAtk:0, dmgMult:0.7, hits:3 },
            { id:'court_order',   name:'COURT ORDER',   subtype:'execute',        mpAtk:0, dmgMult:1.5 }
        ],
        relicDrop: 'relic_chrome_crown',
        tauntPool: [
            'DARLING, YOU SHOULDN\'T HAVE COME HERE.',
            'CHROME DOESN\'T BLEED. YOU DO.',
            'I DIDN\'T CHOOSE TO BE PERFECT. I CHOSE TO BE DANGEROUS.',
            'HOW QUAINT. A HERO.',
            'YOUR RESISTANCE IS ADORABLE. AND FUTILE.'
        ],
        loot: { gold: [65, 105] }
    },
    {
        id: 'secret_overclocked_priest',
        name: 'OVERCLOCKED PRIEST',
        tier: 'boss',
        isSecretBoss: true,
        maxHp: 260, hp: 260,
        atk: 60, def: 15, spd: 90,
        actionCounter: 0,
        telegraph: null, shieldHp: 0, shieldActive: false,
        phase: 1, currentPhase: 1,
        phases: [
            { phase:1, hpThreshold:1.0,  aiPattern:'aggressive', buffs:[], phaseTransitionText: null },
            { phase:2, hpThreshold:0.60, aiPattern:'aggressive', buffs:[{type:'spd_up',value:0.50,duration:-1}], phaseTransitionText:'OVERCLOCK: 200%. MERCY SUBROUTINE: DELETED.' },
            { phase:3, hpThreshold:0.25, aiPattern:'boss',       buffs:[{type:'spd_up',value:0.75,duration:-1},{type:'atk_up',value:0.50,duration:-1}], phaseTransitionText:'THERMAL LIMIT EXCEEDED. PAIN OUTPUT: MAXIMUM.' }
        ],
        abilities: [
            { id:'holy_burst',    name:'HOLY BURST',    subtype:'aoe',            mpAtk:0, dmgMult:0.95 },
            { id:'divine_overclock', name:'DIVINE OVERCLOCK', subtype:'special',  mpAtk:0, effect:'self_haste' },
            { id:'final_rite',    name:'FINAL RITE',    subtype:'execute',        mpAtk:0, dmgMult:1.8 }
        ],
        relicDrop: 'relic_overclocked_coil',
        tauntPool: [
            'MY PRAYERS HAVE ALREADY KILLED YOU.',
            'SPEED IS THEOLOGY.',
            'GOD RUNS AT 4GHz. I SURPASSED THAT.',
            'YOUR SUFFERING IS AN OFFERING.',
            'BLESSED ARE THE FAST, FOR THEY INHERIT THE KILLS.'
        ],
        loot: { gold: [55, 95] }
    },
    {
        id: 'secret_binary_witch',
        name: 'BINARY WITCH',
        tier: 'boss',
        isSecretBoss: true,
        maxHp: 290, hp: 290,
        atk: 45, def: 20, spd: 70,
        actionCounter: 0,
        telegraph: null, shieldHp: 0, shieldActive: false,
        phase: 1, currentPhase: 1,
        phases: [
            { phase:1, hpThreshold:1.0,  aiPattern:'tactical',  buffs:[], phaseTransitionText: null },
            { phase:2, hpThreshold:0.60, aiPattern:'tactical',  buffs:[{type:'atk_up',value:0.25,duration:-1}], phaseTransitionText:'01000100 01001001 01000101 — DIE IN BINARY.' },
            { phase:3, hpThreshold:0.25, aiPattern:'boss',      buffs:[{type:'atk_up',value:0.40,duration:-1},{type:'def_up',value:0.20,duration:-1}], phaseTransitionText:'HEX OVERFLOW. STACK SMASHED. YOU\'RE IN MY HEAP NOW.' }
        ],
        abilities: [
            { id:'hex_curse',     name:'HEX CURSE',     subtype:'special',        mpAtk:0, effect:'random_debuff' },
            { id:'bit_flip',      name:'BIT FLIP',      subtype:'magical',        mpAtk:0, dmgMult:1.0, effect:'stat_invert' },
            { id:'null_pointer',  name:'NULL POINTER',  subtype:'execute',        mpAtk:0, dmgMult:1.4 }
        ],
        relicDrop: 'relic_hex_tome',
        tauntPool: [
            '0xDEAD. THAT\'S YOU.',
            'I CAST IN MACHINE CODE.',
            'YOUR FATE WAS WRITTEN IN HEX.',
            'MAGIC IS JUST UNDOCUMENTED BEHAVIOR.',
            'EVERY SPELL I CAST IS A SEGFAULT IN YOUR FUTURE.'
        ],
        loot: { gold: [60, 100] }
    }
];
```

---

## STEP 2 — SECRET ROOM REWARD TIERS

```javascript
const SECRET_ROOM_TIERS = {
    GOLD: {
        bossHpMult: 1.5,
        bossAtkMult: 1.3,
        rewardPool: 'legendary',
        relicGuaranteed: true,
        goldMult: 1.5
    },
    SILVER: {
        bossHpMult: 1.2,
        bossAtkMult: 1.1,
        rewardPool: 'rare',
        relicGuaranteed: false,
        relicChance: 0.50,
        goldMult: 1.0
    },
    BRONZE: {
        bossHpMult: 1.0,
        bossAtkMult: 1.0,
        rewardPool: 'uncommon',
        relicGuaranteed: false,
        relicChance: 0.20,
        goldMult: 0.75
    }
};
```

---

## STEP 3 — openSecretRoom() FUNCTION

This function is called by `closeMiniGame()` in Block 2.1 when `pendingSecretRoom` is set.

```javascript
function openSecretRoom(tier) {
    const tierData = SECRET_ROOM_TIERS[tier];
    if (!tierData) return;

    // Pick a random secret boss
    const boss = JSON.parse(JSON.stringify(
        SECRET_BOSSES[Math.floor(Math.random() * SECRET_BOSSES.length)]
    )); // deep copy — do not mutate the definition

    // Apply tier modifiers
    boss.maxHp = Math.floor(boss.maxHp * tierData.bossHpMult);
    boss.hp    = boss.maxHp;
    boss.atk   = Math.floor(boss.atk  * tierData.bossAtkMult);

    // Store on game state for the combat system to use
    GameState.secretRoom = {
        active: true,
        tier: tier,
        tierData: tierData,
        boss: boss
    };

    GameState.pendingSecretRoom = null;

    // Show secret room intro banner then load combat
    showSecretRoomIntro(tier, boss, () => {
        loadSecretRoomCombat(boss);
    });
}

function showSecretRoomIntro(tier, boss, onComplete) {
    // Reuse renderPhaseBanner pattern from Phase 1 — or the same showPhaseBanner function
    // Display for 2000ms: "SECRET ROOM" header + tier badge + boss name
    const tierColors = { GOLD: '#ffd700', SILVER: '#cccccc', BRONZE: '#cd7f32' };
    const color = tierColors[tier] || '#ffffff';
    const text = `[${tier}] SECRET ROOM\n${boss.name}`;
    // Adapt to actual banner display mechanism from Phase 1 (GameState._phaseBanner or similar)
    showPhaseBanner(`[${tier}] ${boss.name} AWAITS`, onComplete);
    // Use actual banner function name confirmed in Phase 1
}

function loadSecretRoomCombat(boss) {
    // Load combat with the secret boss using the same mechanism as normal room combat
    // The boss object is already prepped — pass it to whatever function normally starts a combat room
    // After combat victory: call resolveSecretRoom()
    // After combat defeat: normal death handling (secret room loss = run over)
    startCombat([boss], { isSecretRoom: true }); // adapt to actual startCombat signature
}
```

---

## STEP 4 — SECRET ROOM REWARD RESOLUTION

Called after the player defeats the secret boss:

```javascript
function resolveSecretRoom() {
    const sr = GameState.secretRoom;
    if (!sr || !sr.active) return;

    const tier = sr.tierData;
    const boss = sr.boss;

    // Gold reward
    const baseGold = boss.loot.gold[0] + Math.floor(Math.random() * (boss.loot.gold[1] - boss.loot.gold[0]));
    const goldAwarded = Math.floor(baseGold * tier.goldMult);
    GameState.player.gold = (GameState.player.gold || 0) + goldAwarded; // use actual gold property
    DM.say(`SECRET ROOM CLEARED — +${goldAwarded} CR`, 'success');

    // Relic drop
    const getsRelic = tier.relicGuaranteed || Math.random() < (tier.relicChance || 0);
    if (getsRelic && boss.relicDrop) {
        awardRelic(boss.relicDrop); // defined in Block 2.3 — stub here
    }

    // Bonus loot based on tier
    if (tier.rewardPool === 'legendary') {
        // Award a rare/legendary spell offering — use existing spell offering mechanism
        offerBonusSpell('legendary'); // adapt to actual spell offering function
    } else if (tier.rewardPool === 'rare') {
        offerBonusSpell('rare');
    }

    sr.active = false;
    GameState.lastRoomWasMiniGame = false;
}
```

---

## STEP 5 — WIRE COMBAT VICTORY TO SECRET ROOM RESOLUTION

Find where combat victory is processed. Add a check:

```javascript
// In combat victory handler, BEFORE normal loot/next room logic:
if (GameState.secretRoom && GameState.secretRoom.active) {
    resolveSecretRoom();
    // Then show results and proceed to next normal room (not another secret room)
    return;
}
// Normal combat victory continues below...
```

---

## STEP 6 — VISUAL DIFFERENTIATION FOR SECRET ROOMS

When `GameState.secretRoom.active` is true during combat, add visual indicators:

In the combat UI render pass, add:

```javascript
if (GameState.secretRoom && GameState.secretRoom.active) {
    // Gold/silver/bronze tier badge in top-right corner
    const tierColors = { GOLD: '#ffd700', SILVER: '#cccccc', BRONZE: '#cd7f32' };
    const tier = GameState.secretRoom.tier;
    const color = tierColors[tier] || '#ffffff';
    ctx.save();
    ctx.font = '7px "Press Start 2P"';
    ctx.fillStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur = 8;
    ctx.textAlign = 'right';
    ctx.fillText(`★ SECRET [${tier}]`, canvas.width - 12, 20);
    ctx.shadowBlur = 0;
    ctx.textAlign = 'left';
    ctx.restore();
}
```

---

## STUB: awardRelic()

Add this stub so Block 2.1 and 2.2 don't crash when Block 2.3 hasn't run yet:

```javascript
function awardRelic(relicId) {
    // STUB — full implementation in Block 2.3
    // For now: just log it
    DM.say(`RELIC ACQUIRED: ${relicId} (STUB — Block 2.3)`, 'system');
    console.log('[Block 2.3 stub] awardRelic called with:', relicId);
}
```

---

## COMPLETION REPORT FOR BLOCK 2.2

1. Confirm all 6 secret boss definitions added to enemy data store
2. Confirm `openSecretRoom()` is called correctly from `closeMiniGame()` in Block 2.1
3. Confirm tier modifiers apply correctly (GOLD boss has 1.5× HP)
4. Confirm `resolveSecretRoom()` fires after secret boss defeat — not after normal enemy defeat
5. Confirm `awardRelic()` stub is present and doesn't crash
6. Confirm SECRET [TIER] badge renders in combat UI during secret room
7. Any substitutions made (startCombat signature, gold property name, etc.)
8. Confirm game loads and runs without errors

---

*Block 2.2 — Claude Chat Architect Layer · 2026-03-26*
*Block 2.3 (Relics) replaces the awardRelic() stub with full implementation.*

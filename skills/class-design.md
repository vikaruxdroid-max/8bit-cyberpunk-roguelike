SKILL: class-design defines how to create player classes, spells, and class identity.

## Class Design Pillars
Each class needs: a combat fantasy (what it feels like to play), a playstyle (aggressive/defensive/support/hybrid), a weakness to exploit, and visual identity (accent color + sprite silhouette).

## Existing Classes
| Class | Fantasy | Playstyle | Weakness | Accent |
|-------|---------|-----------|----------|--------|
| Warrior | Armored cyber-knight | Tanky frontliner | Low SPD, low MP | Orange #FF4500 |
| Ranger | Cyber-leather hunter | AoE + evasion | Low DEF | Green #39FF14 |
| Rogue | Shadow assassin | Burst damage + debuff | Low HP, low DEF | Magenta #FF00FF |
| Cleric | Bio-medic healer | Sustain + AoE cleanse | Low ATK | Gold #FFD700 |
| Warlock | Void channeler | DoT + lifesteal | Low HP, low DEF | Purple #8800FF |
| Druid | Symbiotic cyber-beast | Buff + AoE stun | Low ATK | Cyan #00FFFF |

## Spell Design Rules
Each class gets exactly 2 spells. One offensive, one utility/defensive.

**Spell 1 (Offensive)**:
- Multiplier: 1.5x-3x ATK
- Cooldown: 3-5 turns
- MP cost: 15-30
- Must have visual feedback: Arena.spawnVFX() + damage number

**Spell 2 (Utility)**:
- Buff, heal, debuff enemy, or dodge
- Duration: 2-4 turns
- Cooldown: 3-5 turns
- MP cost: 10-25
- Must have visual feedback: Arena.spawnVFX() + status text

## Spell Template
```javascript
{
  id: 'spellId',
  name: 'SPELL NAME',
  icon: '⚡',        // emoji for button
  maxCd: 4,          // turns between uses
  mpCost: 20,
  desc: 'Short description for tooltip',
  effect(player, enemies) {
    // Target selection
    const target = Combat.lowestHp(enemies);
    if (!target) return;

    // Damage
    const dmg = Combat.deal(target, Math.floor(player.atk * 2.0), true);

    // VFX
    const pos = Arena.getEnemyPos(GameState.enemies.indexOf(target));
    Arena.spawnVFX('slash', pos.x, pos.y, player.accent || '#fff');

    // Dialog
    DM.say('SPELL NAME! Flavor text!');
  }
}
```

## Class Synergies with Equipment
- Warrior + Shock Gauntlets: stun locks with high DEF to survive
- Ranger + Phase Cloak: dodge tank, impossible to hit
- Rogue + Void Blade: lifesteal sustains low HP pool
- Cleric + Neural Crown: reduced cooldowns = more heals
- Warlock + Void Blade: double lifesteal (skill + weapon)
- Druid + Mana Core: big MP pool fuels Neural Storm spam

## New Class Template
```javascript
// In CLASSES object:
classId: {
  name: 'CLASS NAME',
  hp: 90,
  atk: 20,
  def: 7,
  spd: 10,
  mp: 100,
  accent: '#hexcolor',
  sprite: 'spriteKey',    // must match SPR function
  spells: [
    { id:'spell1Id', name:'SPELL 1', icon:'⚡', maxCd:4, mpCost:20,
      desc:'Description',
      effect(p, en) { /* offensive spell logic */ }
    },
    { id:'spell2Id', name:'SPELL 2', icon:'🛡', maxCd:3, mpCost:15,
      desc:'Description',
      effect(p, en) { /* utility spell logic */ }
    }
  ]
}
```

## Class Balance Rules
- Total stat budget ~220-240 (HP + ATK*3 + DEF*3 + SPD*3 + MP)
- No class should be strictly better than another in all stats
- High ATK classes must have low DEF or HP (glass cannon tradeoff)
- Healers must have lowest ATK (can't out-damage AND out-sustain)
- SPD determines turn order — high SPD classes must sacrifice something else

## Sprite Requirements for New Class
- 14 columns × 20-22 rows pixel grid
- Dominant armor/clothing color matches accent
- Animated visor/eyes using time-based color: `rgba(R,${G+Math.floor(Math.sin(t*.1)*40)},B,.95)`
- Weapon drawn separately after pg() call (sword, bow, staff, etc.)
- Weapon gets neon glow via glow() helper function

## CLASS_LORE Entry
Each class needs a 1-2 sentence lore entry for the character select screen:
```javascript
// In CLASS_LORE object:
classId: "One or two sentences. Cyberpunk tone. What this class IS and WHY they fight."
```

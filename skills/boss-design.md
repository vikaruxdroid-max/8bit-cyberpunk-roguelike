SKILL: boss-design defines boss encounter structure, phase mechanics, and unique abilities.

## Boss Design Principles
- Every boss must feel like a puzzle, not a stat check
- 3 phases minimum, each changes the fight meaningfully
- Phase transitions at 67% and 34% HP with dramatic animation
- Each boss has a unique mechanic the player must adapt to
- Boss dialog escalates: confident → frustrated → desperate/enraged

## Phase System (existing: enemy.checkPhase)
Phase triggers: HP >67% = phase 1, 67-34% = phase 2, <34% = phase 3.
Each phase calls `ability.fn(enemy, player, phaseNumber)`.

**Phase Transition Effects:**
- Arena.triggerShake(14, 22) — heavy shake
- Arena.triggerScreenFlash(bossColor, 0.6) — dramatic flash
- Arena.spawnBurst(x, y, bossColor, 80, 2.5) — massive particle burst
- Arena.spawnText('PHASE 2', x, y, bossColor, 16) — phase label
- DM.say() with phase-specific boss dialog
- 800ms pause before next action (let player read/react)

## Boss Ability Patterns

**Windowed Attacks** (player can prepare):
- Boss telegraphs big attack 1 turn ahead via dialog ("Charging up...")
- Player should block or heal during the warning turn
- Attack deals 2.5-3x ATK damage

**Summon Adds** (phase 2+):
- Boss spawns 1-2 weak enemies (50% grunt stats)
- Adds must die before boss can be damaged again (or boss heals)
- Adds use boss zone's enemy pool

**Enrage Timer** (phase 3):
- After 5 turns in phase 3, boss gets +50% ATK permanently
- DM warns at turn 3: "Power building..."
- Visual: boss glow intensifies each turn

**Area Denial** (zone-specific):
- Boss creates hazard zone (visual: colored overlay on arena floor)
- Player takes X% max HP damage per turn while hazard active
- Hazard lasts 2-3 turns, then boss is vulnerable 2 turns

**Steal/Disable** (Netrunner-style):
- Disable player's strongest spell for 2 turns
- Drain MP on hit
- Copy player buff (steal nanoShield etc.)

## Existing Boss Templates

**Quantum Boss** (The Core): 320 HP, 3-phase
- Phase 1: normal attacks + Overload (cd5, 2x ATK)
- Phase 2: spawns adds (not implemented yet)
- Phase 3: enrage +50% ATK/SPD, shake + flash

**The Architect** (Corporate Strip): 420 HP, 3-phase
- Phase 1: normal + shield buff
- Phase 2: berserk mode + summon drones
- Phase 3: desperate rapid attacks

## New Boss Design Template
```
{
  id: 'bossId',
  name: 'BOSS NAME',
  hp: 300+,           // 3-5x zone grunt HP
  atk: 20+,           // 1.5-2x zone grunt ATK
  def: 10+,
  spd: 6-10,
  sprite: 'spriteKey', // unique or reuse existing
  color: '#hexcolor',
  isBoss: true,
  ability: {
    name: 'Ability Name',
    trigger: 'phase',   // 'phase' for boss phase system
    fn(enemy, player, phase) {
      if (phase === 2) {
        // Phase 2 behavior change
        enemy.atk = Math.floor(enemy.baseAtk * 1.3);
        Arena.spawnVFX('explode', Arena.W*.5, Arena.H*.4, enemy.color);
        Arena.triggerShake(10, 16);
        DM.say('PHASE 2 DIALOG!');
      }
      if (phase === 3) {
        // Phase 3 enrage
        enemy.atk = Math.floor(enemy.baseAtk * 1.6);
        enemy.spd = Math.floor(enemy.baseSpd * 1.4);
        Arena.spawnVFX('explode', Arena.W*.5, Arena.H*.4, '#ff0000');
        Arena.triggerShake(16, 24);
        DM.say('PHASE 3 DIALOG!');
      }
    }
  }
}
```

## Boss Loot Rules
- Always drop 3 items minimum
- 50% rare, 25% legendary
- One drop is always equipment for an empty slot (if player has empty slots)
- Boss-specific unique item (special name, unique stat combo)

## Boss Room Atmosphere
- arena-wrap gets 'boss-room' class (red inset glow)
- Zone background switches to boss variant (isBoss=true in drawBg)
- Music cue (when audio system exists): tension loop
- DM gives dramatic intro before combat starts
- DialogEngine shows boss-specific floor event

SKILL: enemy-design defines how to create enemies with distinct identity, AI behavior, and visual design.

## Enemy Design Pillars
Every enemy needs: a visual silhouette, one signature mechanic, a personality in 3 words.
- Glitch Drone: floating cube, AoE burst, "erratic mindless swarm"
- Netrunner: hooded hacker, spell disable, "cold calculating superior"
- Cyber Ogre: heavy brute, massive single hit, "slow crushing inevitable"

## Ability Trigger Types (existing system)
- `'turn3'` — fires once on turn 3 (used: false flag)
- `'hp50'` — fires once when HP drops below 50% (used: false flag)
- `'cd3'`/`'cd5'` — cooldown-based, fires every N turns (cdLeft counter)
- `'onhit'` — passive, triggers every time enemy attacks
- `'phase'` — boss-only, fires on phase transition with phase number

## AI Behavior Archetypes

**Swarm** (low HP, low ATK, high SPD): Appears in groups of 2-3. Individually weak but overwhelm through numbers. Abilities: buff allies, debuff player SPD.
- Examples: Glitch Drone, Corp Drone

**Glass Cannon** (low HP, high ATK, high SPD): Dangerous but fragile. Kill fast or get killed. Abilities: crit boost, evasion, armor-piercing.
- Examples: Ghost Hacker, Netrunner

**Tank** (high HP, high DEF, low SPD): Absorbs punishment. Slow but devastating when they hit. Abilities: self-heal, damage reflection, stacking buffs.
- Examples: Neon Golem, Cyber Ogre, Chrome Beast

**Debuffer** (medium stats): Doesn't kill directly — weakens the player for others. Abilities: ATK reduction, MP drain, skill disable, poison/bleed.
- Examples: Data Wraith, Neon Spider, Corp Drone

**Hybrid** (balanced stats): Adapts based on situation. Has both offensive and defensive abilities. Most interesting to fight.
- Examples: Circuit Lich (damage + heal), Void Specter (phase + attack)

## Sprite Design Rules
- 14 columns × 18-22 rows at P=4 (56-88px sprites)
- Each enemy needs a dominant color that matches their zone
- Silhouette must be recognizable at 50% opacity
- Animated element: pulsing eyes, flickering parts, or floating bits
- Use `const vc = \`rgba(R,${G+Math.floor(Math.sin(t*.1)*40)},B,.95)\`` for pulse
- Always add to SPRITE_SIZE object after creating sprite

## New Enemy Template
```javascript
// In ETYPES array:
{
  id: 'enemyId',
  name: 'DISPLAY NAME',
  hp: 50,              // base HP before floor scaling
  atk: 12,
  def: 4,
  spd: 8,
  sprite: 'spriteKey', // must match SPR.spriteKey function
  color: '#hexcolor',  // used for glow, particles, UI
  ability: {
    name: 'Ability Name',
    trigger: 'cd3',    // see trigger types above
    cdLeft: 0,         // for cd-based abilities
    fn(enemy, player) {
      // ability logic here
      const dmg = Math.floor(enemy.atk * 1.5);
      player.hp = Math.max(0, player.hp - dmg);
      UI.dmgNumPlayer(dmg, 'phit');
      DM.say('ABILITY NAME! Flavor text!');
    }
  }
}
```

## Enemy Stat Guidelines by Zone Difficulty
| Zone Diff | HP Range | ATK Range | DEF | SPD | Ability Power |
|-----------|----------|-----------|-----|-----|---------------|
| 1 (tutorial) | 35-60 | 8-12 | 2-4 | 4-8 | Weak/simple |
| 2 | 55-90 | 10-15 | 3-6 | 5-10 | One solid ability |
| 3 | 65-110 | 13-20 | 4-8 | 6-12 | Stronger + synergy |
| 4 | 80-140 | 16-26 | 5-10 | 7-13 | Two abilities or one powerful |
| 5 (endgame) | 100-160 | 20-30 | 8-14 | 8-14 | Complex/multi-phase |

## Zone-Enemy Thematic Fit
- NEON NEXUS: scavengers, street thugs, rogue drones
- VOID SECTOR: corrupted programs, reality glitches, data parasites
- CORPORATE STRIP: security bots, executive AI, compliance drones
- RUST MARKET: pit fighters, weapon platforms, smuggler bots
- THE UNDERNET: bio-mechanical creatures, fungal networks, evolved code
- GHOST DISTRICT: echo programs, memory fragments, phantom processes
- DATA HIGHWAY: interceptors, packet sniffers, speed programs
- THE CORE: failsafe processes, root programs, architect fragments

## Death Animation Requirements
- Every enemy death: 65-frame death timer
- White flash phase (frames 65→47): brightness(999%), frozen pose
- Dissolve phase (frames 47→0): shrink + fade + particle burst
- Particle burst: 85 particles in enemy.color, second burst 45 white particles at 130ms delay
- Screen shake: intensity 12, frames 20
- Screen flash: enemy.color, alpha 0.5
- Float text: "DEFEATED" in enemy.color

## Encounter Group Composition
- Zone difficulty 1: 1 enemy
- Zone difficulty 2: 1-2 enemies
- Zone difficulty 3: 1-2 enemies (one may be elite tier)
- Zone difficulty 4: 2-3 enemies
- Zone difficulty 5: 2-3 enemies (at least one elite)
- Never more than 3 enemies (UI/canvas limitation)
- Mixed types preferred: tank + glass cannon, debuffer + swarm

SKILL: dungeon-design defines room types, events, environmental hazards, and dungeon flow.

## Room Types (DungeonGen._pickType)
Current types: combat, loot, rest, merchant, boss. New room types to add:

**TRAP ROOM**: Environmental hazard the player must survive.
- Wire Trap: 10% max HP damage, chance to dodge based on SPD
- Data Mine: drains 20% MP, sparks particle effect
- Gravity Well: reduces SPD by 3 for next combat
- Trap rooms should appear 1-2 times per dungeon, never adjacent to boss

**EVENT ROOM**: Narrative choice with consequences.
- Abandoned Terminal: choose to hack (gain intel = +10% crit next fight, or trigger alarm = extra enemy)
- Wounded Runner: heal them (lose 20% HP, gain quest progress) or loot them (gain gold, lose karma)
- Unstable Power Node: absorb (+15 MP permanently) or destabilize (AoE damage all enemies next room)
- Events use DialogEngine with 2-3 choices, outcomes shown via DM.say()

**ELITE ROOM**: Harder combat with guaranteed rare+ drop.
- 1-2 enemies with 1.5x stats (mini-boss tier)
- Guaranteed rare drop, 15% legendary
- Appear once per dungeon in zones difficulty 3+
- Visual: arena-wrap gets orange border glow

**PUZZLE ROOM**: Simple logic puzzle for rewards.
- Sequence Memory: flash 4-6 colored panels, player repeats
- Wire Connect: match 3 pairs by clicking
- Decrypt: unscramble a 4-letter cyberpunk word
- Success: bonus loot + full MP restore. Failure: nothing, move on
- Timer: 30 seconds, UI overlay on arena-wrap

## Dungeon Flow Rules
- First room always combat (tutorial/warm-up)
- Last room always boss
- Rest room appears in middle third (rooms 2-4 of a 6-room dungeon)
- Merchant appears before boss (second-to-last or third-to-last)
- Never two of same type adjacent (except combat)
- Elite rooms only in zones difficulty 3+
- Event rooms only after zone 1 (not tutorial)
- Trap rooms never before rest rooms

## Room Connections (Branching)
Current: linear path with occasional branch. Ideal structure:
```
Room 0 (combat) → Room 1a (combat) OR Room 1b (event)
                → Room 2 (loot/trap)
                → Room 3a (merchant) OR Room 3b (elite)
                → Room 4 (rest)
                → Room 5 (boss)
```
- Player chooses path at fork points via roomExits overlay
- Each path shows room type icon and risk/reward hint
- Cleared rooms shown as green on minimap, unvisited as gray

## Room Entry Animation
- Scanline wipe transition (existing: screenWipe)
- DM.say() announces room type
- 600ms delay before combat starts or interaction available
- Boss rooms: red pulse on arena-wrap, dramatic DM line

## Environmental Modifiers (per-zone flavor)
- NEON NEXUS: standard, no modifiers
- VOID SECTOR: 10% chance any room glitches (random stat -1 for duration)
- CORPORATE STRIP: security cameras (enemies get first strike 20% of rooms)
- RUST MARKET: unstable floor (random trap damage between rooms, 5% HP)
- THE UNDERNET: toxic air (lose 2% HP per room passively)
- GHOST DISTRICT: haunted (dead enemies have 5% chance to revive at 25% HP)
- DATA HIGHWAY: speed boost (player SPD +2 all rooms)
- THE CORE: all modifiers active at half strength

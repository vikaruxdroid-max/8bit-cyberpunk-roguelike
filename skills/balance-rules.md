# SKILL: balance-rules

## Purpose
Enforce consistent enemy stat scaling, player progression curves,
and game balance rules in 8bit_cyberpunk_FIXED.html.

## Player Base Stats by Class
- Warrior: HP 120, ATK 18, DEF 12, SPD 6, MP 80
- Ranger: HP 90, ATK 22, DEF 7, SPD 10, MP 90
- Rogue: HP 60, ATK 26, DEF 5, SPD 14, MP 100
- Cleric: HP 100, ATK 12, DEF 12, SPD 9, MP 140
- Warlock: HP 65, ATK 25, DEF 6, SPD 6, MP 140
- Druid: HP 95, ATK 15, DEF 8, SPD 9, MP 130

## Player Stat Growth Per Level
- HP: +10 per level
- ATK: +2 per level
- DEF: +1 per level
- SPD: +0.5 per level (round down)
- MP: +8 per level

## Enemy Stat Scaling Formula
Base stats multiply by: 1 + (floor_level * 0.15)
- Grunt: HP 40, ATK 8, DEF 3, SPD 5
- Netrunner: HP 32, ATK 10, DEF 2, SPD 8
- Enforcer: HP 60, ATK 7, DEF 8, SPD 4
- Chrome Beast: HP 80, ATK 12, DEF 6, SPD 2
- Ghost Hacker: HP 35, ATK 11, DEF 1, SPD 10
- Neon Spider: HP 30, ATK 9, DEF 2, SPD 12
- Corporate Drone: HP 45, ATK 8, DEF 4, SPD 6
- Boss: base enemy stats * 3.0 HP, * 1.8 ATK

## Zone Difficulty Ratings
- NEON NEXUS: floor_level 1-2 (tutorial)
- GHOST DISTRICT: floor_level 2-3
- RUST MARKET: floor_level 3-4
- CORPORATE STRIP: floor_level 4-5
- THE UNDERNET: floor_level 5-6
- VOID SECTOR: floor_level 7-8
- DATA HIGHWAY: floor_level 8-9
- THE CORE: floor_level 10 (final)

## Economy Balance
- Credits per common enemy: 10-30
- Credits per rare enemy: 30-60
- Credits per boss: 100-200
- Merchant item cost: item_level * 15 credits
- Starting credits: 0
- Never give player more than 500 credits before zone 4

## Upgrade Balance (victory screen stat choices)
- +HP: always +10 flat
- +ATK: always +3 flat
- +DEF: always +2 flat
- +SPD: always +1 flat
- +MP: always +15 flat
- Full Restore: restore all HP and MP (rare option, 20% chance to appear)
- Skill CD reduction: -1 to all cooldowns (15% chance to appear)
- Three options shown: always random, never show duplicates

## Skill Balance Rules
- Skill damage multipliers: 1.5x to 3x ATK depending on cooldown
- Short cooldown (2 turns): 1.5x-2x damage
- Medium cooldown (3-4 turns): 2x-2.5x damage
- Long cooldown (5+ turns): 2.5x-3x damage
- MP costs: 10-25 per skill depending on power
- Never make a skill that trivializes combat entirely

## Mini-Boss vs Boss Rules
- Mini-boss: 1.5x base enemy stats, drops 2 items, 30% legendary chance
- Zone boss: 3x base enemy stats, drops 3 items, 25% legendary chance
- Final boss (THE CORE): 5x base stats, 3 phases, drops 5 items

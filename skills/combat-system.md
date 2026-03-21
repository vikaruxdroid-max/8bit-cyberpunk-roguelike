# SKILL: combat-system

## Purpose
Document and enforce all combat rules, formulas, and structure in
8bit_cyberpunk_FIXED.html. Always read this before modifying any combat code.

## Core Combat Flow
1. Player selects action (attack, skill, block, item)
2. Speed (SPD) determines turn order — higher SPD acts first
3. Damage calculated, animations play, dialog triggers
4. Status effects tick at end of each turn
5. Check win/lose condition after each action
6. Never skip or reorder these steps

## Damage Formula
- Basic attack: ATK - (target DEF * 0.5), minimum 1 damage
- Critical hit: 15% base chance, 2x damage multiplier
- Miss chance: based on target SPD vs attacker SPD ratio
- Skills: use their own multipliers defined in skill data

## Status Effects — never modify tick order
- HACK: disables one random skill for 2 turns
- BURN: deals 5% max HP per turn for 3 turns
- FREEZE: target skips next turn
- POISON: deals 3% max HP per turn for 4 turns
- SHIELD: reduces incoming damage by 50% for 3 turns
- STUN: target skips next turn, 25% chance on Shock Gauntlets

## Enemy Behavior Patterns
- Aggressive: always attacks, uses power move when player HP above 60%
- Defensive: buffs when own HP drops below 50%, counters after blocking
- Tactical: targets player's highest stat to debuff first
- Each enemy type has an assigned pattern in dungeonConfig

## Combo System
- 3 consecutive hits: +10% damage
- 5 consecutive hits: +25% damage
- 7+ consecutive hits: +40% damage + golden screen edge glow
- Miss or taking damage resets combo to 0

## Block/Counter
- Block reduces damage by 50% for that turn
- Counter triggers if blocked damage is below 20% of player max HP
- Counter deals 75% of player ATK
- Block cooldown: 2 turns

## Turn Timing — never make faster than these values
- Turn delay between actions: 1200ms
- Attack animation: 400ms forward, 300ms back
- Hit reaction: 500ms
- Skill cast wind-up: 600ms
- Skill effect: 800ms
- Death sequence: 1500ms particle explosion + 200ms freeze + 1000ms hold
- Dialog bubble: 35ms per character, 3500ms display after complete

## Combat Pacing Rule
A full turn from action to next prompt must take 4-6 seconds minimum.
Never compress timing to speed up combat — it ruins effect visibility.

## Win/Lose Conditions
- Win: enemy HP reaches 0 → death sequence → victory screen
- Lose: player HP reaches 0 → game over screen with run summary
- Never transition screens until all animations complete

## Z-Index During Combat
- Arena background: 0
- Floor grid: 5
- Sprites: 20
- Effects canvas: 30 (pointer-events: none always)
- UI panels: 40
- Speech bubbles: 45
- Modals/overlays: 60

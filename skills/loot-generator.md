# SKILL: loot-generator

## Purpose
Enforce consistent item generation, naming, stat scaling, and
rarity rules across all loot drops in 8bit_cyberpunk_FIXED.html.

## Item Types and Stat Focus
- Cyber Blade: primary ATK bonus, secondary SPD
- Neural Helm: primary DEF bonus, secondary MP
- Neon Vest: primary DEF, secondary HP
- Circuit Boots: primary SPD, secondary DEF
- Data Ring: primary MP bonus, secondary ATK
- Bio Amulet: primary HP bonus, secondary DEF
- Pulse Gauntlets: primary ATK, secondary stun chance
- Void Blade: high ATK + 15% lifesteal
- Neural Crown: MP bonus + reduce all skill cooldowns by 1
- Phase Cloak: 20% dodge chance
- Shock Gauntlets: 25% stun chance on hit
- Nano Injector: consumable, restores 50% HP

## Rarity Tiers
- Common (white border, #ffffff): 70% drop chance
  - Stat bonus: floor_level * 2 to floor_level * 4
- Rare (cyan border, #00ffff, glow): 25% drop chance
  - Stat bonus: floor_level * 4 to floor_level * 7
- Legendary (gold border, #ffd700, animated glow): 5% drop chance
  - Stat bonus: floor_level * 8 to floor_level * 12
  - Always has 2+ stat bonuses
  - Unique name prefix: Void, Quantum, Spectral, Omega, Zero-Day

## Stat Scaling by Floor
- All stat bonuses multiply by current floor_level
- Boss rooms: 1.5x normal stat bonus range
- Legendary items: always drop at least 1 from boss kills

## Sell Values
- Common: 10-30 credits
- Rare: 50-100 credits
- Legendary: 200-500 credits
- Always confirm before selling legendary items

## Loot Drop Rates by Enemy Type
- Grunt: 1 item, common only
- Netrunner: 1-2 items, 30% rare chance
- Enforcer: 1-2 items, 25% rare chance
- Chrome Beast: 2 items, 20% rare, 5% legendary
- Ghost Hacker: 1-2 items, 35% rare chance
- Neon Spider: 1 item + poison accessory bias
- Corporate Drone: 2 items, ATK reduction item bias
- Boss: 3 items guaranteed, 50% rare, 25% legendary

## Item Card Display Rules
- Level badge: top-left corner, always visible
- Rarity label: top-right corner, colored to match rarity
- Icon: centered, 64x64px minimum
- Name: bold, full width, no truncation
- Slot type: cyan, smaller than name
- Stat bonuses: neon green, bold
- TAKE/DISCARD buttons: full card width, 36px tall
- Max 1 item taken per victory screen
- Once taken, all other TAKE buttons disable

## Inventory Rules
- Bag: 4x6 grid (24 slots maximum)
- Equipment slots: HEAD, WEAPON, OFFHAND, CHEST, LEGS, RING, BOOT, ACCS
- Equipping replaces current item — old item goes to bag
- Bag full: must discard before taking new items
- Stats update immediately on equip/unequip

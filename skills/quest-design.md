SKILL: quest-design defines quest objectives, tracking, reward structure, and progression hooks.

## Quest System Architecture (existing: QM object)
- Pool of 15 quests, 5 active at a time
- Each quest has: id, description, target value, current progress, reward
- Progress tracked via QM.track(statName, value) calls in combat/loot/exploration
- Completed quests apply rewards immediately and get replaced from pool

## Quest Categories

**Combat Quests** (track during fights):
- Kill X enemies total
- Kill X enemies without using spells
- Deal X total damage in one fight
- Land X critical hits
- Survive a fight taking 0 damage (clean run)
- Win a fight in under N turns
- Kill a boss without healing

**Collection Quests** (track via loot/inventory):
- Collect X credits total
- Find a legendary item
- Equip items in all 7 slots
- Sell X items to merchants
- Collect X items of a specific type (blades, armor, etc.)

**Exploration Quests** (track via room/zone progression):
- Clear X rooms total
- Clear a zone without resting
- Visit X different zones
- Find X merchant rooms
- Survive X trap rooms
- Complete an event room successfully

**Mastery Quests** (track via combat performance):
- Reach combo X
- Block X attacks
- Use every spell at least once in a fight
- Win with HP below 10%
- Cast X spells total

## Quest Reward Types
| Reward | Value | When to Use |
|--------|-------|-------------|
| +ATK | 2-4 | Combat quests |
| +DEF | 2-3 | Survival quests |
| +SPD | 1-2 | Speed/combo quests |
| +Max HP | 10-20 | Exploration quests |
| +Max MP | 10-15 | Spell mastery quests |
| Credits | 30-80 | Collection quests |
| CD Reduction | -1 all spells | Rare mastery quests |
| Full Heal | 100% HP+MP | Dangerous challenge quests |

## Quest Template
```javascript
{
  id: 'questId',
  desc: 'Kill 5 enemies without spells',  // shown in quest panel
  stat: 'killsNoSpells',                  // GameState tracking key
  target: 5,                              // completion threshold
  reward: { atk: 3 },                     // stat reward object
  rewardDesc: '+3 ATK'                    // display string
}
```

## Quest Display (existing: #qpanel)
- Quest panel: collapsible sidebar with quest list
- Each quest shows: description + progress bar + reward preview
- Completed quests flash gold, show "+REWARD" float text
- New quest slides in from right with cyan glow

## Quest Tracking Integration Points
Call `QM.track()` at these moments:
- `Combat.deal()` — track damage dealt, kills, crits
- `Combat.playerAttack()` — track attacks, combo
- `Combat.tick()` — track turns, clean runs
- `Game.enterRoom()` — track rooms visited, zone progress
- `Inventory.equip()` — track equipment changes
- `LootSystem.roll()` — track items found
- `UI.updateBars()` — track HP thresholds

## Quest Difficulty Scaling
- Zone 1-2: easy quests (kill 3, deal 50 damage)
- Zone 3-4: medium quests (kill 5 without spells, reach combo 5)
- Zone 5+: hard quests (clean run, sub-3-turn kill, boss no heal)
- Quest pool should refresh with harder versions as zones increase
- Never give impossible quests (e.g., "use healing spell" to non-Cleric)

## Quest Chain Concept (future)
Multi-part quests that tell a micro-story:
1. "Find the signal source" (enter Data Highway)
2. "Defeat the signal guardian" (kill zone boss)
3. "Decrypt the message" (complete event room)
Reward: unique legendary item only available through chain

## Quest UI Rules
- Max 5 active quests visible
- Completed quests auto-replace after 1 room transition
- Progress bar: cyan fill on dark background
- Completed state: gold border + checkmark
- Quest descriptions max 30 characters (fit in sidebar)

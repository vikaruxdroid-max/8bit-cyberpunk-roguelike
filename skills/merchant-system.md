SKILL: merchant-system defines shop mechanics, pricing, stock rotation, and buy/sell flow.

## Merchant Room Flow
1. Player enters merchant room → DM.say() with merchant greeting (zone-flavored)
2. DialogEngine shows NPC greeting with merchant personality
3. Merchant UI overlay appears on arena-wrap
4. Player browses stock, buys/sells, then exits to room navigation

## Merchant UI Layout
Overlay on arena-wrap (same pattern as roomExits):
```
┌─────────────────────────────────────┐
│ ⟐ MERCHANT — [Zone Name]    💰 XXX CR │
├──────────────────┬──────────────────┤
│   FOR SALE (4)   │  YOUR BAG (24)  │
│ ┌──┐ ┌──┐ ┌──┐  │ [existing bag   │
│ │🗡│ │🛡│ │💎│  │  grid from      │
│ └──┘ └──┘ └──┘  │  invPanel]      │
│ Item Name  50CR  │                 │
│ +3 ATK +1 DEF   │                 │
│ [BUY]            │ [SELL SELECTED] │
├──────────────────┴──────────────────┤
│            [LEAVE SHOP]            │
└─────────────────────────────────────┘
```

## Stock Generation
- 3-4 items per merchant visit
- Items generated using LootSystem.roll(floor) with guaranteed variety
- At least 1 weapon/armor, 1 accessory, 1 consumable (Nano Injector)
- Rarity distribution: 60% common, 30% rare, 10% legendary
- Stock is fixed per room (generated on room entry, saved in room object)
- Never sell items the player already has equipped

## Pricing Formula
**Buy price**: `baseValue * (1 + floor * 0.15) * rarityMult`
- Common: baseValue 30-60 CR
- Rare: baseValue 80-150 CR
- Legendary: baseValue 200-400 CR
- Consumables: 20-40 CR

**Sell price**: 40% of buy price (existing: common 10-30, rare 50-100, legendary 200-500)

**Discount events** (10% chance per merchant):
- "Clearance sale" — all items 25% off
- DM.say("Everything must go. Don't ask why.")

## Buy/Sell Flow
**Buying:**
1. Click item in FOR SALE grid → item card shows stats + price
2. Click [BUY] → check gold >= price
3. If affordable and bag not full: deduct gold, add item to inventory, remove from stock
4. If bag full: DM.say("Bag's full. Sell something first.")
5. If too expensive: DM.say("Not enough credits, runner.")

**Selling:**
1. Click item in bag grid → item highlighted + sell price shown
2. Click [SELL SELECTED] → confirm dialog ("Sell [item] for X CR?")
3. On confirm: remove from bag, add gold, update UI
4. Equipped items cannot be sold (must unequip first)

## Merchant Personality by Zone
- NEON NEXUS: friendly street vendor, fair prices
  - "Welcome, runner. Take a look."
  - "Good choice. That'll keep you alive."
- VOID SECTOR: glitching AI merchant, cryptic
  - "Pr1ces are... relative here."
  - "This item exists. Probably."
- CORPORATE STRIP: professional, cold, transactional
  - "Standard pricing applies. No negotiation."
  - "Transaction complete. Move along."
- RUST MARKET: aggressive haggler, sketchy
  - "You won't find this anywhere else. Probably stolen."
  - "Final offer. Take it or flatline."
- THE UNDERNET: organic merchant, weird
  - "Grown fresh. Don't ask from what."
  - "It's alive. Treat it well."
- GHOST DISTRICT: echo of dead merchant
  - "I... used to sell things. I think."
  - "Take it. I can't use it anymore."
- DATA HIGHWAY: speed-talking, impatient
  - "Buy-sell-done. Clock's ticking."
  - "Fast transaction. I like you."

## Special Merchant Items (zone-exclusive)
Each zone's merchant has a 15% chance to stock one zone-exclusive item:
- NEON NEXUS: "Street Runner's Kit" (SPD +3, HP +10)
- VOID SECTOR: "Void Fragment" (MP +20, 5% dodge)
- CORPORATE STRIP: "Executive Override" (ATK +4, DEF +2)
- RUST MARKET: "Scrapyard Special" (ATK +5, random negative stat)
- THE UNDERNET: "Bio-Graft" (HP +25, DEF -1)
- GHOST DISTRICT: "Memory Shard" (MP +15, CD -1)
- DATA HIGHWAY: "Speed Chip" (SPD +5, HP -10)

## Integration Points
- Merchant room type already exists in DungeonGen._pickType
- triggerMerchant() already called in Game.enterRoom for merchant rooms
- Inventory.render() handles bag display
- Gold tracked in GameState.player (credits) and UI element #invGold

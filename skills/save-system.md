# SKILL: save-system

## Purpose
Define the localStorage save schema and read/write patterns for
8bit_cyberpunk_FIXED.html. Always follow this when touching save logic.

## Save Key
localStorage key: "cyberpunk_save"
All data stored as a single JSON object under this key.

## Save Schema
{
  "version": 1,
  "timestamp": Date.now(),
  "player": {
    "name": string,
    "class": string,
    "level": number,
    "hp": number,
    "maxHp": number,
    "mp": number,
    "maxMp": number,
    "atk": number,
    "def": number,
    "spd": number,
    "credits": number,
    "kills": number,
    "totalDamage": number,
    "turnsPlayed": number
  },
  "equipment": {
    "head": item|null,
    "weapon": item|null,
    "offhand": item|null,
    "chest": item|null,
    "legs": item|null,
    "ring": item|null,
    "boot": item|null,
    "accs": item|null
  },
  "inventory": [item, ...],
  "world": {
    "currentZone": string,
    "clearedZones": [string, ...],
    "currentRoom": number,
    "roomsCleared": [number, ...],
    "unlockedZones": [string, ...]
  },
  "quests": {
    "active": [quest_id, ...],
    "completed": [quest_id, ...]
  },
  "records": {
    "highestZone": string,
    "mostKills": number,
    "highestDamage": number,
    "bestItem": item|null,
    "totalRuns": number
  }
}

## Auto-Save Triggers
- After every room cleared
- After every item equipped or discarded
- After every level up
- After every zone transition
- Never auto-save mid-combat

## Save/Load Functions — always use these patterns
Save:
  const save = JSON.stringify(STATE.save);
  localStorage.setItem('cyberpunk_save', save);

Load:
  const raw = localStorage.getItem('cyberpunk_save');
  if (raw) STATE.save = JSON.parse(raw);

## Main Menu Detection
- On game load: check if cyberpunk_save exists in localStorage
- If exists: show CONTINUE button above NEW GAME button
- CONTINUE: loads save directly into game at saved zone/room
- NEW GAME: confirm dialog "This will erase your current save. Continue?"
  → on confirm: localStorage.removeItem('cyberpunk_save') → start fresh

## Save Compatibility
- Always check save.version on load
- If version mismatch: warn player and offer to reset
- Never silently corrupt a save by loading incompatible schema

## Records Persistence
- Records survive NEW GAME — never clear records on reset
- Records stored separately: localStorage key "cyberpunk_records"
- Update records after every run ends (victory or game over)

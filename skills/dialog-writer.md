# SKILL: dialog-writer

## Purpose
Enforce consistent character voice, cyberpunk tone, and dialog
structure for all NPC, enemy, and player dialog in the game.

## Core Tone Rules
- All dialog: punchy, short, aggressive or atmospheric
- Maximum 12 words per line — never exceed this
- Cyberpunk slang vocabulary:
  ALLOWED: flatline, jack in, ICE, wetware, ghost, chrome,
  corp, netrun, splice, burn, frag, slot, wire, data,
  deck, uplink, zero-day, phantom, neon, void, glitch,
  hack, rig, grid, meat, pulse, signal, static, sync
- Never use fantasy language (quest, spell, magic, sword)
- Never use modern casual language (yeah, ok, lol, thanks)
- Tone per character type:
  - Grunts: dumb, aggressive, short sentences
  - Netrunners: technical, cold, superior attitude
  - Bosses: dramatic, threatening, philosophical
  - Merchants: street-smart, transactional, neutral
  - Player: confident, dark humor, never afraid

## Dialog Trigger Rules
- Encounter start: enemy taunts first, player responds
- Every 3 turns: one organic exchange
- Enemy HP below 30%: enemy shows desperation
- Player HP below 30%: player shows grit, enemy mocks
- Skill use: character comments on the skill
- Critical hit: both react
- Status effect applied: quip about the status
- Never repeat same line twice in a row per enemy type

## AI Dialog System Prompt Templates
Enemy system prompt:
"You are [enemy_name], a [enemy_type] in a cyberpunk neon dungeon.
Fighting [player_class] named [player_name].
Speak in short punchy cyberpunk slang. Max 12 words.
Be aggressive, dramatic, in-character.
Situation: [hp_status], turn [turn_number], [active_effects]"

Player system prompt:
"You are a [player_class] fighter in a cyberpunk dungeon.
Respond to your enemy with confidence and attitude.
Max 12 words. Cyberpunk slang. In-character."

## Speech Bubble Rules
- Player bubble: neon cyan border (#00ffff), dark background
- Enemy bubble: neon magenta border (#ff00ff), dark background
- Position: always ABOVE the relevant sprite, never overlapping
- Downward triangle pointer at bottom of bubble
- Typewriter: 35ms per character
- Display time: 3500ms after text completes
- Both bubbles can show simultaneously
- Never block combat action buttons
- Show "..." typing indicator while AI generates response
- Fallback to static dialog_db.json if API fails or times out after 3s

## Combat Notification Bar (top of screen)
- Only for system events: status applied, skill disabled, combo reached
- NOT for character dialog — that goes in speech bubbles
- Auto-dismisses after 3 seconds with fade out
- Neon border, semi-transparent dark background, icon on left

## Zone-Specific Dialog Flavor
- NEON NEXUS: street level slang, bustling city references
- VOID SECTOR: glitchy speech, corrupted words, reality references
- CORPORATE STRIP: formal corp-speak mixed with threats
- RUST MARKET: black market slang, deal references
- THE UNDERNET: organic/bio references, underground culture
- GHOST DISTRICT: echoing, hollow, references to the past
- DATA HIGHWAY: speed references, data stream metaphors
- THE CORE: final boss gravitas, world-ending stakes

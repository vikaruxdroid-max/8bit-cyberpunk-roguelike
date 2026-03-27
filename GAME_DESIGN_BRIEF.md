# NEON DUNGEON: Comprehensive Game Design Brief
## For Claude Chat AI Consultation — Living Document

---

## 1. WHAT THE GAME IS TODAY

**Neon Dungeon** is a single-file browser roguelike (~8800 lines of HTML/CSS/JS, no build system, no backend). It runs entirely client-side. The player creates a cyberpunk runner, picks random spells from large pools, and fights through procedurally generated dungeon zones to reach a final boss.

### Technical Constraints
- **Single HTML file** — all code, styles, and markup in one file
- **No server/backend** — everything runs in the browser
- **No dependencies** — vanilla JS, Canvas 2D API, Web Audio API
- **Save system** — localStorage only
- **Asset loading** — 6 PNG sprites, 2 background images, 2 JSON data files, 2 Google Fonts
- **Target** — Chrome/Edge, 1280x720 minimum, works at 1920x1080

### Current Content Inventory
| System | Count |
|---|---|
| Playable classes (body types) | 5 (Man, Woman, Sage, Cyber, Shadow) |
| Zones (world map) | 8 (linear unlock, final boss at The Core) |
| Enemy types | 14 (9 base + 5 advanced/bosses) |
| Attack spells | 30 (single target, AoE, execute, multi-hit, specials) |
| Defensive spells | 30 (shields, heals, reflect, CC, stat buffs) |
| Potions | 30 (healing, power, shield, utility, exotic) |
| Passive skills | 5 (crit, lifesteal, dodge, block DR, CD reduction) |
| Weapons | 30 (blades, pistols, heavy, energy, tech) |
| Quests per run | 15 in pool, 5 active |
| Level-up choices | 10 stat/ability upgrades |
| Equipment slots | 7 (weapon, head, chest, legs, ring, boots, accessory) |
| VFX types | 6+ (explode, slash, spark, ring, kill cam, spell flash) |
| Procedural audio SFX | 8 (hit, crit, heal, block, spell, death, levelUp, evolve) |

---

## 2. CORE GAMEPLAY LOOP

```
Character Creation (pick 1 of 2 per category, 6 categories)
    |
    v
World Map (8 zones, unlock by clearing prerequisites)
    |
    v
Enter Zone (5-12 rooms: combat, loot, rest, merchant)
    |
    v
Combat Room (auto-attack + 4 manual spells: 2 attack, 1 defense, 1 potion)
    |
    v
Victory Screen (loot + SPELL SWAP: swap 1 of your 4 spells for a new random offering)
    |
    v
Next Room... until Boss
    |
    v
Boss Victory -> Back to World Map -> Next Zone
    |
    v
Clear all zones -> THE CORE -> Quantum Boss -> WIN
```

### How Combat Works Now
- **Speed-based turns**: Player and enemies have action counters that fill by their SPD stat. When counter >= 100, they act.
- **Auto-attack**: Player auto-attacks the lowest HP enemy when their turn comes.
- **4 Manual spells**: 2 attack skills + 1 defensive skill + 1 potion, each with MP cost and cooldown.
- **Block**: Manual block with cooldown, reduces damage by blockDR%.
- **Combo system**: Consecutive hits increase combo counter for bonus damage.
- **Buff/debuff system**: Timed effects (ATK up, DEF up, dodge, stun, bleed, poison, reflect).
- **Spell evolution**: After 10 casts, a spell becomes "EX" version with -1 cooldown.
- **Spell swap**: After each room, player can swap one spell for a new random one from the same pool.

### What Makes It a Roguelike
- Random spell offerings at character creation
- Random enemy encounters per room
- Spell swap decisions that shape your build over the run
- Permadeath (no mid-run saving of progress state)
- Multiple zones with escalating difficulty

---

## 3. THEMATIC VISION

### Primary Themes
- **Cyberpunk noir**: Neon-lit dystopia, corporate megastructures, street-level hackers vs. the machine
- **Warhammer 40K grimdark**: Relentless enemies, no easy victories, the galaxy is hostile and unforgiving
- **Hacker fantasy**: Spells are "programs" and "exploits", combat is "jacking in", the dungeon is "the grid"
- **Survival against overwhelming odds**: The player is always outgunned, skill and spell synergy are the only edge

### Tone References
- Ghost in the Shell (net-diving, identity crisis)
- Blade Runner (rain-soaked neon, existential dread)
- Warhammer 40K (grimdark escalation, "there is only war")
- Neuromancer (console cowboys, ICE, cyberspace)
- Akira (psychic destruction, Neo-Tokyo chaos)

### Visual Identity (Current)
- Dark navy/black backgrounds (#0a0a1a)
- Cyan (#00ffff), magenta (#ff00ff), green (#00ff41) as primary palette
- Pixel art sprites (14x26 pixel characters at 4x scale)
- CRT scanline effects, matrix rain, vapor wave backgrounds
- "Press Start 2P" pixel font + "Share Tech Mono" terminal font
- Apple II boot screen on startup (green phosphor terminal)

---

## 4. WHERE THE GAME NEEDS TO GO

### 4A. Combat Improvements — Make It Skill-Based, Not Passive

**Current problem**: Combat is mostly auto-attack with occasional spell button presses. The player doesn't need to think tactically.

**Vision**: Combat should be a puzzle where the player's spell loadout is the solution. Every enemy encounter should force decisions.

**Ideas to explore**:
- **Enemy telegraphing**: Enemies announce their next attack 1 turn before (e.g., "CHARGING MEGA BLAST"). Player must respond with the right counter (shield, stun, dodge).
- **Spell timing windows**: Some spells are more effective at specific moments (e.g., counter-attack deals 3x if used right after an enemy attack).
- **Elemental/type weaknesses**: Enemies have resistances and vulnerabilities. Player must adapt spell loadout across rooms.
- **Active dodge mechanic**: Click-to-dodge with a timing window instead of passive dodge chance.
- **Threat priority**: Multiple enemies with different roles (tank, healer, DPS) — player must choose targeting order.
- **Boss phases with mechanics**: Bosses that require specific strategies (e.g., "shield phase — must use armor-piercing spell to break through").

### 4B. AI Integration Opportunities

**This is the key question for Claude Chat to explore deeply.**

Potential AI integration points:
1. **AI Dungeon Master narration** — Generate contextual combat commentary, enemy taunts, lore snippets based on the current fight state (API call to Claude)
2. **AI-generated enemy encounters** — Use AI to create unique enemy ability combinations that counter the player's current spell loadout, ensuring every fight feels tailored
3. **Procedural quest generation** — AI creates unique quest objectives based on the player's playstyle and loadout
4. **AI difficulty tuning** — Analyze player performance and dynamically adjust enemy stats/abilities to maintain challenge
5. **AI lore engine** — Generate cyberpunk world-building text for zones, NPCs, item descriptions
6. **Competitive AI analysis** — Compare player runs and generate "coach" tips for improvement
7. **AI-powered enemy AI** — Instead of simple behavior patterns (aggressive/defensive/tactical), use AI to make enemies that genuinely adapt to player strategy mid-fight

**Technical consideration**: The game has no backend. API calls would need to be client-side (CORS, API keys in code, rate limits). Consider: can we add a lightweight serverless function (Cloudflare Worker, Vercel Edge) as a proxy? Or keep everything client-side with cached/pre-generated AI content?

### 4C. Visual Improvements

**Current state**: Canvas-based 2D with pixel sprites. Effective but minimal.

**Ideas to explore**:
- **Parallax depth layers**: Multiple scrolling background layers for city depth
- **Weather/atmosphere effects**: Rain, fog, neon flicker, smoke particles
- **Enemy entrance animations**: Enemies glitch/teleport into the arena
- **Spell cast animations**: Full-screen flash effects, screen distortion on big hits
- **Kill cam**: Slow-motion zoom on final kill (partially implemented)
- **Dynamic lighting**: Neon glow that reacts to combat events
- **Character portraits during dialog**: Anime-style character art in speech bubbles
- **Zone-specific visual themes**: Each zone has unique background art, particle colors, ambient effects

### 4D. Menu & UI Improvements

- **Animated transitions** between screens (slide, fade, glitch effect)
- **Tooltip system** for spells/items on hover
- **Build summary** before entering dungeon ("Your loadout: 2 AoE attacks, 1 shield, 1 heal — balanced build")
- **Run history** screen showing past builds and outcomes
- **Codex/bestiary** that fills as you encounter enemies
- **Spell collection** tracker showing which of the 90+ spells you've discovered

### 4E. Spells, Abilities & Gear Expansion

- **Spell synergies with visual feedback**: When player has complementary spells (e.g., stun + execute), show a "SYNERGY BONUS" indicator
- **Rare/legendary spell variants**: Some spell offerings are golden-bordered with enhanced effects
- **Weapon abilities**: Weapons grant a passive bonus AND a unique proc effect (e.g., "Plasma Katana: 10% chance to cast free Neon Slash on hit")
- **Gear set bonuses**: Collecting matching equipment pieces grants bonus effects
- **Spell fusion**: Combine two spells at a special merchant to create a new hybrid spell

### 4F. Victory Conditions & Endgame

- **Multiple endings** based on choices made during the run
- **New Game+** with harder modifiers and exclusive rewards
- **Daily challenge runs** with fixed seeds and leaderboards
- **Endless mode** after clearing The Core — infinite scaling floors
- **Achievement system** tracking lifetime accomplishments
- **Unlockable content**: New starting spells, portraits, accent colors earned through play

---

## 5. MINI-GAMES BETWEEN STAGES

**Core concept**: Between some dungeon rooms, a random mini-game appears. Completing it reveals a **secret room** with a rare boss encounter and exclusive loot.

### Mini-Game Ideas

1. **Hacking Minigame** (pattern match): A grid of symbols appears — player must find matching pairs before a timer expires. Success = access to hidden server room with a data boss.

2. **Lockpicking** (timing): A rotating dial with a safe zone. Click at the right moment to crack each tumbler. 3 tumblers = door to hidden vault boss.

3. **Code Breaker** (logic puzzle): Wordle-style — guess a 4-digit code. Each guess shows correct/misplaced/wrong. Success = hidden cyberspace arena with a virus boss.

4. **Neural Reflex Test** (reaction time): Random prompts flash on screen — press the correct key (arrow direction, button). Score determines the quality of the secret room reward.

5. **Market Hustle** (risk/reward): A quick gambling mini-game — bet credits on a shell game or card flip. Win big = rare merchant with exclusive items. Lose = nothing but lost credits.

6. **Data Corruption** (memory): A sequence of symbols flashes briefly. Reproduce the sequence from memory. Longer sequences = better rewards.

### Secret Room Structure
- Mini-game success rate determines difficulty/reward tier of secret room
- Secret room bosses are unique (not found in normal zones)
- Secret bosses drop exclusive "relic" items that provide run-long passive bonuses
- Secret rooms are optional — failure just means missing the bonus, not punishment

---

## 6. REPLAYABILITY & COMPETITIVE HOOKS

### What Drives Replayability
- **90+ spell pool with pick-1-of-2 system** — odds of getting the same build twice are astronomically low
- **Spell swap decisions** — same starting build diverges based on swap choices
- **Spell evolution** rewards commitment (10 casts = EX version)
- **5 character classes** with different sprites/aesthetics
- **8 zones** with different enemy compositions requiring different strategies
- **Quest variety** — different quests encourage different playstyles

### Competitive Features to Add
- **Run timer** — track how fast each zone is cleared
- **Score system** — composite of kills, damage, quests, time, gold earned
- **Leaderboards** — daily/weekly/all-time rankings
- **Seed sharing** — share a run seed so others can attempt the same layout
- **Ghost runs** — see a replay of the #1 player's run as you play
- **Seasonal challenges** — monthly themed modifiers with exclusive rewards

### Skill Expression
- Spell timing and combo sequencing
- Target priority (which enemy to focus)
- Spell swap strategy (keep evolving spells vs. adapt to upcoming zone)
- Resource management (MP conservation, cooldown planning)
- Block timing against telegraphed attacks
- Mini-game performance for secret room access

---

## 7. TECHNICAL ARCHITECTURE FOR AI FEATURES

### Option A: Client-Side Only (No Backend)
- Pre-generate AI content (enemy taunts, lore, quest text) and embed in JSON files
- Use small local models via WebLLM/ONNX for simple text generation
- Limitation: No dynamic adaptation, content is static after generation

### Option B: Lightweight Serverless Proxy
- Cloudflare Worker or Vercel Edge Function as API proxy
- Player sends game state → proxy calls Claude API → returns AI response
- Enables: Dynamic narration, adaptive enemies, personalized quests
- Cost: Anthropic API usage per request (can be minimized with caching)

### Option C: Hybrid
- Pre-generated base content (offline-first, no API needed)
- Optional AI enhancement when online (richer narration, adaptive difficulty)
- Graceful degradation — game works fully offline, AI features are bonus

**Recommendation for Claude Chat**: Explore Option C as the most practical path. Ask about cost optimization, response caching, and which game moments benefit most from live AI generation vs. pre-generated content.

---

## 8. LIVING DOCUMENT — NEXT STEPS

This document should evolve as we build. Current priority stack:

### Phase 1: Core Combat Polish (Current)
- [x] 30 attack skills, 30 defensive skills, 30 potions, 30 weapons
- [x] 4-spell combat loadout (2 attack + 1 defense + 1 potion)
- [x] Victory screen spell swap mechanic
- [x] 3x2 character creation grid
- [x] Apple II boot screen with asset preloading
- [ ] Enemy telegraphing system
- [ ] Boss phase mechanics
- [ ] Active dodge/counter-attack timing

### Phase 2: Content & Variety
- [ ] Mini-games between stages (hacking, lockpicking, code breaker)
- [ ] Secret rooms with rare bosses
- [ ] Relic system (currently UI skeleton only, no data)
- [ ] Expand passive skills from 5 to 30
- [ ] Weapon abilities (proc effects)
- [ ] Spell synergy indicators

### Phase 3: Visual & Audio Polish
- [ ] Weather/atmosphere effects per zone
- [ ] Enhanced spell cast animations
- [ ] Enemy entrance/death animations
- [ ] Zone-specific background art (only Neon Nexus has custom art currently)
- [ ] Dynamic music system (procedural)
- [ ] Screen transition effects

### Phase 4: AI Integration
- [ ] Design AI integration architecture (Claude Chat consultation)
- [ ] Serverless proxy setup
- [ ] AI dungeon master narration
- [ ] AI-adaptive enemy encounters
- [ ] AI difficulty tuning
- [ ] Competitive scoring and leaderboards

### Phase 5: Endgame & Competition
- [ ] New Game+ mode
- [ ] Endless mode
- [ ] Daily challenge runs
- [ ] Seed sharing
- [ ] Achievement system
- [ ] Run history and statistics

---

## 9. QUESTIONS FOR CLAUDE CHAT

When bringing this to Claude Chat, ask these specific questions:

1. **Given the single-file architecture and no backend, what's the most practical way to add AI-powered enemy adaptation?**
2. **How can we make combat feel skill-based rather than stat-based, while keeping the idle/auto-attack core?**
3. **What AI integration would have the highest impact on replayability with the lowest implementation cost?**
4. **How should mini-games be structured to enhance the core loop rather than interrupt it?**
5. **What competitive features (leaderboards, daily runs, seed sharing) can work without a traditional backend?**
6. **How can the Warhammer 40K grimdark tone be blended with cyberpunk aesthetics without losing the 8-bit charm?**
7. **What's the optimal moment in the gameplay loop to call an AI API — between rooms, during boss intros, at spell swap, or elsewhere?**
8. **How can AI make each run feel genuinely unique beyond just random spell offerings?**

---

*Last updated: 2026-03-26*
*Game version: 8bit_cyberpunk_FIXED.html (~8800 lines)*
*Repository: github.com/vikaruxdroid-max/8bit-cyberpunk-roguelike*

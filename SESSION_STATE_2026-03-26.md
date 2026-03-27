# NEON DUNGEON — SESSION STATE SNAPSHOT
## Date: 2026-03-26 | Save point for cross-device continuity

---

## WHO YOU ARE TALKING TO

You are talking to **NeuroNeko**, Information Security Manager at Cook County Government.
- GitHub username: `vikaruxdroid-max`
- Local machine username: `carlo`
- Game lives at: `D:\game\8bit_cyberpunk_FIXED.html`
- Repo: `github.com/vikaruxdroid-max/8bit-cyberpunk-roguelike`
- Git workflow: `cd D:\game && git pull` to start, `git add . && git commit -m "..." && git push` to save

---

## WHAT THIS PROJECT IS

**Neon Dungeon** — a single-file browser roguelike (~8800 lines, HTML/CSS/JS, no build system, no backend).
Cyberpunk/grimdark aesthetic. Player builds a spell loadout across 8 zones, fighting to a final boss.
Core mechanic: spell swap decision after every room.

**Full spec document:** `NEON_DUNGEON_CLAUDE_CODE_SPEC.md` (v1.1) — lives in the repo.

---

## TWO-TIER WORKFLOW

```
NeuroNeko (intent) → Claude Chat (architect/translator) → Claude Code (executor)
```

- **This chat** = architect layer. NeuroNeko describes what they want in plain language.
  Claude Chat translates it into precise instruction block files for Claude Code.
- **Claude Code** = executor. Receives instruction block files, reads the spec, implements, reports back.
- Claude Code is **currently active** and mid-development on the game.

**How to resume in a new Claude Chat session:**
1. Upload this file to the new chat
2. Say: *"Read this session state file. You are the architect layer for my Neon Dungeon game project. Resume from the current position."*
3. Upload `NEON_DUNGEON_CLAUDE_CODE_SPEC.md` as well if you want the full spec in context.

---

## CURRENT DEVELOPMENT STATE

### Phases Overview

| Phase | Name | Status |
|---|---|---|
| Phase 1 | Combat Polish | 🔄 IN PROGRESS |
| Phase 2 | Content & Variety | ⏳ Not started |
| Phase 3 | Visual & Audio Polish | ⏳ Not started |
| Phase 4 | AI Integration | ⏳ Not started |
| Phase 5 | Endgame & Competitive | ⏳ Not started |

### Phase 1 — Block Status

| Block | Feature | Status |
|---|---|---|
| 1.1 | Enemy Telegraphing System | ✅ IMPLEMENTED |
| 1.2 | Boss Phase Mechanics | ✅ IMPLEMENTED |
| 1.3 | Active Dodge Window | ✅ IMPLEMENTED → SUPERSEDED by 1.4 |
| 1.4 | Ace Attorney Reaction Combat | 📋 INSTRUCTION BLOCK READY — NOT YET EXECUTED |

**Block 1.4 is the next thing Claude Code needs to execute.**
Instruction file: `PHASE_1_4_REACTION_COMBAT.md`

---

## WHAT BLOCK 1.4 DOES

Replaces the combat presentation layer with an Ace Attorney-style reaction system:

- Named enemy attacks fire an **anime manga speech bubble** above the enemy with attack name + comedy taunt
- A **countdown ring** (2.5–4s depending on tier) gives the player time to react
- Player clicks any of their 4 spell slots to respond
- Response is graded by effectiveness:

| Grade | Trigger | Damage | Result text example |
|---|---|---|---|
| NULLIFY | Correct counter type | 0% | "ERROR 404: ATTACK NOT FOUND." |
| SILENCE | Stun vs special/boss | 0% | "CANCELLED LIKE YOUR SOCIAL CREDIT." |
| ABSORB | Shield vs physical | 30% | "SHIELD TOOK THE HIT. MOSTLY." |
| CLASH | Attack vs attack | 50% | "MUTUAL ASSURED PAIN." |
| RESIST | Any defense | 60% | "DAMAGE REDUCED. DIGNITY INTACT." |
| DIRECT HIT | No action / expired | 100% | "SKILL ISSUE DETECTED." |

- Normal attacks still auto-resolve — no window, no pacing interruption
- Spell button halos pulse with color hints during window
- Comedy text pools per enemy type (Corporate, Virus, Samurai, Boss, Generic)
- Special: using a potion during an attack triggers unique comedy lines

**Removes:** Phase 1.3 dodge bar
**Keeps:** All Phase 1.1 data structures (telegraph objects, counter system)

---

## FILES GENERATED THIS SESSION

| File | Purpose | Status |
|---|---|---|
| `GAME_DESIGN_BRIEF.md` | Original design brief | Reference only |
| `NEON_DUNGEON_CLAUDE_CODE_SPEC.md` | Master spec v1.1 | In repo — Claude Code reads this |
| `PHASE_1_INSTRUCTION_BLOCKS.md` | Blocks 1.1, 1.2, 1.3 + checklist | Executed and complete |
| `PHASE_1_4_REACTION_COMBAT.md` | Block 1.4 instruction | **READY — NOT YET EXECUTED** |
| `SESSION_STATE_2026-03-26.md` | This file | Resume point |

---

## NEXT ACTIONS IN ORDER

1. **Claude Code:** Execute `PHASE_1_4_REACTION_COMBAT.md`
   > *"Read PHASE_1_4_REACTION_COMBAT.md in full. Then read NEON_DUNGEON_CLAUDE_CODE_SPEC.md. Execute Block 1.4 only. Report back when complete."*

2. **After 1.4 confirmed:** Run Phase 1 Final Verification Checklist (bottom of `PHASE_1_INSTRUCTION_BLOCKS.md`)

3. **After all 18 checks pass:** Tell Claude Chat — *"Phase 1 complete and verified. Generate Phase 2 instruction blocks."*

4. **Phase 2 covers:** Mini-games (6 types), Secret rooms, Relic system, 25 new passives, Weapon proc effects, Spell synergy indicators

---

## LOCKED DESIGN DECISIONS

| Decision | Choice |
|---|---|
| AI architecture | Cloudflare Worker proxy (Option C Hybrid) |
| AI model for game calls | claude-haiku-4-5-20251001 |
| AI call timing | Boss intros, room transitions, post-run summary only — never mid-combat |
| Combat feel | Ace Attorney reaction windows |
| Reaction window duration | 2.5s / 3s / 3.5s / 4s by tier |
| Dodge mechanic | Absorbed into reaction spell system (Block 1.4) |
| Mini-games | Canvas-rendered (not HTML/CSS overlays) |
| Run history | localStorage, 50 runs FIFO |
| Daily RNG | LCG algorithm, date-based seed |

---

## ARCHITECT LAYER PREFERENCES

For the Claude Chat instance acting as architect:

- Formal, blunt, technical tone. No praise unless exceptional. Challenge bad ideas with data.
- Always generate instruction blocks as downloadable `.md` files — never inline copy-paste.
- Update `NEON_DUNGEON_CLAUDE_CODE_SPEC.md` when design decisions change. Bump version + changelog.
- Do not generate Phase N+1 blocks until Phase N is confirmed complete.
- Fun and engagement first. Performance second. Visual fidelity third.
- Comedy and personality are features, not decoration.

---

*Snapshot saved: 2026-03-26*
*Resume trigger: Upload this file + say "resume from current position"*
*Next action: Execute PHASE_1_4_REACTION_COMBAT.md in Claude Code*

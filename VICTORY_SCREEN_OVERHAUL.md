# NEON DUNGEON — INSTRUCTION BLOCK: VICTORY-SCREEN-OVERHAUL
## Room Cleared / Loot / Spell Swap Screen — Complete Redesign
### Claude Chat Architect Layer · 2026-03-26

---

> **SCOPE**: Full redesign of the room-cleared screen.
> UX: direct-click spell swap, large loot cards, stat comparison, remove equipment doll.
> Visual: neon cyberpunk treatment, animated header, celebratory energy.
> AI: loot advice line, prominent spell commentary placement.
> All existing game logic preserved — only presentation changes.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. The victory/room-cleared screen HTML element ID and its full inner structure
2. Where the SWAP button click handler is — what function it calls
3. Where the KEEP button click handler is
4. Where loot items (gear) are rendered on this screen
5. Where the spell swap offered spell is stored in state
6. Where `#vicAiComment` (spell commentary div from Block 4.1) is injected
7. The XP bar element and where XP gain animation is triggered
8. Where the equipment doll is rendered (the character silhouette with gear slots)
9. The CONTINUE button element ID and handler

Report all nine before writing any code.

---

## STEP 1 — CSS OVERHAUL

Add to the `<style>` block. Do not remove existing victory screen styles — add new ones
that override where needed using more specific selectors or `!important` sparingly:

```css
/* ══════════════════════════════════════════════════
   VICTORY SCREEN OVERHAUL
   ══════════════════════════════════════════════════ */

#sVS {
    background: #020210;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0;
    overflow: hidden;
    position: relative;
}

/* ── HEADER ─────────────────────────────────────── */
#vsHeader {
    width: 100%;
    padding: 18px 0 10px;
    text-align: center;
    border-bottom: 1px solid rgba(0,255,255,0.2);
    background: linear-gradient(180deg, rgba(0,255,255,0.06) 0%, transparent 100%);
    position: relative;
}

#vsHeaderTitle {
    font-family: 'Press Start 2P', monospace;
    font-size: 18px;
    color: #00ffff;
    letter-spacing: 6px;
    text-shadow: 0 0 20px rgba(0,255,255,0.8), 0 0 40px rgba(0,255,255,0.4);
    animation: vsHeaderPulse 2s ease-in-out infinite;
}
@keyframes vsHeaderPulse {
    0%,100% { text-shadow: 0 0 20px rgba(0,255,255,0.8), 0 0 40px rgba(0,255,255,0.4); }
    50%      { text-shadow: 0 0 30px rgba(0,255,255,1.0), 0 0 60px rgba(0,255,255,0.6); }
}

#vsHeaderStats {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #334455;
    letter-spacing: 2px;
    margin-top: 6px;
}

#vsAiComment {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #556655;
    font-style: italic;
    margin-top: 4px;
    min-height: 14px;
}

/* ── MAIN BODY ──────────────────────────────────── */
#vsBody {
    display: flex;
    flex: 1;
    width: 100%;
    gap: 0;
    overflow: hidden;
}

/* ── LEFT: LOOT ZONE ────────────────────────────── */
#vsLootZone {
    flex: 1;
    padding: 16px;
    border-right: 1px solid rgba(0,255,255,0.1);
    display: flex;
    flex-direction: column;
    gap: 10px;
}

#vsLootTitle {
    font-family: 'Press Start 2P', monospace;
    font-size: 8px;
    color: #ffd700;
    letter-spacing: 3px;
    margin-bottom: 4px;
}

/* Loot card */
.vs-loot-card {
    background: rgba(5,5,25,0.95);
    border: 1px solid #223344;
    padding: 10px 12px;
    cursor: pointer;
    position: relative;
    transition: border-color 0.15s, background 0.15s;
    display: flex;
    align-items: center;
    gap: 12px;
}
.vs-loot-card:hover {
    border-color: #00ffff;
    background: rgba(0,255,255,0.06);
}
.vs-loot-card.taken {
    border-color: #00ff41;
    background: rgba(0,255,65,0.06);
    opacity: 0.6;
    pointer-events: none;
}
.vs-loot-card.discarded {
    border-color: #221122;
    opacity: 0.3;
    pointer-events: none;
}

.vs-loot-icon {
    font-size: 22px;
    min-width: 32px;
    text-align: center;
}

.vs-loot-info {
    flex: 1;
}

.vs-loot-name {
    font-family: 'Press Start 2P', monospace;
    font-size: 7px;
    color: #ffffff;
    margin-bottom: 3px;
}

.vs-loot-stat {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #00ff41;
    margin-bottom: 2px;
}

.vs-loot-slot {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #334455;
}

.vs-loot-compare {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #888800;
    font-style: italic;
}

.vs-loot-rarity {
    font-family: 'Press Start 2P', monospace;
    font-size: 5px;
    padding: 2px 5px;
    border: 1px solid currentColor;
    position: absolute;
    top: 6px;
    right: 8px;
}
.vs-loot-rarity.common   { color: #556677; }
.vs-loot-rarity.uncommon { color: #00aaff; }
.vs-loot-rarity.rare     { color: #aa00ff; }
.vs-loot-rarity.legendary{ color: #ffd700; }

.vs-loot-actions {
    display: flex;
    gap: 6px;
    margin-top: 6px;
}

.vs-btn-take {
    font-family: 'Press Start 2P', monospace;
    font-size: 6px;
    padding: 5px 10px;
    background: rgba(0,255,65,0.1);
    border: 1px solid #00ff41;
    color: #00ff41;
    cursor: pointer;
    letter-spacing: 1px;
    transition: background 0.15s;
}
.vs-btn-take:hover { background: rgba(0,255,65,0.25); }

.vs-btn-discard {
    font-family: 'Press Start 2P', monospace;
    font-size: 6px;
    padding: 5px 8px;
    background: none;
    border: 1px solid #221122;
    color: #443344;
    cursor: pointer;
    letter-spacing: 1px;
    transition: border-color 0.15s, color 0.15s;
}
.vs-btn-discard:hover { border-color: #ff4444; color: #ff4444; }

/* Relic display */
.vs-relic-card {
    background: rgba(255,215,0,0.04);
    border: 1px solid #443300;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.vs-relic-icon { font-size: 18px; }
.vs-relic-name {
    font-family: 'Press Start 2P', monospace;
    font-size: 6px;
    color: #ffd700;
    margin-bottom: 2px;
}
.vs-relic-desc {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #886600;
}

/* Loot AI advice */
#vsLootAi {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #445544;
    font-style: italic;
    padding: 6px 0;
    min-height: 30px;
    border-top: 1px solid #111122;
}

/* ── RIGHT: SPELL SWAP ZONE ─────────────────────── */
#vsSpellZone {
    width: 420px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

#vsSpellTitle {
    font-family: 'Press Start 2P', monospace;
    font-size: 8px;
    color: #00ffff;
    letter-spacing: 3px;
    margin-bottom: 4px;
}

#vsSpellInstruction {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #334455;
    margin-bottom: 8px;
}

/* Current spell slots — 2x2 grid */
#vsCurrentSpells {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
}

.vs-spell-slot {
    background: rgba(5,5,20,0.95);
    border: 1px solid #1a1a3a;
    padding: 8px 10px;
    cursor: pointer;
    transition: border-color 0.15s, background 0.15s;
    position: relative;
    min-height: 64px;
}
.vs-spell-slot:hover {
    border-color: #ff00ff;
    background: rgba(255,0,255,0.06);
}
.vs-spell-slot:hover::after {
    content: 'CLICK TO SWAP';
    position: absolute;
    bottom: 3px;
    right: 4px;
    font-family: 'Press Start 2P', monospace;
    font-size: 4px;
    color: #ff00ff;
}
.vs-spell-slot.selected {
    border-color: #ffd700;
    background: rgba(255,215,0,0.08);
}
.vs-spell-slot.swapped {
    border-color: #00ff41;
    background: rgba(0,255,65,0.06);
}

.vs-spell-slot-name {
    font-family: 'Press Start 2P', monospace;
    font-size: 6px;
    color: #ffffff;
    margin-bottom: 4px;
    line-height: 1.4;
}
.vs-spell-slot-desc {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    color: #445566;
}
.vs-spell-slot-meta {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    color: #334455;
    margin-top: 2px;
}
.vs-spell-ex-badge {
    position: absolute;
    top: 4px;
    right: 4px;
    font-family: 'Press Start 2P', monospace;
    font-size: 5px;
    color: #ffd700;
}

/* Arrow between current and offered */
#vsSwapArrow {
    text-align: center;
    font-size: 18px;
    color: #223344;
    margin: 2px 0;
    letter-spacing: 4px;
}

/* Offered spell — large card */
#vsOfferedSpell {
    background: rgba(5,5,25,0.95);
    border: 1px solid #334455;
    padding: 12px 14px;
    position: relative;
}
#vsOfferedSpell.attack-spell  { border-color: #ff4444; }
#vsOfferedSpell.defense-spell { border-color: #00aaff; }
#vsOfferedSpell.potion-spell  { border-color: #00ff41; }

#vsOfferedLabel {
    font-family: 'Press Start 2P', monospace;
    font-size: 5px;
    color: #334455;
    letter-spacing: 2px;
    margin-bottom: 6px;
}
#vsOfferedName {
    font-family: 'Press Start 2P', monospace;
    font-size: 9px;
    color: #ffffff;
    margin-bottom: 6px;
}
#vsOfferedDesc {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #aaaaaa;
    margin-bottom: 4px;
}
#vsOfferedMeta {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #445566;
}

/* Synergy hint on offered spell */
#vsOfferedSynergy {
    font-family: 'Press Start 2P', monospace;
    font-size: 5px;
    margin-top: 6px;
    padding: 3px 6px;
    border: 1px solid currentColor;
    display: inline-block;
}

/* Keep button */
#vsKeepBtn {
    font-family: 'Press Start 2P', monospace;
    font-size: 6px;
    padding: 8px 0;
    width: 100%;
    background: none;
    border: 1px solid #1a1a2e;
    color: #334455;
    cursor: pointer;
    letter-spacing: 2px;
    transition: border-color 0.15s, color 0.15s;
    margin-top: 4px;
}
#vsKeepBtn:hover { border-color: #334466; color: #667788; }

/* ── FOOTER ─────────────────────────────────────── */
#vsFooter {
    width: 100%;
    padding: 10px 20px;
    border-top: 1px solid rgba(0,255,255,0.15);
    display: flex;
    align-items: center;
    gap: 16px;
    background: rgba(0,0,5,0.8);
}

#vsXpSection {
    flex: 1;
}

#vsXpLabel {
    font-family: 'Press Start 2P', monospace;
    font-size: 6px;
    color: #556677;
    margin-bottom: 4px;
}

#vsXpBar {
    height: 8px;
    background: #0a0a1a;
    border: 1px solid #1a1a3a;
    position: relative;
    overflow: hidden;
}

#vsXpFill {
    height: 100%;
    background: linear-gradient(90deg, #00aaff, #ff00ff);
    transition: width 0.8s ease-out;
    box-shadow: 0 0 8px rgba(0,170,255,0.5);
}

#vsXpText {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #445566;
    margin-top: 2px;
}

#vsContinueBtn {
    font-family: 'Press Start 2P', monospace;
    font-size: 9px;
    padding: 12px 24px;
    background: rgba(0,255,255,0.06);
    border: 2px solid #00ffff;
    color: #00ffff;
    cursor: pointer;
    letter-spacing: 3px;
    transition: background 0.15s, box-shadow 0.15s;
    animation: continuePulse 2s ease-in-out infinite;
}
#vsContinueBtn:hover {
    background: rgba(0,255,255,0.15);
    box-shadow: 0 0 20px rgba(0,255,255,0.4);
    animation: none;
}
@keyframes continuePulse {
    0%,100% { box-shadow: 0 0 6px rgba(0,255,255,0.2); }
    50%      { box-shadow: 0 0 16px rgba(0,255,255,0.5); }
}

/* ══════════════════════════════════════════════════
   END VICTORY SCREEN OVERHAUL
   ══════════════════════════════════════════════════ */
```

---

## STEP 2 — HTML RESTRUCTURE

Replace the inner content of the victory screen element with:

```html
<!-- HEADER -->
<div id="vsHeader">
    <div id="vsHeaderTitle">◈ ROOM CLEARED ◈</div>
    <div id="vsHeaderStats"></div>
    <div id="vsAiComment">ANALYZING COMBAT DATA...</div>
</div>

<!-- MAIN BODY -->
<div id="vsBody">

    <!-- LEFT: LOOT -->
    <div id="vsLootZone">
        <div id="vsLootTitle">⚡ LOOT ACQUIRED</div>
        <div id="vsLootCards"></div><!-- populated by JS -->
        <div id="vsRelicCards"></div><!-- populated by JS, hidden if empty -->
        <div id="vsLootAi"></div><!-- AI loot advice -->
    </div>

    <!-- RIGHT: SPELL SWAP -->
    <div id="vsSpellZone">
        <div id="vsSpellTitle">◈ SPELL SWAP</div>
        <div id="vsSpellInstruction">Click a spell slot to replace it with the offered spell.</div>
        <div id="vsCurrentSpells"></div><!-- populated by JS -->
        <div id="vsSwapArrow">↕</div>
        <div id="vsOfferedSpell">
            <div id="vsOfferedLabel">OFFERED SPELL</div>
            <div id="vsOfferedName"></div>
            <div id="vsOfferedDesc"></div>
            <div id="vsOfferedMeta"></div>
            <div id="vsOfferedSynergy" style="display:none"></div>
        </div>
        <button id="vsKeepBtn">✓ KEEP CURRENT LOADOUT</button>
    </div>

</div>

<!-- FOOTER -->
<div id="vsFooter">
    <div id="vsXpSection">
        <div id="vsXpLabel">EXPERIENCE</div>
        <div id="vsXpBar"><div id="vsXpFill" style="width:0%"></div></div>
        <div id="vsXpText"></div>
    </div>
    <button id="vsContinueBtn">CONTINUE ◈</button>
</div>
```

---

## STEP 3 — JS POPULATION FUNCTIONS

Add a new JS section that populates the redesigned screen when it opens.
Find where `VictoryScreen.show()` or equivalent currently populates the old HTML.
Replace that population logic with calls to these new functions:

```javascript
// ============================================================
// VICTORY SCREEN — Redesigned Population Logic
// ============================================================

function vsPopulateHeader(roomNum, totalRooms, stats) {
    const titleEl = document.getElementById('vsHeaderTitle');
    const statsEl = document.getElementById('vsHeaderStats');
    if (titleEl) titleEl.textContent = `◈ ROOM ${roomNum}/${totalRooms} CLEARED ◈`;
    if (statsEl) {
        const parts = [];
        if (stats.kills !== undefined)      parts.push(`KILLS: ${stats.kills}`);
        if (stats.damageDealt !== undefined) parts.push(`DMG: ${stats.damageDealt}`);
        if (stats.hp !== undefined)          parts.push(`HP: ${stats.hp}/${stats.maxHp}`);
        statsEl.textContent = parts.join('  ·  ');
    }
}

function vsPopulateLoot(lootItems, currentGear) {
    const container = document.getElementById('vsLootCards');
    if (!container) return;
    container.innerHTML = '';

    if (!lootItems || lootItems.length === 0) {
        container.innerHTML = '<div style="font-family:Share Tech Mono;font-size:10px;color:#223344;padding:8px 0">— NO LOOT THIS ROOM —</div>';
        return;
    }

    lootItems.forEach((item, idx) => {
        const card = document.createElement('div');
        card.className = 'vs-loot-card';
        card.dataset.idx = idx;

        // Stat comparison
        const currentItem = currentGear ? currentGear[item.slot] : null;
        const compareText = currentItem
            ? `replaces: ${currentItem.name} (${currentItem.stat || ''})`
            : 'new slot';

        card.innerHTML = `
            <div class="vs-loot-icon">${item.icon || '⬡'}</div>
            <div class="vs-loot-info">
                <div class="vs-loot-name">${item.name}</div>
                <div class="vs-loot-stat">${item.statText || item.stat || ''}</div>
                <div class="vs-loot-slot">${(item.slot || '').toUpperCase()} SLOT</div>
                <div class="vs-loot-compare">${compareText}</div>
                <div class="vs-loot-actions">
                    <button class="vs-btn-take" data-idx="${idx}">▶ TAKE</button>
                    <button class="vs-btn-discard" data-idx="${idx}">✕ DISCARD</button>
                </div>
            </div>
            <div class="vs-loot-rarity ${item.rarity || 'common'}">${(item.rarity || 'COMMON').toUpperCase()}</div>
        `;

        card.querySelector('.vs-btn-take').addEventListener('click', (e) => {
            e.stopPropagation();
            vsLootTake(idx, item);
            card.classList.add('taken');
        });
        card.querySelector('.vs-btn-discard').addEventListener('click', (e) => {
            e.stopPropagation();
            card.classList.add('discarded');
        });

        // Clicking the card itself = take
        card.addEventListener('click', () => {
            if (!card.classList.contains('taken') && !card.classList.contains('discarded')) {
                vsLootTake(idx, item);
                card.classList.add('taken');
            }
        });

        container.appendChild(card);
    });
}

function vsLootTake(idx, item) {
    // Call existing equip/take logic — adapt to actual function name
    // e.g.: Player.equip(item); or LootSystem.take(item);
    // Replace with actual loot take function
    DM.say(`EQUIPPED: ${item.name}`, 'system');
}

function vsPopulateRelics(relicsEarned) {
    const container = document.getElementById('vsRelicCards');
    if (!container) return;
    container.innerHTML = '';
    if (!relicsEarned || relicsEarned.length === 0) return; // hide section entirely

    relicsEarned.forEach(relic => {
        const def = getRelicDef(relic.id || relic);
        if (!def) return;
        const card = document.createElement('div');
        card.className = 'vs-relic-card';
        card.innerHTML = `
            <div class="vs-relic-icon">${def.icon || '◈'}</div>
            <div>
                <div class="vs-relic-name">${def.name}</div>
                <div class="vs-relic-desc">${def.description}</div>
            </div>
        `;
        container.appendChild(card);
    });
}

function vsPopulateSpellSwap(currentSpells, offeredSpell) {
    // Current spell slots — 2×2 grid
    const grid = document.getElementById('vsCurrentSpells');
    if (!grid || !currentSpells) return;
    grid.innerHTML = '';

    currentSpells.forEach((spell, i) => {
        if (!spell) return;
        const slot = document.createElement('div');
        slot.className = 'vs-spell-slot';
        slot.dataset.slotIndex = i;

        const isEX = spell.evolved;
        const typeColor = spell.type === 'attack' ? '#ff4444' :
                          spell.type === 'defense' ? '#00aaff' : '#00ff41';

        slot.style.borderColor = '#1a1a3a';
        slot.innerHTML = `
            ${isEX ? '<div class="vs-spell-ex-badge">EX</div>' : ''}
            <div class="vs-spell-slot-name">${spell.name || '—'}</div>
            <div class="vs-spell-slot-desc">${spell.desc || spell.description || ''}</div>
            <div class="vs-spell-slot-meta">MP:${spell.mpCost || spell.mp || 0}  CD:${spell.cooldown || 0}</div>
        `;

        slot.addEventListener('mouseenter', () => {
            slot.style.borderColor = '#ff00ff';
        });
        slot.addEventListener('mouseleave', () => {
            if (!slot.classList.contains('swapped')) {
                slot.style.borderColor = '#1a1a3a';
            }
        });

        slot.addEventListener('click', () => {
            // Swap this slot with the offered spell
            vsDoSwap(i, offeredSpell);
            slot.classList.add('swapped');
            slot.innerHTML = `
                <div class="vs-spell-slot-name">${offeredSpell.name}</div>
                <div class="vs-spell-slot-desc">${offeredSpell.desc || offeredSpell.description || ''}</div>
                <div class="vs-spell-slot-meta">MP:${offeredSpell.mpCost || offeredSpell.mp || 0}  CD:${offeredSpell.cooldown || 0}</div>
            `;
            slot.style.borderColor = '#00ff41';
            // Disable all other slots after swap
            document.querySelectorAll('.vs-spell-slot').forEach(s => {
                if (s !== slot) {
                    s.style.pointerEvents = 'none';
                    s.style.opacity = '0.4';
                }
            });
            document.getElementById('vsKeepBtn').style.display = 'none';
        });

        grid.appendChild(slot);
    });

    // Offered spell card
    const offeredEl = document.getElementById('vsOfferedSpell');
    const nameEl    = document.getElementById('vsOfferedName');
    const descEl    = document.getElementById('vsOfferedDesc');
    const metaEl    = document.getElementById('vsOfferedMeta');
    const synEl     = document.getElementById('vsOfferedSynergy');

    if (offeredEl && offeredSpell) {
        offeredEl.className = '';
        if (offeredSpell.type === 'attack')  offeredEl.classList.add('attack-spell');
        if (offeredSpell.type === 'defense') offeredEl.classList.add('defense-spell');
        if (offeredSpell.type === 'potion')  offeredEl.classList.add('potion-spell');

        if (nameEl) nameEl.textContent = offeredSpell.name || '—';
        if (descEl) descEl.textContent = offeredSpell.desc || offeredSpell.description || '';
        if (metaEl) metaEl.textContent =
            `MP: ${offeredSpell.mpCost || offeredSpell.mp || 0}  ·  CD: ${offeredSpell.cooldown || 0}  ·  TYPE: ${(offeredSpell.type || '').toUpperCase()}`;

        // Synergy delta hint
        if (synEl && typeof getSwapSynergyDelta === 'function') {
            let bestDelta = null;
            currentSpells.forEach((s, i) => {
                const delta = getSwapSynergyDelta(currentSpells, offeredSpell, i);
                if (delta && (!bestDelta || delta.delta > bestDelta.delta)) bestDelta = delta;
            });
            if (bestDelta) {
                synEl.textContent = bestDelta.label;
                synEl.style.color  = bestDelta.color;
                synEl.style.display = 'inline-block';
            } else {
                synEl.style.display = 'none';
            }
        }
    }
}

function vsDoSwap(slotIndex, offeredSpell) {
    // Call existing swap logic — adapt to actual function
    // e.g.: Player.swapSpell(slotIndex, offeredSpell);
    // Replace with actual swap function used in codebase
    DM.say(`SPELL SWAPPED: slot ${slotIndex+1} → ${offeredSpell.name}`, 'system');
    // Also call refreshSynergies() from Block 2.6
    if (typeof refreshSynergies === 'function') refreshSynergies();
}

function vsPopulateXP(currentXP, maxXP, level) {
    const fillEl = document.getElementById('vsXpFill');
    const textEl = document.getElementById('vsXpText');
    if (fillEl) {
        // Animate fill after short delay
        setTimeout(() => {
            fillEl.style.width = `${Math.min(100, (currentXP / maxXP) * 100)}%`;
        }, 300);
    }
    if (textEl) textEl.textContent = `LEVEL ${level}  ·  ${currentXP} / ${maxXP} XP`;
}
```

---

## STEP 4 — REMOVE EQUIPMENT DOLL

Find the equipment doll rendering (pre-scan item 8) — the character silhouette with gear slots
connected by dotted lines. Remove it entirely from the victory screen. It is confusing and
provides no useful information at the loot decision moment.

If current equipped gear needs to be referenced (for stat comparison), it is handled inline
in the loot card `compareText` logic above. The doll itself is not needed.

---

## STEP 5 — WIRE KEEP BUTTON

Find the existing KEEP button logic. Wire it to the new `#vsKeepBtn`:

```javascript
document.getElementById('vsKeepBtn')?.addEventListener('click', () => {
    // existing keep logic — no swap happens
    // enable CONTINUE if it requires spell decision to be made first
    document.getElementById('vsContinueBtn')?.removeAttribute('disabled');
    document.getElementById('vsKeepBtn').style.opacity = '0.4';
    document.getElementById('vsKeepBtn').style.pointerEvents = 'none';
    DM.say('LOADOUT KEPT.', 'system');
});
```

---

## STEP 6 — WIRE CONTINUE BUTTON

Wire `#vsContinueBtn` to the existing continue/next-room logic:

```javascript
document.getElementById('vsContinueBtn')?.addEventListener('click', () => {
    // existing continue handler — adapt to actual function
    // e.g.: Game.nextRoom(); or VictoryScreen.continue();
});
```

---

## STEP 7 — AI LOOT ADVICE

After loot items are displayed, fetch a non-blocking AI loot tip:

```javascript
async function fetchLootAdvice(lootItems, currentSpells) {
    const lootEl = document.getElementById('vsLootAi');
    if (!lootEl) return;

    if (!lootItems || lootItems.length === 0) return;

    const itemNames   = lootItems.map(i => i.name).filter(Boolean);
    const spellNames  = (currentSpells || []).map(s => s.name).filter(Boolean);

    const advice = await AIService.call('spell_commentary', {
        spells: [...spellNames, ...itemNames]
    }) || null;

    if (advice && lootEl) {
        lootEl.textContent = `> ${advice}`;
        lootEl.style.color = '#556644';
    }
}
```

Call `fetchLootAdvice(lootItems, player.spells)` after `vsPopulateLoot()`.

---

## STEP 8 — WIRE EVERYTHING INTO VictoryScreen.show()

Find `VictoryScreen.show()` or equivalent. Replace the old population calls with:

```javascript
// Inside VictoryScreen.show() or equivalent, after screen is displayed:

// 1. Header
vsPopulateHeader(
    GameState.roomNum || 1,
    GameState.totalRooms || 10,
    { kills: GameState.runStats?.enemiesKilled, hp: player.hp, maxHp: player.maxHp, damageDealt: GameState.runStats?.damageDealt }
);

// 2. Loot (adapt lootItems to actual loot array format)
vsPopulateLoot(currentRoomLoot, player.equipped || player.gear);

// 3. Relics earned this room
vsPopulateRelics(currentRoomRelics || []);

// 4. Spell swap
vsPopulateSpellSwap(player.spells, offeredSpell);

// 5. XP
vsPopulateXP(player.xp, player.xpToLevel, player.level);

// 6. AI spell commentary (already in #vsAiComment from Block 4.1)
// 7. AI loot advice (new)
fetchLootAdvice(currentRoomLoot, player.spells);
```

---

## STEP 9 — "SWAP A SPELL?" INSTRUCTION TEXT FIX

Replace the static "SWAP A SPELL?" label with dynamic text:

- If offered spell is an attack: `◈ OFFERED ATTACK — CLICK A SLOT TO SWAP`
- If offered spell is defense: `◈ OFFERED DEFENSE — CLICK A SLOT TO SWAP`
- If offered spell is potion: `◈ OFFERED POTION — CLICK A SLOT TO SWAP`

```javascript
const typeLabel = offeredSpell?.type?.toUpperCase() || 'SPELL';
const instrEl = document.getElementById('vsSpellInstruction');
if (instrEl) instrEl.textContent =
    `◈ OFFERED ${typeLabel} — CLICK ANY SLOT TO REPLACE IT`;
```

---

## COMPLETION REPORT

1. Confirm equipment doll removed entirely
2. Confirm loot cards render with name, stat, slot, rarity badge, TAKE/DISCARD buttons
3. Confirm clicking loot card directly = take action (not just the button)
4. Confirm clicking a spell slot swaps it with offered spell — no SWAP button needed
5. Confirm offered spell card shows name, description, MP, CD, type-colored border
6. Confirm synergy delta hint appears on offered spell when relevant
7. Confirm AI loot advice appears in loot zone (non-blocking)
8. Confirm AI spell commentary still appears in header (from Block 4.1)
9. Confirm XP bar animates fill on screen open
10. Confirm relics display only when earned — no "NO RELICS THIS ROOM" placeholder
11. Confirm CONTINUE button pulses and is wired correctly
12. Confirm KEEP button disables after use
13. Confirm game loads and runs without errors
14. Screenshot description: what does the victory screen look like now?

---

*VICTORY-SCREEN-OVERHAUL — Claude Chat Architect Layer · 2026-03-26*
*After completion: commit with `feat: victory screen redesign — direct spell swap, loot cards, AI advice, cyberpunk theme`*

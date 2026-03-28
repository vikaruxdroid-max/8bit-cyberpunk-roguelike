# NEON DUNGEON — INSTRUCTION BLOCK: COMBAT-THEME
## Combat Positioning + Cyberpunk Visual Overhaul
### Claude Chat Architect Layer · 2026-03-26

---

> **SCOPE**: Fix sprite positioning, clean up top-right HUD cluster,
> fix combo counter double-render, and apply a full cyberpunk visual
> treatment to the combat screen — neon borders, scan lines, glow effects,
> terminal aesthetics. No combat logic changes.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. Where player sprite X/Y position is set for combat rendering
2. Where enemy sprite X/Y positions are calculated for combat (single enemy vs multiple)
3. Where the top-right minimap/cluster renders — the circular element and small text
4. Where the combo counter renders — confirm if there are two render locations
5. The canvas combat arena bounds — what X range is considered the "arena" (excluding HUD strips top and bottom)

Report all five before writing any code.

---

## FIX 1 — PLAYER SPRITE POSITIONING

**Problem**: Player is flush against the left wall, partially behind the background building.
**Fix**: Move player to 18% from left edge of arena, vertically grounded on the floor line.

```javascript
// Arena floor Y = canvas height - bottom HUD height - sprite height - 8px ground gap
// Arena left edge = 20px padding
// Player X target = canvas.width * 0.18

// Update player render position:
const playerRenderX = Math.floor(canvas.width * 0.18);
const playerRenderY = arenaFloorY - SPRITE_SIZE; // use actual floor Y variable
```

Also add a subtle ground shadow under the player sprite:
```javascript
function drawGroundShadow(ctx, x, y, w) {
    ctx.save();
    const gradient = ctx.createRadialGradient(x + w/2, y, 2, x + w/2, y, w * 0.7);
    gradient.addColorStop(0, 'rgba(0,255,255,0.15)');
    gradient.addColorStop(1, 'rgba(0,255,255,0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(x - w * 0.2, y - 4, w * 1.4, 10);
    ctx.restore();
}
// Call drawGroundShadow(ctx, playerRenderX, playerRenderY + SPRITE_SIZE, SPRITE_SIZE) after drawing player
```

---

## FIX 2 — ENEMY SPRITE POSITIONING

**Problem**: Enemies cluster too far right, partially off-screen.
**Fix**: Distribute enemies evenly across the RIGHT 60% of the arena (40%–95% of canvas width).

```javascript
// Enemy positioning formula:
function getEnemyRenderX(enemyIndex, totalEnemies, canvasWidth) {
    const arenaStart = canvasWidth * 0.40; // enemies start at 40% from left
    const arenaEnd   = canvasWidth * 0.92; // enemies end at 92% from left
    const arenaWidth = arenaEnd - arenaStart;
    
    if (totalEnemies === 1) {
        return arenaStart + arenaWidth * 0.45; // single enemy centered in right zone
    }
    if (totalEnemies === 2) {
        return arenaStart + arenaWidth * (enemyIndex === 0 ? 0.25 : 0.70);
    }
    if (totalEnemies === 3) {
        return arenaStart + arenaWidth * (enemyIndex * 0.38 + 0.05);
    }
    // 4+ enemies: evenly distributed
    const step = arenaWidth / (totalEnemies + 1);
    return arenaStart + step * (enemyIndex + 1);
}
```

Also add ground shadows under enemies matching player:
```javascript
// Call drawGroundShadow(ctx, enemyRenderX, enemyRenderY + SPRITE_SIZE, SPRITE_SIZE) for each enemy
// Use enemy accent color instead of cyan:
// gradient stop 0: rgba(R,G,B, 0.12) where RGB is the enemy's primary color
```

---

## FIX 3 — CLEAN UP TOP-RIGHT HUD CLUSTER

**Problem**: The top-right has a circular element and small unreadable text cluster.
**Fix**: Identify what each element is, remove non-essential ones, style the rest.

1. Find the circular element — identify its purpose (likely a timer, encounter indicator, or leftover artifact)
   - If it's purely decorative or a leftover: remove it
   - If it's functional: keep it but restyle to match HUD aesthetic

2. Find the small text cluster in top-right — likely room count minimap or encounter data
   - If it duplicates information already in the main HUD: remove it
   - If it's the minimap: replace with a cleaner version (see below)

3. Minimap replacement — if a minimap exists, render it as a simple dot-progress strip:
```javascript
function renderRoomProgress(ctx, currentRoom, totalRooms, x, y) {
    const dotSize   = 6;
    const dotGap    = 4;
    const totalW    = totalRooms * (dotSize + dotGap);
    
    ctx.save();
    for (let i = 0; i < totalRooms; i++) {
        const dx = x - totalW + i * (dotSize + dotGap);
        ctx.beginPath();
        ctx.arc(dx + dotSize/2, y, dotSize/2, 0, Math.PI * 2);
        
        if (i < currentRoom - 1) {
            ctx.fillStyle = '#334455'; // cleared
        } else if (i === currentRoom - 1) {
            ctx.fillStyle = '#00ffff'; // current
            ctx.shadowColor = '#00ffff';
            ctx.shadowBlur = 6;
        } else {
            ctx.fillStyle = '#111122'; // upcoming
        }
        ctx.fill();
        ctx.shadowBlur = 0;
    }
    ctx.restore();
}
// Render at top-right, below the credits line
```

---

## FIX 4 — COMBO COUNTER DEDUP

Find ALL locations where the combo counter is rendered. There should be exactly one.
Remove any duplicate render calls. Confirm the single remaining one uses the threshold >= 2.

---

## CYBERPUNK THEME PASS

Apply these visual enhancements to the combat screen. Add to the combat render pass
in the correct layer order.

### Theme 1 — Neon border frame around arena

```javascript
function renderArenaBorder(ctx, cw, ch, topHudH, bottomHudH) {
    const x = 0, y = topHudH;
    const w = cw, h = ch - topHudH - bottomHudH;
    const pulse = 0.7 + Math.sin(Date.now() / 1200) * 0.3;
    
    ctx.save();
    
    // Outer glow
    ctx.strokeStyle = `rgba(0,255,255,${pulse * 0.3})`;
    ctx.lineWidth = 3;
    ctx.shadowColor = '#00ffff';
    ctx.shadowBlur = 12;
    ctx.strokeRect(x + 1, y + 1, w - 2, h - 2);
    
    // Corner accents — L-shaped brackets at each corner
    const cornerLen = 20;
    ctx.strokeStyle = '#00ffff';
    ctx.lineWidth = 2;
    ctx.shadowBlur = 6;
    
    // Top-left
    ctx.beginPath(); ctx.moveTo(x, y + cornerLen); ctx.lineTo(x, y); ctx.lineTo(x + cornerLen, y); ctx.stroke();
    // Top-right
    ctx.beginPath(); ctx.moveTo(w - cornerLen, y); ctx.lineTo(w, y); ctx.lineTo(w, y + cornerLen); ctx.stroke();
    // Bottom-left
    ctx.beginPath(); ctx.moveTo(x, ch - bottomHudH - cornerLen); ctx.lineTo(x, ch - bottomHudH); ctx.lineTo(x + cornerLen, ch - bottomHudH); ctx.stroke();
    // Bottom-right
    ctx.beginPath(); ctx.moveTo(w - cornerLen, ch - bottomHudH); ctx.lineTo(w, ch - bottomHudH); ctx.lineTo(w, ch - bottomHudH - cornerLen); ctx.stroke();
    
    ctx.shadowBlur = 0;
    ctx.restore();
}
```

Call `renderArenaBorder` AFTER drawing the background, BEFORE sprites.
Use actual `topHudH` and `bottomHudH` values confirmed in pre-scan.

---

### Theme 2 — Scanline overlay

```javascript
function renderScanlines(ctx, cw, ch, topHudH, bottomHudH) {
    ctx.save();
    ctx.globalAlpha = 0.06;
    ctx.fillStyle = '#000000';
    for (let y = topHudH; y < ch - bottomHudH; y += 3) {
        ctx.fillRect(0, y, cw, 1);
    }
    ctx.restore();
}
```

Call AFTER all game elements, BEFORE spell bar and UI overlays.
Performance note: this is fast (simple fillRect loop), no concern.

---

### Theme 3 — Neon HUD separator lines

Replace the plain red border line on the top HUD with a glowing cyan version:

```javascript
// In renderCombatHUD(), replace the bottom border stroke with:
const hudSepPulse = 0.6 + Math.sin(Date.now() / 800) * 0.4;
ctx.strokeStyle = `rgba(0,255,255,${hudSepPulse})`;
ctx.lineWidth = 1;
ctx.shadowColor = '#00ffff';
ctx.shadowBlur = 8;
ctx.beginPath();
ctx.moveTo(0, hudH);
ctx.lineTo(cw, hudH);
ctx.stroke();
ctx.shadowBlur = 0;
```

Same treatment for the bottom HUD separator (above the bottom strip).

---

### Theme 4 — Player neon accent glow

After drawing the player sprite, add a subtle color accent glow at the player's feet:

```javascript
function renderPlayerGlow(ctx, x, y, spriteW, spriteH, accentColor) {
    ctx.save();
    const glowY = y + spriteH - 4;
    const gradient = ctx.createLinearGradient(x, glowY, x + spriteW, glowY);
    gradient.addColorStop(0, 'transparent');
    gradient.addColorStop(0.3, accentColor + '44');
    gradient.addColorStop(0.7, accentColor + '44');
    gradient.addColorStop(1, 'transparent');
    ctx.fillStyle = gradient;
    ctx.fillRect(x - 8, glowY, spriteW + 16, 8);
    ctx.restore();
}
// accentColor = player's selected accent color from character creation
// Use GameState.player.accentColor or equivalent
```

---

### Theme 5 — Spell bar cyberpunk styling

Enhance the spell bar background with a terminal panel look:

```javascript
// In renderSpellBar(), add BEFORE drawing individual slots:

// Dark terminal panel background
const barTotalW = 4 * 90 + 3 * 10 + 24; // slots + gaps + padding
const barX = cw/2 - barTotalW/2;
const barY = startY - 8;
const barH = slotH + 16;

ctx.save();
ctx.fillStyle = 'rgba(2,2,15,0.92)';
ctx.fillRect(barX, barY, barTotalW, barH);

// Top border — glowing cyan line
ctx.strokeStyle = '#00ffff';
ctx.lineWidth = 1;
ctx.shadowColor = '#00ffff';
ctx.shadowBlur = 6;
ctx.beginPath();
ctx.moveTo(barX, barY);
ctx.lineTo(barX + barTotalW, barY);
ctx.stroke();
ctx.shadowBlur = 0;

// Corner brackets on spell bar panel
const cl = 10;
ctx.strokeStyle = '#00ffff';
ctx.lineWidth = 1;
ctx.beginPath();
ctx.moveTo(barX, barY + cl); ctx.lineTo(barX, barY); ctx.lineTo(barX + cl, barY); ctx.stroke();
ctx.beginPath();
ctx.moveTo(barX + barTotalW - cl, barY); ctx.lineTo(barX + barTotalW, barY); ctx.lineTo(barX + barTotalW, barY + cl); ctx.stroke();

// "SPELLS" label left of bar
ctx.font = '6px "Press Start 2P"';
ctx.fillStyle = '#223344';
ctx.fillText('SPELLS', barX + 4, barY + 6);
ctx.restore();
```

---

### Theme 6 — Enemy HP bar cyberpunk styling

Enhance the enemy HP bar to feel more like a targeting reticle:

```javascript
// In renderEnemyHPBar(), add before drawing the bar:

// Targeting corner brackets around HP bar
const bx = barX - 4, by = barY - 2, bw = barW + 8, bh = barH + 4;
const tl = 6; // tick length
ctx.save();
ctx.strokeStyle = pct > 0.5 ? '#00ff41' : pct > 0.3 ? '#ffaa00' : '#ff4444';
ctx.lineWidth = 1;
// Top-left tick
ctx.beginPath(); ctx.moveTo(bx, by + tl); ctx.lineTo(bx, by); ctx.lineTo(bx + tl, by); ctx.stroke();
// Top-right tick
ctx.beginPath(); ctx.moveTo(bx + bw - tl, by); ctx.lineTo(bx + bw, by); ctx.lineTo(bx + bw, by + tl); ctx.stroke();
// Bottom-left tick
ctx.beginPath(); ctx.moveTo(bx, by + bh - tl); ctx.lineTo(bx, by + bh); ctx.lineTo(bx + tl, by + bh); ctx.stroke();
// Bottom-right tick
ctx.beginPath(); ctx.moveTo(bx + bw - tl, by + bh); ctx.lineTo(bx + bw, by + bh); ctx.lineTo(bx + bw, by + bh - tl); ctx.stroke();
ctx.restore();
```

---

### Theme 7 — Glitch flicker on low HP

When player HP is below 25%, add a subtle red glitch flicker to the arena border:

```javascript
// In renderArenaBorder(), add at the end:
const playerHpPct = GameState.player.hp / GameState.player.maxHp;
if (playerHpPct < 0.25) {
    const flicker = Math.random() > 0.85; // occasional random flicker
    if (flicker) {
        ctx.save();
        ctx.strokeStyle = 'rgba(255,50,50,0.4)';
        ctx.lineWidth = 2;
        ctx.strokeRect(x + 2, y + 2, w - 4, h - 4);
        ctx.restore();
    }
}
```

---

## COMPLETION REPORT

1. Confirm player renders at ~18% from left, not against the wall
2. Confirm enemies spread across 40–92% of canvas width
3. Confirm ground shadows under player and enemies
4. Confirm top-right cluster cleaned up — describe what remains
5. Confirm combo only renders once, threshold >= 2
6. Confirm arena neon border renders with pulsing cyan corners
7. Confirm scanlines visible over arena (subtle, not overpowering)
8. Confirm HUD separator lines glow cyan
9. Confirm spell bar has terminal panel background with top border line
10. Confirm enemy HP bars have targeting reticle brackets
11. Confirm low-HP red flicker activates below 25%
12. Confirm game loads and runs without errors
13. Screenshot description: what does the combat screen look like now?

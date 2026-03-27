# NEON DUNGEON — INSTRUCTION BLOCK 2.1
## MINI-GAMES SYSTEM (6 Types)
### Claude Chat Architect Layer · 2026-03-26
### Depends on: Phase 1 complete (commit 09a76b2)

---

> **SCOPE**: Add 6 canvas-rendered mini-games that appear between dungeon rooms.
> All mini-games render on Canvas — NO HTML/CSS overlays.
> Uses existing actual function names: DM.say(), Arena.spawnText(), GameState.

---

## PRE-IMPLEMENTATION SCAN

Locate and report:

1. Where room transitions are handled — the function/event that fires after a combat room clears and before the next room loads
2. The main canvas variable and 2D context variable names
3. How the current screen/state machine works — what variable controls which screen is active (e.g. `GameState.screen`, `currentScreen`, etc.)
4. Whether a `deltaTime` value is available in the main game loop — and what variable name it uses
5. The input/click handler pattern — how canvas click coordinates are captured during gameplay
6. Where `Math.random()` is called for room generation — to confirm seeded RNG hookup point for daily challenges later

Report all six before writing any code.

---

## STEP 1 — ADD MINI-GAME TRIGGER LOGIC

Find the room transition handler (pre-scan item 1). After a non-boss combat room resolves successfully, add:

```javascript
// After combat room victory, before loading next room:
function checkMiniGameTrigger() {
    const state = GameState; // use actual state object
    
    // Cannot trigger: in final room before boss, or last room was already a mini-game
    if (state.nextRoomIsBoss || state.lastRoomWasMiniGame) return false;
    
    // 25% base chance every 3rd room; 40% after zone boss defeated
    const roomsMod = state.roomsCleared % 3 === 0;
    if (!roomsMod) return false;
    
    const chance = state.zoneBossDefeated ? 0.40 : 0.25;
    return Math.random() < chance;
}
```

If `checkMiniGameTrigger()` returns true, set the game screen to `'minigame'` and call
`openMiniGame()` (defined in Step 2) before proceeding to next room load.

Add `lastRoomWasMiniGame: false` to game state initialization if not present.
Set it `true` after a mini-game triggers, `false` after any normal room.

---

## STEP 2 — MINI-GAME STATE OBJECT

Add to game state:

```javascript
miniGame: {
    active: false,
    type: null,           // 'hack'|'lock'|'code'|'reflex'|'hustle'|'memory'
    phase: 'intro',       // 'intro'|'playing'|'result'
    score: null,          // 'GOLD'|'SILVER'|'BRONZE'|'FAIL'
    timer: 0,             // ms remaining
    timerMax: 0,
    data: {},             // type-specific state (see each mini-game)
    introTimer: 1500,     // ms to show "MINI-GAME: [NAME]" splash before starting
    resultTimer: 2000,    // ms to show result before transitioning to secret room or next room
}
```

---

## STEP 3 — MINI-GAME ORCHESTRATOR

```javascript
// ============================================================
// MINI-GAME SYSTEM — Phase 2.1
// ============================================================

const MINIGAME_TYPES = ['hack', 'lock', 'code', 'reflex', 'hustle', 'memory'];

const MINIGAME_NAMES = {
    hack:   'HACKING TERMINAL',
    lock:   'LOCKPICK SEQUENCE',
    code:   'CODE BREAKER',
    reflex: 'NEURAL REFLEX TEST',
    hustle: 'MARKET HUSTLE',
    memory: 'DATA CORRUPTION'
};

function openMiniGame() {
    const mg = GameState.miniGame;
    mg.active = true;
    mg.type = MINIGAME_TYPES[Math.floor(Math.random() * MINIGAME_TYPES.length)];
    mg.phase = 'intro';
    mg.score = null;
    mg.introTimer = 1500;
    mg.resultTimer = 2000;
    mg.data = {};
    initMiniGameData(mg.type);
}

function initMiniGameData(type) {
    const mg = GameState.miniGame;
    switch (type) {
        case 'hack':
            mg.timer = 30000; mg.timerMax = 30000;
            mg.data = { grid: generateHackGrid(), revealed: new Array(16).fill(false), matched: new Array(16).fill(false), firstPick: null, lockout: false, lockoutTimer: 0 };
            break;
        case 'lock':
            mg.timer = 20000; mg.timerMax = 20000;
            mg.data = { tumblers: 3, solved: 0, angle: 0, sweepSpeed: 0.04, safeStart: Math.random() * Math.PI * 2, safeWidth: Math.PI / 6, failed: false };
            break;
        case 'code':
            mg.timer = 0; mg.timerMax = 0; // no time limit
            mg.data = { secret: generateCodeSecret(), guesses: [], currentInput: [], maxGuesses: 6 };
            break;
        case 'reflex':
            mg.timer = 0; mg.timerMax = 0;
            mg.data = { prompts: generateReflexPrompts(5), current: 0, score: 0, showAt: 0, windowMs: 800, promptVisible: false };
            break;
        case 'hustle':
            mg.timer = 0; mg.timerMax = 0;
            mg.data = { cups: [0,1,2], ballCup: 0, shuffles: 0, maxShuffles: 6 + GameState.zone * 2, shuffleTimer: 0, shuffleSpeed: 600, bet: 25, revealed: false, playerPick: null };
            break;
        case 'memory':
            const len = Math.min(7, 4 + Math.floor(GameState.zone / 2));
            mg.timer = 10000; mg.timerMax = 10000;
            mg.data = { sequence: generateMemorySequence(len), showing: true, showIndex: 0, showTimer: 500, input: [], symbols: ['⌘','⟁','⬡','◈','⊛','⌬','⊕','⋈'] };
            break;
    }
}

function updateMiniGame(deltaTime) {
    const mg = GameState.miniGame;
    if (!mg.active) return;

    if (mg.phase === 'intro') {
        mg.introTimer -= deltaTime;
        if (mg.introTimer <= 0) {
            mg.phase = 'playing';
        }
        return;
    }

    if (mg.phase === 'result') {
        mg.resultTimer -= deltaTime;
        if (mg.resultTimer <= 0) {
            closeMiniGame();
        }
        return;
    }

    // Tick active timer
    if (mg.timerMax > 0) {
        mg.timer = Math.max(0, mg.timer - deltaTime);
        if (mg.timer <= 0) {
            resolveMiniGame('timeout');
            return;
        }
    }

    // Type-specific update
    switch (mg.type) {
        case 'lock':   updateLockpick(deltaTime); break;
        case 'reflex': updateReflex(deltaTime); break;
        case 'hustle': updateHustle(deltaTime); break;
        case 'memory': updateMemory(deltaTime); break;
    }
}

function resolveMiniGame(reason) {
    const mg = GameState.miniGame;
    
    // Determine score tier
    if (reason === 'timeout' || reason === 'fail') {
        mg.score = 'FAIL';
    } else {
        mg.score = reason; // 'GOLD'|'SILVER'|'BRONZE' passed in by mini-game logic
    }

    mg.phase = 'result';
    DM.say(`MINI-GAME: ${MINIGAME_NAMES[mg.type]} — ${mg.score}`, 'system');

    // If not FAIL, flag that a secret room should follow
    if (mg.score !== 'FAIL') {
        GameState.pendingSecretRoom = mg.score; // picked up by Block 2.2
    }
}

function closeMiniGame() {
    const mg = GameState.miniGame;
    mg.active = false;
    GameState.lastRoomWasMiniGame = true;
    // Proceed to secret room if earned (handled by Block 2.2), else next normal room
    if (GameState.pendingSecretRoom) {
        openSecretRoom(GameState.pendingSecretRoom); // defined in Block 2.2 — stub if not yet implemented
    } else {
        loadNextRoom(); // use actual next room loading function
    }
}
```

---

## STEP 4 — MINI-GAME 1: HACKING (Pattern Match)

```javascript
function generateHackGrid() {
    const symbols = ['⌘','⟁','⬡','◈','⊛','⌬','⊕','⋈'];
    const pairs = [...symbols, ...symbols];
    // Fisher-Yates shuffle
    for (let i = pairs.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [pairs[i], pairs[j]] = [pairs[j], pairs[i]];
    }
    return pairs;
}

function handleHackClick(cellIndex) {
    const d = GameState.miniGame.data;
    if (d.lockout || d.matched[cellIndex] || d.revealed[cellIndex]) return;

    d.revealed[cellIndex] = true;

    if (d.firstPick === null) {
        d.firstPick = cellIndex;
    } else {
        const a = d.firstPick;
        const b = cellIndex;
        if (d.grid[a] === d.grid[b]) {
            d.matched[a] = d.matched[b] = true;
            d.firstPick = null;
            if (d.matched.every(m => m)) {
                // All matched — score by time remaining
                const pct = GameState.miniGame.timer / GameState.miniGame.timerMax;
                resolveMiniGame(pct > 0.5 ? 'GOLD' : pct > 0.17 ? 'SILVER' : 'BRONZE');
            }
        } else {
            d.lockout = true;
            d.lockoutTimer = 800;
            // Unreveal after lockout
        }
        d.firstPick = null;
    }
}

// In updateMiniGame, add lockout timer:
// if (mg.type === 'hack' && mg.data.lockout) {
//     mg.data.lockoutTimer -= deltaTime;
//     if (mg.data.lockoutTimer <= 0) {
//         mg.data.lockout = false;
//         mg.data.revealed = mg.data.revealed.map((r, i) => mg.data.matched[i] ? r : false);
//     }
// }

function renderHackGame(ctx) {
    const mg = GameState.miniGame;
    const d = mg.data;
    const cw = canvas.width, ch = canvas.height;
    const cellSize = 56;
    const cols = 4, rows = 4;
    const gridW = cols * cellSize + (cols - 1) * 8;
    const gridH = rows * cellSize + (rows - 1) * 8;
    const startX = cw / 2 - gridW / 2;
    const startY = ch / 2 - gridH / 2;

    for (let i = 0; i < 16; i++) {
        const col = i % cols;
        const row = Math.floor(i / cols);
        const x = startX + col * (cellSize + 8);
        const y = startY + row * (cellSize + 8);

        ctx.save();
        if (d.matched[i]) {
            ctx.fillStyle = '#003300';
            ctx.strokeStyle = '#00ff41';
        } else if (d.revealed[i]) {
            ctx.fillStyle = '#1a001a';
            ctx.strokeStyle = '#ff00ff';
        } else {
            ctx.fillStyle = '#0a0a1a';
            ctx.strokeStyle = '#00ffff';
        }
        ctx.lineWidth = 1;
        ctx.fillRect(x, y, cellSize, cellSize);
        ctx.strokeRect(x, y, cellSize, cellSize);

        if (d.revealed[i] || d.matched[i]) {
            ctx.font = '20px "Share Tech Mono"';
            ctx.fillStyle = d.matched[i] ? '#00ff41' : '#ff00ff';
            ctx.textAlign = 'center';
            ctx.fillText(d.grid[i], x + cellSize / 2, y + cellSize / 2 + 7);
            ctx.textAlign = 'left';
        } else {
            ctx.font = '10px "Press Start 2P"';
            ctx.fillStyle = '#1a3a3a';
            ctx.textAlign = 'center';
            ctx.fillText('?', x + cellSize / 2, y + cellSize / 2 + 4);
            ctx.textAlign = 'left';
        }
        ctx.restore();
    }
}
```

---

## STEP 5 — MINI-GAME 2: LOCKPICK (Timing)

```javascript
function updateLockpick(deltaTime) {
    const d = GameState.miniGame.data;
    d.angle = (d.angle + d.sweepSpeed * deltaTime / 16) % (Math.PI * 2);
}

function handleLockpickClick() {
    const d = GameState.miniGame.data;
    // Check if sweep angle is within safe zone
    let diff = Math.abs(d.angle - d.safeStart);
    if (diff > Math.PI) diff = Math.PI * 2 - diff;

    if (diff < d.safeWidth / 2) {
        d.solved++;
        DM.say(`TUMBLER ${d.solved} LOCKED`, 'system');
        if (d.solved >= d.tumblers) {
            resolveMiniGame('GOLD');
            return;
        }
        // Shrink safe zone for next tumbler
        d.safeWidth = Math.max(0.15, d.safeWidth - 0.05);
        d.safeStart = Math.random() * Math.PI * 2;
        d.sweepSpeed += 0.005;
        // Give 3 seconds per remaining tumbler
        GameState.miniGame.timer = 20000 - (d.solved * 5000);
    } else {
        // Miss — reset this tumbler, -3 seconds
        GameState.miniGame.timer = Math.max(1000, GameState.miniGame.timer - 3000);
        DM.say('SLIP! TUMBLER RESET', 'warning');
        d.safeStart = Math.random() * Math.PI * 2;
    }
}

function renderLockpick(ctx) {
    const d = GameState.miniGame.data;
    const cw = canvas.width, ch = canvas.height;
    const cx = cw / 2, cy = ch / 2;
    const r = 120;

    // Outer ring
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.strokeStyle = '#333355';
    ctx.lineWidth = 12;
    ctx.stroke();

    // Safe zone arc
    ctx.beginPath();
    ctx.arc(cx, cy, r, d.safeStart - d.safeWidth / 2, d.safeStart + d.safeWidth / 2);
    ctx.strokeStyle = '#00ff41';
    ctx.lineWidth = 12;
    ctx.stroke();

    // Sweep indicator
    const indX = cx + Math.cos(d.angle) * r;
    const indY = cy + Math.sin(d.angle) * r;
    ctx.beginPath();
    ctx.arc(indX, indY, 8, 0, Math.PI * 2);
    ctx.fillStyle = '#ff00ff';
    ctx.shadowColor = '#ff00ff';
    ctx.shadowBlur = 10;
    ctx.fill();
    ctx.shadowBlur = 0;

    // Tumbler status
    ctx.font = '9px "Press Start 2P"';
    ctx.fillStyle = '#00ffff';
    ctx.textAlign = 'center';
    ctx.fillText(`TUMBLER ${d.solved + 1} / ${d.tumblers}`, cx, cy + r + 30);
    ctx.textAlign = 'left';
    ctx.restore();
}
```

---

## STEP 6 — MINI-GAME 3: CODE BREAKER (Wordle-Style)

```javascript
function generateCodeSecret() {
    return [0,1,2,3].map(() => Math.floor(Math.random() * 10));
}

function handleCodeInput(digit) {
    const d = GameState.miniGame.data;
    if (d.currentInput.length < 4) d.currentInput.push(digit);
}

function handleCodeSubmit() {
    const d = GameState.miniGame.data;
    if (d.currentInput.length < 4) return;

    const guess = [...d.currentInput];
    const result = guess.map((g, i) => {
        if (g === d.secret[i]) return 'correct';
        if (d.secret.includes(g)) return 'misplaced';
        return 'wrong';
    });

    d.guesses.push({ digits: guess, result });
    d.currentInput = [];

    if (result.every(r => r === 'correct')) {
        const guessCount = d.guesses.length;
        resolveMiniGame(guessCount <= 2 ? 'GOLD' : guessCount <= 4 ? 'SILVER' : 'BRONZE');
        return;
    }

    if (d.guesses.length >= d.maxGuesses) {
        resolveMiniGame('FAIL');
    }
}

function handleCodeDelete() {
    GameState.miniGame.data.currentInput.pop();
}

function renderCodeBreaker(ctx) {
    const d = GameState.miniGame.data;
    const cw = canvas.width, ch = canvas.height;
    const cellW = 50, cellH = 50, gap = 10;
    const rowH = cellH + gap;
    const gridX = cw / 2 - (cellW * 4 + gap * 3) / 2;
    const gridY = 120;

    // Past guesses
    d.guesses.forEach((g, row) => {
        g.digits.forEach((digit, col) => {
            const x = gridX + col * (cellW + gap);
            const y = gridY + row * rowH;
            const color = g.result[col] === 'correct' ? '#00ff41' : g.result[col] === 'misplaced' ? '#ffff00' : '#333355';
            ctx.save();
            ctx.fillStyle = color;
            ctx.fillRect(x, y, cellW, cellH);
            ctx.font = '16px "Press Start 2P"';
            ctx.fillStyle = '#000000';
            ctx.textAlign = 'center';
            ctx.fillText(digit, x + cellW / 2, y + cellH / 2 + 6);
            ctx.textAlign = 'left';
            ctx.restore();
        });
    });

    // Current input row
    const curRow = d.guesses.length;
    [0,1,2,3].forEach((col) => {
        const x = gridX + col * (cellW + gap);
        const y = gridY + curRow * rowH;
        ctx.save();
        ctx.fillStyle = '#0a0a1a';
        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 1;
        ctx.fillRect(x, y, cellW, cellH);
        ctx.strokeRect(x, y, cellW, cellH);
        if (d.currentInput[col] !== undefined) {
            ctx.font = '16px "Press Start 2P"';
            ctx.fillStyle = '#00ffff';
            ctx.textAlign = 'center';
            ctx.fillText(d.currentInput[col], x + cellW / 2, y + cellH / 2 + 6);
            ctx.textAlign = 'left';
        }
        ctx.restore();
    });

    // Number buttons 0-9 + DELETE + SUBMIT
    const btnY = gridY + 7 * rowH + 20;
    const btnW = 44, btnH = 36;
    for (let i = 0; i < 10; i++) {
        const x = gridX + (i % 5) * (btnW + 8);
        const y = btnY + Math.floor(i / 5) * (btnH + 8);
        ctx.save();
        ctx.fillStyle = '#111122';
        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 1;
        ctx.fillRect(x, y, btnW, btnH);
        ctx.strokeRect(x, y, btnW, btnH);
        ctx.font = '11px "Press Start 2P"';
        ctx.fillStyle = '#00ffff';
        ctx.textAlign = 'center';
        ctx.fillText(i, x + btnW / 2, y + btnH / 2 + 4);
        ctx.textAlign = 'left';
        ctx.restore();
    }
}
```

---

## STEP 7 — MINI-GAME 4: NEURAL REFLEX (Reaction)

```javascript
function generateReflexPrompts(count) {
    const options = ['UP','DOWN','LEFT','RIGHT','A','B'];
    return Array.from({ length: count }, () => options[Math.floor(Math.random() * options.length)]);
}

function updateReflex(deltaTime) {
    const d = GameState.miniGame.data;
    if (d.current >= d.prompts.length) return;

    if (!d.promptVisible) {
        d.showAt -= deltaTime;
        if (d.showAt <= 0) {
            d.promptVisible = true;
            d.showAt = d.windowMs;
        }
    } else {
        d.showAt -= deltaTime;
        if (d.showAt <= 0) {
            // Missed — no input in time
            d.promptVisible = false;
            d.current++;
            d.showAt = 400; // gap before next
            if (d.current >= d.prompts.length) finishReflex();
        }
    }
}

function handleReflexInput(label) {
    const d = GameState.miniGame.data;
    if (!d.promptVisible || d.current >= d.prompts.length) return;

    if (label === d.prompts[d.current]) {
        const reactionTime = d.windowMs - d.showAt;
        if (reactionTime < 600) d.score++;
        else if (reactionTime < d.windowMs) d.score += 0.5;
    }
    d.promptVisible = false;
    d.current++;
    d.showAt = 400;
    if (d.current >= d.prompts.length) finishReflex();
}

function finishReflex() {
    const d = GameState.miniGame.data;
    const pct = d.score / d.prompts.length;
    resolveMiniGame(pct >= 0.8 ? 'GOLD' : pct >= 0.5 ? 'SILVER' : pct > 0 ? 'BRONZE' : 'FAIL');
}

function renderReflex(ctx) {
    const d = GameState.miniGame.data;
    const cw = canvas.width, ch = canvas.height;
    if (!d.promptVisible || d.current >= d.prompts.length) return;

    const prompt = d.prompts[d.current];
    ctx.save();
    ctx.font = '32px "Press Start 2P"';
    ctx.fillStyle = '#ff00ff';
    ctx.shadowColor = '#ff00ff';
    ctx.shadowBlur = 20;
    ctx.textAlign = 'center';
    ctx.fillText(prompt, cw / 2, ch / 2);
    ctx.shadowBlur = 0;
    ctx.textAlign = 'left';
    ctx.restore();

    // On-screen buttons
    const btns = ['UP','DOWN','LEFT','RIGHT','A','B'];
    btns.forEach((label, i) => {
        const x = 80 + (i % 3) * 120;
        const y = ch - 120 + Math.floor(i / 3) * 50;
        ctx.save();
        ctx.fillStyle = label === prompt ? '#1a001a' : '#0a0a1a';
        ctx.strokeStyle = label === prompt ? '#ff00ff' : '#333355';
        ctx.lineWidth = 1;
        ctx.fillRect(x, y, 100, 36);
        ctx.strokeRect(x, y, 100, 36);
        ctx.font = '8px "Press Start 2P"';
        ctx.fillStyle = '#aaaaaa';
        ctx.textAlign = 'center';
        ctx.fillText(label, x + 50, y + 22);
        ctx.textAlign = 'left';
        ctx.restore();
    });
}
```

---

## STEP 8 — MINI-GAME 5: MARKET HUSTLE (Shell Game)

```javascript
function updateHustle(deltaTime) {
    const d = GameState.miniGame.data;
    if (d.shuffles >= d.maxShuffles || d.revealed) return;

    d.shuffleTimer -= deltaTime;
    if (d.shuffleTimer <= 0) {
        // Swap two random cups
        const a = Math.floor(Math.random() * 3);
        let b = Math.floor(Math.random() * 2);
        if (b >= a) b++;
        [d.cups[a], d.cups[b]] = [d.cups[b], d.cups[a]];
        d.shuffles++;
        d.shuffleTimer = d.shuffleSpeed;
        d.shuffleSpeed = Math.max(200, d.shuffleSpeed - 30);
    }
}

function handleHustleClick(cupIndex) {
    const d = GameState.miniGame.data;
    if (d.shuffles < d.maxShuffles || d.revealed) return;

    d.playerPick = cupIndex;
    d.revealed = true;
    const won = d.cups[cupIndex] === d.ballCup;
    if (won) {
        GameState.player.gold = (GameState.player.gold || 0) + d.bet * 2; // use actual gold property
        resolveMiniGame('GOLD');
    } else {
        GameState.player.gold = Math.max(0, (GameState.player.gold || 0) - d.bet);
        resolveMiniGame('BRONZE'); // still gets a secret room but lower tier
    }
}

function renderHustle(ctx) {
    const d = GameState.miniGame.data;
    const cw = canvas.width, ch = canvas.height;
    const cupW = 70, cupH = 90;
    const positions = [cw/2 - 160, cw/2 - 35, cw/2 + 90];

    positions.forEach((x, i) => {
        const isRevealed = d.revealed;
        const hasBall = d.cups[i] === d.ballCup;
        const y = ch / 2 - cupH / 2;

        ctx.save();
        ctx.fillStyle = d.playerPick === i ? '#1a1a00' : '#0a0a1a';
        ctx.strokeStyle = d.playerPick === i ? '#ffd700' : '#00ffff';
        ctx.lineWidth = 1.5;
        ctx.fillRect(x, y, cupW, cupH);
        ctx.strokeRect(x, y, cupW, cupH);

        ctx.font = '8px "Press Start 2P"';
        ctx.fillStyle = '#aaaaaa';
        ctx.textAlign = 'center';
        ctx.fillText(`CUP ${i+1}`, x + cupW / 2, y + cupH + 20);

        if (isRevealed && hasBall) {
            ctx.font = '24px "Share Tech Mono"';
            ctx.fillStyle = '#ffd700';
            ctx.fillText('●', x + cupW / 2, y + cupH / 2 + 8);
        }
        ctx.textAlign = 'left';
        ctx.restore();
    });

    // Bet display
    if (!d.revealed) {
        ctx.font = '8px "Press Start 2P"';
        ctx.fillStyle = '#ffd700';
        ctx.textAlign = 'center';
        ctx.fillText(`BET: ${d.bet} CR`, cw / 2, ch / 2 + cupH / 2 + 50);
        if (d.shuffles >= d.maxShuffles) {
            ctx.fillStyle = '#00ffff';
            ctx.fillText('PICK A CUP', cw / 2, ch / 2 + cupH / 2 + 70);
        }
        ctx.textAlign = 'left';
    }
}
```

---

## STEP 9 — MINI-GAME 6: DATA CORRUPTION (Memory Sequence)

```javascript
function generateMemorySequence(len) {
    const symbols = ['⌘','⟁','⬡','◈','⊛','⌬','⊕','⋈'];
    return Array.from({ length: len }, () => symbols[Math.floor(Math.random() * symbols.length)]);
}

function updateMemory(deltaTime) {
    const d = GameState.miniGame.data;
    if (!d.showing) return;

    d.showTimer -= deltaTime;
    if (d.showTimer <= 0) {
        d.showIndex++;
        if (d.showIndex >= d.sequence.length) {
            d.showing = false;
            GameState.miniGame.timer = 10000; // start countdown for input
            GameState.miniGame.timerMax = 10000;
        } else {
            d.showTimer = d.showIndex < d.sequence.length ? 500 : 200; // symbol + gap
        }
    }
}

function handleMemoryInput(symbol) {
    const d = GameState.miniGame.data;
    if (d.showing) return;
    d.input.push(symbol);

    const idx = d.input.length - 1;
    if (d.input[idx] !== d.sequence[idx]) {
        resolveMiniGame('FAIL');
        return;
    }
    if (d.input.length === d.sequence.length) {
        const timeBonus = GameState.miniGame.timer / GameState.miniGame.timerMax;
        resolveMiniGame(timeBonus > 0.6 ? 'GOLD' : timeBonus > 0.3 ? 'SILVER' : 'BRONZE');
    }
}

function renderMemory(ctx) {
    const d = GameState.miniGame.data;
    const cw = canvas.width, ch = canvas.height;
    const symbols = d.symbols;
    const btnSize = 70, gap = 12;
    const cols = 4;
    const gridW = cols * btnSize + (cols - 1) * gap;
    const gridX = cw / 2 - gridW / 2;
    const gridY = ch - 200;

    // Show sequence symbol during showing phase
    if (d.showing && d.showIndex < d.sequence.length) {
        ctx.save();
        ctx.font = '48px "Share Tech Mono"';
        ctx.fillStyle = '#ff00ff';
        ctx.shadowColor = '#ff00ff';
        ctx.shadowBlur = 20;
        ctx.textAlign = 'center';
        ctx.fillText(d.sequence[d.showIndex], cw / 2, ch / 2);
        ctx.shadowBlur = 0;
        ctx.textAlign = 'left';
        ctx.restore();
    }

    if (!d.showing) {
        // Symbol grid for input
        symbols.forEach((sym, i) => {
            const col = i % cols;
            const row = Math.floor(i / cols);
            const x = gridX + col * (btnSize + gap);
            const y = gridY + row * (btnSize + gap);

            ctx.save();
            ctx.fillStyle = '#0a0a1a';
            ctx.strokeStyle = '#00ffff';
            ctx.lineWidth = 1;
            ctx.fillRect(x, y, btnSize, btnSize);
            ctx.strokeRect(x, y, btnSize, btnSize);
            ctx.font = '22px "Share Tech Mono"';
            ctx.fillStyle = '#00ffff';
            ctx.textAlign = 'center';
            ctx.fillText(sym, x + btnSize / 2, y + btnSize / 2 + 8);
            ctx.textAlign = 'left';
            ctx.restore();
        });

        // Progress dots
        d.sequence.forEach((_, i) => {
            const filled = i < d.input.length;
            ctx.save();
            ctx.beginPath();
            ctx.arc(cw / 2 - (d.sequence.length * 16) / 2 + i * 16 + 8, 80, 5, 0, Math.PI * 2);
            ctx.fillStyle = filled ? '#00ff41' : '#333355';
            ctx.fill();
            ctx.restore();
        });
    }
}
```

---

## STEP 10 — MASTER RENDER DISPATCHER

Find where the main canvas render pass runs. Add mini-game rendering as a full-screen override:

```javascript
// In main render function, BEFORE normal game rendering:
if (GameState.miniGame && GameState.miniGame.active) {
    renderMiniGame(ctx);
    return; // skip normal game rendering while mini-game is active
}
```

Add the dispatcher:

```javascript
function renderMiniGame(ctx) {
    const mg = GameState.miniGame;
    const cw = canvas.width, ch = canvas.height;

    // Background
    ctx.fillStyle = '#050510';
    ctx.fillRect(0, 0, cw, ch);

    // CRT scanline overlay
    for (let y = 0; y < ch; y += 4) {
        ctx.fillStyle = 'rgba(0,0,0,0.15)';
        ctx.fillRect(0, y, cw, 2);
    }

    if (mg.phase === 'intro') {
        ctx.save();
        ctx.font = '12px "Press Start 2P"';
        ctx.fillStyle = '#00ffff';
        ctx.textAlign = 'center';
        ctx.fillText('MINI-GAME', cw / 2, ch / 2 - 20);
        ctx.fillStyle = '#ff00ff';
        ctx.font = '9px "Press Start 2P"';
        ctx.fillText(MINIGAME_NAMES[mg.type], cw / 2, ch / 2 + 10);
        ctx.textAlign = 'left';
        ctx.restore();
        return;
    }

    if (mg.phase === 'result') {
        renderMiniGameResult(ctx, mg);
        return;
    }

    // Header — mini-game name + timer
    ctx.save();
    ctx.font = '8px "Press Start 2P"';
    ctx.fillStyle = '#555577';
    ctx.fillText(MINIGAME_NAMES[mg.type], 20, 30);
    if (mg.timerMax > 0) {
        const pct = mg.timer / mg.timerMax;
        const timerColor = pct > 0.5 ? '#00ffff' : pct > 0.25 ? '#ff8800' : '#ff4444';
        ctx.fillStyle = timerColor;
        ctx.textAlign = 'right';
        ctx.fillText(`${Math.ceil(mg.timer / 1000)}s`, cw - 20, 30);
        ctx.textAlign = 'left';
        // Timer bar
        ctx.fillStyle = timerColor;
        ctx.fillRect(20, 38, (cw - 40) * pct, 3);
    }
    ctx.restore();

    // Type-specific render
    switch (mg.type) {
        case 'hack':   renderHackGame(ctx); break;
        case 'lock':   renderLockpick(ctx); break;
        case 'code':   renderCodeBreaker(ctx); break;
        case 'reflex': renderReflex(ctx); break;
        case 'hustle': renderHustle(ctx); break;
        case 'memory': renderMemory(ctx); break;
    }
}

function renderMiniGameResult(ctx, mg) {
    const cw = canvas.width, ch = canvas.height;
    const scoreColors = { GOLD: '#ffd700', SILVER: '#cccccc', BRONZE: '#cd7f32', FAIL: '#ff4444' };
    const color = scoreColors[mg.score] || '#ffffff';

    ctx.save();
    ctx.font = '14px "Press Start 2P"';
    ctx.fillStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur = 16;
    ctx.textAlign = 'center';
    ctx.fillText(mg.score, cw / 2, ch / 2 - 10);
    ctx.shadowBlur = 0;
    ctx.font = '7px "Press Start 2P"';
    ctx.fillStyle = '#aaaaaa';
    if (mg.score !== 'FAIL') {
        ctx.fillText('SECRET ROOM UNLOCKED', cw / 2, ch / 2 + 20);
    } else {
        ctx.fillText('NO SECRET ROOM', cw / 2, ch / 2 + 20);
    }
    ctx.textAlign = 'left';
    ctx.restore();
}
```

---

## STEP 11 — HOOK CLICK HANDLER

In the canvas click handler (where spell clicks, dodge, etc. are handled), add at the top:

```javascript
if (GameState.miniGame && GameState.miniGame.active && GameState.miniGame.phase === 'playing') {
    handleMiniGameClick(event, clickX, clickY); // clickX/Y = canvas-relative coordinates
    return;
}
```

Add dispatcher:

```javascript
function handleMiniGameClick(event, x, y) {
    const mg = GameState.miniGame;
    switch (mg.type) {
        case 'hack':
            // Hit-test grid cells
            // (implement cell index calculation from x/y using same coords as renderHackGame)
            const cellIndex = getMiniGameHackCell(x, y);
            if (cellIndex !== null) handleHackClick(cellIndex);
            break;
        case 'lock':
            handleLockpickClick();
            break;
        case 'code':
            const codeBtn = getMiniGameCodeBtn(x, y);
            if (codeBtn === 'DELETE') handleCodeDelete();
            else if (codeBtn === 'SUBMIT') handleCodeSubmit();
            else if (codeBtn !== null) handleCodeInput(codeBtn);
            break;
        case 'reflex':
            const reflexBtn = getMiniGameReflexBtn(x, y);
            if (reflexBtn) handleReflexInput(reflexBtn);
            break;
        case 'hustle':
            const cupIndex = getMiniGameHustleCup(x, y);
            if (cupIndex !== null) handleHustleClick(cupIndex);
            break;
        case 'memory':
            const memSym = getMiniGameMemorySymbol(x, y);
            if (memSym) handleMemoryInput(memSym);
            break;
    }
}
```

Implement each `getMiniGame*` hit-test function using the same coordinate math used in the
corresponding render function (reuse constants like `gridX`, `gridY`, `cellSize`, etc.).

---

## STEP 12 — ALSO UPDATE GAME LOOP

In the main game update loop (where `deltaTime` is used), add:

```javascript
if (GameState.miniGame && GameState.miniGame.active) {
    updateMiniGame(deltaTime);
}
```

---

## COMPLETION REPORT FOR BLOCK 2.1

1. Exact name of the room transition function that was hooked
2. Confirm all 6 mini-game types render without errors
3. Confirm trigger logic fires at correct chance (25%/40%)
4. Confirm mini-game result correctly sets `GameState.pendingSecretRoom`
5. Confirm `lastRoomWasMiniGame` prevents back-to-back triggers
6. Any substitutions made (gold property name, next room function name, etc.)
7. Any mini-game type that could NOT be fully implemented and why
8. Confirm game loads and runs without errors

---

*Block 2.1 — Claude Chat Architect Layer · 2026-03-26*
*Execute after Phase 1 is complete and commit 09a76b2 is on master.*
*Block 2.2 (Secret Rooms) depends on `GameState.pendingSecretRoom` set by this block.*

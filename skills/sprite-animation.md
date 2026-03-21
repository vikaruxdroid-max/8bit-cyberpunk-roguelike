# SKILL: sprite-animation

## Purpose
Define all sprite animation patterns, timing, and rendering rules
for player and enemy sprites in 8bit_cyberpunk_FIXED.html.

## Sprite Rendering Rules
- Player sprite: left 25% of arena, vertically centered
- Enemy sprite: right 25% of arena, vertically centered, mirrored (scaleX -1)
- Both sprites: 2x scale minimum at 1920x1080
- HP bar: floats 10px above sprite top, same width as sprite
- Name label: above HP bar, centered, bold neon font
- Status icons: below sprite, horizontal row, 24px each
- Never let sprites overlap center of arena
- Sprites must remain visible throughout entire combat session

## Animation States

### IDLE (always active when no other animation playing)
- Subtle vertical bob: translateY(0) → translateY(-4px) → translateY(0)
- Duration: 800ms, infinite loop, ease-in-out
- Both player and enemy bob independently (offset timing by 200ms)

### ATTACK
- Sprite lunges toward opponent: translateX(+60px) for player,
  translateX(-60px) for enemy
- Forward: 400ms ease-out
- Hold at extended position: 100ms
- Snap back: 300ms ease-in
- Total: 800ms

### HIT RECEIVED
- Flash white: filter brightness(10) for 100ms
- Jolt backward: opposite direction of attack, translateX(-20px)
- Return: 400ms ease-out
- Total: 500ms
- Runs simultaneously with attacker's attack animation

### DEATH
- Flash white 3 times: 150ms on, 150ms off x3
- Dissolve from bottom up: clipPath or opacity gradient rising upward
- Particle explosion at moment of last flash
- Duration: 1500ms total
- Sprite hidden after animation completes

### SKILL CAST
- Wind-up glow: drop-shadow in skill color, pulsing, 600ms
- Cast release: quick scale up (1.2x) then back (200ms)
- Projectile or effect animates toward target
- Total wind-up + cast: 800ms

### BLOCK
- Blue shield bubble: radial gradient circle around sprite
- Bubble appears in 200ms, holds while blocking, fades in 300ms
- Sprite slightly dims behind bubble

### LEVEL UP
- Gold particle burst upward from sprite
- Sprite flashes gold 3 times
- "LEVEL UP!" text floats upward above sprite
- Duration: 1200ms

## Particle System Rules
- All particles: managed in a separate effects canvas (z-index 30)
- Canvas: pointer-events none always
- Particle object: {x, y, vx, vy, life, maxLife, color, size, alpha}
- Update loop: runs at requestAnimationFrame, independent of game loop
- Particle count limits:
  - Normal hit: 20-30 particles
  - Critical hit: 40-50 particles
  - Death explosion: 80-100 particles
  - Skill effect: 30-40 particles
  - Status orbit: 8-12 particles per status

## Damage Number Rules
- Float upward from hit point: translateY(-80px) over 1500ms
- Fade out: opacity 1 → 0 in last 500ms of float
- Horizontal drift: random -20px to +20px
- Font size scales with damage:
  - Under 20 damage: 1rem
  - 20-50 damage: 1.4rem
  - 50-100 damage: 1.8rem
  - Over 100 damage: 2.4rem bold
- Colors:
  - Physical hit: #ffffff
  - Skill hit: #00ffff
  - Critical: #ffd700 bold
  - Heal: #00ff41
  - Status tick: #ff00ff
  - Miss: #888888 italic

# SKILL: zone-background

## Purpose
Define canvas animation patterns and visual rules for each
zone's combat arena background in 8bit_cyberpunk_FIXED.html.

## General Canvas Rules
- Effects canvas: always position absolute over arena
- Always pointer-events: none
- Always same dimensions as arena container
- Always runs its own requestAnimationFrame loop
- Never block sprite rendering or UI clicks
- Background layers render in this order:
  1. Sky/atmosphere layer
  2. Architecture/structure layer
  3. Ground/floor layer
  4. Ambient particle layer
  5. Sprites (not on canvas)
  6. Hit effects canvas (top layer)

## Zone Backgrounds

### NEON NEXUS (cyan #00ffff theme)
- Scrolling perspective grid floor in cyan
- Holographic billboard rectangles in background, slow color cycle
- Floating neon hex particles drifting slowly
- Hot pink and lime green Splatoon-style ink splatter decorations on walls
- Busy city atmosphere — many small light points in far background
- Arena floor reflects active combat effect colors

### VOID SECTOR (purple #7b00ff theme)
- Deep purple/black atmosphere
- Corrupted data streams: vertical falling characters in dark purple
- Glitching geometry: background elements occasionally offset and snap back
- Reality tear effect: random thin horizontal lines flash white
- Screen glitch flash: full screen briefly desaturates every 8-12 seconds
- Oppressive and unstable feel

### CORPORATE STRIP (cold blue #0066ff theme)
- Clean cold blue/silver color scheme
- Corporate logo rectangles on back wall, slow pulse
- Sterile fluorescent flicker effect on ceiling lights
- Security camera icons in upper corners, slow pan animation
- Grid pattern on floor — precise and mechanical
- Professional but threatening atmosphere

### RUST MARKET (orange #ff6600 theme)
- Warm orange/amber lighting
- Fire barrel: flickering orange light source bottom-left
- Market stall silhouettes in background
- Graffiti neon tag shapes on walls in multiple colors
- Floating ember particles rising slowly
- Chaotic busy atmosphere with many small color points

### THE UNDERNET (toxic green #00ff41 theme)
- Dark background, toxic green ambient light
- Dripping liquid: vertical green drops falling from top edge
- Bio-mechanical pipe structures: thick horizontal pipes in background
- Pulsing wall: background slowly breathes in and out (scale oscillation)
- Toxic spore particles floating upward slowly
- Oppressive underground claustrophobic feel

### GHOST DISTRICT (gray/white theme)
- Dark gray atmosphere
- Ghostly afterimage effect: faint duplicates of sprites offset slightly
- Abandoned building silhouettes: dark rectangles in background
- Wind particles: white dots drifting left to right slowly
- Occasional white flash suggesting distant lightning
- Lonely and haunting atmosphere

### DATA HIGHWAY (electric blue #00e5ff theme)
- Electric blue high-energy atmosphere
- Data packet particles streaming horizontally at high speed (left to right)
- Speed line effect: radial lines from center suggesting fast movement
- Clean geometric hexagon pattern in background
- Pulse wave: expanding circles from center at regular intervals
- High energy and fast feel

### THE CORE — BOSS CHAMBER (red/gold theme)
- Red/gold dramatic color scheme
- Massive architectural scale suggested by large dark columns
- Dramatic upward lighting: gradient from red at bottom to black at top
- Particle intensity at maximum — constant heavy particle rain
- Boss phase 2: arena tints darker, particle color shifts to magenta
- Boss phase 3: arena pulses red rapidly, all particles turn white
- Screen edge vignette in deep red throughout

## Ambient Effects All Zones Share
- Low HP warning (player below 25%): red vignette pulse on screen edges
- Status effect environment: subtle color tint matching active status
- Combo 7+: golden screen edge glow
- Boss room always: constant subtle screen edge glow in boss color

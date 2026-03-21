\# SKILL: cyberpunk-theme



\## Purpose

Enforce consistent visual styling across all UI elements in 

8bit\_cyberpunk\_FIXED.html



\## Color Tokens — ALWAYS use these, never hardcode other values

\- Primary neon: #00ffff (cyan)

\- Secondary neon: #ff00ff (magenta)

\- Accent: #00ff41 (neon green)

\- Warning: #ff6600 (orange)

\- Danger: #ff0040 (red)

\- Background: #0a0a1a (deep navy)

\- Panel: #0d0d2b (dark blue)

\- Text primary: #ffffff

\- Text dim: #888888



\## Typography

\- Font: 'Share Tech Mono' or monospace fallback

\- Never use serif fonts

\- Headers: uppercase, letter-spacing 2-4px

\- Body: normal case, 0.9-1.1rem



\## Borders and Panels

\- All panels: 1-2px solid neon border with box-shadow glow

\- Border glow formula: box-shadow: 0 0 8px \[border-color]

\- Panel background: rgba(0,0,0,0.85)

\- Border radius: 4px maximum — keep it sharp



\## Buttons

\- Default: neon cyan border, transparent background

\- Hover: background fills with 20% opacity of border color

\- Active/confirm: neon green

\- Danger/cancel: neon red

\- Disabled: gray #444, no glow, cursor: not-allowed



\## Animations

\- All transitions: 150-200ms ease

\- Glow pulse: keyframe between 80% and 100% opacity, 2s infinite

\- No bounce or elastic easing — keep it sharp and digital



\## Layout Rules

\- Never use external images unless already in D:\\game

\- No external CSS frameworks

\- All screens: 100vw x 100vh, no scrolling

\- Z-index hierarchy: background(0) → arena(10) → sprites(20) → 

&#x20; effects canvas(30) → UI panels(40) → overlays(50) → modals(60)


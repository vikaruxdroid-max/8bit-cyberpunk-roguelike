SKILL: sound-design defines audio implementation using Web Audio API with no external files.

## Architecture — No Audio Files
All sound is generated procedurally using Web Audio API oscillators and noise.
No MP3/WAV/OGG files. No CDN. No dependencies. Everything synthesized in code.

## Audio Manager Pattern
```javascript
const Audio = {
  ctx: null,
  volume: 0.5,  // from GameState.settings.volume (0-100 → 0-1)
  muted: false,

  init() {
    // Create on first user interaction (browser requirement)
    if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)();
  },

  // Play a synthesized sound effect
  play(type) {
    if (this.muted || !this.ctx) return;
    this['_' + type]?.();
  },

  _hit() { /* oscillator-based hit sound */ },
  _crit() { /* bigger hit */ },
  _heal() { /* ascending tone */ },
  // etc.
};
```

## Sound Effect Recipes (all procedural)

**Player Attack Hit** — short percussive click:
- Square wave, 200Hz → 80Hz sweep, 60ms duration
- Gain: 0.3 → 0, linear ramp

**Critical Hit** — bigger punch:
- Square wave 300Hz → 100Hz, 100ms
- Layer: white noise burst 40ms
- Gain: 0.5 → 0

**Enemy Hit (player takes damage)** — low thud:
- Sine wave 120Hz → 60Hz, 80ms
- Gain: 0.4 → 0

**Heal** — ascending chime:
- Sine wave 400Hz → 800Hz, 200ms
- Gain: 0.2 → 0, ease out

**Block** — metallic clang:
- Triangle wave 800Hz → 400Hz, 50ms
- Gain: 0.3 → 0

**Spell Cast** — rising sweep:
- Sawtooth wave 200Hz → 1200Hz, 300ms
- Gain: 0.15 → 0

**Enemy Death** — descending crash:
- White noise 150ms + square 300Hz → 50Hz 200ms
- Gain: 0.4 → 0

**Level Up** — ascending arpeggio:
- Sine wave: play 400Hz, 500Hz, 600Hz, 800Hz each 80ms
- Gain: 0.25 per note

**Menu Select** — UI click:
- Square wave 600Hz, 30ms
- Gain: 0.1

**Menu Hover** — subtle tick:
- Square wave 400Hz, 15ms
- Gain: 0.05

**Combo Milestone (5+)** — power chord:
- Square 200Hz + 300Hz + 400Hz, 150ms
- Gain: 0.2 → 0

**Boss Phase Transition** — dramatic slam:
- White noise 200ms + sine 80Hz → 40Hz 400ms
- Gain: 0.6 → 0, layer with sine 200Hz 100ms

## Where to Trigger Sounds
```
Combat.deal()           → 'hit' or 'crit'
Combat.enemyAttack()    → 'enemyHit'
Combat.playerAttack()   → 'hit'
Player heal             → 'heal'
Block activated         → 'block'
Spell cast              → 'spell'
Enemy death             → 'death'
Level up                → 'levelUp'
Combo 5/7               → 'combo'
Boss phase change       → 'bossPhase'
UI button click         → 'uiClick'
UI button hover         → 'uiHover'
Loot drop               → 'loot'
Quest complete          → 'questDone'
```

## Background Music (optional, low priority)
Procedural ambient drone using Web Audio API:
- Base: low sine wave 60Hz at 0.03 gain (barely audible)
- Layer: filtered white noise (bandpass 200-400Hz) at 0.02 gain
- Modulate filter frequency slowly (0.1Hz LFO)
- Different filter settings per zone for mood variation
- Boss fight: add pulsing sine at 120Hz synced to combat tick rate

## Volume Control Integration
- Existing: volume slider in settings (#volSlider)
- GameState.settings.volume (0-100)
- Map to Audio.volume = GameState.settings.volume / 100
- Mute button: Audio.muted toggle
- AudioContext requires user gesture to start — init on first click/keypress

## Implementation Rules
- NEVER add external audio files
- Always check `Audio.ctx` exists before playing
- Keep all sounds under 500ms duration
- Gain never above 0.6 (prevent clipping)
- Use `setTimeout` or `AudioParam.linearRampToValueAtTime` for envelopes
- Clean up oscillator nodes after use (oscillator.stop() + disconnect())
- Total concurrent sounds: max 8 (prevent audio overload)

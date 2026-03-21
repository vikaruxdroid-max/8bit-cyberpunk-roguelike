Add a new enemy to the game: $ARGUMENTS

Steps:
1. Read skills/balance-rules.md for stat scaling formulas
2. Read skills/sprite-animation.md for sprite creation patterns
3. Read the existing ETYPES array and SPR object in 8bit_cyberpunk_FIXED.html
4. Create the pixel art sprite function in SPR following the 14-column grid pattern
5. Add SPRITE_SIZE entry
6. Add enemy type to ETYPES with balanced stats using the scaling formula
7. Add the enemy to at least one zone's enemy pool in ZONES
8. Report the new enemy's stats, abilities, and which zones it appears in

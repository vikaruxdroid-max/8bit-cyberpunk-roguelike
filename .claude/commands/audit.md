Audit the game code for common issues.

Check 8bit_cyberpunk_FIXED.html for:
1. Unbalanced ctx.save()/restore() pairs — every save must have a matching restore
2. Canvas state leaks — globalAlpha, filter, shadowBlur, shadowColor not restored after drawing
3. Invalid CSS color values — check rgba() strings are properly formed
4. Missing null checks on GameState properties accessed in render loops
5. Duplicate function names or variable shadowing
6. Event listeners added multiple times without cleanup
7. setInterval/setTimeout without proper cleanup on screen changes
8. CSS z-index conflicts between overlapping elements

Report each issue found with the line number and a fix.

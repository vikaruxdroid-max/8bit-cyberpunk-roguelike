Fix this bug in the game: $ARGUMENTS

Steps:
1. Read the relevant sections of 8bit_cyberpunk_FIXED.html to understand the current code
2. Read any relevant skill files from skills/ for context on intended behavior
3. Identify the root cause — do NOT guess, trace the actual code path
4. Fix the minimal amount of code needed
5. Check for unbalanced ctx.save()/restore() pairs in canvas rendering code
6. Check for leaked canvas state (globalAlpha, filter, shadowBlur) after any drawing function
7. Report: what was broken, why, and what was changed

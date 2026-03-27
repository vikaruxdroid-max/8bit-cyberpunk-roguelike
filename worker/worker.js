// Neon Dungeon AI Proxy Worker
// Deploy via: wrangler deploy
// Required env var: ANTHROPIC_API_KEY (set via: wrangler secret put ANTHROPIC_API_KEY)

const ALLOWED_FEATURES = ['boss_narration', 'run_coaching', 'difficulty_tuning', 'zone_lore', 'spell_commentary'];
const MAX_TOKENS = {
  boss_narration:    80,
  run_coaching:      120,
  difficulty_tuning: 150,
  zone_lore:         100,
  spell_commentary:  80
};

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    let body;
    try { body = await request.json(); }
    catch { return new Response('Invalid JSON', { status: 400 }); }

    const { feature, payload } = body;

    if (!ALLOWED_FEATURES.includes(feature)) {
      return new Response('Unknown feature', { status: 400 });
    }

    const prompt = buildPrompt(feature, payload);
    if (!prompt) return new Response('Failed to build prompt', { status: 400 });

    try {
      const res = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': env.ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: 'claude-haiku-4-5-20251001',
          max_tokens: MAX_TOKENS[feature] || 100,
          messages: [{ role: 'user', content: prompt }]
        })
      });

      if (!res.ok) throw new Error(`Claude API error: ${res.status}`);

      const data = await res.json();
      const result = data.content?.[0]?.text || '';

      return new Response(
        JSON.stringify({ result }),
        { headers: { ...CORS, 'Content-Type': 'application/json' } }
      );

    } catch (err) {
      console.error('Claude API call failed:', err);
      // Return 200 with null so game falls back gracefully
      return new Response(
        JSON.stringify({ result: null, error: 'AI unavailable' }),
        { status: 200, headers: { ...CORS, 'Content-Type': 'application/json' } }
      );
    }
  }
};

function buildPrompt(feature, p) {
  switch (feature) {
    case 'boss_narration':
      return `You are the Dungeon Master of Neon Dungeon, a grimdark cyberpunk roguelike set in a neon-soaked dystopia. Your tone is Warhammer 40K grimness blended with Ghost in the Shell philosophical dread.

CURRENT CONTEXT:
- Player class: ${p.playerClass}
- Player level: ${p.playerLevel}
- Player HP: ${p.playerHp}%
- Player's active spells: ${(p.playerSpells||[]).join(', ')}
- Zone: ${p.zoneName}
- Boss: ${p.bossName}
- Run depth: Zone ${p.runDepth} of 8

REQUIREMENTS:
- Write exactly 2 sentences of combat narration for this boss encounter
- First sentence: describe the boss appearing/speaking (menacing, specific to their identity)
- Second sentence: hint at what the player must do to survive (vague but tactically relevant)
- Tone: cold, brutal, no hope
- No emojis, no exclamation points, no hero's journey encouragement
- Maximum 40 words total

Respond with ONLY the narration text. No preamble, no labels, no quotes.`;

    case 'run_coaching':
      return `You are a cold, data-driven combat analyst reviewing a cyberpunk dungeon run. Provide tactical coaching with zero sentimentality.

RUN DATA:
- Outcome: ${p.outcome}
${p.deathCause ? `- Died to: ${p.deathCause}` : ''}
- Zones cleared: ${p.zonesCleared}/8
- Damage dealt/taken ratio: ${((p.totalDamageDealt||0) / Math.max(1, p.totalDamageTaken||1)).toFixed(2)}
- Missed counter opportunities: ${p.missedCounters}

REQUIREMENTS:
- 3 bullet points maximum
- Each point: one specific, actionable coaching tip based on the data
- Be blunt. If they played poorly, say so with data.
- Maximum 15 words per bullet point
- Format: start each bullet with "▸ "

Respond with ONLY the 3 bullet points. No preamble, no score, no encouragement.`;

    case 'difficulty_tuning':
      return `You are a difficulty balancer for a roguelike game. Analyze player performance and return a JSON tuning object.

PERFORMANCE DATA (Zone ${p.currentZone} → ${p.nextZone}):
- HP entering boss: ${p.hpPercentageEnteringBoss}% of max
- Turns to kill boss: ${p.turnsToKillBoss} (expected: 15-25)
- Counter miss rate: ${p.counterMissRate}% (healthy: <40%)
- Deaths this run: ${p.deathsThisRun}

TUNING RULES:
- If player is dominant (boss HP > 70%, turns < 12, miss rate < 20%): increase challenge
- If player is struggling (boss HP < 30%, turns > 30, miss rate > 60%): reduce challenge
- If player is balanced: minor adjustment only
- Max tuning swing: ±25% stat multiplier, ±15% ability probability
- Never reduce below 0.7× base stats; never exceed 1.5× base stats

Respond with ONLY valid JSON, no markdown, no explanation:
{"enemyStatMultiplier":1.0,"abilityProbability":1.0,"reasoning":"one sentence max"}`;

    case 'zone_lore':
      return `You are the lore keeper of Neon Dungeon, a grimdark cyberpunk city where data is flesh and corporate law is gravity.

ZONE: ${p.zoneName}
ZONE ID: ${p.zoneId}
ZONES CLEARED: ${p.zonesCleared}

Write a 2-sentence atmospheric description of this zone. Cold, specific, world-building. No generic cyberpunk cliches.
Maximum 35 words. Respond with ONLY the description.`;

    case 'spell_commentary':
      return `You are a cynical netrunner commenting on a loadout swap in a cyberpunk dungeon run.

KEPT: ${p.keptSpell}
SWAPPED OUT: ${p.rejectedSpell}
SWAPPED IN: ${p.newSpell}
ZONE: ${p.zoneName}

Write ONE sentence of dry tactical commentary on this swap decision. Blunt. Max 20 words.
Respond with ONLY the sentence.`;

    default:
      return null;
  }
}

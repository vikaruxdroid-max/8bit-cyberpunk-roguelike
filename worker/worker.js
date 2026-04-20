const ALLOWED_FEATURES = ['boss_narration','run_coaching','difficulty_tuning','zone_lore','spell_commentary'];
const MAX_TOKENS = { boss_narration:80, run_coaching:120, difficulty_tuning:150, zone_lore:100, spell_commentary:80 };

export default {
    async fetch(request, env) {
        const cors = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '86400'
        };
        if (request.method === 'OPTIONS') return new Response(null, { headers: cors });
        if (request.method !== 'POST') return new Response('Method not allowed', { status: 405, headers: cors });

        let body;
        try { body = await request.json(); }
        catch { return new Response('Invalid JSON', { status: 400, headers: cors }); }

        const { feature, payload } = body;
        if (!ALLOWED_FEATURES.includes(feature)) return new Response('Unknown feature', { status: 400, headers: cors });

        const prompt = buildPrompt(feature, payload);
        if (!prompt) return new Response('Failed to build prompt', { status: 400, headers: cors });

        try {
            const res = await fetch('https://api.anthropic.com/v1/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': env.ANTHROPIC_API_KEY,
                    'anthropic-version': '2023-06-01'
                },
                body: JSON.stringify({
                    model: 'claude-haiku-4-5',
                    max_tokens: MAX_TOKENS[feature] || 100,
                    messages: [{ role: 'user', content: prompt }]
                })
            });
            if (!res.ok) throw new Error('Claude API error: ' + res.status);
            const data = await res.json();
            const result = data.content[0]?.text || '';
            return new Response(JSON.stringify({ result }), { headers: { ...cors, 'Content-Type': 'application/json' } });
        } catch (err) {
            return new Response(JSON.stringify({ result: null, error: 'AI unavailable' }), { status: 200, headers: { ...cors, 'Content-Type': 'application/json' } });
        }
    }
};

function buildPrompt(feature, payload) {
    switch(feature) {
        case 'boss_narration': return `You are the Dungeon Master of Neon Dungeon, a grimdark cyberpunk roguelike. Tone: Warhammer 40K grimness blended with Ghost in the Shell dread. Write exactly 2 sentences for this boss encounter. First sentence: the boss appearing (menacing, specific). Second sentence: hint at survival (vague but tactical). No emojis, no exclamation points. Max 40 words total. Boss: ${payload.bossName}. Zone: ${payload.zoneName}. Player class: ${payload.playerClass}. Player spells: ${(payload.playerSpells||[]).join(', ')}. Respond with ONLY the narration.`;
        case 'run_coaching': return `You are a cold data-driven combat analyst. 3 bullet points max. Each: one specific actionable tip based on this data. Blunt. Max 15 words per bullet. Start each with "? ". Outcome: ${payload.outcome}. Zones cleared: ${payload.zonesCleared}/8. Missed counters: ${payload.missedCounters}. Damage ratio: ${payload.damageRatio}. Respond with ONLY the 3 bullets.`;
        case 'difficulty_tuning': return `Roguelike difficulty balancer. Analyze and return JSON only. HP entering boss: ${payload.hpPct}%. Turns to kill boss: ${payload.bossTurns}. Counter miss rate: ${payload.counterMissRate}%. If dominant (HP>70%, turns<12, miss<20%): increase. If struggling (HP<30%, turns>30, miss>60%): reduce. Max swing: �25% stats, �15% ability prob. Never below 0.7x or above 1.5x base. Respond ONLY with valid JSON: {"enemyStatMultiplier":1.0,"abilityProbability":1.0,"reasoning":"one sentence"}`;
        case 'zone_lore': return `Write 1 sentence of cyberpunk noir lore for zone: ${payload.zoneName}. Grimdark tone. No hero narrative. Max 25 words. Respond with ONLY the sentence.`;
        case 'spell_commentary': return `You are a cynical combat AI. Comment on this spell loadout in 1 sentence. Max 20 words. Dry humor or tactical observation. Spells: ${(payload.spells||[]).join(', ')}. Respond with ONLY the comment.`;
        default: return null;
    }
}

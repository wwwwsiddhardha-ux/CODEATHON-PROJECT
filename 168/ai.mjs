export async function analyzeWithAI(skillData) {
  try {
    const response = await fetch("https://api.featherless.ai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer rc_26acec666cebb9b80ab4f35247abca905056e677ba990ddab3d8aa9e121576a8"
      },
      body: JSON.stringify({
        model: "Qwen/Qwen2.5-7B-Instruct",
        messages: [
          {
            role: "system",
            content: "You are a skill investment advisor."
          },
          {
            role: "user",
            content: `
Demand: ${skillData.demand}
Interest: ${skillData.interest}
Competition: ${skillData.competition}
Score: ${skillData.score}

Return JSON:
{
  "recommendation": "",
  "risk": "",
  "reward": "",
  "reason": ""
}
            `
          }
        ]
      })
    });

    const data = await response.json();

    let text = data.choices?.[0]?.message?.content;

    // Clean
    text = text.replace(/```json/g, "").replace(/```/g, "").trim();

    const start = text.indexOf("{");
    const end = text.lastIndexOf("}");

    if (start !== -1 && end !== -1) {
      text = text.substring(start, end + 1);
    }

    return JSON.parse(text);

  } catch (err) {
    return {
      recommendation: "Error",
      risk: "Unknown",
      reward: "Unknown",
      reason: "AI failed"
    };
  }
}
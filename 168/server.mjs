import express from "express";
import cors from "cors";
import { analyzeWithAI } from "./ai.mjs";

const app = express();
app.use(cors());
app.use(express.json());

// 🔹 Fetch GitHub data
async function getSkillDemand(skill) {
  const res = await fetch(
    `https://api.github.com/search/repositories?q=${skill}`
  );
  const data = await res.json();
  return data.total_count;
}

// 🔹 Normalize
function normalizeDemands(skills) {
  const max = Math.max(...skills.map(s => s.demand));

  return skills.map(s => ({
    ...s,
    demand: Number(((s.demand / max) * 10).toFixed(2))
  }));
}

// 🔹 Score
function calculateScores(data) {
  return data.map(s => {
    const competition = 10 - s.demand;

    const score =
      (s.demand * 0.5) +
      (s.interest * 0.3) -
      (competition * 0.2);

    return {
      ...s,
      competition,
      score: Number(score.toFixed(2))
    };
  });
}

// 🔹 Allocate time
function allocateTime(data, totalHours) {
  const totalScore = data.reduce((sum, s) => sum + s.score, 0);

  return data.map(s => ({
    ...s,
    hours: Number(((s.score / totalScore) * totalHours).toFixed(2))
  }));
}

// 🚀 API
app.post("/analyze", async (req, res) => {
  const { skills } = req.body;

  let data = [];

  // Step 1: Fetch real data
  for (let s of skills) {
    const demand = await getSkillDemand(s.name);
    data.push({
      skill: s.name,
      demand,
      interest: Number(s.interest)
    });
  }

  // Step 2: Normalize
  data = normalizeDemands(data);

  // Step 3: Score
  data = calculateScores(data);

  // Step 4: Allocate time
  data = allocateTime(data, 20);

  // Step 5: AI
  let final = [];

  for (let skill of data) {
    const ai = await analyzeWithAI(skill);

    final.push({
      skill: skill.skill,
      hours: skill.hours,
      ...ai
    });
  }

  res.json(final);
});

// Start server
app.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});
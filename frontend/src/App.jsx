/**
 * App.jsx — Root component.
 * Orchestrates profile input → API calls → dashboard rendering.
 */
import { useState } from "react";
import ProfileForm from "./components/ProfileForm";
import SkillPieChart from "./components/SkillPieChart";
import RiskRewardChart from "./components/RiskRewardChart";
import RecommendationPanel from "./components/RecommendationPanel";
import WeeklyRoadmap from "./components/WeeklyRoadmap";
import MarketTrends from "./components/MarketTrends";
import { getRecommendations, getRoadmap } from "./api/client";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [result, setResult]   = useState(null);  // { recommendations, roadmap }

  const handleSubmit = async (profile) => {
    setLoading(true);
    setError(null);
    try {
      // Run both API calls in parallel
      const [recommendations, roadmap] = await Promise.all([
        getRecommendations(profile),
        getRoadmap(profile),
      ]);
      setResult({ recommendations, roadmap });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to connect to backend. Is FastAPI running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 flex items-center gap-3">
        <span className="text-2xl">📊</span>
        <div>
          <h1 className="text-xl font-bold text-white">Skill Investment Portfolio Engine</h1>
          <p className="text-xs text-gray-500">Treat your skills like financial investments</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 flex flex-col gap-8">
        {/* Profile Input */}
        <div className="max-w-xl">
          <ProfileForm onSubmit={handleSubmit} loading={loading} />
        </div>

        {/* Error */}
        {error && (
          <div className="bg-rose-950 border border-rose-700 text-rose-300 rounded-xl px-4 py-3 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Dashboard — shown after analysis */}
        {result && (
          <div className="flex flex-col gap-6">
            {/* Row 1: Recommendations + Market Trends */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RecommendationPanel data={result.recommendations} />
              <MarketTrends skills={result.recommendations.scored_skills} />
            </div>

            {/* Row 2: Pie Chart + Risk/Reward */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SkillPieChart skills={result.recommendations.scored_skills} />
              <RiskRewardChart skills={result.recommendations.scored_skills} />
            </div>

            {/* Row 3: Weekly Roadmap (full width) */}
            <WeeklyRoadmap
              plan={result.roadmap.weekly_plan}
              totalHours={result.roadmap.total_hours}
            />
          </div>
        )}
      </main>
    </div>
  );
}

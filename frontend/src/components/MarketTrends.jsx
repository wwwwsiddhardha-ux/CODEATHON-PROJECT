/**
 * MarketTrends — displays real-time market demand signals per skill.
 * Shows demand score bar, job count, and average salary.
 */
export default function MarketTrends({ skills }) {
  return (
    <div className="bg-gray-900 rounded-2xl p-6 shadow-xl">
      <h2 className="text-lg font-bold text-brand mb-4">Market Demand Signals</h2>
      <div className="flex flex-col gap-3">
        {skills
          .slice()
          .sort((a, b) => b.demand_score - a.demand_score)
          .map((skill) => (
            <div key={skill.name} className="flex flex-col gap-1">
              <div className="flex justify-between text-sm">
                <span className="font-medium">{skill.name}</span>
                <span className="text-gray-400">
                  Demand: <span className="text-white">{skill.demand_score}/10</span>
                </span>
              </div>
              {/* Demand bar */}
              <div className="w-full bg-gray-800 rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-brand transition-all"
                  style={{ width: `${(skill.demand_score / 10) * 100}%` }}
                />
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}

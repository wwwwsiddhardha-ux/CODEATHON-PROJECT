/**
 * RecommendationPanel — displays AI-generated invest/reduce advice
 * and the plain-English portfolio summary from Featherless AI.
 */
export default function RecommendationPanel({ data }) {
  const { invest_more = [], reduce_focus = [], summary = "" } = data;

  return (
    <div className="bg-gray-900 rounded-2xl p-6 shadow-xl flex flex-col gap-4">
      <h2 className="text-lg font-bold text-brand">AI Recommendations</h2>

      {summary && (
        <p className="text-sm text-gray-300 bg-gray-800 rounded-xl p-4 leading-relaxed">
          💡 {summary}
        </p>
      )}

      <div className="grid grid-cols-2 gap-4">
        {/* Invest More */}
        <div className="bg-emerald-950 border border-emerald-700 rounded-xl p-4">
          <p className="text-xs font-semibold text-emerald-400 mb-2">📈 Invest More</p>
          <ul className="flex flex-col gap-1">
            {invest_more.map((skill) => (
              <li key={skill} className="text-sm font-medium text-emerald-300">
                ✓ {skill}
              </li>
            ))}
          </ul>
        </div>

        {/* Reduce Focus */}
        <div className="bg-rose-950 border border-rose-700 rounded-xl p-4">
          <p className="text-xs font-semibold text-rose-400 mb-2">📉 Reduce Focus</p>
          <ul className="flex flex-col gap-1">
            {reduce_focus.map((skill) => (
              <li key={skill} className="text-sm font-medium text-rose-300">
                ↓ {skill}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

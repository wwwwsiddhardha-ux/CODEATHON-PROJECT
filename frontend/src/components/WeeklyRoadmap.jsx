/**
 * WeeklyRoadmap — displays the weekly learning plan.
 * Shows hours per skill as a horizontal bar chart + text breakdown.
 */
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const COLORS = ["#6366f1","#22d3ee","#f59e0b","#10b981","#f43f5e","#a78bfa"];

export default function WeeklyRoadmap({ plan, totalHours }) {
  return (
    <div className="bg-gray-900 rounded-2xl p-6 shadow-xl flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-brand">Weekly Learning Roadmap</h2>
        <span className="text-sm text-gray-400">{totalHours} hrs / week</span>
      </div>

      {/* Bar chart */}
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={plan} layout="vertical" margin={{ left: 20 }}>
          <XAxis type="number" stroke="#9ca3af" fontSize={11} />
          <YAxis type="category" dataKey="skill" stroke="#9ca3af" fontSize={11} width={90} />
          <Tooltip
            contentStyle={{ background: "#1f2937", border: "none", borderRadius: 8 }}
            formatter={(v) => [`${v} hrs`]}
          />
          <Bar dataKey="hours" radius={[0, 6, 6, 0]}>
            {plan.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Text breakdown */}
      <ul className="flex flex-col gap-2 mt-2">
        {plan.map((item) => (
          <li key={item.skill} className="flex items-start gap-3 text-sm">
            <span className="font-semibold text-brand min-w-[90px]">
              {item.skill}
            </span>
            <span className="text-gray-400">
              <span className="text-white font-medium">{item.hours} hrs</span> — {item.reason}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

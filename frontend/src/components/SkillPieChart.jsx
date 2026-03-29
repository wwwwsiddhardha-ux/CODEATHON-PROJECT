/**
 * SkillPieChart — visualizes skill portfolio allocation as a pie chart.
 * Each slice = % of weekly time to invest in that skill.
 */
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLORS = ["#6366f1","#22d3ee","#f59e0b","#10b981","#f43f5e","#a78bfa","#34d399","#fb923c"];

export default function SkillPieChart({ skills }) {
  const data = skills.map((s) => ({
    name: s.name,
    value: parseFloat(s.allocation_percent),
  }));

  return (
    <div className="bg-gray-900 rounded-2xl p-6 shadow-xl">
      <h2 className="text-lg font-bold mb-4 text-brand">Portfolio Allocation</h2>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            outerRadius={100}
            dataKey="value"
            label={({ name, value }) => `${name} ${value}%`}
            labelLine={false}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v) => `${v}%`} contentStyle={{ background: "#1f2937", border: "none" }} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

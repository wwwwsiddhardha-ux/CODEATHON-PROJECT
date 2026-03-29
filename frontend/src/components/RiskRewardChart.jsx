/**
 * RiskRewardChart — scatter plot showing Risk vs Reward for each skill.
 * Top-right quadrant = high reward, low risk = best investments.
 */
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Label, ReferenceLine,
} from "recharts";

const CustomDot = (props) => {
  const { cx, cy, payload } = props;
  return (
    <g>
      <circle cx={cx} cy={cy} r={8} fill="#6366f1" fillOpacity={0.85} />
      <text x={cx} y={cy - 12} textAnchor="middle" fill="#e5e7eb" fontSize={11}>
        {payload.name}
      </text>
    </g>
  );
};

export default function RiskRewardChart({ skills }) {
  const data = skills.map((s) => ({
    name: s.name,
    risk: parseFloat(s.risk_score),
    reward: parseFloat(s.reward_score),
  }));

  return (
    <div className="bg-gray-900 rounded-2xl p-6 shadow-xl">
      <h2 className="text-lg font-bold mb-4 text-brand">Risk vs Reward</h2>
      <p className="text-xs text-gray-500 mb-4">Top-right = best investment (high reward, low risk)</p>
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 30, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis type="number" dataKey="risk" domain={[0, 10]} stroke="#9ca3af">
            <Label value="Risk Score →" offset={-10} position="insideBottom" fill="#9ca3af" fontSize={12} />
          </XAxis>
          <YAxis type="number" dataKey="reward" domain={[0, 10]} stroke="#9ca3af">
            <Label value="Reward →" angle={-90} position="insideLeft" fill="#9ca3af" fontSize={12} />
          </YAxis>
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            contentStyle={{ background: "#1f2937", border: "none", borderRadius: 8 }}
            formatter={(v, n) => [v.toFixed(1), n]}
          />
          <ReferenceLine x={5} stroke="#4b5563" strokeDasharray="4 4" />
          <ReferenceLine y={5} stroke="#4b5563" strokeDasharray="4 4" />
          <Scatter data={data} shape={<CustomDot />} />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

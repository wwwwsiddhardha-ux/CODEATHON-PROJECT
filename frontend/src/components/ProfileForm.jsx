/**
 * ProfileForm — collects user profile input.
 * Skills are entered as "SkillName:Proficiency" pairs (e.g. "Python:8").
 */
import { useState } from "react";

const DEFAULT_SKILLS = "Python:8, React:6, Docker:5, AWS:4, SQL:7";

export default function ProfileForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    name: "Alex",
    skillsRaw: DEFAULT_SKILLS,
    interests: "cloud, AI, automation",
    career_goal: "DevOps Engineer",
    hours_per_week: 20,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Parse "Python:8, React:6" → [{name, proficiency}]
    const skills = form.skillsRaw.split(",").map((s) => {
      const [name, prof] = s.trim().split(":");
      return { name: name.trim(), proficiency: parseInt(prof) || 5 };
    });
    onSubmit({
      name: form.name,
      skills,
      interests: form.interests.split(",").map((i) => i.trim()),
      career_goal: form.career_goal,
      hours_per_week: parseInt(form.hours_per_week),
    });
  };

  const field = (label, key, type = "text", extra = {}) => (
    <div className="flex flex-col gap-1">
      <label className="text-sm text-gray-400">{label}</label>
      <input
        type={type}
        value={form[key]}
        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
        className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand"
        {...extra}
      />
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className="bg-gray-900 rounded-2xl p-6 flex flex-col gap-4 shadow-xl">
      <h2 className="text-xl font-bold text-brand">Your Skill Profile</h2>
      {field("Your Name", "name")}
      {field("Skills (Name:Level, ...)", "skillsRaw", "text", {
        placeholder: "Python:8, React:6, Docker:5",
      })}
      {field("Interests (comma-separated)", "interests")}
      {field("Career Goal", "career_goal", "text", {
        placeholder: "e.g. AI Engineer, DevOps Engineer",
      })}
      {field("Hours Available Per Week", "hours_per_week", "number", { min: 1, max: 80 })}
      <button
        type="submit"
        disabled={loading}
        className="mt-2 bg-brand hover:bg-brand-dark transition rounded-xl py-2 font-semibold disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Analyze My Portfolio →"}
      </button>
    </form>
  );
}

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        fed: {
          bg: "#0a0f1a",
          surface: "#111827",
          border: "#1f2937",
          accent: "#6366f1",
          muted: "#6b7280",
          text: "#e5e7eb",
          green: "#10b981",
          red: "#ef4444",
          yellow: "#f59e0b",
          purple: "#8b5cf6",
          hawkish: "#ef4444",
          dovish: "#3b82f6",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
    },
  },
  plugins: [],
};

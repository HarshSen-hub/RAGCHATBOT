import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        app: {
          bg: "var(--color-bg)",
          sidebar: "#111827",
          sidebarHover: "#1F2937",
          card: "var(--color-card)",
          accent: "#F97316",
          accentHover: "#EA580C",
          accentSoft: "var(--color-accent-soft)",
          border: "var(--color-border)",
          text: "var(--color-text)",
          muted: "var(--color-muted)",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "sans-serif",
        ],
      },
      borderRadius: {
        xl: "0.875rem",
        "2xl": "1.25rem",
        "3xl": "1.75rem",
      },
      boxShadow: {
        soft: "0 2px 8px rgba(17, 24, 39, 0.06)",
        card: "0 4px 16px rgba(17, 24, 39, 0.08)",
        lift: "0 12px 32px rgba(17, 24, 39, 0.12)",
      },
      keyframes: {
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        blink: {
          "0%, 80%, 100%": { opacity: "0.2" },
          "40%": { opacity: "1" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-400px 0" },
          "100%": { backgroundPosition: "400px 0" },
        },
      },
      animation: {
        "fade-in-up": "fade-in-up 0.35s ease-out",
        blink: "blink 1.4s infinite both",
        shimmer: "shimmer 1.6s infinite linear",
      },
    },
  },
  plugins: [],
} satisfies Config;

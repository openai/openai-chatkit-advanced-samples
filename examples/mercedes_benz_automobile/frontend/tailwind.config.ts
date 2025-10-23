import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        mercedes: {
          silver: "#C0C0C0",
          darkgray: "#2B2B2B",
          blue: "#00ADEF",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;

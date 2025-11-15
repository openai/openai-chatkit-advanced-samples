import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Lora", "serif"],
      },
      colors: {
        surface: {
          light: "#f3f4f6",
          dark: "#0b1120",
        },
      },
    },
  },
  plugins: [],
};

export default config;

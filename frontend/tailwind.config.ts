import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#16302B",
        moss: "#5F8B4C",
        leaf: "#A3C36D",
        sand: "#F5EFD9",
        clay: "#C97B63",
      },
      boxShadow: {
        panel: "0 20px 50px rgba(22, 48, 43, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;

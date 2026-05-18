/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        carbon: "#111410",
        panel: "#171b16",
        steel: "#8d9a8c",
        limewire: "#d5ff5b",
        ember: "#ff6b35",
        ink: "#f2f4ea"
      },
      fontFamily: {
        display: ["Archivo", "Aptos", "sans-serif"],
        body: ["IBM Plex Sans Condensed", "Aptos", "sans-serif"],
        mono: ["IBM Plex Mono", "SFMono-Regular", "monospace"]
      }
    }
  },
  plugins: []
};


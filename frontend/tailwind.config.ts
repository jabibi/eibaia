import type { Config } from "tailwindcss";

export default <Partial<Config>>{
  content: [
    "./src/pages/**/*.vue",
    "./src/layouts/**/*.vue",
    "./src/core/**/*.vue",
    "./src/modules/**/*.vue",
    "./src/app.vue",
  ],
  theme: {
    extend: {},
  },
};

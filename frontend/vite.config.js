import { defineConfig } from "vite";
import { resolve } from "path";
// Dev server on :5173 proxies /api to Flask on :5000.
export default defineConfig({
  server: { proxy: { "/api": "http://127.0.0.1:5000" } },
  build: { rollupOptions: { input: {
    index: resolve(__dirname, "index.html"),
    students: resolve(__dirname, "students.html"),
    form: resolve(__dirname, "form.html") } } },
});

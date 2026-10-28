// Empaquetador estático para Cloudflare Pages (npm run build -> dist/)
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const srcDir = path.join(root, "viralforge", "ui");
const distDir = path.join(root, "dist");
const staticDir = path.join(distDir, "static");

fs.rmSync(distDir, { recursive: true, force: true });
fs.mkdirSync(staticDir, { recursive: true });

for (const file of ["index.html", "styles.css", "app.js"]) {
  const src = path.join(srcDir, file);
  fs.copyFileSync(src, path.join(distDir, file));
  if (file !== "index.html") {
    fs.copyFileSync(src, path.join(staticDir, file));
  }
}

fs.writeFileSync(
  path.join(distDir, "_headers"),
  "/*\n  Access-Control-Allow-Origin: *\n"
);

console.log("[ViralForge] Build para Cloudflare Pages completado en ./dist");

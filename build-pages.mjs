// Empaquetador estático para Cloudflare Pages (npm run build -> dist/) con Cache-Busting automático
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const srcDir = path.join(root, "viralforge", "ui");
const distDir = path.join(root, "dist");
const staticDir = path.join(distDir, "static");

fs.rmSync(distDir, { recursive: true, force: true });
fs.mkdirSync(staticDir, { recursive: true });

const buildVer = Date.now().toString(36);

for (const file of ["styles.css", "app.js"]) {
  const src = path.join(srcDir, file);
  fs.copyFileSync(src, path.join(distDir, file));
  fs.copyFileSync(src, path.join(staticDir, file));
}

// Inyectar cache-busting ?v=buildVer en index.html para evitar caché antigua de Cloudflare CDN
let html = fs.readFileSync(path.join(srcDir, "index.html"), "utf-8");
html = html
  .replace(/\/static\/styles\.css(\?v=[^"']*)?/g, `/static/styles.css?v=${buildVer}`)
  .replace(/\/static\/app\.js(\?v=[^"']*)?/g, `/static/app.js?v=${buildVer}`);
fs.writeFileSync(path.join(distDir, "index.html"), html, "utf-8");

for (const assetName of ["poses_1439.json", "cinetic_techniques.json", "costumes_1407.json"]) {
  const assetSrc = path.join(root, "assets", assetName);
  if (fs.existsSync(assetSrc)) {
    fs.copyFileSync(assetSrc, path.join(srcDir, assetName));
    fs.copyFileSync(assetSrc, path.join(distDir, assetName));
    fs.copyFileSync(assetSrc, path.join(staticDir, assetName));
  }
}

fs.writeFileSync(
  path.join(distDir, "_headers"),
  [
    "/*",
    "  Access-Control-Allow-Origin: *",
    "/index.html",
    "  Cache-Control: public, max-age=0, must-revalidate",
    "/static/*",
    "  Cache-Control: public, max-age=0, must-revalidate",
    "",
  ].join("\n")
);

console.log(`[ViralForge] Build v=${buildVer} completado en ./dist`);

"""Generate EDS Edge Function implementation guide PPTX (Adobe branding)."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

# Adobe brand colours
RED   = RGBColor(0xFF, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)
LGREY = RGBColor(0xF0, 0xF0, 0xF0)
DGREY = RGBColor(0x33, 0x33, 0x33)
CODE_BG = RGBColor(0xF5, 0xF5, 0xF5)

W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H

BLANK = prs.slide_layouts[6]  # completely blank


# ── helpers ───────────────────────────────────────────────────────────────────

def add_rect(slide, x, y, w, h, fill_rgb, line_rgb=None):
    shape = slide.shapes.add_shape(1, x, y, w, h)  # MSO_SHAPE_TYPE.RECTANGLE=1
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if line_rgb:
        shape.line.color.rgb = line_rgb
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, text, x, y, w, h,
             size=18, bold=False, color=BLACK,
             align=PP_ALIGN.LEFT, wrap=True):
    txb = slide.shapes.add_textbox(x, y, w, h)
    txb.word_wrap = wrap
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.color.rgb = color
    return txb


def add_bullet_slide(title_text, bullets, code=None):
    slide = prs.slides.add_slide(BLANK)

    # white background
    add_rect(slide, 0, 0, W, H, WHITE)

    # red left accent bar
    add_rect(slide, 0, 0, Inches(0.18), H, RED)

    # red title text
    add_text(slide, title_text,
             Inches(0.35), Inches(0.3), Inches(12.5), Inches(0.8),
             size=28, bold=True, color=RED)

    # separator line
    sep = slide.shapes.add_shape(1, Inches(0.35), Inches(1.05), Inches(12.6), Pt(2))
    sep.fill.solid(); sep.fill.fore_color.rgb = RED
    sep.line.fill.background()

    # bullets
    y = Inches(1.25)
    for bullet in bullets:
        indent = bullet.startswith("  ")
        txt = bullet.lstrip()
        bsize = 16 if not indent else 14
        bcolor = DGREY
        prefix = "• " if not indent else "    – "
        add_text(slide, prefix + txt,
                 Inches(0.5), y, Inches(12.2), Inches(0.45),
                 size=bsize, color=bcolor)
        y += Inches(0.42 if not indent else 0.38)

    # optional code block
    if code:
        cy = y + Inches(0.1)
        ch = H - cy - Inches(0.3)
        add_rect(slide, Inches(0.5), cy, Inches(12.3), ch, CODE_BG)
        txb = slide.shapes.add_textbox(Inches(0.65), cy + Inches(0.1),
                                        Inches(12.0), ch - Inches(0.2))
        txb.word_wrap = False
        tf = txb.text_frame
        tf.word_wrap = False
        first = True
        for line in code.split("\n"):
            if first:
                p = tf.paragraphs[0]; first = False
            else:
                p = tf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = line
            run.font.size  = Pt(12)
            run.font.bold  = False
            run.font.color.rgb = DGREY
            run.font.name  = "Courier New"

    # Adobe wordmark bottom-left
    add_text(slide, "Adobe",
             Inches(0.35), H - Inches(0.5), Inches(1.5), Inches(0.4),
             size=13, bold=True, color=RED)

    # copyright bottom-right
    add_text(slide, "©2024 Adobe. All Rights Reserved. Adobe Confidential.",
             Inches(8), H - Inches(0.5), Inches(5), Inches(0.4),
             size=9, color=RGBColor(0x99, 0x99, 0x99), align=PP_ALIGN.RIGHT)

    return slide


# ── slide 1 — title ──────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, W, H, RED)
add_text(s, "Edge Delivery Services",
         Inches(0.6), Inches(2.8), Inches(7), Inches(1),
         size=40, bold=False, color=WHITE)
add_text(s, "How to Configure an Edge Function with EDS",
         Inches(0.6), Inches(3.75), Inches(7), Inches(0.6),
         size=20, bold=True, color=WHITE)
add_text(s, "Adobe Experience Manager — Developer Guide",
         Inches(0.6), Inches(4.35), Inches(7), Inches(0.5),
         size=18, bold=False, color=WHITE)
add_text(s, "Adobe",
         Inches(0.6), Inches(1.8), Inches(2), Inches(0.6),
         size=22, bold=True, color=WHITE)

# ── slide 2 — agenda ─────────────────────────────────────────────────────────
add_bullet_slide("Agenda", [
    "What is an Edge Function in EDS?",
    "Folder & File Structure",
    "Worker Configuration — wrangler.toml",
    "CORS & Caching Strategy",
    "Environment Variables & Secrets",
    "Deploying the Worker",
    "Connecting a Block to the Edge Function",
    "Best Practices & Summary",
])

# ── slide 3 — what is ────────────────────────────────────────────────────────
add_bullet_slide("What is an Edge Function in EDS?", [
    "A Cloudflare Worker that acts as a secure API proxy between the EDS page and external services",
    "Runs at the network edge — low latency, no origin server needed",
    "Handles CORS so browser pages on aem.live / aem.page can call protected APIs",
    "Adds response caching (Cloudflare Cache API) to reduce upstream API calls",
    "Keeps secrets (API tokens, keys) out of the browser and out of the codebase",
    "",
    "Why not call the API directly from the block?",
    "  API tokens would be exposed in the browser",
    "  No control over CORS headers on third-party services",
    "  No caching layer — every page view hits the upstream API",
])

# ── slide 4 — folder structure ───────────────────────────────────────────────
add_bullet_slide("Folder & File Structure", [
    "All edge function code lives under /edge/ at the project root",
    "wrangler.toml (project root) points to the entry file and configures the Worker",
    "Secrets are never committed — stored in .dev.vars locally and via wrangler secret put in production",
], code="""\
myeds-xwalk/
├── edge/
│    └── api-proxy.js       ← Worker entry point (fetch handler)
├── wrangler.toml           ← Worker name, entry, vars (committed)
├── .dev.vars               ← Local secrets (git-ignored)
└── blocks/
     └── weather/
          └── weather.js    ← Block that calls the Worker via /api/*""")

# ── slide 5 — wrangler.toml ──────────────────────────────────────────────────
add_bullet_slide("Worker Configuration — wrangler.toml", [
    "name — the Worker subdomain: <name>.workers.dev",
    "main — path to the JS entry file",
    "compatibility_date — locks the Workers runtime behaviour",
    "[vars] — non-secret environment variables (safe to commit)",
    "Secrets (tokens, keys) are set separately with: npx wrangler secret put MY_SECRET",
], code="""\
name             = "myeds-xwalk-api"
main             = "edge/api-proxy.js"
compatibility_date = "2024-09-23"

[dev]
port = 8787          # local: http://localhost:8787

[vars]
API_BASE_URL = "https://author-p12345.adobeaemcloud.com/graphql/execute.json/..."

# Secret — never in this file:
#   npx wrangler secret put AEM_TOKEN
# Local dev — add to .dev.vars (git-ignored):
#   AEM_TOKEN=eyJ...""")

# ── slide 6 — CORS & caching ─────────────────────────────────────────────────
add_bullet_slide("CORS & Caching Strategy", [
    "CORS — only allow requests from your own AEM origins (aem.live, aem.page, localhost)",
    "Always whitelist both .aem.live and .aem.page — they serve the same content on different CDNs",
    "Caching — use caches.default (Cloudflare Cache API) to avoid hammering upstream APIs",
    "  Geocoding data: 24 h TTL (location coordinates are stable)",
    "  Weather / forecast data: 15 min TTL (changes frequently)",
    "  Financial rates: 5 min TTL (can change during the day)",
], code="""\
const ALLOWED_ORIGINS = [
  'https://main--myproject--owner.aem.live',
  'https://main--myproject--owner.aem.page',
  'http://localhost:3000',
];

function corsHeaders(origin) {
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return { 'Access-Control-Allow-Origin': allow,
           'Access-Control-Allow-Methods': 'GET, OPTIONS' };
}

async function cachedFetch(url, ttl) {
  const cache = caches.default;
  const hit = await cache.match(new Request(url));
  if (hit) return hit;
  const res = await fetch(url);
  const response = new Response(res.body, res);
  response.headers.set('Cache-Control', \`public, max-age=\${ttl}\`);
  await cache.put(new Request(url), response.clone());
  return response;
}""")

# ── slide 7 — env vars & secrets ─────────────────────────────────────────────
add_bullet_slide("Environment Variables & Secrets", [
    "Two types of config values: plain vars ([vars] in wrangler.toml) and secrets",
    "Plain vars — non-sensitive, committed to git (API base URLs, feature flags)",
    "Secrets — tokens, API keys; never committed; injected at deploy time by Cloudflare",
    "",
    "Setting a production secret (run once, stored encrypted in Cloudflare):",
    "  npx wrangler secret put AEM_TOKEN",
    "",
    "Local dev secret — create .dev.vars in the project root (git-ignored):",
    "  AEM_TOKEN=eyJhbGci...",
    "",
    "Accessing a secret inside the Worker — available on the env object:",
    "  env.AEM_TOKEN",
])

# ── slide 8 — deploying ───────────────────────────────────────────────────────
add_bullet_slide("Deploying the Worker", [
    "One command deploys the Worker to Cloudflare's global edge network",
    "Credentials come from the global wrangler OAuth login (~/.config/wrangler/)",
    "Worker is live at: https://<name>.<account>.workers.dev",
    "Re-deploy any time you change edge/api-proxy.js or wrangler.toml",
], code="""\
# 1. Login once (opens browser — stores OAuth token globally)
npx wrangler login

# 2. Deploy
npm run deploy:edge
#  └─ runs: wrangler deploy

# 3. Verify
npx wrangler tail            # stream live request logs
curl https://myeds-xwalk-api.fsevin.workers.dev/api/geocode?name=Paris

# package.json shortcut
"scripts": {
  "dev:edge":    "wrangler dev",      # local: http://localhost:8787
  "deploy:edge": "wrangler deploy"
}""")

# ── slide 9 — connecting block ───────────────────────────────────────────────
add_bullet_slide("Connecting a Block to the Edge Function", [
    "The block JS must point to the Worker URL in production and localhost in dev",
    "Content structure: EDS renders table rows as nested <div> elements — no <p> tags",
    "  Query with: block.querySelector('div:first-child p, div:first-child div')",
    "Always set Content-Type: application/json; charset=utf-8 on Worker responses",
    "  Prevents mojibake on accented characters (e.g. Île-de-France)",
], code="""\
// blocks/myblock/myblock.js

const EDGE_ORIGIN = window.location.hostname === 'localhost'
  ? 'http://localhost:8787'
  : 'https://myeds-xwalk-api.fsevin.workers.dev';

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(\`HTTP \${res.status}\`);
  return res.json();
}

export default async function decorate(block) {
  // Read location from first cell (works with both <p> and <div> content)
  const location = block.querySelector('div:first-child p, div:first-child div')
    ?.textContent?.trim() || '';

  const data = await fetchJSON(\`\${EDGE_ORIGIN}/api/geocode?name=\${encodeURIComponent(location)}\`);
  block.innerHTML = \`<p>\${data.results?.[0]?.name}</p>\`;
}""")

# ── slide 10 — best practices ─────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, W, H, WHITE)
add_rect(s, 0, 0, Inches(0.18), H, RED)
add_text(s, "Best Practices & Summary",
         Inches(0.35), Inches(0.3), Inches(12.5), Inches(0.8),
         size=28, bold=True, color=RED)
sep = s.shapes.add_shape(1, Inches(0.35), Inches(1.05), Inches(12.6), Pt(2))
sep.fill.solid(); sep.fill.fore_color.rgb = RED; sep.line.fill.background()

headers = ["Step", "Action", "Notes"]
rows_data = [
    ["1. Create Worker",   "Add edge/api-proxy.js\nExport a fetch handler",          "Handle OPTIONS preflight\nReturn JSON with charset=utf-8"],
    ["2. Configure",       "Set name, main, vars\nin wrangler.toml",                  "Never put secrets in toml\nUse wrangler secret put"],
    ["3. CORS & Cache",    "Whitelist aem.live +\naem.page origins",                  "Cache stable data longer\n(geocode 24h, rates 5min)"],
    ["4. Local dev",       "npx wrangler dev\n→ localhost:8787",                      "Put AEM_TOKEN in .dev.vars\n(git-ignored)"],
    ["5. Deploy",          "npm run deploy:edge",                                      "Verify with wrangler tail\nor curl the worker URL"],
    ["6. Connect block",   "Set EDGE_ORIGIN by hostname\nQuery div, p selectors",     "Purge AEM CDN cache after\npushing JS changes"],
]

col_w = [Inches(2.1), Inches(3.8), Inches(4.5)]
col_x = [Inches(0.35), Inches(2.5), Inches(6.35)]
row_h = Inches(0.72)
header_y = Inches(1.2)

for ci, (hdr, cx, cw) in enumerate(zip(headers, col_x, col_w)):
    add_rect(s, cx, header_y, cw - Inches(0.05), Inches(0.45), BLACK)
    add_text(s, hdr, cx + Inches(0.08), header_y + Inches(0.05),
             cw - Inches(0.15), Inches(0.38),
             size=14, bold=True, color=WHITE)

for ri, row in enumerate(rows_data):
    ry = header_y + Inches(0.45) + ri * row_h
    bg = LGREY if ri % 2 == 0 else WHITE
    for ci, (cell, cx, cw) in enumerate(zip(row, col_x, col_w)):
        add_rect(s, cx, ry, cw - Inches(0.05), row_h - Inches(0.05), bg)
        add_text(s, cell, cx + Inches(0.08), ry + Inches(0.06),
                 cw - Inches(0.18), row_h - Inches(0.1),
                 size=12, color=DGREY)

add_text(s, "Adobe", Inches(0.35), H - Inches(0.5), Inches(1.5), Inches(0.4),
         size=13, bold=True, color=RED)
add_text(s, "©2024 Adobe. All Rights Reserved. Adobe Confidential.",
         Inches(8), H - Inches(0.5), Inches(5), Inches(0.4),
         size=9, color=RGBColor(0x99, 0x99, 0x99), align=PP_ALIGN.RIGHT)

# ── slide 11 — end ────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, W, H, RED)
add_text(s, "Adobe",
         Inches(5.9), Inches(3.3), Inches(1.6), Inches(0.7),
         size=30, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# ── save ──────────────────────────────────────────────────────────────────────
out = "/Users/sevin/Library/CloudStorage/OneDrive-Adobe/NEW/Workspace/EDS/myeds-xwalk/EDS-EdgeFunction-Guide.pptx"
prs.save(out)
print(f"Saved → {out}")

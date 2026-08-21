"""Generate Firefly Image Generation block implementation guide PPTX (Adobe branding)."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Adobe brand colours
RED = RGBColor(0xFF, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)
LGREY = RGBColor(0xF0, 0xF0, 0xF0)
DGREY = RGBColor(0x33, 0x33, 0x33)
CODE_BG = RGBColor(0xF5, 0xF5, 0xF5)

W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width = W
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
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return txb


def add_bullet_slide(title_text, bullets, code=None):
    slide = prs.slides.add_slide(BLANK)

    add_rect(slide, 0, 0, W, H, WHITE)
    add_rect(slide, 0, 0, Inches(0.18), H, RED)

    add_text(slide, title_text,
             Inches(0.35), Inches(0.3), Inches(12.5), Inches(0.8),
             size=28, bold=True, color=RED)

    sep = slide.shapes.add_shape(1, Inches(0.35), Inches(1.05), Inches(12.6), Pt(2))
    sep.fill.solid()
    sep.fill.fore_color.rgb = RED
    sep.line.fill.background()

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
                p = tf.paragraphs[0]
                first = False
            else:
                p = tf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = line
            run.font.size = Pt(11.5)
            run.font.bold = False
            run.font.color.rgb = DGREY
            run.font.name = "Courier New"

    add_text(slide, "Adobe",
             Inches(0.35), H - Inches(0.5), Inches(1.5), Inches(0.4),
             size=13, bold=True, color=RED)
    add_text(slide, "©2026 Adobe. All Rights Reserved. Adobe Confidential.",
             Inches(8), H - Inches(0.5), Inches(5), Inches(0.4),
             size=9, color=RGBColor(0x99, 0x99, 0x99), align=PP_ALIGN.RIGHT)

    return slide


# ── slide 1 — title ──────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, W, H, RED)
add_text(s, "Adobe Firefly Image Block",
         Inches(0.6), Inches(2.8), Inches(9), Inches(1),
         size=40, bold=False, color=WHITE)
add_text(s, "Building an AI Image-Generation Block for Edge Delivery Services",
         Inches(0.6), Inches(3.75), Inches(10), Inches(0.6),
         size=20, bold=True, color=WHITE)
add_text(s, "Adobe Experience Manager — Developer Guide",
         Inches(0.6), Inches(4.35), Inches(8), Inches(0.5),
         size=18, bold=False, color=WHITE)
add_text(s, "Adobe",
         Inches(0.6), Inches(1.8), Inches(2), Inches(0.6),
         size=22, bold=True, color=WHITE)

# ── slide 2 — agenda ─────────────────────────────────────────────────────────
add_bullet_slide("Agenda", [
    "Why Firefly calls need a server-side proxy",
    "Architecture overview",
    "Step 1 — Add the Firefly route to the edge Worker",
    "Step 2 — Adobe IMS client_credentials authentication",
    "Step 3 — Configure wrangler.toml & secrets",
    "Step 4 — Build the block: model, JS, CSS",
    "Step 5 — Register the block & deploy",
    "Step 6 — Test and troubleshoot real errors we hit",
    "Step 7 — Commit & push",
    "Best Practices & Summary",
])

# ── slide 3 — why a proxy ─────────────────────────────────────────────────────
add_bullet_slide("Why Firefly Needs a Server-Side Proxy", [
    "Firefly's Generate Image API requires two credentials on every call:",
    "  Authorization: Bearer <IMS access token>",
    "  x-api-key: <client_id>",
    "The IMS access token itself is obtained via a client_credentials exchange",
    "using client_id + client_secret — the secret must never reach the browser",
    "",
    "So the block never calls firefly-api.adobe.io directly.",
    "It calls our own Cloudflare Worker, which holds the secret and proxies the request",
    "— the exact same pattern already used for the AEM GraphQL \"rates\" block (AEM_TOKEN)",
])

# ── slide 4 — architecture ────────────────────────────────────────────────────
add_bullet_slide("Architecture Overview", [
    "1. Author enters a Prompt + Aspect ratio in the Universal Editor",
    "2. blocks/firefly/firefly.js reads the authored text out of the block's <div>s",
    "3. Block POSTs { prompt, size } to the edge Worker: /api/firefly/generate",
    "4. Worker exchanges client_id + client_secret for an IMS access token",
    "   (cached in-isolate until near expiry — avoids re-authenticating every request)",
    "5. Worker calls POST https://firefly-api.adobe.io/v3/images/generate",
    "6. Worker returns only { url } — a pre-signed, time-limited image URL — to the block",
    "7. Block renders an <img> pointing at that URL",
], code="""\
Author (Universal Editor)
        │  prompt, aspectRatio
        ▼
blocks/firefly/firefly.js  ──POST /api/firefly/generate──▶  edge/api-proxy.js (Cloudflare Worker)
                                                                     │
                                                     client_credentials + Adobe IMS
                                                                     ▼
                                                     POST /v3/images/generate (Firefly API)
                                                                     │
                                                              { url } ◀──── image result""")

# ── slide 5 — step 1: worker route ───────────────────────────────────────────
add_bullet_slide("Step 1 — Add the Firefly Route to the Edge Worker", [
    "Extend the existing edge/api-proxy.js — don't create a second Worker",
    "New handler validates the prompt, resolves a size, then calls Firefly",
    "Only { url } is returned to the browser — never the token or client_secret",
], code="""\
async function handleFireflyGenerate(request, env, cors) {
  const body = await request.json();
  const prompt = body?.prompt?.trim();
  if (!prompt) return jsonError('Missing prompt', 400, cors);

  const size = FIREFLY_VALID_SIZES.includes(body?.size) ? body.size : '1024x1024';
  const [width, height] = size.split('x').map(Number);

  const token = await getFireflyToken(env);

  const res = await fetch('https://firefly-api.adobe.io/v3/images/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
      'x-api-key': env.FIREFLY_CLIENT_ID,
    },
    body: JSON.stringify({ prompt, size: { width, height }, numVariations: 1 }),
  });

  const data = await res.json();
  return new Response(JSON.stringify({ url: data.outputs[0].image.url }),
    { status: 200, headers: { 'Content-Type': 'application/json', ...cors } });
}""")

# ── slide 6 — step 2: IMS auth ───────────────────────────────────────────────
add_bullet_slide("Step 2 — Adobe IMS client_credentials Authentication", [
    "IMS access tokens are short-lived (~24h) — cache in a module-level variable",
    "so the Worker doesn't re-authenticate on every single image request",
    "Refresh a minute early to avoid using a token that expires mid-flight",
    "Also relax the Worker's route dispatch to allow POST only for this one route",
    "(every other route in api-proxy.js stays GET-only)",
], code="""\
let cachedImsToken = null;
let cachedImsTokenExpiry = 0;

async function getFireflyToken(env) {
  if (cachedImsToken && Date.now() < cachedImsTokenExpiry) return cachedImsToken;

  const res = await fetch('https://ims-na1.adobelogin.com/ims/token/v3', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: env.FIREFLY_CLIENT_ID,
      client_secret: env.FIREFLY_CLIENT_SECRET,
      scope: env.FIREFLY_SCOPES,
    }),
  });

  const data = await res.json();
  cachedImsToken = data.access_token;
  cachedImsTokenExpiry = Date.now() + ((data.expires_in - 60) * 1000);
  return cachedImsToken;
}""")

# ── slide 7 — step 3: wrangler.toml ──────────────────────────────────────────
add_bullet_slide("Step 3 — Configure wrangler.toml & Secrets", [
    "client_id is not sensitive — commit it as a plain [vars] entry",
    "client_secret IS sensitive — set it only as an encrypted Worker secret, never in git",
    "Mirror the existing AEM_TOKEN convention already used for the rates block",
], code="""\
[vars]
FIREFLY_CLIENT_ID = "86c5ad4a573c4f198adec39064c6cbbd"
FIREFLY_SCOPES = "openid,AdobeID,session,additional_info,read_organizations,firefly_api,ff_apis"

# Firefly client secret — store as a secret, never commit it:
#   npx wrangler secret put FIREFLY_CLIENT_SECRET
# For local dev, add to a .dev.vars file (git-ignored):
#   FIREFLY_CLIENT_SECRET=<your-client-secret>""")

# ── slide 8 — step 4a: block model ───────────────────────────────────────────
add_bullet_slide("Step 4 — Build the Block: Authoring Model", [
    "blocks/<name>/_<name>.json declares the Universal Editor fields for the block",
    "\"prompt\" — required richtext field the author fills in",
    "\"aspectRatio\" — optional select field mapped to Firefly's supported sizes",
    "This file is auto-merged into the root component-*.json files at build time",
], code="""\
// blocks/firefly/_firefly.json
{
  "models": [{
    "id": "firefly",
    "fields": [
      { "component": "richtext", "name": "prompt", "label": "Prompt",
        "valueType": "string", "required": true },
      { "component": "select", "name": "aspectRatio", "label": "Aspect ratio",
        "valueType": "string",
        "options": [
          { "name": "Square (1024x1024)",    "value": "1024x1024" },
          { "name": "Landscape (1344x768)",  "value": "1344x768" },
          { "name": "Portrait (768x1344)",   "value": "768x1344" }
        ] }
    ]
  }]
}""")

# ── slide 9 — step 4b: block js ──────────────────────────────────────────────
add_bullet_slide("Step 4 — Build the Block: firefly.js", [
    "Read authored text straight out of the block's <div> children (same as weather.js)",
    "Show a loading state, POST to the Worker, then swap in the resulting <img>",
    "Same EDGE_ORIGIN localhost/production switch used by every other block",
], code="""\
const EDGE_ORIGIN = window.location.hostname === 'localhost'
  ? 'http://localhost:8787' : 'https://myeds-xwalk-api.fsevin.workers.dev';

export default async function decorate(block) {
  const prompt = block.querySelector('div:first-child p, div:first-child div')
    ?.textContent?.trim() || '';
  const aspectRatio = block.querySelector('div:nth-child(2) p, div:nth-child(2) div')
    ?.textContent?.trim() || '1024x1024';

  block.innerHTML = '<div class="firefly-loading">Generating image…</div>';
  try {
    const res = await fetch(`${EDGE_ORIGIN}/api/firefly/generate`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, size: aspectRatio }),
    });
    const { url } = await res.json();
    const img = document.createElement('img');
    img.src = url; img.alt = prompt; img.className = 'firefly-image';
    block.innerHTML = ''; block.append(img);
  } catch (e) {
    block.innerHTML = '<p class="firefly-error">Unable to generate image right now.</p>';
  }
}""")

# ── slide 10 — step 5: register & deploy ─────────────────────────────────────
add_bullet_slide("Step 5 — Register the Block & Deploy", [
    "No manual registry — a new blocks/<name>/ folder is auto-discovered by aem.js",
    "Run build:json to merge _firefly.json into the root component-*.json files",
    "so the block's fields show up as authoring options in the Universal Editor",
    "Deploy the Worker separately from the EDS site — the site itself deploys",
    "automatically via the AEM Code Sync GitHub App",
], code="""\
# Merge blocks/firefly/_firefly.json into the root component config
npm run build:json
#  → writes component-models.json, component-definition.json, component-filters.json

# Deploy the Cloudflare Worker (the EDS site deploys itself on git push)
npm run deploy:edge
#  → runs: wrangler deploy
#  → live at https://myeds-xwalk-api.fsevin.workers.dev""")

# ── slide 11 — step 6: troubleshooting ───────────────────────────────────────
add_bullet_slide("Step 6 — Test & Troubleshoot", [
    "Bug 1 — 502 \"Firefly authentication failed\"",
    "  Cause: wrangler.toml still had the placeholder FIREFLY_CLIENT_ID",
    "  Fix: set the real client_id, then npm run deploy:edge",
    "",
    "Bug 2 — 502 \"Firefly generate failed: 406 Unsupported Accept Type\"",
    "  Cause 1: outbound fetch() to Firefly was missing an explicit Accept header",
    "  Fix: add Accept: 'application/json' to the request headers",
    "  Cause 2: the sandbox Postman env's IMS scope string was incomplete",
    "  Fix: use the full scope list — openid,AdobeID,session,additional_info,",
    "       read_organizations,firefly_api,ff_apis",
], code="""\
# Debug directly against the deployed Worker (bypasses the browser/block entirely)
curl -s -X POST https://myeds-xwalk-api.fsevin.workers.dev/api/firefly/generate \\
  -H "Content-Type: application/json" \\
  -H "Origin: https://main--myeds-xwalk--fsevin.aem.live" \\
  -d '{"prompt":"a red panda skateboarding through Shibuya at night"}'
# → {"url":"https://pre-signed-firefly-prod.s3-accelerate.amazonaws.com/..."}""")

# ── slide 12 — step 7: commit & push ─────────────────────────────────────────
add_bullet_slide("Step 7 — Commit & Push", [
    "Commit the source + regenerated config; never commit local dev/cache state",
], code="""\
git add edge/api-proxy.js wrangler.toml \\
        blocks/firefly/_firefly.json blocks/firefly/firefly.js blocks/firefly/firefly.css \\
        component-models.json component-definition.json component-filters.json \\
        models/_section.json

git commit -m "Add Firefly image generation block"
git push

# Excluded on purpose:
#   .dev.vars              — local secrets, git-ignored
#   .wrangler/state/...    — local Workers dev cache, not source""")

# ── slide 13 — best practices summary table ──────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, W, H, WHITE)
add_rect(s, 0, 0, Inches(0.18), H, RED)
add_text(s, "Best Practices & Summary",
         Inches(0.35), Inches(0.3), Inches(12.5), Inches(0.8),
         size=28, bold=True, color=RED)
sep = s.shapes.add_shape(1, Inches(0.35), Inches(1.05), Inches(12.6), Pt(2))
sep.fill.solid()
sep.fill.fore_color.rgb = RED
sep.line.fill.background()

headers = ["Step", "Action", "Notes"]
rows_data = [
    ["1. Worker route",  "Add handleFireflyGenerate()\nto edge/api-proxy.js",       "Never return the IMS token\nor client_secret to the browser"],
    ["2. IMS auth",      "client_credentials exchange,\ncache token in-isolate",     "Refresh 60s before expiry\nto avoid mid-flight failures"],
    ["3. Secrets",       "client_id in [vars],\nclient_secret via wrangler secret",  "Add a .dev.vars line for\nlocal wrangler dev"],
    ["4. Block files",   "_firefly.json, firefly.js,\nfirefly.css",                  "Read authored text via\ndiv:nth-child(n) selectors"],
    ["5. Register",      "npm run build:json",                                       "Merges into component-\nmodels/definition/filters.json"],
    ["6. Deploy & test", "npm run deploy:edge,\ncurl the Worker directly",           "Check Accept header +\nIMS scopes on 406/502s"],
    ["7. Commit",        "git add source + generated\nJSON, exclude local state",    "Never commit .dev.vars\nor .wrangler/ cache"],
]

col_w = [Inches(2.1), Inches(3.8), Inches(4.5)]
col_x = [Inches(0.35), Inches(2.5), Inches(6.35)]
row_h = Inches(0.68)
header_y = Inches(1.2)

for hdr, cx, cw in zip(headers, col_x, col_w):
    add_rect(s, cx, header_y, cw - Inches(0.05), Inches(0.45), BLACK)
    add_text(s, hdr, cx + Inches(0.08), header_y + Inches(0.05),
             cw - Inches(0.15), Inches(0.38),
             size=14, bold=True, color=WHITE)

for ri, row in enumerate(rows_data):
    ry = header_y + Inches(0.45) + ri * row_h
    bg = LGREY if ri % 2 == 0 else WHITE
    for cell, cx, cw in zip(row, col_x, col_w):
        add_rect(s, cx, ry, cw - Inches(0.05), row_h - Inches(0.05), bg)
        add_text(s, cell, cx + Inches(0.08), ry + Inches(0.06),
                 cw - Inches(0.18), row_h - Inches(0.1),
                 size=11.5, color=DGREY)

add_text(s, "Adobe", Inches(0.35), H - Inches(0.5), Inches(1.5), Inches(0.4),
         size=13, bold=True, color=RED)
add_text(s, "©2026 Adobe. All Rights Reserved. Adobe Confidential.",
         Inches(8), H - Inches(0.5), Inches(5), Inches(0.4),
         size=9, color=RGBColor(0x99, 0x99, 0x99), align=PP_ALIGN.RIGHT)

# ── slide 14 — end ────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, W, H, RED)
add_text(s, "Adobe",
          Inches(5.9), Inches(3.3), Inches(1.6), Inches(0.7),
          size=30, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# ── save ──────────────────────────────────────────────────────────────────────
out = "/Users/sevin/Library/CloudStorage/OneDrive-Adobe/NEW/Workspace/EDS/myeds-xwalk/docs/Firefly-Block-Build-Guide.pptx"
prs.save(out)
print(f"Saved → {out}")

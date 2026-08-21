"""Generate Product Variant (product-variant) block implementation guide PPTX (Adobe branding)."""
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


def add_footer(slide):
    add_text(slide, "Adobe", Inches(0.35), H - Inches(0.5), Inches(1.5), Inches(0.4),
             size=13, bold=True, color=RED)
    add_text(slide, "©2026 Adobe. All Rights Reserved. Adobe Confidential.",
             Inches(8), H - Inches(0.5), Inches(5), Inches(0.4),
             size=9, color=RGBColor(0x99, 0x99, 0x99), align=PP_ALIGN.RIGHT)


def add_header(slide, title_text):
    add_rect(slide, 0, 0, W, H, WHITE)
    add_rect(slide, 0, 0, Inches(0.18), H, RED)
    add_text(slide, title_text,
             Inches(0.35), Inches(0.3), Inches(12.5), Inches(0.8),
             size=28, bold=True, color=RED)
    sep = slide.shapes.add_shape(1, Inches(0.35), Inches(1.05), Inches(12.6), Pt(2))
    sep.fill.solid()
    sep.fill.fore_color.rgb = RED
    sep.line.fill.background()


def add_bullet_slide(title_text, bullets, code=None):
    slide = prs.slides.add_slide(BLANK)
    add_header(slide, title_text)

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

    add_footer(slide)
    return slide


def add_table_slide(title_text, headers, rows_data, col_w, col_x, row_h, header_y=Inches(1.2)):
    s = prs.slides.add_slide(BLANK)
    add_header(s, title_text)

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

    add_footer(s)
    return s


# ── slide 1 — title ──────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, W, H, RED)
add_text(s, "The product-variant Block",
         Inches(0.6), Inches(2.8), Inches(11), Inches(1),
         size=40, bold=False, color=WHITE)
add_text(s, "Contextual Product Photo Variants via Firefly Structure Reference",
         Inches(0.6), Inches(3.75), Inches(11.5), Inches(0.6),
         size=20, bold=True, color=WHITE)
add_text(s, "Adobe Experience Manager — Developer Guide",
         Inches(0.6), Inches(4.35), Inches(8), Inches(0.5),
         size=18, bold=False, color=WHITE)
add_text(s, "Adobe",
         Inches(0.6), Inches(1.8), Inches(2), Inches(0.6),
         size=22, bold=True, color=WHITE)

# ── slide 2 — agenda ─────────────────────────────────────────────────────────
add_bullet_slide("Agenda", [
    "What product-variant does, and why Structure Reference",
    "Architecture overview",
    "Step 1 — Authoring model: productImage, prompt, aspectRatio, resultImage",
    "Step 2 — Edge Worker route: upload image, generate with structure reference",
    "Step 3 — Block JS: source photo, persisted result, or published fallback",
    "Step 4 — Auto-generate on prompt entry (debounced), shared DAM-persist helpers",
    "Step 5 — Register the block (build:json + section filter)",
    "Step 6 — Deploy the Worker (a separate step from the code push!)",
    "Real example — tennis racquet, two variants",
    "Issues hit along the way — and how each was diagnosed",
    "Best Practices & Summary",
])

# ── slide 3 — what & why ─────────────────────────────────────────────────────
add_bullet_slide("What It Does, and Why Structure Reference", [
    "Author picks an existing product photo and writes a prompt describing",
    "a variation — seasonal, regional, or promotional",
    "Goal: keep the product recognizable, change only its context",
    "",
    "Firefly's Structure Reference (v3/images/generate) uses a reference",
    "image to carry over shape, outline and composition into a newly",
    "generated scene driven by the text prompt",
    "  Reuses the same Firefly Services credentials already configured",
    "  for the firefly/ai-image blocks — no new Adobe product/entitlement",
    "",
    "Alternative considered: Generative Fill + auto background mask for",
    "pixel-perfect product preservation — rejected for v1, it needs the",
    "separate Photoshop API (different credentials/entitlement)",
])

# ── slide 4 — architecture ────────────────────────────────────────────────────
add_bullet_slide("Architecture Overview", [
    "1. Author picks a Product image and types a Prompt (+ aspect ratio)",
    "2. 1.2s after the last edit, the block reads the photo's own <img> bytes",
    "3. Bytes + prompt are POSTed as multipart form data to the edge Worker",
    "4. Worker uploads the photo to Firefly's storage API for an uploadId,",
    "   then calls Generate Images with structure.imageReference = uploadId",
    "5. Worker streams the resulting image bytes straight back",
    "6. Block shows an inline preview, then persists to AEM DAM and patches",
    "   its own \"resultImage\" property — same pattern as ai-image",
    "7. Page reloads — later renders (author or published) just show the",
    "   persisted <picture>, no further Firefly calls",
], code="""\
Author picks photo + types prompt
        │  (debounced 1.2s)
        ▼
product-variant.js  ──POST /api/firefly/generate-variant──▶  edge/api-proxy.js
   (multipart: image bytes, prompt, size)        │
        │                              POST /v2/storage/image  → uploadId
        │                              POST /v3/images/generate
        │                                structure.imageReference.source.uploadId
        ▼
  inline preview
        │
        ├── uploadToDam() / patchBlockImage('resultImage', ...)
        └── window.location.reload()""")

# ── slide 5 — step 1: model ───────────────────────────────────────────────────
add_bullet_slide("Step 1 — Authoring Model", [
    "productImage (reference, required) — the source product photo",
    "prompt (richtext, required) — the desired variation, in plain English",
    "aspectRatio (select) — same 3 sizes as firefly/ai-image",
    "resultImage (reference) — written programmatically, never picked",
    "",
    "Only 4 top-level fields: the project's xwalk ESLint rules cap a block",
    "at 4 cells (max-cells). A first draft also had variationType and",
    "strength select fields — folded into prompt guidance text and a",
    "hardcoded server-side default instead of blowing the field budget",
], code="""\
// blocks/product-variant/_product-variant.json
{ "models": [{
  "id": "product-variant",
  "fields": [
    { "component": "reference", "name": "productImage",
      "label": "Product image", "required": true },
    { "component": "richtext", "name": "prompt", "label": "Prompt",
      "description": "e.g. 'a Christmas edition with festive wrapping'",
      "required": true },
    { "component": "select", "name": "aspectRatio", "label": "Aspect ratio",
      "options": [ /* 1024x1024, 1344x768, 768x1344 */ ] },
    { "component": "reference", "name": "resultImage",
      "label": "Generated variant" }
  ]
}]}""")

# ── slide 6 — step 2: worker route ───────────────────────────────────────────
add_bullet_slide("Step 2 — Edge Worker: Upload + Structure Reference", [
    "Reuses getFireflyToken() — the same cached IMS client_credentials",
    "auth as firefly/ai-image, no duplicated auth logic",
    "New helper uploads the photo bytes to Firefly's storage API and",
    "returns an uploadId, which is then passed as a structure reference",
    "Route reads multipart form data (an image file is attached), unlike",
    "the JSON-bodied firefly/ai-image routes",
], code="""\
// edge/api-proxy.js
async function uploadImageToFirefly(bytes, mimeType, env) {
  const token = await getFireflyToken(env);
  const res = await fetch('https://firefly-api.adobe.io/v2/storage/image', {
    method: 'POST',
    headers: { 'Content-Type': mimeType, Authorization: `Bearer ${token}`,
               'x-api-key': env.FIREFLY_CLIENT_ID },
    body: bytes,
  });
  return (await res.json()).images[0].id;                     // uploadId
}

async function fireflyGenerateVariant(prompt, size, uploadId, strength, env) {
  // POST /v3/images/generate  { prompt, size, contentClass: 'photo',
  //   structure: { strength, imageReference: { source: { uploadId } } } }
}
// Route: POST /api/firefly/generate-variant  (multipart: image, prompt, size)""")

# ── slide 7 — step 3: block js reading state ─────────────────────────────────
add_bullet_slide("Step 3 — Reading Block State: Source, Result, or Neither", [
    "Two reference fields means two possible <picture> elements — can't",
    "just do block.querySelector('picture') like ai-image did",
    "Fields read positionally by index, matching JSON field declaration",
    "order: productImage=1, prompt=2, aspectRatio=3, resultImage=4",
    "resultImage present → render it, done (works on published pages too)",
    "No data-aue-resource (not the UE canvas) → fall back to the original",
    "product photo untouched, so the page is never empty",
], code="""\
// Field order mirrors _product-variant.json — each field is a direct child div.
function fieldPicture(block, index) {
  return block.querySelector(`:scope > div:nth-child(${index}) picture`);
}

const sourcePicture = fieldPicture(block, 1);   // productImage
const resultPicture = fieldPicture(block, 4);   // resultImage

if (resultPicture) { /* render persisted variant, return */ }
if (!sourcePicture) return;               // required field still empty
if (!resource) { /* published page: render the original product photo */ }""")

# ── slide 8 — step 4: debounce + shared persistence ──────────────────────────
add_bullet_slide("Step 4 — Auto-Generate, Shared DAM Persistence", [
    "Same debounce + in-flight-guard pattern as ai-image (1.2s, keyed by",
    "resource) — Universal Editor re-runs decorate() on every field edit",
    "The photo's bytes come from fetch(sourceImg.src) in the browser, not",
    "the Worker — the browser already has the authenticated session that",
    "rendered that <img>, so no extra server-side auth is needed",
    "Extracted getCsrfToken/uploadToDam/patchBlockImage out of ai-image.js",
    "into scripts/dam-persist.js — both blocks import the same helpers",
    "instead of duplicating ~50 lines",
], code="""\
// blocks/product-variant/product-variant.js
import { getCsrfToken, uploadToDam, patchBlockImage } from '../../scripts/dam-persist.js';

const sourceBlob = await (await fetch(sourceImg.src, { credentials: 'include' })).blob();
const form = new FormData();
form.append('image', sourceBlob, 'product.jpg');
form.append('prompt', prompt);
form.append('size', size);
const blob = await (await fetch(`${EDGE_ORIGIN}/api/firefly/generate-variant`,
  { method: 'POST', body: form })).blob();

const assetPath = await uploadToDam(blob, mimeType, csrfToken, 'product-variant');
await patchBlockImage(resourcePath, 'resultImage', assetPath, csrfToken);""")

# ── slide 9 — step 5: registration ───────────────────────────────────────────
add_bullet_slide("Step 5 — Registering the Block", [
    "_product-variant.json is auto-picked up by the existing",
    "../blocks/*/_*.json globs in models/_component-models.json and",
    "models/_component-definition.json — no manual registration there",
    "But a block also needs to be added to every filter that should allow",
    "it — here, models/_section.json's \"section\" filter component list",
    "The block's id must match exactly in every one of those three places",
    "(a components-list typo silently hides the block from the picker",
    "with no error anywhere — it just never appears)",
    "Run npm run build:json to regenerate the merged root JSON files",
], code="""\
// models/_section.json
{ "filters": [{
  "id": "section",
  "components": [
    "text", "image", "button", "title", "hero", "cards", "columns",
    "fragment", "teaser", "weather", "rates", "firefly", "ai-image",
    "product-variant"        // must exactly match the block's own "id"
  ]
}]}

$ npm run build:json   # regenerates component-{models,definition,filters}.json""")

# ── slide 10 — step 6: deploy ─────────────────────────────────────────────────
add_bullet_slide("Step 6 — Deploying the Worker (Easy to Miss!)", [
    "This project has two independent deploy targets that a single",
    "git push does NOT both update:",
    "  EDS code bus (blocks/**, component-*.json) — auto-synced from",
    "  GitHub on push, serves the block's JS/CSS/model to Universal Editor",
    "  Cloudflare Worker (edge/api-proxy.js) — requires an explicit",
    "  wrangler deploy; git push alone leaves the old Worker code running",
    "Pushing new Worker routes without redeploying looks exactly like a",
    "generic \"Failed to fetch\" in the block — see the issues table next",
], code="""\
$ npm run build:json && npm run lint     # regenerate + verify
$ git add <changed files> && git commit -m "..."
$ git push origin main                   # updates EDS code bus only

$ npm run deploy:edge                    # a.k.a. `wrangler deploy`
                                          # updates the Cloudflare Worker""")

# ── slide 11 — real example ───────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "Real Example — Tennis Racquet")
add_text(s, "Same racquet silhouette, head shape and grip carried through both variants:",
         Inches(0.5), Inches(1.15), Inches(12.2), Inches(0.4), size=15, color=DGREY)

img_h = Inches(4.6)
s.shapes.add_picture(
    "/Users/sevin/Library/CloudStorage/OneDrive-Adobe/NEW/Workspace/EDS/myeds-xwalk/docs/head-racket.jpg",
    Inches(0.5), Inches(1.7), height=img_h)
s.shapes.add_picture("/tmp/racket-variant.jpg", Inches(4.75), Inches(1.7), height=img_h)
s.shapes.add_picture("/tmp/prod-variant-test.jpg", Inches(9.0), Inches(1.7), height=img_h)

add_text(s, "Original product photo", Inches(0.5), Inches(6.4), Inches(4.0), Inches(0.4),
         size=13, bold=True, color=DGREY, align=PP_ALIGN.CENTER)
add_text(s, "Prompt: \"...festive Christmas display\nwith a decorated tree...\"",
         Inches(4.75), Inches(6.4), Inches(4.0), Inches(0.7),
         size=12, color=DGREY, align=PP_ALIGN.CENTER)
add_text(s, "Prompt: \"...on a beach in summer\nwith sunshine and palm trees\"",
         Inches(9.0), Inches(6.4), Inches(4.0), Inches(0.7),
         size=12, color=DGREY, align=PP_ALIGN.CENTER)
add_footer(s)

# ── slide 12 — issues table ────────────────────────────────────────────────────
add_table_slide("Issues Hit Along the Way",
    ["Symptom", "Root Cause", "Fix"],
    [
        ["ESLint error: \"Avoid using more\nthan 4 cells\" on the model",
         "xwalk's max-cells rule caps a\nblock at 4 top-level fields;\nfirst draft had 6",
         "Dropped variationType/strength\nfields; folded guidance into the\nprompt field's description"],
        ["Worker: \"IMS token request\nfailed: 400\" on every call",
         ".dev.vars had a literal\nplaceholder string for\nFIREFLY_CLIENT_SECRET",
         "Called IMS directly with curl to\nconfirm invalid_client, then\npasted the real rotated secret"],
        ["Block never appears in\nUniversal Editor after push",
         "EDS code bus hadn't re-synced\nfrom GitHub in 5 days — a\nGitHub–code-sync gap, not a\ncontent bug",
         "Confirmed via admin.hlx.page\n/code status; forced a resync\nwith a POST to the same endpoint"],
        ["Block exists but still isn't\nselectable inside a Section",
         "models/_section.json filter\nlisted \"products-variant\"\n(typo) instead of the block's\nreal id",
         "Fixed the id to match exactly\nacross _product-variant.json,\n_section.json and the block folder"],
        ["\"Something went wrong:\nFailed to fetch\" in the editor",
         "git push updates EDS code\nonly — the Cloudflare Worker\nstill ran old code with no\n/generate-variant route",
         "npm run deploy:edge; verified\nwith a direct curl against the\nWorker before retesting in UE"],
    ],
    col_w=[Inches(3.6), Inches(4.2), Inches(4.6)],
    col_x=[Inches(0.35), Inches(4.05), Inches(8.35)],
    row_h=Inches(1.05))

# ── slide 13 — best practices summary table ──────────────────────────────────
add_table_slide("Best Practices & Summary",
    ["Step", "Action", "Notes"],
    [
        ["1. Model", "productImage, prompt,\naspectRatio, resultImage", "Keep to ≤4 fields —\nxwalk's max-cells lint rule"],
        ["2. Worker route", "Upload photo → uploadId →\nstructure-reference generate", "Reuse existing IMS auth,\ndon't duplicate it"],
        ["3. Read block state", "Query fields by position,\nnot generic querySelector", "Needed once a block has\nmore than one image field"],
        ["4. Auto-generate", "Debounce + in-flight guard,\nshared dam-persist.js", "Extract shared helpers\ninstead of copy-pasting"],
        ["5. Register", "Add the block id to every\nrelevant filter, then build:json", "A typo hides the block with\nno visible error anywhere"],
        ["6. Deploy", "git push (code) AND\nwrangler deploy (Worker)", "Two independent targets —\neasy to update only one"],
        ["7. Verify", "curl the Worker route\ndirectly before testing in UE", "Isolates Worker bugs from\nAEM/UE/code-sync bugs"],
    ],
    col_w=[Inches(2.1), Inches(3.8), Inches(4.5)],
    col_x=[Inches(0.35), Inches(2.5), Inches(6.35)],
    row_h=Inches(0.68))

# ── slide 14 — end ────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, W, H, RED)
add_text(s, "Adobe",
         Inches(5.9), Inches(3.3), Inches(1.6), Inches(0.7),
         size=30, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# ── save ──────────────────────────────────────────────────────────────────────
out = "/Users/sevin/Library/CloudStorage/OneDrive-Adobe/NEW/Workspace/EDS/myeds-xwalk/docs/Product-Variant-Block-Build-Guide.pptx"
prs.save(out)
print(f"Saved → {out}")

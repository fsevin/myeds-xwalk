"""Generate Video Player (video-player) block usage + implementation guide PPTX (Adobe branding)."""
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
add_text(s, "The video-player Block",
         Inches(0.6), Inches(2.8), Inches(11), Inches(1),
         size=40, bold=False, color=WHITE)
add_text(s, "DAM-Sourced Video Playback with Autoplay, Loop & Poster Options",
         Inches(0.6), Inches(3.75), Inches(11.5), Inches(0.6),
         size=20, bold=True, color=WHITE)
add_text(s, "Adobe Experience Manager — Author & Developer Guide",
         Inches(0.6), Inches(4.35), Inches(8), Inches(0.5),
         size=18, bold=False, color=WHITE)
add_text(s, "Adobe",
         Inches(0.6), Inches(1.8), Inches(2), Inches(0.6),
         size=22, bold=True, color=WHITE)

# ── slide 2 — agenda ─────────────────────────────────────────────────────────
add_bullet_slide("Agenda", [
    "What video-player does, and why a native <video> element",
    "How authors use it — step by step in Universal Editor",
    "Step 1 — Content model: video, poster, classes (options)",
    "Step 2 — The markup contract: reference fields become <a> and <picture>",
    "Step 3 — Block JS: reading fields, building the <video> element",
    "Step 4 — Styling (video-player.css)",
    "Step 5 — Registering the block (build:json + section filter)",
    "Publishing tips — Cloud Configuration & DAM asset publishing",
    "Issues hit along the way — the Varnish 404 story",
    "Best Practices & Summary",
])

# ── slide 3 — what & why ─────────────────────────────────────────────────────
add_bullet_slide("What It Does, and Why a Native <video> Element", [
    "Author picks any video asset from the DAM, plus an optional poster",
    "(thumbnail) image, and toggles a handful of playback options",
    "Renders a plain HTML5 <video> tag — no third-party player library,",
    "no extra JS payload, works everywhere without a load-time dependency",
    "",
    "Options are authored as simple checkboxes (multiselect \"Options\"",
    "field) rather than four separate boolean fields — matches the",
    "documented \"classes\" block-options convention used elsewhere in EDS",
    "  Autoplay — starts playing as soon as the video is visible",
    "  Loop — restarts automatically when it reaches the end",
    "  Muted — silences audio (forced on automatically if Autoplay is set)",
    "  Hide controls — removes the native play/pause/scrub bar",
])

# ── slide 4 — how authors use it ─────────────────────────────────────────────
add_bullet_slide("How Authors Use It", [
    "1. In Universal Editor, add a Section, then insert the",
    "   \"Video Player\" block from the Blocks group",
    "2. Click the Video field → pick a video asset from the DAM",
    "   (e.g. /content/dam/myeds-xwalk/video/fs-tennis.mp4)",
    "3. Optionally click Poster image → pick a thumbnail image",
    "   shown before playback starts / while the video loads",
    "4. Under Options, check any combination of Autoplay, Loop,",
    "   Muted, Hide controls that fits the use case",
    "5. Preview the page — then Publish the page AND publish the",
    "   video asset itself (see \"Publishing Tips\" — this step is",
    "   easy to miss and is the #1 cause of a video not appearing)",
])

# ── slide 5 — step 1: content model ──────────────────────────────────────────
add_bullet_slide("Step 1 — Content Model", [
    "video (reference, required) — the DAM video asset",
    "poster (reference) — optional DAM image used as the poster thumbnail",
    "classes (multiselect, named \"classes\") — Autoplay / Loop / Muted /",
    "Hide controls — authored as checkboxes, rendered as CSS classes",
    "directly on the block itself (not as a child div/field cell)",
    "",
    "Only 3 top-level fields — kept deliberately small and matches the",
    "\"classes\" block-options convention documented for EDS block models",
], code="""\
// blocks/video-player/_video-player.json
{ "models": [{
  "id": "video-player",
  "fields": [
    { "component": "reference", "name": "video", "label": "Video",
      "description": "Select a video asset from the DAM", "required": true },
    { "component": "reference", "name": "poster", "label": "Poster image",
      "description": "Optional thumbnail shown before the video plays" },
    { "component": "multiselect", "name": "classes", "label": "Options",
      "options": [
        { "name": "Autoplay", "value": "autoplay" },
        { "name": "Loop", "value": "loop" },
        { "name": "Muted", "value": "muted" },
        { "name": "Hide controls", "value": "hide-controls" }
      ] }
  ]
}]}""")

# ── slide 6 — step 2: markup contract ────────────────────────────────────────
add_bullet_slide("Step 2 — The Markup Contract Matters", [
    "Not all \"reference\" fields render the same way once published:",
    "  An image reference (poster) renders as <picture><img> — EDS's",
    "  media bus automatically fetches and rehosts these into the site's",
    "  own content bus at publish time (as ./media_xxxx.png)",
    "  A non-image reference (video) renders as a plain <a href=\"...\">",
    "  pointing at the raw /content/dam/... path — the media bus does",
    "  NOT rehost it, so that path must be reachable on its own",
    "",
    "This distinction is the reason video needs extra publishing steps",
    "that an image field never needs — see \"Publishing Tips\" ahead",
], code="""\
<!-- rendered block markup, field order: video, poster -->
<div class="video-player autoplay muted">
  <div><a href="/content/dam/myeds-xwalk/video/fs-tennis.mp4">...</a></div>
  <div><picture><img src="./media_1a2b3c.png" alt=""></picture></div>
</div>""")

# ── slide 7 — step 3: block js ───────────────────────────────────────────────
add_bullet_slide("Step 3 — Block JS: Reading Fields, Building <video>", [
    "Fields are read positionally by index, matching the JSON field",
    "declaration order — same convention as ai-image/product-variant",
    "Options are read as CSS classes on the block itself via classList",
    "(the \"classes\" multiselect field's rendering contract)",
    "Autoplay forces Muted + playsInline — browsers block unmuted,",
    "non-inline autoplay outright, so this keeps the option honest",
    "No video selected yet → block renders nothing (empty state while",
    "the author is still filling in the required field)",
], code="""\
// blocks/video-player/video-player.js
function fieldLink(block, index) {
  return block.querySelector(`:scope > div:nth-child(${index}) a`);
}
function fieldPicture(block, index) {
  return block.querySelector(`:scope > div:nth-child(${index}) picture`);
}

const videoLink = fieldLink(block, 1);            // video
const posterPicture = fieldPicture(block, 2);     // poster

const autoplay = block.classList.contains('autoplay');
const muted = block.classList.contains('muted') || autoplay;
const controls = !block.classList.contains('hide-controls');

const video = document.createElement('video');
video.src = videoLink.href;
video.controls = controls;
video.muted = muted;
video.playsInline = true;
video.autoplay = autoplay;
if (posterPicture) video.poster = posterPicture.querySelector('img')?.src;""")

# ── slide 8 — step 4: css ────────────────────────────────────────────────────
add_bullet_slide("Step 4 — Styling (video-player.css)", [
    "Deliberately minimal — the native <video> element already handles",
    "controls, aspect ratio and responsiveness reasonably well on its own",
    "display: block removes the few pixels of inline-element gap below",
    "the video that browsers add by default",
    "A black background avoids a flash of white while the video/poster",
    "is still loading, especially on slower connections",
], code="""\
/* blocks/video-player/video-player.css */
.video-player video {
  display: block;
  width: 100%;
  height: auto;
  background: #000;
}""")

# ── slide 9 — step 5: registration ───────────────────────────────────────────
add_bullet_slide("Step 5 — Registering the Block", [
    "_video-player.json is auto-picked up by the existing",
    "../blocks/*/_*.json globs in models/_component-models.json and",
    "models/_component-definition.json — no manual registration there",
    "But it still needs adding to every filter that should allow it —",
    "here, models/_section.json's \"section\" filter component list",
    "The block's id must match exactly in every one of those places",
    "(a components-list typo silently hides the block with no error)",
    "Run npm run build:json to regenerate the merged root JSON files",
], code="""\
// models/_section.json
{ "filters": [{
  "id": "section",
  "components": [
    "text", "image", "button", "title", "hero", "cards", "columns",
    "fragment", "teaser", "weather", "rates", "firefly", "ai-image",
    "product-variant", "video-player"   // must match the block's own "id"
  ]
}]}

$ npm run build:json   # regenerates component-{models,definition,filters}.json""")

# ── slide 10 — publishing tips: cloud configuration ──────────────────────────
add_bullet_slide("Publishing Tips — Cloud Configuration & DAM Assets", [
    "1. paths.json — add the DAM folder to \"includes\" so Edge Delivery",
    "   Services is even allowed to serve /content/dam/... paths directly",
    "     \"includes\": [\"/content/myeds-xwalk/\", \"/content/dam/myeds-xwalk/\"]",
    "2. Assign the Cloud Configuration — open the DAM folder's Properties",
    "   → Cloud Services tab → set Cloud Configuration to the same one",
    "   the site uses (e.g. /conf/myeds-xwalk) → Save",
    "3. Publish the video asset ITSELF — this is separate from publishing",
    "   the page; a page publish alone will not push the binary out",
    "4. Republish the page after the above so the block markup regenerates",
    "5. Large/oversized files: add an edge-delivery-services-mp4",
    "   processing profile (bitrate ~300) on the folder for a compliant",
    "   rendition, or the asset may still fail to serve once published",
    "6. If a private folder's video still 404s after all of the above,",
    "   check the Cloud Manager technical account has read access to it",
])

# ── slide 11 — issues table ───────────────────────────────────────────────────
add_table_slide("Issues Hit Along the Way",
    ["Symptom", "Root Cause", "Fix"],
    [
        ["Video plays fine in Universal\nEditor, but is blank on the\npublished page",
         "Author-canvas rendering reads\nfrom AEM directly; the published\npage instead needs the DAM\nasset servable via aem.live",
         "Recognized as a publishing-\npipeline gap, not a block-code\nbug — see steps 2–4 above"],
        ["Direct hit on the video URL\nreturns a Varnish 404\n(\"Error 54113\")",
         "The video renders as <a href=\n\"/content/dam/...\"> — unlike an\nimage <picture>, this is never\nauto-rehosted by the media bus",
         "Added /content/dam/myeds-xwalk/\nto paths.json's \"includes\" array\nso the path is recognized at all"],
        ["Still 404 after the paths.json\nfix was pushed",
         "paths.json only tells EDS which\npaths it MAY serve — the asset\nstill hadn't been given a Cloud\nConfiguration or been published",
         "Assigned Cloud Configuration to\nthe DAM folder, published the\nasset itself, then republished\nthe page"],
        ["Confusion about which config\nfile actually controls this",
         "The repo also authors a\n\"configuration\" content page\nmapped to /.helix/config.json —\neasy to assume that's authoritative",
         "Confirmed paths.json in the\nrepo's main branch is the\ncurrent, precedent-taking\nmechanism for path mapping"],
    ],
    col_w=[Inches(4.0), Inches(4.2), Inches(4.2)],
    col_x=[Inches(0.35), Inches(4.45), Inches(8.75)],
    row_h=Inches(1.35))

# ── slide 12 — best practices summary table ──────────────────────────────────
add_table_slide("Best Practices & Summary",
    ["Step", "Action", "Notes"],
    [
        ["1. Model", "video, poster, classes\n(Options multiselect)", "Keep it to 3 fields —\noptions as checkboxes, not\nseparate boolean fields"],
        ["2. Author content", "Pick DAM video + poster,\ncheck Autoplay/Loop/Muted", "Autoplay always implies\nMuted — browsers require it"],
        ["3. Block JS", "Read fields by position,\nread options via classList", "Same convention as\nai-image/product-variant"],
        ["4. Register", "Add block id to every\nrelevant filter, then build:json", "A typo hides the block with\nno visible error anywhere"],
        ["5. Publish page", "Republish the page in\nUniversal Editor / Sites", "Regenerates the block's\nrendered markup only"],
        ["6. Publish asset", "Publish/activate the video\nasset itself in DAM", "Separate action from\npublishing the page — easy\nto miss"],
        ["7. Cloud config", "Assign the site's Cloud\nConfiguration to the DAM folder", "Required before EDS will\nfetch/serve the asset at all"],
        ["8. Path mapping", "Add the DAM path to\npaths.json's \"includes\"", "Images skip this via the\nmedia bus; video does not"],
    ],
    col_w=[Inches(2.1), Inches(3.8), Inches(4.5)],
    col_x=[Inches(0.35), Inches(2.5), Inches(6.35)],
    row_h=Inches(0.6))

# ── slide 13 — end ────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, W, H, RED)
add_text(s, "Adobe",
         Inches(5.9), Inches(3.3), Inches(1.6), Inches(0.7),
         size=30, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# ── save ──────────────────────────────────────────────────────────────────────
out = "/Users/sevin/Library/CloudStorage/OneDrive-Adobe/NEW/Workspace/EDS/myeds-xwalk/docs/Video-Player-Block-Build-Guide.pptx"
prs.save(out)
print(f"Saved → {out}")

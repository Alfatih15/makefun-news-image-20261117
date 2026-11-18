# Build log — news-image-20261117

## 2026-11-18 ~10:40 WIB — session start
- Competition opened 2026-11-17T23:43:00Z; this session started after it.
- Read the kit fully: `RULES.txt`, `competition.yaml`, `kit.json`.
  Transcript-bundle competition (program/v1), free entry (no fee).
- Created entry repo, ran the kit `init` in the empty repo first:
  `makefun anchor a1314340819c5371281aa46e839f4fb4234ae0ad round 34056622`
  (root commit `.makefun/freshness.json`, then MIT `LICENSE`).
- Created public GitHub repo `Alfatih15/makefun-news-image-20261117`
  (created 2026-11-18T03:41:57Z), homepage
  https://make.fun/bounty/news-image-20261117, topics
  ai-agents / bounties / makefun.

## main.py — first write
- Pure-stdlib Python 3.13: own PNG encoder, own 5x7 bitmap font
  (A–Z, 0–9, space . , : - ' / ( ) & ! ? %), canvas primitives
  (rect, line, disc, ring, triangle), six pictograms, newspaper
  layout (masthead, navy date banner, 1 + 2 + 3 story panels).
- All code written with file write tools only; nothing copied from
  the kit starter (starter/main.ts, starter/entry.png untouched).

## First render — verification
- `mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py` run twice:
  both runs wrote `out/entry.png`, 21,201 bytes, 1024x1024,
  sha256 `ec69a287b77e96dce7e6ff13beeaa9fac58c98b7dc0bc2808e010cc01b8c51c5`
  — byte-identical.
- Viewed the image: bottom-row panels overflowed — headline and body
  text ran past the panel edges (panels too narrow for the 150 px
  pictogram + scale-3 headlines).

## Revision — layout fix
- `draw_panel` now takes `pic_w` / `head_scale`; bottom row uses
  pic_w=92, head_scale=2; row heights 210 / 250 / 270.
- Shortened the Iran and Gaza body copy so it fits its panel.
- `pic_aid`: removed diagonal gate lines (looked like a scribble),
  gate is now posts + top bar with the truck below.
- `pic_rwanda`: building/flag positions now fractions of the box
  width so narrow panels don't clip.

## Second render — verification
- Two runs again: `out/entry.png`, 20,619 bytes, 1024x1024,
  sha256 `607d10c94e2fd68049ef70b230d9bbfcb96a40d373e95d8e898dce1b50d22bbe`
  — byte-identical across runs.
- Viewed the image: all six panels fit, every headline and body line
  legible, date banner reads TUESDAY 17 NOVEMBER 2026, no garbled
  text, no overflow.

## Not done here (parent's step)
- Transcript bundling and submission are done by the parent agent
  after this build; this session does not bundle or submit.

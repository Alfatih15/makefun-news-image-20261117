# The World Today — 17 November 2026

A make.fun bounty entry for
[news-image-20261117](https://make.fun/bounty/news-image-20261117):
sum up 17 November 2026's world news in one image.

## What it does

`main.py` (Python 3.13, standard library only) draws a newspaper
front page **programmatically** and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `./out`):

- its own PNG encoder (`zlib` + `struct`, no PIL)
- its own 5x7 bitmap font, defined in code
- six drawn pictograms (bridge, tanker, summit, jets, aid truck,
  facility) built from rectangles, lines, circles and triangles
- no network, no files read, no randomness — two runs write
  byte-identical output

## Layout

Masthead **THE WORLD TODAY**, a navy date banner reading
**TUESDAY 17 NOVEMBER 2026**, then six story panels:

1. **UKRAINE** — Kerch Bridge hit again
2. **IRAN / GULF** — tankers burn off Hormuz
3. **CHINA** — Xi, Trump, Putin to meet
4. **JAPAN** — Japan scrambles jets
5. **GAZA** — aid call for Gaza
6. **EUROPE** — Rwanda return centre

All six stories were first reported on Tuesday 17 November 2026.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Output: `out/entry.png`, 1024x1024, ~21 KB, deterministic
(sha256 identical across runs).

## License

MIT — see `LICENSE`.

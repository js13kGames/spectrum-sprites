# Spectrum Sprites

Turn-based artillery for two teams of small elemental creatures, on procedurally
generated destructible islands, with online play and a narwhal. The whole game is
one HTML file that fits inside the js13kGames 13,312 byte limit.

Built for js13kGames 2026 (Online category).

## Play

Open `dist/index.html` in a browser after building, or play the packaged
`SpectrumSprites_13k.zip` (a single `index.html`, no external files).

## Controls

- A / D: walk the terrain
- Space: jump
- Mouse: aim
- Hold and release left mouse: charge and fire
- Right mouse: weapon wheel
- Mouse wheel: zoom
- Rope and Blink: cross gaps and drop into caves
- Enter or click: start

Local hotseat on one keyboard, or host and join an online match with a four
letter room code over the official js13kGames relay.

## Build

The readable source is `src/index.html`. The build minifies it with Terser,
packs it with Roadroller, and stores it as a Zopfli-compressed zip.

Requirements: Python 3, Node.js, and the Python `zopfli` package.

```
npm install            # installs the pinned Terser and Roadroller
pip install zopfli     # optional but produces the smallest zip
npm run build          # writes dist/ and SpectrumSprites_13k.zip
```

`npm run build` runs `python tools/pack.py`, which rebuilds deterministically:
the same source always produces the same bytes.

## Notes

Everything is generated at runtime. No image, audio, or font assets. Sound is
synthesized with WebAudio and all art is drawn on a canvas.

AI use: code assistant only.

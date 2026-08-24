# Spectrum Sprites

A tiny turn-based artillery game about six elemental weirdos, destructible rainbow islands, underground caverns, online matches, procedural sound/music, and a sea unicorn that eventually gets annoyed enough to join the fight.

Built for **js13kGames 2026**. The current 0.20 release packs the whole playable submission into one `index.html` inside a **13,288 byte ZIP**.

## What's in it

- Local hotseat, VS Computer, Quick Match, and room-code online play
- Six Spectrum Sprites with asymmetric signature attacks
- Twelve weapon slots with finite team ammo and battlefield crates
- Live destructible terrain and procedurally generated cavern routes
- Multi-level deterministic spawns
- ROPE and BLINK traversal
- Rising tide + mid-match Sea Unicorn encounter
- Physics-matched projectile prediction
- Synthesized WebAudio effects and generative music
- Fullscreen-safe pointer input
- Deterministic online state/hash recovery

## Controls

- **A / D** — move
- **Space** — jump
- **Mouse** — aim
- **Hold / release LMB** — charge and fire
- **RMB** — armory
- **Mouse wheel** — zoom
- **M** — toggle music
- **Enter** — menu/select/rematch

## Build

Readable authority lives in `src/index.html`.

Requirements:

- Python 3
- Node.js
- Python `zopfli`
- pinned Terser 5.50.0 + Roadroller 2.1.0 from `package-lock.json`

```bash
npm ci
python -m pip install -r requirements.txt
npm run build
```

Windows users can run `package.bat`; Linux/macOS users can run `./package.sh` after installing dependencies.

The release path is intentionally boring and reproducible:

`src/index.html -> Terser -> Roadroller (pinned model params) -> Zopfli -> SpectrumSprites_13k.zip`

The packer invokes the JS tool entrypoints through `node` directly, so it does not depend on executable bits surviving a ZIP extraction. If the pinned tools or a compliant compressor are unavailable, it **fails instead of overwriting a known-good submission with an oversized fallback**.

## Verification

```bash
npm run accept
```

The current source passes **123 static/release checks**, readable runtime validation, 10,000-seed spawn stress, packed/readable spawn agreement, AI full-match tests, and Quick Match pairing tests.

## Online

See [ONLINE.md](ONLINE.md) for the relay/lockstep model and recovery behavior.

## Size discipline

The project is intentionally kept compression-aware even when the readable source is not byte-golfed. Final ZIP size is the metric that matters; source-size "optimizations" that make the packed ZIP larger get reverted. Because compression apparently enjoys having opinions.

## Dev log

See [DEVLOG.md](DEVLOG.md) for the increasingly questionable decisions that got this thing under 13K.

## License

MIT. See [LICENSE](LICENSE).

# Dev Log

## 0.20 — somehow still under 13K

Spectrum Sprites started as "what if I made a tiny artillery game" and then apparently nobody told me to stop.

The current build has destructible terrain, caverns, six asymmetric Sprites, twelve weapon slots, ROPE/BLINK movement, trajectory prediction, procedural audio/music, AI, local play, Quick Match, room-code online play, rising water, and a sea unicorn that eventually shows up because normal artillery clearly wasn't enough.

Recent work was mostly the glamorous stuff nobody notices unless it breaks:

- rebuilt the release path as clean source -> Terser -> Roadroller -> Zopfli
- killed an old compatibility-patch setup that was wasting almost 1 KB, because clever hacks eventually become expensive hacks
- added real-physics trajectory dots so aiming isn't just educated guessing
- fixed fullscreen BLINK input
- added multilevel randomized starts instead of lining everybody up politely on the surface
- added AI and Quick Match
- tightened online recovery and killed a couple wonderfully obscure desync/crash cases
- fixed the packer so ZIP extraction doesn't randomly decide executable bits are a premium feature

Current submission: **13,288 / 13,312 bytes**.

So there are 24 bytes left. Plenty of room. Practically luxurious.

The main compression lesson from this project: I stopped caring whether a source edit *looks* smaller. I measure the final ZIP. More than once I made the JavaScript shorter and the submission larger, because compression apparently gets a vote.

For now this is the jam build. After the jam I may expand it, but I want to keep the same rule: new stuff still has to earn its bytes even when 13K isn't standing behind me with a knife.

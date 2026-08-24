# Spectrum Sprites — Online Notes

Online play uses the js13kGames WebSocket relay and deterministic lockstep-style state.

## Match setup

- The host creates/claims a relay room and provides the deterministic match seed.
- Terrain, cavern flow, spawns, crates, and gameplay PRNG derive from shared state.
- Room-code host/join and Quick Match both end in the same match authority path.
- Quick Match uses deterministic time-window room pools, small join jitter, host tie-breaking, and automatic retry when a pool is full or stale.

## Gameplay messages

The compact protocol uses single-letter packet types for assignment/start, movement, fire, decisive effects, crate state, turn hashes, snapshots, and recovery. Gameplay packets are ignored until a client has actually started a match, so late joiners/spectators cannot accidentally execute turn-zero actions.

Movement packets are turn-scoped. Decisive actions carry turn/active identity, and the host periodically compares gameplay hashes. On mismatch, the authoritative snapshot path restores terrain damage, crates, Sprite state, transition timing, and Sea Unicorn authority state.

Cosmetic-only state (for example free-running Sea Unicorn patrol position between authoritative events) is intentionally excluded from gameplay hashes.

## Disconnects / room handling

- A pre-match guest slot is released if that peer leaves.
- Extra guests receive a room-full assignment instead of hanging forever.
- If an opponent leaves during a match, the remaining player can continue locally.
- Quick Match retries automatically rather than leaving the player in a dead room.

## Submission

The game has no external runtime assets. Online networking is native WebSocket; the packaged submission remains a single `index.html`.

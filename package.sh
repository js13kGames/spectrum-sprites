#!/usr/bin/env sh
# Deterministic release build. With npm available, run `npm install` once to provision pinned tools.
set -eu
export PYTHONUTF8=1
python tools/pack.py
python tests/verify.py
node scripts/runtime_stub.mjs
# Optional exact-payload boot verification when a Puppeteer/Chrome harness is provisioned.
if [ -n "${PPTR:-}" ] || [ -n "${TEMP:-}" ] && [ -f "${TEMP}/ss-buildtools/node_modules/puppeteer-core/package.json" ]; then
  node scripts/harness.mjs dist/release.html boot evidence/release
else
  echo "browser screenshot harness not provisioned; exact Node payload verification completed"
fi
echo "release build ok"

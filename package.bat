@echo off
setlocal
set PYTHONUTF8=1
python tools\pack.py || exit /b 1
python tests\verify.py || exit /b 1
node scripts\runtime_stub.mjs || exit /b 1
echo release build ok

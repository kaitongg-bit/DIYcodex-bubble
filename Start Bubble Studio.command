#!/bin/zsh
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
cd "${0:A:h}"
if ! /usr/bin/curl -fsS --max-time 1 http://127.0.0.1:19329/api/library >/dev/null 2>&1; then
  mkdir -p .local
  PYTHON_BIN="$(command -v python3 || true)"
  if [[ -z "$PYTHON_BIN" ]]; then
    print '未找到 Python 3，请先安装 Python 3.9 或以上版本。详见 README。'
    read -r '?按回车关闭。'
    exit 1
  fi
  nohup "$PYTHON_BIN" "$PWD/app/server.py" > "$PWD/.local/studio.log" 2>&1 < /dev/null &
  for attempt in {1..30}; do
    /usr/bin/curl -fsS --max-time 1 http://127.0.0.1:19329/api/library >/dev/null 2>&1 && break
    sleep 0.2
  done
fi
setup=$(/usr/bin/curl -fsS --max-time 10 \
  -H 'Origin: http://127.0.0.1:19329' -H 'X-Bubble-Studio: 1' \
  -H 'Content-Type: application/json' --data '{}' \
  http://127.0.0.1:19329/api/first-run 2>/dev/null || true)
if [[ "$setup" == *'"firstRun": true'* ]]; then
  /usr/bin/curl -fsS --max-time 30 \
    -H 'Origin: http://127.0.0.1:19329' -H 'X-Bubble-Studio: 1' \
    -H 'Content-Type: application/json' --data '{}' \
    http://127.0.0.1:19329/api/launch-active >/dev/null 2>&1 || true
fi
/usr/bin/open http://127.0.0.1:19329

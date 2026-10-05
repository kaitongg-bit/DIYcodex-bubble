#!/bin/zsh
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
cd "${0:A:h}/../.."
PYTHON_BIN="$(command -v python3 || true)"
if [[ -z "$PYTHON_BIN" ]]; then
  print '未找到 Python 3，请先安装 Python 3.9 或以上版本。'
  read -r '?按回车关闭。'
  exit 1
fi
if ! /usr/bin/curl -fsS --max-time 1 http://127.0.0.1:19329/api/library >/dev/null 2>&1; then
  mkdir -p .local
  nohup "$PYTHON_BIN" "$PWD/app/server.py" > "$PWD/.local/studio.log" 2>&1 < /dev/null &
  for attempt in {1..30}; do
    /usr/bin/curl -fsS --max-time 1 http://127.0.0.1:19329/api/library >/dev/null 2>&1 && break
    sleep 0.2
  done
fi
response=$(/usr/bin/curl -fsS --max-time 30 \
  -H 'Origin: http://127.0.0.1:19329' \
  -H 'X-Bubble-Studio: 1' \
  -H 'Content-Type: application/json' \
  --data '{}' http://127.0.0.1:19329/api/launch-active)
result=$?
if (( result != 0 )); then
  print '未能启动已选气泡。请查看工坊中的连接状态。'
else
  print "$response" | "$PYTHON_BIN" -c 'import json,sys; data=json.load(sys.stdin); print(data.get("message") or data.get("error") or "请查看工坊中的连接状态。")'
fi
/usr/bin/open http://127.0.0.1:19329

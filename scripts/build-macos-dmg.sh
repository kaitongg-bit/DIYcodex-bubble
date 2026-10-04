#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
DIST="$ROOT/dist"
STAGE="$DIST/dmg-stage"
RES="$STAGE/DIY Codex Bubble.app/Contents/Resources"
MACOS="$STAGE/DIY Codex Bubble.app/Contents/MacOS"

rm -rf "$STAGE"
mkdir -p "$RES" "$MACOS" "$DIST"

rsync -a --delete \
  --exclude '.git' --exclude '.local' --exclude '__pycache__' \
  --exclude 'dist' --exclude 'DIY Codex Bubble.app' \
  "$ROOT/" "$RES/"

ICONSET="$DIST/AppIcon.iconset"
mkdir -p "$ICONSET"
for size in 16 32 128 256 512; do
  sips -z "$size" "$size" "$ROOT/assets/app-icon.png" --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
  retina=$((size * 2))
  sips -z "$retina" "$retina" "$ROOT/assets/app-icon.png" --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o "$RES/AppIcon.icns"

cat > "$STAGE/DIY Codex Bubble.app/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleIdentifier</key><string>cc.kaitongg.diycodexbubble</string>
<key>CFBundleName</key><string>DIY Codex Bubble</string>
<key>CFBundleDisplayName</key><string>DIY Codex Bubble</string>
<key>CFBundleExecutable</key><string>launcher</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleIconFile</key><string>AppIcon</string>
<key>CFBundleShortVersionString</key><string>0.2.3</string>
<key>CFBundleVersion</key><string>0.2.3</string>
<key>LSUIElement</key><true/>
</dict></plist>
PLIST

cat > "$MACOS/launcher" <<'LAUNCHER'
#!/bin/zsh
set -euo pipefail
ROOT="${0:A:h:h}/Resources"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export BUBBLE_STUDIO_DATA="${HOME}/Library/Application Support/DIY Codex Bubble"
exec /usr/bin/python3 "$ROOT/scripts/login-start.py" --studio
LAUNCHER
chmod +x "$MACOS/launcher"

rm -f "$DIST/DIYcodex-bubble-macos.dmg"
hdiutil create -volname "DIY Codex Bubble" -srcfolder "$STAGE" \
  -ov -format UDZO "$DIST/DIYcodex-bubble-macos.dmg" >/dev/null

printf 'Built %s\n' "$DIST/DIYcodex-bubble-macos.dmg"

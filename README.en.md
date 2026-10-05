<p align="center">
  <img src="presets/alien-cat.png" alt="DIY Codex Bubble" width="96">



</p>

<h2 align="center">DIY Codex Bubble · Bubble Studio</h2>

<h4 align="center">Turn any image into your Codex chat bubble.</h4>

<p align="center">
  <a href="https://github.com/kaitongg-bit/DIYcodex-bubble"><img src="https://img.shields.io/github/stars/kaitongg-bit/DIYcodex-bubble" alt="Stars"></a>
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey" alt="macOS and Windows">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT">
</p>

<p align="center">
  <a href="./README.md">中文</a> · <strong>English</strong>
</p>

<p align="center">
  <a href="https://github.com/kaitongg-bit/DIYcodex-bubble/releases/latest"><strong>Download</strong></a> ·
  <a href="https://kaitongg-bit.github.io/DIYcodex-bubble/">Bubble Gallery</a> ·
  <a href="#gallery-and-community">Contribute</a> ·
  <a href="DEVELOPMENT.md">Development</a>
</p>

Works with the **Codex / ChatGPT and Doubao desktop apps** on macOS and Windows, with real-device verification on both platforms. Only **your messages** get a bubble — assistant replies keep their original look. Click **Restore default** to switch back anytime.

**macOS / Windows verified · English / 中文 UI · Local library · MIT licensed**

> An independent appearance tool. **Not an official OpenAI or Codex product.** It does not modify the official app installation. The desktop studio lives on `main`; the public gallery is generated separately and published from `gh-pages`, so source downloads do not include it.

## Design your own bubble?

The companion [douyinQIPAO design skill](https://github.com/kaitongg-bit/douyinQIPAO) helps you create original PNGs — a Codex-powered generator that follows Douyin bubble specs, maintained and updated independently, so it never needs to move in lockstep with this studio. Once it's ready, import the image here to tune, preview, and apply.

## Features

- **Keep your favorites together.** Import PNGs or pick a local asset folder in the system file picker. Search, favorite, and switch anytime.
- **Tune directly on the canvas.** Drag the gold handles to set stretch guides; move and resize the blue text box — no four-sided coordinate inputs.
- **Preview before applying.** Try short messages, long messages, or your own text, in light and dark themes.
- **Add the finishing touches.** Text color, scale, corner radius, and an extra border; **Fit to chat** sizes large images comfortably.
- **Apply when ready.** Each bubble keeps its own settings. Switch designs or restore the default anytime.

Use **EN / 中文** in the top-right corner to switch languages. Bubble settings and unsaved edits stay in place.

## Screenshots

<table align="center">
  <tr>
    <td align="center"><img src="docs/images/chatgpt-chat.png" alt="Custom user bubbles in the ChatGPT desktop app" width="420"><br><sub>Real ChatGPT chat: your messages get a custom bubble while assistant replies keep their original look</sub></td>
    <td align="center"><img src="docs/images/doubao-chat.png" alt="Custom user bubbles in the Doubao desktop app" width="420"><br><sub>Real Doubao chat: your messages get a custom bubble while assistant replies keep their original look</sub></td>
  </tr>
</table>

<p align="center">
  <img src="docs/images/studio-overview-en.jpg" alt="Light-mode Bubble Studio with an alien-cat preview and LOVE and cooking-cat assets in the library" width="900"><br>
  <sub>Light-mode studio preview (the studio itself, not a real conversation screenshot)</sub>
</p>

## Quick start

Download from the [latest release](https://github.com/kaitongg-bit/DIYcodex-bubble/releases/latest). You do not need to fork the repository, download source code, or run terminal commands. Chrome is not required; the studio opens in your default browser.

### Which download?

| Platform / preference | File | How to open |
| --- | --- | --- |
| macOS | `.dmg` | Open the DMG, drag **DIY Codex Bubble.app** into Applications, then open it |
| Windows 10/11 x64, recommended | `windows-x64-light-setup.exe` | Install, then open **DIY Codex Bubble** from the desktop or Start menu |
| Windows, runtimes included for offline setup | `windows-x64-offline-setup.exe` | Same installation flow, with Python and Node.js bundled |
| Windows, portable | `windows-x64-light-portable.zip` / `windows-x64-offline-portable.zip` | Extract fully to a permanent folder and open **DIY Codex Bubble.exe** |

GitHub's **Source code (zip / tar.gz)** downloads are development source, not portable builds. For your first installation, choose the DMG or EXE installer. Keep the entire portable folder together; do not move only its EXE.

### First launch

1. If macOS blocks the first launch, use System Settings → Privacy & Security → Open Anyway. The Windows installer is unsigned and may trigger SmartScreen; administrator rights are not required.
2. Compatible Python (3.10+, below 4) and Node.js (22+) are reused. The Windows light edition downloads missing runtimes with progress into its own directory without changing system settings.
3. First launch applies **Alien cat** to Codex and enables **Restore after computer startup**. If Codex is already running normally, save your work, fully quit it, then use the studio's Restart button. The studio does not force-quit apps.
4. Keep the preset, select another image, adjust stretch guides, or switch to Doubao and apply a separate bubble. **Restore default** reverses the selected app's skin.

Codex / Doubao bubbles have been verified on real devices on both macOS and Windows. App updates and installation methods may affect connectivity; see the troubleshooting notes below.

The default small installer is around **4 MB** and reuses compatible runtimes. Close the setup progress window to cancel a download; reopen to retry. The full offline build downloads at around 33 MB and uses around 107–111 MB after installation. On computers without runtimes, the small build will also use additional disk space after first setup; most savings come from reusing existing installations. Images, settings, and downloaded runtimes are stored separately, and upgrades preserve settings.

**After your computer starts and reaches the desktop:** the local service starts in the background and tries to restore apps with applied bubbles. No terminal or web page is needed. **After fully quitting an app:** open **DIY Codex Bubble** and use the Restart button in the studio. The original Codex / Doubao icon cannot add startup flags after a full quit; if you reopen an app through its original icon, fully quit it and restart it from the studio. Computer startup is per-user and can be turned off in the studio.

**To change bubbles later:** open **DIY Codex Bubble**, or open `http://127.0.0.1:19329` in your browser. The one-time setup launcher is not needed again.

For running from source, see [Development notes](DEVELOPMENT.en.md).

The Windows edition checks common folders on local drives, running apps, registry entries, shortcuts, and Microsoft Store packages from expected publishers. If an app is not found, click “Choose application location” in the workshop and select the installed `Doubao.exe`, `Codex.exe`, or `ChatGPT.exe`. Your choice is saved. Do not select the downloaded `OnlineInstaller`. Some Store app builds may ignore the debugging flags. If the studio remains disconnected, report the Windows and app versions in [Issues](https://github.com/kaitongg-bit/DIYcodex-bubble/issues), along with relevant errors from `.local/app-start.log` after removing private paths. Do not upload chat content.

The installed Windows app stores settings and logs in `%LOCALAPPDATA%\DIY Codex Bubble\Data`; upgrades preserve them. The unsigned installer may trigger SmartScreen. Legacy source ZIP / `.cmd` launchers remain available for development and require separately installed Python and Node.js. Please report connection issues as described above.

## Usage

Click **Check for updates** in the studio header, then **Download and update**. Installed Mac apps and Windows installer editions verify the package, replace the app and reopen the studio, keeping bubbles, settings and favorites. Source checkouts and portable editions link to downloads.

### Updates and connection troubleshooting

- **Do not uninstall before updating.** Install the new Windows release into the same location to replace the old program. Apps settings lists one installation; bubbles, settings, and favorites are retained. Previously downloaded installers are not deleted automatically. On macOS, replace the studio app in Applications.
- **Windows update says “Access denied” or cannot stop the background service?** Cancel installation and exit the old studio service before retrying. Closing a browser tab does not stop the service. If it cannot be stopped, restart Windows and run the new installer first.
- **Doubao still appears to be running after you quit it?** Check for `Doubao.exe` in Task Manager's Details tab. Save your work before ending it, then restart Doubao from the studio. Restart the computer if the process cannot be ended.
- **Gallery import says `127.0.0.1` refused the connection?** Open **DIY Codex Bubble** on the same computer, wait for the local studio page, then click the gallery import button again. The public gallery cannot start a local service that is not running.
- **Portable or source updates?** Download the new release. These editions do not currently support automatic program replacement from the studio.

Open the installed studio, then click **Import into my studio** in the online gallery to import both the PNG and settings into a dedicated community folder. Preview before applying to Codex / Doubao. **Open selected asset folder** reveals the image folder. Renaming an external PNG changes its display name, but saved settings are tied to its path; keep tuned filenames unchanged.

### One studio, two apps

Choose Codex or Doubao in the header. They share the PNG library and editor, while active bubbles and connection status stay separate. Switching apps does not apply a theme; **Restore** affects only the selected app. Deleting an image used by both restores both.

<p align="center">
  <img src="docs/images/dual-platform-studio.jpg" alt="Bubble Studio with Doubao selected" width="900">
</p>

Doubao's user-message selector is built in; the supported installation is `/Applications/Doubao.app`, and app updates may require adaptation. Existing Codex settings migrate without losing artwork or active themes; Doubao starts with no active theme. If you ran an older standalone Doubao studio, stop it first to avoid competing monitors. Its private `.local/` files are not bundled or published; connect your original asset folder to reuse PNGs.

### A tip for better stretching

**Keep stretch guides on straight, continuous edges.** Leave characters, tails, curved corners, and detailed decorations in fixed areas. Check both short and long messages before applying.

Images do not need to match Douyin dimensions. Larger PNGs work too; use **Fit to chat** to size them. 100% means the original image size. Scaling the artwork does not change the text's font size.

### Recoverable deletion

The **×** on an asset moves its PNG to the studio's recovery folder; **Undo delete** restores it. **This also moves the original file from a connected folder.**

To delete permanently, click **Open recovery folder** and delete unwanted files in your system file manager. The studio cannot undo that deletion; refresh the library to update recovery records.

## Gallery and community

[Open the online gallery](https://kaitongg-bit.github.io/DIYcodex-bubble/). Pick a design and try it in a Codex-inspired desktop chat simulator, with light/dark themes and your own sample messages. It never connects to your account or reads real conversations.

The studio's **Online bubble gallery** link opens this public site directly. The review console is for the maintainer's local machine with access to the private submission queue, so it is not shown in the public navigation.

<p align="center">
  <img src="docs/images/chat-simulation.png" alt="Chat simulator in the online gallery" width="420"><br>
  <sub>The simulator in the online gallery: check bubble effects with short and long messages (independent simulation, not a real Codex screenshot)</sub>
</p>

**Alien Cat, LOVE, and Cooking Cat** are included on the desktop studio's first launch. Alien Cat is applied to Codex on first launch. Use **Restore built-in presets** to recover deleted presets.

- **Use a community bubble**: Open the local studio, then click **Import into my studio** on a work's detail page. Its PNG and settings are imported together. Preview, then apply to Codex / Doubao. Manual PNG and `.bubble.json` downloads remain available.
- **Create in the online workshop**: Choose **Create a bubble** and upload a PNG. A full Codex simulation appears above an editor that shares the desktop studio's stretch, text-position, and rendering logic. **Save settings** lets you download the original PNG and `.bubble.json`; until you choose **Publish my bubble**, the image stays in your browser — nothing is uploaded and there is no AI image generation.
- **Publish**: Choose **Publish my bubble** and enter a nickname and bubble name. The PNG and its current settings enter a private review queue together; the maintainer publishes approved works manually, no account required. Review criteria: [COMMUNITY.md](COMMUNITY.md).
- **Download counts**: Public counts come from each PNG's GitHub Releases download statistics. They may be delayed and do not represent unique users; unavailable counts are shown as unavailable. The local gallery labels its separate, local-only counter.

Want to design your own bubble? The companion [bubble design skill](https://github.com/kaitongg-bit/douyinQIPAO) helps you create PNG artwork in your own Codex session. Import the finished PNG here to tune, preview, and apply it.

## License and responsibility

The code is released under the [MIT License](LICENSE) — free to use, modify, and distribute, including commercially.

The code license does not grant rights to images, character IP, likenesses, or trademarks. Users must obtain the necessary rights and are responsible for their content and actions; character IP, nudity, or adult content does not become licensed just by being made or shown with this tool. The authors and maintainers do not endorse user content or uses. The software is provided "as is" under the MIT License, with liability limited to the extent permitted by applicable law. See [Usage responsibility](RESPONSIBILITY.md).

## Related documents

- [Development notes](DEVELOPMENT.en.md) · [中文](DEVELOPMENT.md)
- [Community notes](COMMUNITY.en.md) · [中文](COMMUNITY.md)
- [Agent instructions](AGENTS.en.md) · [中文](AGENTS.md)
- [Usage responsibility](RESPONSIBILITY.en.md) · [中文](RESPONSIBILITY.md)

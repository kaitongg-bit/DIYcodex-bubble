# Agent instructions

[中文](AGENTS.md)

This project is DIY Codex Bubble (Bubble Studio). The macOS Codex/ChatGPT and Doubao desktop integrations are verified; Windows launching and file operations are beta, and desktop injection still needs real-device testing. User-facing documentation lives in README; development details live in DEVELOPMENT.md.

## Change constraints

- Change only user-sent message bubbles; never assistant messages.
- Platform must be explicit: debug ports, applied assets, and advanced selectors are isolated per platform. Do not guess messages from background or corner radius, and do not inject into unknown pages. Switching platforms never applies a theme; restore affects only the current platform.
- Apply via runtime styles only; never modify the official desktop app bundle, and never read or export chat content.
- Editing never rewrites the original PNG; deletion must be recoverable, and restore never overwrites a same-named file at the original location.
- Open the recovery folder for the user to manage; never auto-empty the system Trash.
- The design skill is maintained separately at `https://github.com/kaitongg-bit/douyinQIPAO` and is not bundled with this project.
- Never commit `.local/`, private assets, favorites, personal settings, logs, or personal paths. Exceptions: the Alien Cat, LOVE, and Cooking Cat PNGs in `presets/` are authorized as public built-in presets and downloadable assets; `community/approved/fluffy-cat-demo.png` is authorized as a public submission-flow demo and is not part of the three default presets. Any other image still needs separate distribution rights; screenshot approval is not PNG download approval.
- Verify asset operations with isolated data directories and original demo PNGs; never touch the user's real assets.
- Keep a single canvas that edits stretch guides and the text box together; do not bring back four-side coordinate, padding-number, or mode-switch inputs.

## Verification and delivery

Behavior changes run the service tests and JavaScript syntax checks; doc-only changes just check links, images, and content. UI changes are verified on real pages, with screenshots excluding private content. Full test commands and architecture are in DEVELOPMENT.md.

This project is released under the MIT License (see LICENSE); docs and code must not claim commercial restrictions or other license limits. Asset rights and usage responsibility are in RESPONSIBILITY.md; do not describe disclaimers as unconditional or absolute.

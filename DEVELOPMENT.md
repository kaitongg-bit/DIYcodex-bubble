# 开发与运行说明

[English](DEVELOPMENT.en.md)

面向贡献者的技术信息。普通用户请先读 [README](README.md)。

## 运行源码

macOS 已实测；Windows 桌面注入为测试版。需要 Python 3.9+、Node.js 22+；无需 npm 安装或前端构建。Windows 可双击 `Start Bubble Studio.cmd` 或 `Start Bubble Apps.cmd`；也可运行 `py -3 app/server.py`。

```sh
git clone https://github.com/kaitongg-bit/DIYcodex-bubble.git
cd DIYcodex-bubble
python3 app/server.py
```

打开 http://127.0.0.1:19329 。可用 `BUBBLE_STUDIO_DATA` 设置私有数据目录、`BUBBLE_STUDIO_NODE` 指定 Node 路径，`--port` 指定工作台端口。

## 结构

- `app/server.py`：本机素材库、导入、预设、回收区与系统文件夹窗口。
- `app/bridge.mjs`：连接桌面应用、应用与撤销用户消息样式。
- `app/static/`：可视化编辑器、预览与九切片画布绘制；`i18n.mjs` 管理中英文 UI，语言保存在浏览器本地，不改变气泡预设。
- `tests/`：隔离临时目录的服务测试。
- `.local/`：私人素材、收藏、设置、回收文件和日志，不提交。

## 参数与连接

PNG 两轴分别支持 2–4096 px；直接导入单张限制 2 MB，连接文件夹读取不设这一限制。新素材默认按不超过 240×98 页面像素适配，已有预设不自动覆盖。缩放范围 1%–200%，100% 为原图像素大小；文字字号不随素材缩放。

圆角 0 保留原图，边框粗细 0 关闭描边。圆角裁切画布四角；额外边框沿画布外框描边。调节不重写 PNG。

通过绑定 `127.0.0.1:19327` 的 CDP 端口注入运行时样式，不修改官方应用包。九切片绘制到同一画布，避免分块接缝。匹配数是当前挂载的用户消息数，虚拟化或页面切换时可能为 0。调试端口对本机程序可见，完全退出并正常启动桌面应用可关闭它。关闭工作台不会自动撤销已注入样式；请先恢复默认或完全重启应用。

目前仅 macOS 桌面端经过实机验证。Windows 的本机服务与启动代码有模拟测试，但 Store 安装位置、CDP 参数和页面选择器仍需在 Windows 实机验收；应用升级后可能需要适配。

Windows 启动器是 `scripts/windows-launch.py`，由两个 `.cmd` 文件调用。服务会先查找常见安装位置，再查找发布者匹配的 Microsoft Store 包；需要时可设置 `BUBBLE_STUDIO_CODEX_EXE` / `BUBBLE_STUDIO_DOUBAO_EXE` 为实际程序路径。已运行的应用不会被强制结束；启动器只会提示先完全退出。

首次启动会调用 `/api/first-run`，自动选择外星小猫 Codex 预设并写入当前用户的登录启动项；已有状态不被覆盖。登录入口 `scripts/login-start.py` 静默启动服务后调用 `/api/launch-active`，不打开浏览器。macOS 登录项位于 `~/Library/LaunchAgents/`，Windows 位于当前用户的 Startup 文件夹；关闭页面开关只删除本项目的条目。macOS 发布物以 DMG 中的 `DIY Codex Bubble.app` 为用户入口；Windows 仍由 ZIP 中的 `Start Bubble Studio.cmd` 启动。旧的 `.command`、`.app`、`.vbs` 文件只保留给开发和故障排查，不应作为普通用户文档中的主要路径。

`Start Bubble Apps.command` 在本机启动工坊后调用 `/api/launch-active`，为每个已应用平台分别以对应 CDP 端口启动应用。后台监控继续按平台重连并应用已保存的样式。普通启动的应用无法在运行中追加调试端口，接口只提示用户手动完全退出，不强制结束进程。完全退出后通过该启动器重新打开，才能恢复连接。

## 验证

```sh
python3 -m unittest discover -s tests -v
node --check app/bridge.mjs
node --check app/static/app.js
```

截图和本地验收必须使用隔离演示数据，不包含用户私人素材、路径或聊天。历史验收记录保留在 Git 提交历史中，不作为终端用户文档发布。

## 静态作品库与模拟聊天

`codex-preview.mjs` 与 `codex-preview.css` 提供独立 DOM 模拟器，共用九切片绘制。仅模拟用户消息加背景，助手内容保持普通样式，不调用真实账号、聊天或模型。

`presets/manifest.json` 管理已获分发授权的内置 PNG 与配置。首次读取本机库将它们复制到私有数据目录，不覆盖用户设置；删除后不会自行重建，显式恢复才补回。

`python3 scripts/export-gallery.py /tmp/bubble-gallery` 导出零后端站点。本机 `/gallery` 使用本机下载计数；静态页面从公开 GitHub Releases API 读取全站 PNG 下载统计。PNG 的私有预览使用浏览器 Blob URL，无上传。社区收录规则见 COMMUNITY.md。

公开作品库的导出文件只发布到仓库的 `gh-pages` 分支，由 GitHub Pages 使用；它们不会进入默认 `main` 分支，也不会随桌面工坊源码下载。普通贡献者克隆 `main` 即可开发本机工坊。发布 Pages 时先运行导出脚本，再在部署分支提交生成物。

## 双平台适配

`app/platforms.mjs` 定义 Codex（19327）与豆包（19326）的端口、默认用户消息选择器及页面允许列表。工坊端口仍为 19329。`bridge.mjs <state> <action> <platform>` 显式指定平台；逐页面容错，但所有页面失败时 connected 为 false。高级覆盖配置位于私有 `platforms.<key>.userSelector`，不共享旧顶层 selector，也不做启发式扫描。

私有状态的 `platforms.codex.active` / `platforms.doubao.active` 保存各自应用快照；旧顶层 active 迁移到 Codex。顶层 active/debugPort 为当前选择平台的兼容视图，保存时同步相应快照。原图预设、收藏、素材库继续共享。后台各平台监控只使用对应快照；API 拒绝带有过期平台标记的写操作。

补充桥测试：`node --test tests/bridge.test.mjs`。实机启动不得强制关闭任何应用；旧独立工坊必须避免同时监控。


## Anonymous submission intake

See [community/DEPLOYMENT.md](community/DEPLOYMENT.md) for Worker secrets, Turnstile, private queue, owner-only moderation and the verified local acceptance boundary. Regression tests: `node --test tests/submissions.test.mjs`.

DMG 不包含 `.git`，作者审核发布必须连接独立的源码 checkout。在本机数据目录（macOS 为 `~/Library/Application Support/DIY Codex Bubble`）放置私有 `review.json`，格式为 `{"repository":"源码仓库绝对路径"}`；也可用 `BUBBLE_STUDIO_REVIEW_ROOT` 覆盖。此配置不随发布包分发。审核脚本从该仓库查找 gh-pages 工作树；需要时另设 `PAGES_WORKTREE`。普通用户无需配置审核台。

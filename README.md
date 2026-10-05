<p align="center">
  <img src="presets/alien-cat.png" alt="DIY Codex Bubble" width="96">



</p>

<h2 align="center">DIY Codex Bubble · 气泡工坊</h2>

<h4 align="center">把自己的图，变成 Codex 聊天气泡。</h4>

<p align="center">
  <a href="https://github.com/kaitongg-bit/DIYcodex-bubble"><img src="https://img.shields.io/github/stars/kaitongg-bit/DIYcodex-bubble" alt="Stars"></a>
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey" alt="macOS and Windows">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT">
</p>

<p align="center">
  <strong>中文</strong> · <a href="./README.en.md">English</a>
</p>

<p align="center">
  <a href="https://github.com/kaitongg-bit/DIYcodex-bubble/releases/latest"><strong>下载最新版</strong></a> ·
  <a href="https://kaitongg-bit.github.io/DIYcodex-bubble/">在线气泡库</a> ·
  <a href="#社区与作品库">贡献气泡</a> ·
  <a href="DEVELOPMENT.md">开发说明</a>
</p>

支持 **macOS 和 Windows 上的 Codex / ChatGPT、豆包桌面端**，两平台均已实机验证。只替换 **你发送的消息气泡**，助手回复保持原样；想换回来，点「恢复默认」即可。

**macOS / Windows 已验证 · 中英文界面 · 本机素材库 · MIT 许可**

> 非 OpenAI / Codex 官方产品，独立的聊天外观工具，不修改官方应用安装包。桌面工坊源码在 `main` 分支；在线作品库是单独生成并发布到 `gh-pages` 的 Pages 站点，不会混进源码下载。

## 想画一款自己的气泡？

配套的 [douyinQIPAO 设计 Skill](https://github.com/kaitongg-bit/douyinQIPAO) 可以帮助你设计原创 PNG——利用 Codex 按抖音气泡规范生成，独立维护和更新，不必跟着工坊一起升级。画好后把图片导入这里，再调整、预览、应用。

## 特性

- **把素材收进自己的库** —— 导入 PNG，或在系统文件夹窗口中选择整个素材文件夹；搜索、收藏、随时切换。
- **直接在图上调** —— 拖动金色手柄设置拉伸线，拖动蓝色文字框调整文字位置和空间，不用计算四边数字。
- **短句长话都看看** —— 实时预览短句、长消息和自己的文字，可切换浅色、深色背景。
- **再加一点细节** —— 文字颜色、缩放、圆角和边框；「适合聊天」帮你把大图缩到合适大小。
- **满意就应用** —— 每款气泡各自保存设置，可随时换款，也可一键恢复默认。

点击右上角 **EN / 中文** 切换网页语言，已调整的气泡和未保存的设置会保留。

## 截图

<table align="center">
  <tr>
    <td align="center"><img src="docs/images/chatgpt-chat.png" alt="ChatGPT 中的真实聊天气泡效果" width="420"><br><sub>ChatGPT 实际使用效果：你发出的消息换上气泡，助手回复保持原样</sub></td>
    <td align="center"><img src="docs/images/doubao-chat.png" alt="豆包中的真实聊天气泡效果" width="420"><br><sub>豆包实际使用效果：你的消息换上气泡，助手回复保持原样</sub></td>
  </tr>
</table>

<p align="center">
  <img src="docs/images/studio-overview.jpg" alt="气泡工坊：左边选素材，中间拖动调整，右边预览聊天效果" width="900"><br>
  <sub>浅色工坊预览：外星小猫正在预览，LOVE 与小猫炒菜在左侧素材库（展示的是工坊，不是真实聊天页面）</sub>
</p>

## 快速开始

从 [最新版发布页](https://github.com/kaitongg-bit/DIYcodex-bubble/releases/latest) 下载。普通用户不需要 Fork 仓库、下载源码或手动运行终端命令，也不要求安装 Chrome；工坊使用你的默认浏览器。

### 选哪个文件？

| 你的电脑 / 使用方式 | 下载文件 | 打开方式 |
| --- | --- | --- |
| macOS | `.dmg` | 打开 DMG，把 **DIY Codex Bubble.app** 拖到“应用程序”，再打开它 |
| Windows 10/11 x64，推荐 | `windows-x64-light-setup.exe` | 双击安装，从桌面或开始菜单打开 **DIY Codex Bubble** |
| Windows，需要离线准备运行环境 | `windows-x64-offline-setup.exe` | 同上，安装包包含 Python 和 Node.js |
| Windows，不想安装 | `windows-x64-light-portable.zip` / `windows-x64-offline-portable.zip` | 完整解压到固定文件夹，双击其中的 **DIY Codex Bubble.exe** |

发布页里的 **Source code (zip / tar.gz)** 是开发源码，不是上面的便携版；第一次使用请选择 DMG 或 EXE 安装包。便携版保留整个解压文件夹，不要只移动里面的 EXE。

### 第一次打开

1. macOS 首次打开若被拦截，到“系统设置 → 隐私与安全性 → 仍要打开”放行。Windows 安装包目前未签名，可能出现 SmartScreen 提示；工坊安装和运行不需要管理员权限。
2. 工坊会复用兼容的 Python（3.10+、低于 4）和 Node.js（22+）；Windows 轻量版缺少环境时，会显示进度并下载到工坊自己的目录，不改系统环境。
3. 首次运行会自动把内置 **外星小猫** 应用到 Codex，并开启「电脑开机后自动恢复」。如果 Codex 此前已普通启动，保存输入并完全退出，再点工坊的「重新启动」；工坊不会强制关闭正在使用的应用。
4. 可以直接用外星小猫，也可以换图片、调拉伸线，或在顶部切换到豆包单独应用。点「恢复默认」可撤销当前平台的换肤。

macOS 和 Windows 的 Codex / 豆包气泡均已实机验证。应用更新或不同安装方式可能影响连接，遇到问题可按下方说明反馈。

Windows 默认提供约 **4 MB** 的小安装包：已有兼容环境就不重复安装；首次下载可以关闭窗口取消，之后重新打开会重试。完整离线版约 33 MB，安装后约 107–111 MB。若电脑没有运行环境，小安装包首次准备后也会增加相应的磁盘占用；已有环境的用户才会省下这些空间。图片、设置和下载的环境分别保存在本机独立目录，升级保留设置。

macOS 使用 DMG 安装，Windows 使用 EXE 安装包，两者都从 **DIY Codex Bubble** 应用入口打开工坊。macOS 首次打开可能需要“仍要打开”；Windows 安装包目前未签名，也可能出现 SmartScreen 提示。

**以后电脑开机并进入桌面：** 后台会启动工坊服务，并尝试恢复此前已应用过气泡的应用；无需打开终端或网页。**如果中途彻底退出应用：** 打开“DIY Codex Bubble”应用，在工坊里点对应的“重新启动”按钮。原版 Codex／豆包图标无法给已彻底退出的应用补上启动参数；如果直接用原图标重开，需先完全退出，再从工坊重新启动。开机自动恢复设置仅作用于当前电脑用户，工坊右侧可关闭。

**想再次换气泡：** 打开“DIY Codex Bubble”应用即可重新进入工坊；也可以在浏览器打开 `http://127.0.0.1:19329`。

需要从源码启动？见 [运行与开发说明](DEVELOPMENT.md)。

Windows 版会查找各个本地磁盘的常见安装位置、运行中的应用、注册表、快捷方式与可信发布者的 Microsoft Store 包。若找不到应用，点击工坊里的“选择应用位置”，选取已安装的 `Doubao.exe`、`Codex.exe` 或 `ChatGPT.exe`；位置会自动保存。不要选择下载的 `OnlineInstaller` 安装器。部分 Windows 商店应用可能不接受调试端口参数；若一直显示“未连接”，请在 [Issues](https://github.com/kaitongg-bit/DIYcodex-bubble/issues) 附上 Windows 版本、应用版本与 `.local/app-start.log` 中去除私人路径后的报错，勿上传聊天内容。

Windows 安装版的设置与日志位于 `%LOCALAPPDATA%\DIY Codex Bubble\Data`；升级保留设置。旧的源码 ZIP / `.cmd` 方式仍可用于开发，但需要自行安装 Python 和 Node.js。遇到连接问题请按上面的方式反馈。

## 使用说明

工坊顶部点击「检查更新」，发现新版后选择「下载并更新」。正式安装的 Mac 应用与 Windows 安装版会校验安装包、替换旧程序并重开工坊；气泡、设置和收藏保留。源码与便携版提供下载页入口。

### 更新与常见连接问题

- **更新不用先卸载。** Windows 新安装包安装到原位置，会覆盖旧程序，应用管理中只保留一个工坊；气泡、设置和收藏保留。旧的下载文件不会自动删除。macOS 更新时替换“应用程序”中的工坊应用。
- **Windows 更新提示“拒绝访问 / 无法关闭工坊后台”？** 取消安装，退出旧工坊后台后再运行安装包。关闭浏览器标签页不等于关闭后台。如果无法结束后台，重启 Windows 后先运行新版安装包。
- **已退出豆包，仍提示“已普通启动”？** 豆包可能仍有后台进程；在任务管理器的“详细信息”中检查 `Doubao.exe`。确认已保存内容后退出它，再从工坊启动；无法退出时可以重启电脑。
- **在线库“应用到工坊”提示 `127.0.0.1` 拒绝连接？** 先在同一台电脑打开 **DIY Codex Bubble**，等本机工坊网页出现，再回在线库点击导入。本机服务未运行时，在线库无法替你启动它。
- **便携版或源码如何更新？** 从发布页下载新版；这两种方式目前不支持工坊内自动替换程序。

在线气泡库里点击「应用到我的工坊」，可自动导入 PNG 和设置到本机社区气泡目录。请先打开已安装的工坊；导入后预览，再点击应用到 Codex / 豆包。素材库下方「打开所选素材文件夹」可直接打开图片所在目录。外部 PNG 重命名后名称会更新，但原设置按路径关联，建议调好后保留文件名。

### 一个工坊，两款应用

顶部选择 Codex 或豆包，共用同一套 PNG 库与编辑器，各自保存已应用气泡和连接状态。**切换平台不会自动换肤**；「恢复默认」只恢复当前平台。删除被两边使用的图片时，两边都会恢复默认。

<p align="center">
  <img src="docs/images/dual-platform-studio.jpg" alt="同一工坊切换到豆包" width="900">
</p>

豆包用户消息选择器已内置，首次使用不必编辑配置文件；支持 `/Applications/Doubao.app`，应用升级后可能需要适配。升级时会保留原版 Codex 的素材、设置和已应用气泡；豆包从未应用状态开始。如果之前运行过独立豆包版，请先关闭旧工坊服务，再使用统一工坊，避免两套监控互相覆盖。旧豆包文件夹和私人 `.local/` 不会被合入或公开，原图片仍可通过「连接素材文件夹」使用。

### 调气泡的一个小窍门

**拉伸线尽量落在平直、连续的边上。** 把尾巴、角色、弧形边角和复杂装饰留在固定区域，长消息就不容易把它们拉坏。应用前，记得同时看看短句和长消息。

不要求 PNG 是抖音规格：常见大图也可以导入，点「适合聊天」调整大小。100% 表示原图大小，文字字号不会跟着图案一起放大。

### 删除也有后悔药

素材卡片上的 **×** 会把 PNG 移入工坊回收区，点「撤销删除」可以恢复。**连接文件夹中的原文件也会一起移入回收区**，请留意这一点。

想彻底删掉，点「打开回收文件夹」，在系统文件管理器中删除不需要的文件；删除后无法由工坊撤销，回到工坊刷新即可更新记录。

## 社区与作品库

[打开在线作品库](https://kaitongg-bit.github.io/DIYcodex-bubble/)：选一款气泡，就能在接近 Codex 桌面布局的聊天模拟器里试效果，支持浅色、深色和输入自己的消息；不连接你的账号，也不读取真实聊天。

工坊顶部的「在线气泡库」直接打开这个公开网站。「审核台」只供项目维护者在有私有待审库权限的本机使用，因此不放在普通用户导航里。

<p align="center">
  <img src="docs/images/chat-simulation.png" alt="在线作品库的聊天模拟器预览" width="420"><br>
  <sub>在线作品库的聊天模拟器：看看短句、长消息中的气泡效果（独立模拟页面，不是真实 Codex 截图）</sub>
</p>

首次打开本机工坊，**外星小猫、LOVE、小猫炒菜** 三款预设已经在库里，首次启动会为 Codex 应用外星小猫；删掉以后想找回，点「恢复内置预设」。

- **使用社区气泡**：先打开本机工坊，再在作品详情页点「应用到我的工坊」，PNG 和设置会一起导入。预览后应用到 Codex / 豆包；也可下载 PNG 和 `.bubble.json` 手动导入。
- **在线制作**：在线工坊点「我要制作」后选择 PNG，先看到完整 Codex 模拟页，下方就是与本机工坊共用编辑逻辑的拉伸线、文字框和聊天预览。点「保存设置」可下载原 PNG 与 `.bubble.json`；未点击「我要发布」前，图片只在当前浏览器处理，不上传，也不接入 AI 生图。
- **投稿**：点「我要发布」，填写昵称与气泡名。PNG 和当前设置一起进入私有待审库，维护者人工审核后才会出现在在线气泡库，无需注册。审核标准见 [COMMUNITY.md](COMMUNITY.md)。
- **下载统计**：作品下载次数读取 GitHub Releases 的 PNG 下载统计，可能延迟，并非独立用户数；接口不可用时显示「暂未统计」。本机作品库另显示本机统计，不冒充全站数据。

想画一款自己的气泡？配套的 [气泡设计 skill](https://github.com/kaitongg-bit/douyinQIPAO) 可以帮助你设计原创 PNG，独立维护和更新，不必跟着工坊一起升级。画好后把图片导入这里，再调整、预览、应用。

## 许可与责任

本项目代码采用 [MIT 许可证](LICENSE)，可自由使用、修改和分发，包括商用。

代码许可不授予图片、角色 IP、肖像或商标等素材的任何权利。用户需自行取得素材授权，并承担内容制作、传播及违法侵权行为的相应责任；角色 IP、裸露或成人内容不因通过本工具制作或展示而获得授权。作者与维护者不为用户素材和用途背书；软件按 MIT 许可证条款"按现状"提供，在适用法律允许的范围内不承担由此产生的责任。详见 [素材权利与使用责任](RESPONSIBILITY.md)。

## 相关文档

- [运行与开发说明](DEVELOPMENT.md) · [English](DEVELOPMENT.en.md)
- [社区投稿与作品库](COMMUNITY.md) · [English](COMMUNITY.en.md)
- [Agent 工作指引](AGENTS.md) · [English](AGENTS.en.md)
- [素材权利与使用责任](RESPONSIBILITY.md) · [English](RESPONSIBILITY.en.md)

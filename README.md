<p align="center">
  <img src="presets/alien-cat.png" alt="DIY Codex Bubble" width="96">
</p>

<h2 align="center">DIY Codex Bubble · 气泡工坊</h2>

<h4 align="center">把自己的图，变成 Codex 聊天气泡。</h4>

<p align="center">
  <a href="https://github.com/kaitongg-bit/DIYcodex-bubble"><img src="https://img.shields.io/github/stars/kaitongg-bit/DIYcodex-bubble" alt="Stars"></a>
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20beta-lightgrey" alt="macOS and Windows beta">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Node.js-22%2B-blue" alt="Node.js 22+">
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

支持 **macOS 上的 Codex / ChatGPT 和豆包桌面端**；新增 Windows 测试版入口。只替换 **你发送的消息气泡**，助手回复保持原样；想换回来，点「恢复默认」即可。

**macOS 已验证 · Windows 测试版 · 中英文界面 · 本机素材库 · MIT 许可**

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

macOS 桌面应用已经实机验证；Windows 版的本机工坊、文件操作和启动流程已适配，但桌面气泡注入还需要 Windows 用户实机验收。需要 Python 3.9+ 和 Node.js 22+；暂不提供免安装运行环境的独立 App。

1. [下载最新版 ZIP](https://github.com/kaitongg-bit/DIYcodex-bubble/releases/latest)，解压到一个方便保留的位置。
2. macOS 在 **Finder（访达）** 双击 `Start Bubble Studio.command`；Windows 在资源管理器双击 `Start Bubble Studio.cmd`。只需这样完成首次设置。
3. 首次运行会自动把内置 **外星小猫** 应用到 Codex，并开启「登录电脑后自动恢复」。如果 Codex 此前已普通启动，页面会提示先完全退出，再点「重新启动」；工坊不会强制关闭正在使用的应用。
4. 之后可以直接用外星小猫，也可以在工坊里换图片、调拉伸线，或切换到豆包单独应用气泡。顶部「恢复默认」可随时撤销当前平台的换肤。

`Open Bubble Apps.app` 是压缩包里的轻量启动壳，不是另一个聊天应用；它只负责启动本机服务和已选的 Codex／豆包，图片与设置仍由工坊管理。Windows 对应文件为 `Open Bubble Apps.vbs`。

**以后登录电脑：** 后台会启动工坊服务，并尝试恢复此前已应用过气泡的应用；无需打开终端或网页。**如果中途彻底退出应用：** 双击 `Open Bubble Apps.app`（macOS）或 `Open Bubble Apps.vbs`（Windows）即可静默重新启动已选应用。不知道它在哪？在工坊右侧点「找到启动图标」，文件管理器会直接选中它；可以把这个入口固定到 Dock 或桌面。原版 Codex／豆包图标无法给已彻底退出的应用补上启动参数；如果直接用原图标重开，需先完全退出，再用气泡入口打开。所有登录启动设置仅作用于当前用户，工坊右侧可关闭。

首次打开工坊，页面上方会显示新手教程；收起后可随时点顶部「新手教程」重新查看。启动工坊不需要管理员权限，也不用手动敲终端命令。移动或删除工坊文件夹后，请在新位置重新开启登录自动恢复。

**双击后只看到了代码？** 请从系统文件管理器打开对应的启动文件，Codex 的文件预览只是查看代码。如果提示缺少运行环境，或需要从源码启动，见 [运行与开发说明](DEVELOPMENT.md)。

Windows 测试版会查找常见的应用安装位置和可信发布者的 Microsoft Store 包。若找不到应用，可在启动工坊前设置 `BUBBLE_STUDIO_CODEX_EXE` 或 `BUBBLE_STUDIO_DOUBAO_EXE` 为实际 `.exe` 路径。部分 Windows 商店应用可能不接受调试端口参数；若一直显示“未连接”，请在 [Issues](https://github.com/kaitongg-bit/DIYcodex-bubble/issues) 附上 Windows 版本、应用版本与 `.local/app-start.log` 中去除私人路径后的报错，勿上传聊天内容。

页面顶部的「下载最新版」ZIP 已包含 Windows 的 `.cmd` 入口；Windows 桌面注入仍标为测试版，遇到连接问题请按上面的方式反馈。

## 使用说明

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

首次打开本机工坊，**外星小猫、LOVE、小猫炒菜** 三款预设已经在库里，不会自动应用到聊天；删掉以后想找回，点「恢复内置预设」。

- **导入作品设置**：作品详情页可下载 PNG 和配套 `.bubble.json`。导入 PNG、选中它，再点「导入设置」，即可保留这款作品的拉伸与文字位置，确认效果后再应用。
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

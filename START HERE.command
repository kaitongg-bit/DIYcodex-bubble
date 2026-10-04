#!/bin/zsh
ROOT="${0:A:h}"
/usr/bin/open -R "$ROOT/Start Bubble Studio.command"
printf '\nDIY Codex Bubble 已在 Finder 中标出首次启动文件。\n请双击 Start Bubble Studio.command；以后恢复气泡请双击 Open Bubble Apps.command。\n按回车关闭此窗口。\n'
read -r

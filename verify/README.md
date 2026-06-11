# 验证脚本

本目录存放手动 / MCP 跑的验证脚本。

## mobile-smoke（Task 22）

**MCP browser 跑的 7 项检查**：

1. 顶部栏 + 底部 nav DOM 存在
2. 默认标题"枢纽"
3. 切"分类"tab → 分类网格显示
4. 切"枢纽"tab → 卡片网格显示
5. 主题切换按钮工作
6. 搜索按钮弹出覆盖层
7. Console error 数 = 0（**注意：18 个 pre-existing error 是 state-server CORS + favicon 404，与移动端无关**）

**运行方式**：用 mcp__plugin_playwright_playwright__browser_navigate 打开 http://127.0.0.1:8765/链接跳转.html，依次 evaluate / click / take_screenshot。

视口：390x844（iPhone 14 物理像素），用 browser_resize 设置。

**截图**（不入 git）：
- `mobile-theme-after.png` — 切到深色主题后的截图
- `mobile-final.png` — 切回枢纽 tab 后的截图

**运行结果**（2026-06-11）：
- 1: PASS
- 2: PASS
- 3: PASS
- 4: PASS
- 5: PASS
- 6: PASS
- 7: 18 个 error（pre-existing CORS / favicon 404，与移动端重构无关）

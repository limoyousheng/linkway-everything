# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 项目结构

本目录是一个个人工作区，不是典型的可构建工程。没有 `package.json`、构建系统、测试或代码检查工具。

- `AI平台导航.html` — 单文件静态 HTML 仪表盘，列出常用 AI 平台的快速访问卡片。Tailwind CSS（CDN）和 Font Awesome 4.7.0（CDN）通过 `<script>`/`<link>` 引用，不安装任何本地依赖。约 1180 行。
- `open-ai-platform-edge.cmd` — Windows 启动脚本：在后台启动 `pythonw -m http.server 8765`，并用 Microsoft Edge 打开该 HTML 页。
- `.Codex/settings.local.json` — 项目级 Codex 权限白名单（允许访问 minimaxi.com / 阿里云 OSS 等域名的 WebFetch，以及 `python`、`npx skills`、`Codex mcp`、`uvx`、`codex` 等命令）。
- 其它非代码资源忽略。

## 常用命令

```bash
# 方式一：直接打开 HTML（最简单，双击亦可）
start "" "AI平台导航.html"

# 方式二：通过本地 HTTP 服务访问（与 .cmd 脚本等价）
pythonw -m http.server 8765 --bind 127.0.0.1
# 浏览器访问 http://127.0.0.1:8765/AI平台导航.html
# 关闭服务：结束占用 8765 端口的 pythonw.exe 进程

# 一键启动（仅 Windows）
open-ai-platform-edge.cmd

# 语法检查（提取 <script> 块用 node 解析）
node -e "const fs=require('fs');const h=fs.readFileSync('AI平台导航.html','utf8');const m=h.match(/<script>\\s*document\\.addEventListener\\('DOMContentLoaded'[\\s\\S]*?<\\/script>/);try{new Function(m[0].replace(/^<script>/,'').replace(/<\\/script>$/,''));console.log('OK')}catch(e){console.log('ERR',e.message)}"
```

无构建、无 Lint、无测试、无类型检查命令。

## `AI平台导航.html` 架构

单文件 SPA，纯 HTML + 内联 Tailwind 配置 + 原生 JS（无框架、无打包、无 npm）。**所有数据（分类、卡片、主题）由 JS 维护并通过 `localStorage` 持久化**，刷新后保留。

**自顶向下结构：**

1. **`<head>`** — viewport / theme-color 元标签；`tailwind.config = { … }` 内联在 `<script>` 中（自定义色板、字体、动画 keyframes、自定义阴影等）；Tailwind v3 与 Font Awesome 4.7.0 CDN 引用。
2. **`<style type="text/tailwindcss">`** — `@layer utilities` 中定义组件类（`.glass-effect`、`.platform-card`、各种渐变背景），以及 `prefers-reduced-motion` 媒体查询；集中定义 `html.dark …` 暗色模式覆写规则；以及 `.category-btn.drop-target` 的拖拽高亮态。
3. **`<body>` 标记**：
   - 固定头部 `#theme-toggle`（主题切换）、`#manage-categories-btn`（管理分类）、`#add-site-btn`（添加网站）；统计徽章 `#stat-platforms` / `#stat-categories` 由 JS 动态填充。
   - 搜索框 `#search-input`。
   - 分类按钮容器 `#category-buttons`（由 JS 渲染）。
   - 卡片网格 `#card-grid`（由 JS 渲染）。
   - **三个模态框/弹层**：
     - `#add-site-modal` — 卡片表单（添加/编辑双模），含名称/URL/描述/分类下拉，**图标 URL 输入 + 本地文件上传 + 实时预览 + 清除按钮**。
     - `#categories-modal` — 分类管理：列表（每行可重命名/删除，显示该分类下平台数）+ 新增分类表单（名称 + 颜色）。**每行最左侧的「上长中短下长」三横线抓手支持长按 300ms 拖动重排**。
     - `#card-actions-popover` — 卡片右上角三点弹出的浮层，含「编辑 / 移动到分类（hover 出二级子菜单，列出全部分类）/ 删除」。
4. **`<script>`**（文件底部，`DOMContentLoaded` 内）— 数据驱动实现：
   - **状态模型 `state`** — `{ categories: [{id, name, color}], cards: [{id, name, url, description, categoryId, iconUrl}], theme }`。
   - **持久化** — `localStorage` key `ai-nav-state-v1`；启动时 `loadState` 读取，首次访问时使用内置 `DEFAULT_CATEGORIES` / `DEFAULT_CARDS` 种子。每次 mutation 立即 `saveState`。
   - **`COLOR_MAP`** — 10 种颜色（蓝/紫/绿/红/青/橙/粉/黄/蓝绿/灰）对应的 Tailwind 渐变 / 背景 / 文字 / 默认 Font Awesome 图标。新增分类时只选颜色，图标由颜色派生。
   - **渲染入口 `renderAll()`** — 重建分类按钮、卡片网格、统计、卡片表单的分类下拉。
   - **拖拽** — 卡片 `draggable=true`，分类按钮是 dropzone（拖入时高亮 `.drop-target`）。`dataTransfer` 传递 cardId，drop 时改 `categoryId` 并 re-render。`全部` 按钮不可作为 dropzone。
   - **图标** — 自定义 `iconUrl` 用 `<img>` 渲染；图片加载失败 (`onerror`) 回退到分类默认 Font Awesome 图标。本地上传走 `FileReader.readAsDataURL` 转 data URL 存入 `iconUrl`。
   - **删除分类** — 受保护的内置 `cat-other` 分类不可删/不可重命名；删其他分类时把内部所有卡片 `categoryId` 改为 `cat-other`（自动重建 `其他` 分类）。
   - **主题** — 切换 `<html>.dark` + `colorScheme` + body 背景，同时写入 `state.theme`。
   - **Toast** — 固定底部居中，3 秒后淡出。

**新增/修改** 时注意：

- 文件中的面向用户字符串与文件名均为简体中文，新增内容请保持一致。
- 新增分类颜色请用 `COLOR_MAP` 已有的 10 种之一，无需修改 Tailwind 配置。
- 卡片上 `wrapper.draggable = true`，不要在 `buildCardElement` 里去掉，否则会丢拖拽能力。
- 分类长按重排只在管理分类模态框内有效（`#categories-modal`），通过 `setupCategoryReorder()` 绑定，事件挂在 `document` 上但仅在该模态框打开时被激活。`categoryReorderBound` 标志保证只绑一次；重新渲染列表时不需要重绑。提交顺序变更后调用 `renderAll()` + `renderCategoryManageList()`，主页面的分类按钮会按新顺序刷新。
- 上传的图标以 data URL 形式存进 localStorage，注意配额（一般 5MB），太大的本地图片会让存储失败并被静默吞掉。

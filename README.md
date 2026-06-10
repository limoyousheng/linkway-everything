# 链接跳转

> 一个装在单文件 HTML 里的私人链接收藏夹。玻璃卡片、玻璃侧边栏、长按拖拽排序、自定义分类/图标/颜色。**纯本地，所有数据存浏览器 localStorage，不上任何服务器。**

---

## 30 秒上手

1. **下载**这 7 个文件（git clone / GitHub ZIP / U 盘拷）：

   ```
   链接跳转.html       ← 主页面，双击它
   链接跳转.cmd        ← （可选）一键启动脚本
   state-server.py     ← （可选）自动抓图标/抓描述的本地代理
   tailwindcss.js      ← 样式库（离线用，已本地化）
   sortable.min.js     ← 拖拽库（离线用，已本地化）
   README.md            ← 你正在看的这个文件
   LICENSE              ← 个人使用许可证
   .gitignore
   ```

2. **双击 `链接跳转.html`**，浏览器打开 → 直接用。

就这么简单。**不需要装任何东西、不需要联网、不需要 Python。**

---

## 你能用它做什么

- **添加链接**：点「刻印新站点」→ 填网址 + 名称 + 分类 → 保存
- **搜索**：顶部搜索框，按名称/描述/网址/分类过滤
- **分类管理**：左侧栏底部「创建分类」按钮，可以重命名、换颜色、换图标、删除
- **拖拽排序**：长按卡片 75ms → 拖到目标位置；拖到左侧栏分类可以换分类
- **主题切换**：右上角太阳/月亮图标，深色/浅色
- **编辑/删除**：卡片右上角三点按钮
- **每个分类都能**：
  - 10 种预设颜色 + **自定义颜色**（用 color picker 选任意颜色）
  - 20 种 Material Symbols 图标任选
  - 受保护的「其他」兜底分类（删不掉、改不了名字）

---

## 两种使用模式

### 模式一：纯离线（默认就够用）

直接双击 `链接跳转.html`，浏览器用 `file://` 打开。

- ✅ **完整可用**：所有功能（添加/编辑/删除/搜索/拖拽/主题/分类/图标/颜色）
- ✅ **完全离线**：Tailwind 和 SortableJS 都已打包在 `tailwindcss.js` 和 `sortable.min.js`，不需要联网
- ❌ 不能「自动抓图标」和「自动抓描述」（需要联网才能抓别人的网站）

> **大多数人就用这个模式。** 把这 7 个文件拷给任何人，**双击 HTML 就能用**。

### 模式二：离线 + 自动抓（可选增强）

如果你想用「自动抓图标」「自动抓描述」两个按钮：

1. **装一次 Python 3.8+**（如果没装过）
   - 下载：<https://www.python.org/downloads/>
   - 安装时**必须**勾选 `Add Python to PATH`（安装界面第一屏底部的复选框）
   - 装完新开一个 cmd 窗口，跑 `python --version` 验证

2. **双击 `链接跳转.cmd`**，它会自动：
   - 启动静态服务（端口 8765）
   - 启动抓取代理（端口 9001）
   - 用 Edge 打开仪表盘

> 抓图标/抓描述的原理：`state-server.py` 用 Python 抓目标站点的 HTML，绕过浏览器的 CORS 限制，从 `<link rel="icon">` 找图标、从 `<meta description>` 找描述。**完全本地运行，不经过任何第三方服务**。
> 抓到的图标会存到 `icons/` 文件夹（按 URL 哈希命名），下次直接本地读，**断网也能显示已抓过的图标**。删除卡片时本地图标文件也会同步删除。

---

## 文件清单

| 文件 | 作用 | 必须？ |
|---|---|---|
| `链接跳转.html` | 主页面（约 2700 行，所有逻辑都在里面） | ✅ |
| `tailwindcss.js` | 样式库（已下载，410KB） | ✅ |
| `sortable.min.js` | 拖拽库（已下载，45KB） | ✅ |
| `链接跳转.cmd` | Windows 一键启动脚本 | 可选 |
| `state-server.py` | 自动抓图标/抓描述的本地代理 | 可选 |
| `icons/` | 抓取的图标缓存（自动生成，不用管） | 自动 |
| `README.md` | 你正在看的 | 参考 |
| `LICENSE` | 个人使用许可证 | 参考 |
| `.gitignore` | Git 排除配置 | 仅 git 用 |

> **最少要拷 3 个文件**就能离线用：`链接跳转.html` + `tailwindcss.js` + `sortable.min.js`。

---

## 数据存在哪里

所有数据（你添加的卡片、分类、颜色、图标、主题）都存在浏览器的 **localStorage** 里：

- 浏览器关掉再开 → 数据还在
- 清除浏览器数据 → 数据没了（建议「添加/编辑」前先备份）
- 换浏览器/换电脑 → 数据**不会**自动跟过去（除非你用同一台电脑同一个浏览器）

要备份/迁移：打开浏览器 DevTools (F12) → Application → Local Storage → 复制 `ai-nav-state-v1` 的 value。

---

## 常见问题

**Q: 双击 HTML 打开后是空白的？**
A: 三个文件必须放**同一个文件夹**。`链接跳转.html` 通过相对路径 `./tailwindcss.js` 和 `./sortable.min.js` 找这两个库。

**Q: 浏览器显示乱码？**
A: 确保文件是 UTF-8 编码。用 VS Code / Notepad++ 打开后另存为 UTF-8 即可。Windows 记事本另存为 "UTF-8"（不是 "UTF-8 BOM"）。

**Q: 我用的是 Chrome / Firefox，不是 Edge，能用吗？**
A: 完全可以。浏览器是兼容的。
- 离线模式：双击 HTML，Chrome/Firefox 默认就用 `file://` 打开
- 模式二：编辑 `链接跳转.cmd`，把 `start msedge.exe` 改成 `start chrome.exe` 或手动用 Firefox 打开 `http://127.0.0.1:8765/链接跳转.html`

**Q: 「自动抓图标」点了没反应？**
A: `state-server.py` 没在跑。要么切到模式二（双击 `链接跳转.cmd`），要么不抓，手动上传图标（点「图标印记 → Choose File」选本地图片）。

**Q: 防火墙弹「是否允许 Python 通信」？**
A: 点「允许」。`127.0.0.1` 是本机回环，本来就不出网卡，Windows 弹这个只是走个形式。

**Q: 端口 9001 被占用了？**
A: 打开 `链接跳转.cmd`，找到 `STATE_PORT=9001` 改成别的（如 9090）。如果改了端口，**还要同时改 HTML 里所有 `http://127.0.0.1:9001` 引用**（搜 `127.0.0.1:9001` 能找到 3 处）。

**Q: Mac / Linux 能用吗？**
A: HTML + 离线模式可以。`.cmd` 是 Windows 专用，Mac/Linux 需要写个对应的 shell 脚本（参考 `.cmd` 里的命令）。

---

## 「自动抓」能抓到什么、不能抓什么

能抓到：
- 普通 HTML 站点（V2EX、阮一峰博客、绝大多数公司官网）
- 有 `<link rel="icon">` 标签的站
- 有 `<meta name="description">` 标签的站

抓不到（或抓到的没信息量）：
- **JS 渲染站**（豆包、Notion、各种 SPA）：HTML 头里没 meta，要等 JS 跑完才有
- **反爬严格的站**（ChatGPT、GitHub、Twitter）：服务端会拒绝 Python urllib
- **需要登录的站**：抓不到任何 meta
- **简陋站**：会回退到 `<title>`，但 title 经常是「首页 - XX网」这种没信息量的

---

## 数据格式

localStorage 里的 `ai-nav-state-v1` 是 JSON：

```json
{
  "categories": [
    { "id": "cat-chat", "name": "聊天AI", "color": "blue", "icon": "chat_bubble" }
  ],
  "cards": [
    {
      "id": "c-1",
      "name": "ChatGPT",
      "url": "https://chatgpt.com/",
      "description": "OpenAI 开发的...",
      "categoryId": "cat-chat",
      "iconUrl": "https://www.google.com/s2/favicons?domain=chatgpt.com&sz=64"
    }
  ],
  "theme": "light"
}
```

你直接编辑这个 JSON 也能批量改（但**先备份**）。

---

## 进阶：和 Claude Code 协作

如果你的 `state-server` 在跑（模式二），它会同时提供 `http://127.0.0.1:9001/state`，让 Claude Code 通过 WebFetch 拉取你浏览器的实时数据 —— 可以让 AI 帮你整理分类、补全描述。

要让 Claude 能访问，需要在 Claude Code 项目配置里把 `127.0.0.1:9001` 加入 WebFetch 白名单。

---

## 许可

本项目仅限**个人非商业使用**。你可以下载、运行、学习、个人修改。

**禁止**：商用、转售、再分发、用于盈利活动。

详细条款见 [LICENSE](./LICENSE)。如需商用授权请联系：1776619796@qq.com

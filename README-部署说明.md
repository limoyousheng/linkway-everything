# AI 平台导航 — 部署说明

把这个目录拷到另一台 Windows 电脑上（U盘、网盘、git clone 都可以），**双击 `open-ai-platform-edge.cmd`** 即可启动。

## 一次性准备

另一台电脑需要：

1. **Python 3.8+**
   - 下载：<https://www.python.org/downloads/>
   - 安装时**必须勾选** `Add Python to PATH`（第一屏底部那个复选框）
   - 安装完新开一个 cmd 窗口跑 `pythonw --version` 验证

2. **Microsoft Edge**（Win10/11 默认自带）

不需要 node、npm、git、任何包管理器。

## 启动方式

1. 把整个 `1231` 文件夹（任意路径）放到目标电脑
2. 双击 `open-ai-platform-edge.cmd`
3. Edge 自动打开仪表盘

**这个脚本会启动两个本地服务：**

| 端口 | 用途 |
|---|---|
| `8765` | 静态文件服务，提供 `AI平台导航.html` |
| `9001` | `state-server.py`，提供**抓图标**、**抓描述**、**状态同步** |

**抓图标/抓描述怎么工作的：**
浏览器里的 JS 调 `http://127.0.0.1:9001/fetch-html?url=...` 或 `/fetch-meta?url=...`。
`state-server.py` 用 Python 抓目标站点的 HTML 回来（绕过浏览器的 CORS 限制），再正则解析 `<link rel="icon">` / `<meta description>` 等标签。
**完全本地，不经过任何第三方服务**。

## 验证服务是否正常

双击 `.cmd` 后**等 2 秒**，新开一个 cmd 窗口跑：

```cmd
curl http://127.0.0.1:9001/health
```

应该看到 `{"ok": true}`。

如果返回连不上：
- 看是否有 "端口 9001 已被占用" 的提示
- 用 `netstat -ano | findstr :9001` 查占用进程 PID，任务管理器里结束它
- 或者修改 `.cmd` 里 `STATE_PORT=9001` 改个不冲突的端口，**同时修改 HTML 里所有 `http://127.0.0.1:9001` 引用**

## 常见问题

**Q: 浏览器能打开仪表盘，但点"自动获取图标"提示"未找到图标"。**
A: state-server 没起来。检查 `curl http://127.0.0.1:9001/health` 是否返回 200。最大可能是端口被占或 Python 没装好。

**Q: state-server 起来了，但 502 抓不到某些站。**
A: 正常。ChatGPT、GitHub 等反爬严格的站会拒绝 Python urllib；JS 渲染站（豆包、Notion）HTML 里没 meta。详见限制清单。

**Q: 防火墙弹出"是否允许 Python 通信"，点允许就行吗？**
A: 对。127.0.0.1 是本机回环，本来就不出网卡，但 Windows 仍会弹允许提示。

**Q: 我可以换 Chrome / Firefox 吗？**
A: 可以。删掉 `.cmd` 里的 `start msedge.exe` 那行，浏览器手动打开 `http://127.0.0.1:8765/AI平台导航.html` 即可。

## 限制清单

- **JS 渲染站抓不到**（豆包、Notion、各种 SPA）：HTML 头里没 meta，要等 JS 跑完才有
- **反爬严格的站**（ChatGPT、GitHub、Twitter）：服务端会拒绝 Python urllib，返回 502
- **需要登录的站**：抓不到任何 meta
- **没有 meta 的简陋站**：会回退到 `<title>`，但 title 经常是"首页 - XX网"这种没信息量的

## 想要把状态同步到 Claude 一起协作

state-server 同时提供 `http://127.0.0.1:9001/state`，让 Claude Code 通过 WebFetch 拉取你浏览器的 localStorage 实时数据。
要开启这个能力，需要在 Claude Code 项目配置里把 `127.0.0.1:9001` 加入 WebFetch 白名单。

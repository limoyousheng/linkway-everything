@echo off
setlocal

REM ============================================================
REM  AI 平台导航 - 一键启动（双击运行）
REM  启动两个本地服务并用 Edge 打开仪表盘：
REM    1) 8765 : 静态文件服务（提供 AI平台导航.html）
REM    2) 9001 : state-server.py（跨域代理 + 状态同步）
REM  需要：Python 3.8+（自带 pythonw.exe）、Microsoft Edge
REM ============================================================

set "ROOT=%~dp0"
set "PORT=8765"
set "STATE_PORT=9001"
set "PAGE=http://127.0.0.1:%PORT%/AI%E5%B9%B3%E5%8F%B0%E5%AF%BC%E8%88%AA.html"

REM ---- 检测 Python 是否可用 ----
where pythonw >nul 2>nul
if errorlevel 1 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo [错误] 未检测到 Python。请先安装 Python 3.8+ 并勾选"Add Python to PATH"。
        echo 下载：https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set "PY=py -3"
) else (
    set "PY=pythonw"
)

REM ---- 检测端口是否被占用 ----
netstat -ano | findstr /R "[: ]%PORT%.*LISTENING" >nul 2>nul
if not errorlevel 1 (
    echo [警告] 端口 %PORT% 已被占用，原有服务可能被复用。
)
netstat -ano | findstr /R "[: ]%STATE_PORT%.*LISTENING" >nul 2>nul
if not errorlevel 1 (
    echo [警告] 端口 %STATE_PORT% 已被占用，state-server 启动会失败。
    echo         如需释放端口请先结束占用进程，或修改本脚本中的 STATE_PORT 变量。
)

cd /d "%ROOT%"

REM ---- 启动静态文件服务 ----
echo 启动静态服务：http://127.0.0.1:%PORT%/
start "" %PY% -m http.server %PORT% --bind 127.0.0.1

REM ---- 启动 state-server（提供抓图标、抓描述、状态同步）----
echo 启动 state-server：http://127.0.0.1:%STATE_PORT%/
start "" %PY% "%ROOT%state-server.py"

REM ---- 等 1.5s 让服务 listen ----
timeout /t 2 /nobreak >nul

REM ---- 打开 Edge ----
where msedge >nul 2>nul
if not errorlevel 1 (
    start "" msedge.exe --new-window "%PAGE%"
) else (
    echo 未找到 msedge.exe，请手动用浏览器打开：%PAGE%
)

endlocal

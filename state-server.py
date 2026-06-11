"""
本地状态同步服务：监听 9001，接收浏览器 POST 来的 localStorage state 并缓存，
供 Claude Code 通过 WebFetch 拉取。

接口：
  GET  /state        - 返回最近一次 POST 的 state JSON（或空 state）
  GET  /health       - 健康检查
  POST /state        - 浏览器推送 state；body = JSON
  GET  /fetch-html?url=<encoded>  - 跨域代理：拉取目标页面 HTML（绕过浏览器 CORS），
                                  供前端解析 link[rel=icon] 用
  GET  /fetch-meta?url=<encoded>  - 跨域代理：拉取页面 HTML，提取
                                  meta[name=description] / meta[property=og:description] / title，
                                  按优先级返回首个非空结果（不调用任何 AI）
  GET  /save-icon?url=<encoded>   - 下载远程图标到 ./icons/<hash>.<ext>，
                                  返回本地 URL（浏览器下次直接读本地）
  GET  /icons/<filename>          - 直接从 ./icons/ 目录提供静态文件（带 CORS）
  DELETE/GET /delete-icon?filename=<encoded> - 删除 ./icons/ 中的指定文件
  GET  /             - 简单说明页

启动：pythonw state-server.py
"""
import hashlib
import json
import re
import threading
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ICONS_DIR = SCRIPT_DIR / "icons"
ICONS_DIR.mkdir(exist_ok=True)

LATEST_STATE = {
    "categories": [],
    "cards": [],
    "theme": "light",
    "_meta": {"received": False, "last_update": None},
}
_LOCK = threading.Lock()


def fetch_html(target_url, timeout=5):
    """服务端拉取 HTML，绕过浏览器 CORS。返回 (status_code, body_text or error_str)。"""
    parsed = urllib.parse.urlparse(target_url)
    if parsed.scheme not in ("http", "https"):
        return 400, "only http/https allowed"
    req = urllib.request.Request(
        target_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0 Safari/537.36"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            raw = resp.read()
            # meta 提取只看 head，限制最大字节数避免浪费
            return resp.status, raw[:256 * 1024].decode(charset, errors="replace")
    except Exception as e:
        return 502, f"fetch failed: {e}"


def _attr_in_tag(tag, name):
    """从单个 meta 标签字符串里提取指定属性（name/property/content）的值。"""
    pat = r'\b' + re.escape(name) + r'\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))'
    m = re.search(pat, tag, re.IGNORECASE)
    if not m:
        return None
    return (m.group(1) or m.group(2) or m.group(3) or "").strip() or None


def _meta_content(html, key):
    """在 <meta> 标签中查找 name/property == key 的 content。"""
    for m in re.finditer(r'<meta\b[^>]*?/?>', html, re.IGNORECASE | re.DOTALL):
        tag = m.group(0)
        if _attr_in_tag(tag, 'name') == key or _attr_in_tag(tag, 'property') == key:
            content = _attr_in_tag(tag, 'content')
            if content:
                return content
    return None


def _title(html):
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    if not m:
        return None
    t = m.group(1).strip()
    return re.sub(r'\s+', ' ', t) if t else None


def _extract_jsonld(html):
    """从 <script type="application/ld+json"> 中按优先级取描述性字段：
    description > headline > about > name。支持 @graph 嵌套结构和数组形式的 JSON-LD。

    很多站（知乎、CSDN、Medium、Wikipedia 等）在 JSON-LD 里写了比 og:description
    更准的人工描述，作为 og/meta 都没抓到时的兜底。"""
    for m in re.finditer(
        r'<script\b[^>]*\btype\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.IGNORECASE | re.DOTALL,
    ):
        raw = m.group(1)
        # 防 JSON 里夹带 </script> 提前闭合（极少见但遇到过）
        raw = re.sub(r'</?script[^>]*>', '', raw).strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        # 候选 entity 列表：支持 @graph（多个 entity）、顶层对象、顶层数组
        candidates = []
        if isinstance(data, dict) and isinstance(data.get('@graph'), list):
            candidates = [x for x in data['@graph'] if isinstance(x, dict)]
        elif isinstance(data, dict):
            candidates = [data]
        elif isinstance(data, list):
            candidates = [x for x in data if isinstance(x, dict)]
        for item in candidates:
            for key in ('description', 'headline', 'about', 'name'):
                v = item.get(key)
                if isinstance(v, str) and v.strip():
                    return v.strip()
                # 某些 schema 把 name 写成对象 { @value: "..." }
                if key == 'name' and isinstance(v, dict):
                    n = v.get('@value') or v.get('value')
                    if isinstance(n, str) and n.strip():
                        return n.strip()
    return None


def extract_meta(html):
    """按优先级提取页面描述：og:description > description > JSON-LD > title。"""
    desc = (
        _meta_content(html, 'og:description')
        or _meta_content(html, 'description')
        or _meta_content(html, 'Description')
        or _extract_jsonld(html)
    )
    title = _title(html)
    source = "none"
    if desc:
        if _meta_content(html, 'og:description'):
            source = "og:description"
        elif _meta_content(html, 'description') or _meta_content(html, 'Description'):
            source = "meta description"
        elif _extract_jsonld(html):
            source = "json-ld"
    elif title:
        source = "title"
    return {
        "description": desc,
        "title": title,
        "source": source,
    }


class Handler(BaseHTTPRequestHandler):
    def _json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _text(self, code, text, content_type="text/plain; charset=utf-8"):
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._json(204, {})

    def do_GET(self):
        if self.path == "/health":
            return self._json(200, {"ok": True})
        if self.path == "/state":
            with _LOCK:
                return self._json(200, LATEST_STATE)
        if self.path == "/":
            return self._json(200, {
                "service": "state-server",
                "endpoints": [
                    "/state",
                    "/health",
                    "/fetch-html?url=<url>",
                    "/fetch-meta?url=<url>",
                    "/save-icon?url=<url>",
                    "/icons/<filename>",
                    "/delete-icon?filename=<file>",
                ],
                "note": "POST /state from the browser to update.",
            })
        if self.path.startswith("/fetch-html?"):
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1])
            urls = qs.get("url", [])
            if not urls:
                return self._json(400, {"error": "missing url param"})
            code, body = fetch_html(urls[0])
            if code != 200:
                return self._json(code, {"error": body})
            return self._text(200, body, "text/html; charset=utf-8")
        if self.path.startswith("/fetch-meta?"):
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1])
            urls = qs.get("url", [])
            if not urls:
                return self._json(400, {"error": "missing url param"})
            code, body = fetch_html(urls[0])
            if code != 200:
                return self._json(code, {"error": body})
            meta = extract_meta(body)
            return self._json(200, meta)
        if self.path.startswith("/save-icon"):
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
            urls = qs.get("url", [])
            if not urls:
                return self._json(400, {"error": "missing url param"})
            try:
                filename = _save_icon_to_disk(urls[0])
            except Exception as e:
                return self._json(502, {"error": f"download failed: {e}", "remoteUrl": urls[0]})
            local_url = f"http://127.0.0.1:9001/icons/{filename}"
            return self._json(200, {"localUrl": local_url, "filename": filename, "remoteUrl": urls[0]})
        if self.path.startswith("/delete-icon"):
            return self._delete_icon()
        if self.path.startswith("/icons/"):
            return self._serve_icon()
        return self._json(404, {"error": "not found"})

    def do_DELETE(self):
        if self.path.startswith("/delete-icon"):
            return self._delete_icon()
        body = b"method not allowed"
        self.send_response(405)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_icon(self):
        """从 ICONS_DIR 提供静态图标文件。"""
        rel = self.path[len("/icons/"):]
        # 防路径穿越
        if "/" in rel or "\\" in rel or ".." in rel or not rel:
            return self._json(404, {"error": "invalid path"})
        fp = ICONS_DIR / rel
        if not fp.exists() or not fp.is_file():
            return self._json(404, {"error": "not found"})
        ext = fp.suffix.lower()
        ctype = _ICON_CT.get(ext, "application/octet-stream")
        try:
            data = fp.read_bytes()
        except OSError as e:
            return self._json(500, {"error": f"read failed: {e}"})
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, max-age=86400")
        self.end_headers()
        self.wfile.write(data)

    def _delete_icon(self):
        qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
        names = qs.get("filename", [])
        if not names:
            return self._json(400, {"error": "missing filename param"})
        fname = names[0]
        if "/" in fname or "\\" in fname or ".." in fname or not fname:
            return self._json(400, {"error": "invalid filename"})
        fp = ICONS_DIR / fname
        if fp.exists() and fp.is_file():
            try:
                fp.unlink()
                return self._json(200, {"deleted": True, "filename": fname})
            except OSError as e:
                return self._json(500, {"error": f"delete failed: {e}"})
        return self._json(200, {"deleted": False, "filename": fname, "reason": "not found"})

    def do_POST(self):
        if self.path != "/state":
            return self._json(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length > 0 else b"{}"
            parsed = json.loads(raw.decode("utf-8"))
        except Exception as e:
            return self._json(400, {"error": "bad json", "detail": str(e)})

        if not isinstance(parsed, dict):
            return self._json(400, {"error": "expected object"})

        with _LOCK:
            LATEST_STATE.clear()
            LATEST_STATE.update({
                "categories": parsed.get("categories", []),
                "cards": parsed.get("cards", []),
                "theme": parsed.get("theme", "light"),
                "_meta": {
                    "received": True,
                    "last_update": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                    "card_count": len(parsed.get("cards", [])),
                    "category_count": len(parsed.get("categories", [])),
                },
            })
        return self._json(200, {"ok": True})

    def log_message(self, fmt, *args):
        # 静默：避免控制台刷屏
        pass


def _download_icon(remote_url, timeout=10):
    """下载远程图标二进制，返回 (bytes, ext)。失败抛异常。"""
    parsed = urllib.parse.urlparse(remote_url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("only http/https allowed")
    req = urllib.request.Request(
        remote_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0 Safari/537.36",
            "Accept": "image/*,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        ctype = (resp.headers.get("Content-Type") or "image/png").split(";")[0].strip().lower()
    ext_map = {
        "image/png": "png", "image/jpeg": "jpg", "image/jpg": "jpg",
        "image/gif": "gif", "image/webp": "webp", "image/svg+xml": "svg",
        "image/x-icon": "ico", "image/vnd.microsoft.icon": "ico",
    }
    ext = ext_map.get(ctype, "png")
    return data, ext


def _save_icon_to_disk(remote_url):
    """下载图标存到 ICONS_DIR，按 URL 的 md5 前 16 位 + 扩展名命名。
    返回文件名（如 'abc123.png'）。"""
    data, ext = _download_icon(remote_url)
    h = hashlib.md5(remote_url.encode("utf-8")).hexdigest()[:16]
    filename = f"{h}.{ext}"
    (ICONS_DIR / filename).write_bytes(data)
    return filename


# 图标文件的 Content-Type 映射（按扩展名）
_ICON_CT = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


if __name__ == "__main__":
    addr = ("127.0.0.1", 9001)
    print(f"state-server listening on http://{addr[0]}:{addr[1]}")
    ThreadingHTTPServer(addr, Handler).serve_forever()

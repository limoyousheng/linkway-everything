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
  GET  /             - 简单说明页

启动：pythonw state-server.py
"""
import json
import re
import threading
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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


def extract_meta(html):
    """按优先级提取页面描述：og:description > description > title。"""
    desc = (
        _meta_content(html, 'og:description')
        or _meta_content(html, 'description')
        or _meta_content(html, 'Description')
    )
    title = _title(html)
    source = "none"
    if desc:
        source = "og:description" if "og:description" in (str(desc) + "") else "meta description"
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
        return self._json(404, {"error": "not found"})

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


if __name__ == "__main__":
    addr = ("127.0.0.1", 9001)
    print(f"state-server listening on http://{addr[0]}:{addr[1]}")
    ThreadingHTTPServer(addr, Handler).serve_forever()

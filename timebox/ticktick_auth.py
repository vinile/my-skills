#!/usr/bin/env python3
"""
ticktick_auth.py  —  TickTick 一次性 OAuth 授权脚本
运行后会在浏览器打开授权页，完成后 token 自动保存到 ~/.config/timebox/ticktick.json
"""

import http.server, webbrowser, json, os, urllib.parse, urllib.request, base64, threading
from pathlib import Path

CLIENT_ID     = "2gUmdA4v1Pxt9UV2Dx"
CLIENT_SECRET = "2MW8WEAtO2tVSXsS40cU2lzgtPlk7LIK"
REDIRECT_URI  = "http://localhost:8765/callback"
TOKEN_FILE    = Path.home() / ".config" / "timebox" / "ticktick.json"

AUTH_URL  = "https://ticktick.com/oauth/authorize"
TOKEN_URL = "https://ticktick.com/oauth/token"
PORT      = 8765

received_code = None

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global received_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            received_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h2 style='font-family:sans-serif;padding:40px'>✅ 授权成功！可以关闭此页面。</h2>".encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad request")
        threading.Thread(target=self.server.shutdown).start()

    def log_message(self, *args): pass  # 静默日志

def main():
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 1. 启动本地回调服务器
    server = http.server.HTTPServer(("localhost", PORT), CallbackHandler)

    # 2. 构造授权 URL 并打开浏览器
    auth_params = urllib.parse.urlencode({
        "client_id":     CLIENT_ID,
        "response_type": "code",
        "redirect_uri":  REDIRECT_URI,
        "scope":         "tasks:write tasks:read",
    })
    auth_full_url = f"{AUTH_URL}?{auth_params}"
    print(f"\n正在打开浏览器授权页...")
    print(f"如果浏览器未自动打开，请手动访问：\n{auth_full_url}\n")
    webbrowser.open(auth_full_url)

    # 3. 等待回调（阻塞直到收到 code 或关闭）
    print("等待授权完成（在浏览器中点击同意）...")
    server.serve_forever()

    if not received_code:
        print("❌ 未收到授权码，请重试")
        return

    print(f"✓ 收到授权码，正在换取 Token...")

    # 4. 用 code 换取 access_token
    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    token_data = urllib.parse.urlencode({
        "grant_type":   "authorization_code",
        "code":         received_code,
        "redirect_uri": REDIRECT_URI,
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=token_data, method="POST")
    req.add_header("Authorization", f"Basic {credentials}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req) as resp:
            token = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ Token 换取失败：HTTP {e.code}\n{body}")
        return

    # 5. 保存 token 到本地文件
    TOKEN_FILE.write_text(json.dumps(token, indent=2, ensure_ascii=False))
    print(f"\n✅ 授权成功！Token 已保存到：{TOKEN_FILE}")
    print(f"   token_type  : {token.get('token_type', '?')}")
    print(f"   expires_in  : {token.get('expires_in', '?')} 秒")
    print(f"   scope       : {token.get('scope', '?')}")
    print(f"   has refresh : {'refresh_token' in token}")

if __name__ == "__main__":
    main()

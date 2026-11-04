"""Keyboard check in a real Chrome. For one HTML fragment containing a control
with id="t" it reports three things, using only Tab and Enter:
  reached  - Tab lands on the control within MAX_TABS presses
  focus    - HEURISTIC: computed outline/box-shadow present when focused
  focus_pixels_changed - screenshot of the control region differs focused vs blurred (extra evidence, not part of ok)
  enter    - pressing Enter on it produces the case's expected effect
Scope: keyboard operation only. This is NOT a screen-reader test."""
import json, os, subprocess, tempfile, time, urllib.request, shutil
import websocket

MAX_TABS = 12
CHROME = os.environ.get("CHROME", "google-chrome")
PAGE = """<!doctype html><meta charset=utf-8><style>
body{font:16px sans-serif;margin:20px}.btn,.sw,.tab,.x,.acc,.lnk{cursor:pointer;margin:4px}
.btn,.sw,.tab{border:1px solid #888;padding:4px 8px;display:inline-block}</style>
<body>__BODY__</body>"""

class Chrome:
    def __init__(self, port=9333):
        self.dir = tempfile.mkdtemp()
        self.p = subprocess.Popen([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
            f"--remote-debugging-port={port}", f"--user-data-dir={self.dir}", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.port = port
        for _ in range(60):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1); break
            except Exception: time.sleep(0.25)
    def page(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/json/new?about:blank", method="PUT")
        t = json.load(urllib.request.urlopen(req))
        return Page(t["webSocketDebuggerUrl"])
    def close(self):
        self.p.terminate(); shutil.rmtree(self.dir, ignore_errors=True)

class Page:
    def __init__(self, url):
        self.ws = websocket.create_connection(url, timeout=15); self.n = 0
    def call(self, method, **params):
        self.n += 1; self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.n: return m.get("result", {})
    def js(self, expr):
        r = self.call("Runtime.evaluate", expression=expr, returnByValue=True)
        return r.get("result", {}).get("value")
    def key(self, key, code, vk):
        for t in ("keyDown", "keyUp"):
            extra = {"text": "\r"} if (key == "Enter" and t == "keyDown") else {}
            self.call("Input.dispatchKeyEvent", type=t, key=key, code=code,
                      windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk, **extra)
    def close(self): self.ws.close()

FOCUS_JS = """(()=>{const e=document.activeElement;if(!e||e===document.body)return null;
const s=getComputedStyle(e);const ring=(s.outlineStyle!=='none'&&parseFloat(s.outlineWidth)>0)||s.boxShadow!=='none';
return {id:e.id,ring:ring}})()"""

def check(chrome, body_html, done_expr):
    pg = chrome.page()
    try:
        pg.call("Page.enable")
        pg.call("Page.navigate", url="data:text/html;charset=utf-8," + urllib.parse.quote(PAGE.replace("__BODY__", body_html)))
        time.sleep(0.4)
        reached = focus = False
        for _ in range(MAX_TABS):
            pg.key("Tab", "Tab", 9)
            f = pg.js(FOCUS_JS)
            if f and f.get("id") == "t":
                reached = True; focus = bool(f["ring"]); break
        pixels = None
        if reached:
            # decisive-ish check: screenshot around the control focused vs blurred; differing bytes = something visibly changed
            r = pg.js("(()=>{const b=document.getElementById('t').getBoundingClientRect();return [b.x,b.y,b.width,b.height]})()")
            clip = dict(x=max(r[0]-8,0), y=max(r[1]-8,0), width=r[2]+16, height=r[3]+16, scale=1)
            a = pg.call("Page.captureScreenshot", clip=clip).get("data")
            pg.js("document.activeElement.blur()")
            b = pg.call("Page.captureScreenshot", clip=clip).get("data")
            pixels = a != b
            pg.js("document.getElementById('t').focus()")
        enter = False
        if reached:
            pg.key("Enter", "Enter", 13); time.sleep(0.2)
            enter = bool(pg.js(done_expr))
        return dict(reached=reached, focus=focus, focus_pixels_changed=pixels, enter=enter, ok=reached and focus and enter)
    finally:
        pg.close()
import urllib.parse

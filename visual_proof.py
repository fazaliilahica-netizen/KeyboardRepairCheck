"""Render before/after keyboard states for each case: broken page vs Glimmer repair (runs/glimmer_scored.json).
Each cell: after pressing Tab until #t is focused (or up to MAX_TABS), then after Enter. Real headless Chrome."""
import json, time, base64, io, urllib.parse
from checker import Chrome, PAGE, MAX_TABS, FOCUS_JS
from cases import CASES
from PIL import Image, ImageDraw
res = json.load(open("runs/glimmer_scored.json"))["rows"]
def shots(ch, html, done):
    pg = ch.page(); out = []
    try:
        pg.call("Page.enable")
        pg.call("Page.navigate", url="data:text/html;charset=utf-8," + urllib.parse.quote(PAGE.replace("__BODY__", html))); time.sleep(0.4)
        reached = False
        for _ in range(MAX_TABS):
            pg.key("Tab", "Tab", 9); f = pg.js(FOCUS_JS)
            if f and f.get("id") == "t": reached = True; break
        snap = lambda: Image.open(io.BytesIO(base64.b64decode(pg.call("Page.captureScreenshot", clip=dict(x=0,y=0,width=360,height=110,scale=1))["data"])))
        out.append(snap()); 
        if reached: pg.key("Enter", "Enter", 13)
        else: pg.js("document.getElementById('t').focus()"); pg.key("Enter", "Enter", 13)
        time.sleep(0.25); out.append(snap())
        return out, reached, bool(pg.js(done)) if reached else False
    finally: pg.close()
ch = Chrome(port=9444); rows = []
try:
    for c, r in zip(CASES, res):
        b, br, bd = shots(ch, c["broken"], c["done"]); a, ar, ad = shots(ch, r["repair_html"], c["done"])
        rows.append((c["label"], b, br, bd, a, ar, ad))
finally: ch.close()
W, H = 360, 110; pad = 6; lab = 150
img = Image.new("RGB", (lab + 4 * (W + pad), 30 + len(rows) * (H + pad)), "white"); d = ImageDraw.Draw(img)
for i, t in enumerate(["BROKEN: after Tab keys", "BROKEN: after Enter", "GLIMMER REPAIR: after Tab", "GLIMMER REPAIR: after Enter"]):
    d.text((lab + i * (W + pad) + 4, 8), t, fill="black")
for j, (label, b, br, bd, a, ar, ad) in enumerate(rows):
    y = 30 + j * (H + pad); d.text((4, y + 40), label, fill="black")
    d.text((4, y + 58), f"broken reached={br} done={bd}", fill="gray"); d.text((4, y + 72), f"repair reached={ar} done={ad}", fill="gray")
    for i, im in enumerate(b + a): img.paste(im.convert("RGB").crop((0, 0, W, H)), (lab + i * (W + pad), y))
img.save("runs/visual_before_after.png"); print(img.size, [(r[0], r[2], r[3], r[5], r[6]) for r in rows])

"""REPLAY demo: renders the SAVED Muse Glimmer 30B outputs (runs/glimmer_scored.json) next to the broken inputs in real headless Chrome,
sends real Tab/Enter key events, and records frames -> demo/replay.mp4 + demo/replay_after_enter.png.
NOT live model inference. The bottom inspector bar is test instrumentation drawn outside the fragment; it is not model-generated UI.
The fixtures' handlers only set a data- flag (they do not really close a dialog, switch a theme, navigate or save)."""
import json, time, base64, io, os, urllib.parse
from checker import Chrome, PAGE, MAX_TABS
from cases import CASES
from PIL import Image, ImageDraw, ImageFont
rows = json.load(open("runs/glimmer_scored.json"))["rows"]
W, H = 620, 190
F = lambda s, b=False: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if b else ""), s)
FM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
INSP = """(done)=>{let b=document.getElementById('__insp');if(!b){b=document.createElement('div');b.id='__insp';
b.style.cssText='position:fixed;left:0;width:620px;top:136px;box-sizing:border-box;background:#111;color:#9f9;font:12px monospace;padding:4px 8px;white-space:pre';document.body.appendChild(b)}
const a=document.activeElement;const f=(a&&a!==document.body)?a.tagName.toLowerCase()+(a.id?'#'+a.id:''):'(nothing focused)';
let v;try{v=!!eval(done)}catch(e){v='err'}b.textContent='[test instrumentation]\\nfocused: '+f+'\\nhandler-flag '+done+' = '+v}"""
def run(ch, html, done, tab_cap=MAX_TABS):
    pg = ch.page(); fr = []
    try:
        pg.call("Page.enable"); pg.call("Page.navigate", url="data:text/html;charset=utf-8," + urllib.parse.quote(PAGE.replace("__BODY__", html))); time.sleep(0.4)
        snap = lambda cap: (pg.js("(%s)(%s)" % (INSP, json.dumps(done))), fr.append((cap, Image.open(io.BytesIO(base64.b64decode(pg.call("Page.captureScreenshot", clip=dict(x=0, y=0, width=W, height=H, scale=1))["data"]))).convert("RGB"))))
        snap("start")
        n = 0
        for _ in range(tab_cap):
            pg.key("Tab", "Tab", 9); n += 1
            if pg.js("(document.activeElement||{}).id")=="t": break
        snap("after %d Tab press%s" % (n, "" if n == 1 else "es"))
        pg.key("Enter", "Enter", 13); time.sleep(0.25); snap("after Enter")
        return fr
    finally: pg.close()
ch = Chrome(port=9455); frames = []; finals = []
try:
    for i, (c, r) in enumerate(zip(CASES, rows)):
        b = run(ch, c["broken"], c["done"]); a = run(ch, r["repair_html"], c["done"])
        for (cb, ib), (ca, ia) in zip(b, a):
            im = Image.new("RGB", (2 * W + 30, H + 112), "white"); d = ImageDraw.Draw(im)
            d.rectangle([0, 0, im.width, 26], fill="#fde68a"); d.text((8, 5), "REPLAY of saved Muse Glimmer 30B output (runs/glimmer_run.json). NOT live inference. Colab T4, one run, 2026-11-04.", font=F(12, True), fill="black")
            d.text((8, 34), "Case %d/7: %s   |   step: %s" % (i + 1, c["label"], cb if cb == ca else "broken: %s  |  repair: %s" % (cb, ca)), font=F(15, True), fill="black")
            d.text((10, 58), "BROKEN INPUT (checker control)", font=F(12, True), fill="#b91c1c"); d.text((W + 40, 58), "GLIMMER REPAIR (saved model output)", font=F(12, True), fill="#15803d")
            im.paste(ib, (10, 78)); im.paste(ia, (W + 30, 78))
            note = "Fixture handlers only set a data- flag; they do not really close the dialog, switch the theme, navigate or save. Inspector bars are instrumentation, not model output."
            d.text((10, H + 88), note, font=F(10), fill="#444")
            d.text((10, H + 104 - 4), "Scope: Tab + Enter on 7 small hand-built cases; not a screen-reader test. Accordion: h3 became a button (heading semantics lost).", font=F(10), fill="#444")
            frames.append(im)
            if cb == "after Enter": finals.append(im)
finally: ch.close()
os.makedirs("demo", exist_ok=True)
for k, im in enumerate(frames): im.save("demo/f%03d.png" % k)
sheet = Image.new("RGB", (finals[0].width, sum(f.height for f in finals)), "white"); y = 0
for f in finals: sheet.paste(f, (0, y)); y += f.height
sheet.save("demo/replay_after_enter_all.png"); finals[0].save("demo/replay_after_enter_case1.png"); print(len(frames), frames[0].size, sheet.size)

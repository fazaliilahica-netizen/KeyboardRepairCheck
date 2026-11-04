"""Builds demo/keyboard_repair_check_demo.mp4 (captions only, no audio) from saved evidence. REPLAY of saved outputs, not live inference."""
import json, subprocess, os, textwrap
from PIL import Image, ImageDraw, ImageFont
from cases import CASES
W, H = 1280, 720
def F(s, b=False): return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if b else ""), s)
def M(s): return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", s)
BANNER = "REPLAY of saved Muse Glimmer 30B outputs from one real run (2026-11-04). Not live inference."
def base(title=None, caption=None, banner=True):
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    if banner: d.rectangle([0, 0, W, 30], fill="#fde68a"); d.text((12, 6), BANNER, font=F(14, True), fill="black")
    if title: d.text((40, 52), title, font=F(34, True), fill="#111")
    if caption:
        d.rectangle([0, H - 110, W, H], fill="#111")
        y = H - 100
        for ln in textwrap.wrap(caption, 95)[:3]: d.text((40, y), ln, font=F(21), fill="white"); y += 30
    return im, d
def bullets(d, items, y=130, size=26, x=60, wrap=70):
    for t in items:
        ls = textwrap.wrap(t, wrap)
        d.text((x - 24, y), "-", font=F(size, True), fill="#111")
        for ln in ls: d.text((x, y), ln, font=F(size), fill="#111"); y += size + 8
        y += 14
scenes = []  # (image, seconds)
# 1 intro
im, d = base(None, "Keyboard Repair Check. Can an open-weight Meta model fix a web widget so a keyboard user can actually use it? We tested that with Muse Glimmer 30B, using a real browser.")
d.text((60, 190), "Keyboard Repair Check", font=F(64, True), fill="#111")
d.text((60, 290), "Does a model's repair of a broken widget work with Tab and Enter?", font=F(30), fill="#333")
d.text((60, 360), "Model: Muse Glimmer 30B (open weights, Apache 2.0), Q4_K_M, llama.cpp", font=F(24), fill="#555")
d.text((60, 400), "Scope: 7 small hand-built cases, Tab and Enter only", font=F(24), fill="#555")
scenes.append((im, 14))
# 2 problem
im, d = base("The problem", "A div with a click handler works with a mouse. A keyboard user cannot Tab to it, sees no focus ring, and Enter does nothing. AI tools write this kind of markup often. We built a checker for it.")
d.rectangle([60, 130, 1220, 220], fill="#f3f4f6"); d.text((80, 150), CASES[0]["broken"][:100], font=M(18), fill="#111")
d.text((80, 182), "<-- broken input, case 1 of 7 (a div, not a button)", font=F(16), fill="#b91c1c")
bullets(d, ["Tab never lands on it.", "No visible focus.", "Enter has no effect."], y=270)
scenes.append((im, 18))
# 3 how
im, d = base("How the test works", "A broken fragment goes to Muse Glimmer 30B on a free Colab T4 GPU. The model returns a repaired fragment. A real headless Chrome then presses Tab and Enter and records what happens.")
steps = ["Broken HTML\nfragment", "Muse Glimmer 30B\nllama.cpp b10353\nfree Colab T4", "Repaired\nfragment", "Real Chrome\nTab, focus ring,\nEnter"]
for i, s in enumerate(steps):
    x = 50 + i * 300; d.rounded_rectangle([x, 220, x + 260, 400], 12, outline="#111", width=3, fill="#f9fafb")
    for k, ln in enumerate(s.split("\n")): d.text((x + 14, 250 + k * 34), ln, font=F(22, True if k == 0 else False), fill="#111")
    if i < 3: d.text((x + 266, 290), "->", font=F(30, True), fill="#111")
scenes.append((im, 20))
# 4 replay per case
rows = json.load(open("runs/glimmer_scored.json"))["rows"]
capt = {0: "Menu button: the model turned the div into a button. After Tab the repair has focus; Enter sets the handler flag and the menu list appears.",
        1: "Dialog close: span became a button, and the visible text Settings was kept.",
        2: "Dark-mode switch: div became a button. The fixture only sets a data flag, it does not really change the theme.",
        3: "Tab buttons: div became a button; Enter sets the panel text to Details shown.",
        4: "Accordion header: h3 became a button and Enter reveals Ships in 2 days. The heading element is lost. That is a semantic regression.",
        5: "Fake link: span became a button. The fixture only sets a flag, it does not navigate.",
        6: "Save button: the model removed outline none, so the focus ring is visible again."}
for i in range(7):
    for j, sec in zip(range(3), (2.5, 2.5, 3.5)):
        fr = Image.open("demo/frames/f%03d.png" % (i * 3 + j)).convert("RGB")
        im, d = base(None, capt[i] if j == 2 else "Case %d of 7: %s. Left is the broken input, right is the saved Glimmer repair. Test instrumentation bars are not model output." % (i + 1, CASES[i]["label"]), banner=False)
        im.paste(fr.resize((W, int(fr.height * W / fr.width))), (0, 90)); scenes.append((im, sec if i else sec + 0))
# 5 results
im, d = base("Results", "On our checker the broken pages pass 0 of 7 and Glimmer's repairs pass 7 of 7. The small Llama 1B check scored 0 and then 1 of 7. These are small cases and one run each, so this shows the pipeline works, not general ability.")
bullets(d, ["Broken pages: 0/7 pass (control)", "Hand-written fixes: 7/7 (stand-in, no model, checker sanity)", "Llama 3.2 1B (method check only): 0/7 and 1/7 in two runs", "Muse Glimmer 30B, one run: 7/7 pass; text and handlers kept in all 7", "Per case: 185 to 501 s on the free T4"], y=120, size=27, wrap=68)
scenes.append((im, 24))
# 6 limits
im, d = base("Limits", "Limits: only Tab and Enter, only seven small cases, one run. The prompt tells the model which id is broken and asks for native elements. It is not a screen-reader test and not accessibility certification.")
bullets(d, ["Tab and Enter only. Not a screen-reader test.", "7 small hand-built fragments, one run each, no repeats.", "The prompt names the broken id and asks for native elements.", "Accordion h3 became a button: heading semantics lost.", "The checker tests only the element with id t.", "Native buttons change the default look.", "No novelty claim. Raw outputs and hashes are in the repo."], y=120, size=25, wrap=75)
scenes.append((im, 28))
# 7 close
im, d = base("Reproduce it", "Everything is in the repo: cases, checker, the Colab cell, the raw model output and the scored results. Model file hash and llama.cpp commit are recorded. Thank you.")
bullets(d, ["Raw output: runs/glimmer_run.json (md5 a3a23c1b...0410a539)", "Scored: runs/glimmer_scored.json", "Model sha256 4cc57c0f...183f60e, llama.cpp b10353 f8def7fe...", "Run: python run.py --repairs runs/glimmer_run.json"], y=130, size=26, wrap=72)
scenes.append((im, 14))
os.makedirs("demo/video", exist_ok=True); lst = []
for k, (im, sec) in enumerate(scenes):
    p = "demo/video/s%03d.png" % k; im.save(p); lst += ["file '%s'" % os.path.abspath(p), "duration %s" % sec]
lst.append("file '%s'" % os.path.abspath("demo/video/s%03d.png" % (len(scenes) - 1)))
open("demo/video/list.txt", "w").write("\n".join(lst)); print(len(scenes), sum(s for _, s in scenes))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "demo/video/list.txt", "-vf", "fps=10,format=yuv420p", "-movflags", "+faststart", "demo/keyboard_repair_check_demo.mp4"], check=True)

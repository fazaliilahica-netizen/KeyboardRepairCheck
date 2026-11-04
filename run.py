"""Run all cases: check the broken page, get a repair, check the repair.
  python run.py --stand-in            hand-written fixes (NO model; labelled in output)
  python run.py --model NAME          repairs from an OpenAI-compatible endpoint
                                      (set MODEL_BASE_URL, optional MODEL_API_KEY)"""
import argparse, json, os, re, sys, time, urllib.request
from cases import CASES
from checker import Chrome, check

from cases import SYSTEM
RAW = []

def ask_model(base, model, html, key=None):
    body = json.dumps({"model": model, "temperature": 0.2, "max_tokens": 1500,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": html}]}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", body,
        {"Content-Type": "application/json", **({"Authorization": "Bearer " + key} if key else {})})
    out = json.load(urllib.request.urlopen(req, timeout=300))
    txt = out["choices"][0]["message"]["content"]
    RAW.append(dict(request=json.loads(body), raw_response=txt, finish=out["choices"][0].get("finish_reason")))
    txt = re.sub(r"<think>.*?</think>", "", txt, flags=re.S).strip()
    m = re.search(r"```(?:html)?\s*(.*?)```", txt, re.S)
    return (m.group(1) if m else txt).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stand-in", action="store_true"); ap.add_argument("--model")
    ap.add_argument("--repairs", help="JSON {case_id: html} produced by a real model run elsewhere")
    ap.add_argument("--out", default="runs/latest.json")
    a = ap.parse_args()
    if not a.stand_in and not a.model and not a.repairs: sys.exit("choose --stand-in or --model NAME")
    base = os.environ.get("MODEL_BASE_URL"); key = os.environ.get("MODEL_API_KEY")
    if a.model and not base: sys.exit("set MODEL_BASE_URL")
    rep = None
    if a.repairs:
        raw = json.load(open(a.repairs))
        if "results" in raw:  # colab_cell.py output: keep raw, strip think tags / fences the same way as ask_model
            def clean(t):
                t = re.sub(r"<think>.*?</think>", "", t or "", flags=re.S).strip()
                m = re.search(r"```(?:html)?\s*(.*?)```", t, re.S); return (m.group(1) if m else t).strip()
            rep = {r["id"]: clean(r["response"]["choices"][0]["message"].get("content")) for r in raw["results"]}
        else: rep = raw
    src = f"repairs file {a.repairs} (model output generated outside this script)" if rep else "stand-in (hand-written, NO model)" if a.stand_in else f"model: {a.model}"
    ch = Chrome(); rows = []
    try:
        for c in CASES:
            if rep is not None and c["id"] not in rep: continue
            before = check(ch, c["broken"], c["done"])
            repair = rep[c["id"]] if rep else c["fixed"] if a.stand_in else ask_model(base, a.model, c["broken"], key)
            after = check(ch, repair, c["done"])
            rows.append(dict(id=c["id"], raw=(RAW[-1] if (a.model and not a.repairs) else None), label=c["label"], before=before, repair_html=repair, after=after))
            print(f'{c["label"]:34s} before={"OK" if before["ok"] else "FAIL":4s} after={"OK" if after["ok"] else "FAIL"}  {after}')
    finally:
        ch.close()
    n = len(rows); res = dict(source=src, time=time.strftime("%Y-%m-%d %H:%M:%S"),
        before_ok=sum(r["before"]["ok"] for r in rows), after_ok=sum(r["after"]["ok"] for r in rows), total=n, rows=rows)
    os.makedirs(os.path.dirname(a.out), exist_ok=True); json.dump(res, open(a.out, "w"), indent=1)
    print(f'\nSource: {src}\nBroken pages passing: {res["before_ok"]}/{n}. Repaired pages passing: {res["after_ok"]}/{n}.')
if __name__ == "__main__":
    main()

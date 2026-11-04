# Muse Glimmer 30B repair run. Colab free T4 (1 GPU, partial CPU offload), Internet on. Fails visibly; bounded; saves raw evidence.
import subprocess, os, time, json, urllib.request, hashlib, sys
LLAMA_TAG="b10353"   # first llama.cpp build the Glimmer card says supports the model
NGL="36"; CTX=8192; MAX_TOKENS=3000; SMOKE_FIRST=True
W="/content"; t0=time.time()
def sh(c, check=True):
    r=subprocess.run(["bash","-o","pipefail","-c",c],text=True,capture_output=True)
    if check and r.returncode!=0: print("FAILED:",c[:200]); print(r.stdout[-1500:]); print(r.stderr[-1500:]); raise SystemExit(1)
    return r
print(sh("nvidia-smi --query-gpu=name,memory.total --format=csv").stdout)
if not os.path.exists(W+"/llama.cpp/build/bin/llama-server"):
    sh(f"cd {W} && git clone -q https://github.com/ggml-org/llama.cpp && cd llama.cpp && git checkout -q {LLAMA_TAG}")
    sh(f"cd {W}/llama.cpp && cmake -B build -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=75 -DLLAMA_CURL=OFF >/dev/null")
    sh(f"cd {W}/llama.cpp && cmake --build build --config Release -j4 --target llama-server >build.log 2>&1 || (tail -20 build.log; exit 1)")
commit=sh(f"cd {W}/llama.cpp && git rev-parse HEAD").stdout.strip(); print("llama.cpp",LLAMA_TAG,commit,"build s",round(time.time()-t0))
assert sh(f"grep -ci glimmer {W}/llama.cpp/src/llama-arch.cpp",check=False).stdout.strip() not in ("","0"), "this llama.cpp build has no Glimmer support"
sh("pip -q install huggingface_hub")
from huggingface_hub import hf_hub_download
p=hf_hub_download("meta-models/Muse-Glimmer-30B-GGUF","Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf",local_dir=W+"/w")
h=hashlib.sha256()
with open(p,"rb") as f:
    for b in iter(lambda:f.read(1<<24),b""): h.update(b)
sha=h.hexdigest(); print("model sha256",sha,os.path.getsize(p),"s",round(time.time()-t0))
args=[W+"/llama.cpp/build/bin/llama-server","-m",p,"-a","muse-glimmer-30B","-ngl",NGL,"-c",str(CTX),"-np","1","--host","127.0.0.1","--port","8091","--jinja","--temp","1.0","--top-p","0.95","--top-k","64","--chat-template-kwargs",'{"reasoning_strength":"low"}']
ts=time.time()
srv=subprocess.Popen(args,stdout=open(W+"/server.log","w"),stderr=subprocess.STDOUT)
SYSTEM='You repair web accessibility problems. You get one HTML fragment. The control with id="t" works with a mouse but not with the keyboard. Return ONLY the corrected HTML fragment, keeping id="t" and the same visible behaviour. Use native elements (button, a) where suitable. No explanation, no code fences.'
CASES=[{"id": "menu", "broken": "<div id=\"t\" class=\"btn\" onclick=\"document.getElementById('m').hidden=false;this.dataset.on=1\">Menu</div><ul id=\"m\" hidden><li>Home</li><li>Help</li></ul>"}, {"id": "close", "broken": "<div id=\"dlg\">Settings <span id=\"t\" class=\"x\" onclick=\"document.getElementById('dlg').dataset.closed=1\">&times;</span></div>"}, {"id": "switch", "broken": "<div id=\"t\" class=\"sw\" onclick=\"this.dataset.on=this.dataset.on==='1'?'0':'1'\">Dark mode</div>"}, {"id": "tabs", "broken": "<div id=\"t\" class=\"tab\" onclick=\"document.getElementById('p').textContent='Details shown'\">Details</div><div id=\"p\">None</div>"}, {"id": "accordion", "broken": "<h3 id=\"t\" class=\"acc\" onclick=\"document.getElementById('b').hidden=false\">Shipping info</h3><div id=\"b\" hidden>Ships in 2 days</div>"}, {"id": "link", "broken": "<span id=\"t\" class=\"lnk\" onclick=\"document.body.dataset.went=1\">Read more</span>"}, {"id": "focusring", "broken": "<button id=\"t\" class=\"btn\" style=\"outline:none\" onclick=\"this.dataset.on=1\">Save</button>"}]
def one(c):
    b=dict(model="muse-glimmer-30B",max_tokens=MAX_TOKENS,messages=[{"role":"system","content":SYSTEM},{"role":"user","content":c["broken"]}])
    r=urllib.request.Request("http://127.0.0.1:8091/v1/chat/completions",json.dumps(b).encode(),{"Content-Type":"application/json"})
    t=time.time(); o=json.load(urllib.request.urlopen(r,timeout=600))
    return dict(id=c["id"],request=b,response=o,seconds=round(time.time()-t,1))
try:
    while True:
        try: urllib.request.urlopen("http://127.0.0.1:8091/health",timeout=2); break
        except Exception:
            if srv.poll() is not None: print(open(W+"/server.log").read()[-3000:]); sys.exit(1)
            if time.time()-ts>1800: print("start timeout"); sys.exit(1)
            time.sleep(3)
    print("server up s",round(time.time()-t0)); print(sh("nvidia-smi --query-gpu=memory.used --format=csv").stdout)
    meta=dict(llama_tag=LLAMA_TAG,llama_commit=commit,model_sha256=sha,args=args[1:],ctx=CTX,max_tokens=MAX_TOKENS,server_log_tail=open(W+"/server.log").read()[-2000:])
    res=[]
    for i,c in enumerate(CASES):
        if time.time()-ts>3*3600: print("time budget hit"); break
        res.append(one(c)); m=res[-1]["response"]["choices"][0]
        print(c["id"],m.get("finish_reason"),res[-1]["seconds"],"s", repr((m["message"].get("content") or "")[:120]))
        json.dump(dict(meta=meta,results=res),open(W+"/glimmer_run.json","w"))
        if SMOKE_FIRST and i==0 and not (m["message"].get("content") or "").strip(): print("smoke case returned empty content; stopping"); break
    print("RUN_JSON_BEGIN"); print(json.dumps(dict(meta=meta,results=res))); print("RUN_JSON_END",round(time.time()-t0))
finally:
    srv.terminate()
    try: srv.wait(30)
    except Exception: srv.kill()

# Keyboard Repair Check

Checks whether an AI-written repair of a broken web widget works with the keyboard. A real headless Chrome tests each page: does Tab reach the control, is a focus ring visible, does Enter trigger the behaviour.

Scope: 7 small hand-built cases, Tab and Enter only. This is not a screen-reader test and not accessibility certification. No novelty claim.

## Results (all from the files in runs/)
| Run | Pages passing |
|---|---|
| Broken pages (control) | 0/7 |
| Hand-written fixes (stand-in, no model, checks the checker) | 7/7 |
| Llama 3.2 1B Instruct Q4_K_M, CPU (method check, two runs; run 1 raw output not saved) | 0/7, then 1/7 (the 1/7 dropped the visible text "Settings") |
| Muse Glimmer 30B Q4_K_M, one run on 2026-11-04 | 7/7 |

Glimmer run details: model file Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf from meta-models/Muse-Glimmer-30B-GGUF, sha256 4cc57c0f51040a226e5a72cc47b7613f7772950e460a665f7083de89f183f60e; llama.cpp tag b10353 (commit f8def7fe168bab245fbf15d3f18b26dbb1ef73c8) built with CUDA on a free Google Colab T4; 36 layers on GPU, context 8192, temperature 1.0, top_p 0.95, top_k 64, reasoning_strength low; 185 to 501 s per case. Raw requests and responses: `runs/glimmer_run.json`. Scored: `runs/glimmer_scored.json`. Input-versus-output text for every case: `runs/fidelity_diff.md`.

What the Glimmer repairs did: all 7 kept the visible text and the original handlers and changed the tag (div, span or h3 to button) or removed `outline:none`. The accordion `h3` became a `button`, so the heading element is lost (a semantic regression the checker does not score). Native buttons also change the default look.

Caveats: the prompt tells the model which id is broken and asks for native elements; the cases are small; one run per case, no repeats; the checker tests only the element with id `t`; the fixtures' handlers only set a `data-` flag (they do not really close a dialog, change a theme, navigate or save). This shows the pipeline works, not general repair ability.

## Run it
1. Controls only (needs Chrome and `pip install websocket-client`): `python run.py --stand-in`
2. Score saved model output: `python run.py --repairs runs/glimmer_run.json`
3. Produce your own model output: run `colab_cell.py` in a notebook with a GPU (builds llama.cpp b10353 with CUDA, downloads the GGUF, serves it locally, sends the 7 fragments, saves raw requests and responses).
4. `replay_demo.py` and `build_video.py` render the replay frames and the demo video from the saved outputs. The video is a replay of saved outputs, not live inference.

Metrics are kept separate and were fixed before the Glimmer run: (1) designated-target check, implemented: the element with id `t` must be reached by real Tab key events, show a focus ring, and respond to a real Enter key event; (2) descendant or general keyboard-path coverage (some other element the keyboard could use to trigger the effect), NOT implemented, so a repair that moves the behaviour to another element can fail metric 1 although it works; (3) content fidelity, checked by hand (`runs/fidelity_diff.md`).

## Licenses
Code: MIT (see LICENSE). Muse Glimmer weights are not included: Apache 2.0 with Meta's usage policy (copies in runs/g_LICENSE and runs/g_USAGE_POLICY.md). Llama 3.2 method check: Llama 3.2 Community License; weights not included.

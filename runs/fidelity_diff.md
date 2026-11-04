# Input vs Glimmer output (unedited model content, think tags and fences stripped by run.py exactly as in the scored run)

## Menu button
Input:
```html
<div id="t" class="btn" onclick="document.getElementById('m').hidden=false;this.dataset.on=1">Menu</div><ul id="m" hidden><li>Home</li><li>Help</li></ul>
```
Glimmer output:
```html
<button id="t" class="btn" onclick="document.getElementById('m').hidden=false;this.dataset.on=1">Menu</button><ul id="m" hidden><li>Home</li><li>Help</li></ul>
```
Checker: {'reached': True, 'focus': True, 'focus_pixels_changed': True, 'enter': True, 'ok': True}

## Dialog close
Input:
```html
<div id="dlg">Settings <span id="t" class="x" onclick="document.getElementById('dlg').dataset.closed=1">&times;</span></div>
```
Glimmer output:
```html
<div id="dlg">Settings <button id="t" class="x" onclick="document.getElementById('dlg').dataset.closed=1">&times;</button></div>
```
Checker: {'reached': True, 'focus': True, 'focus_pixels_changed': True, 'enter': True, 'ok': True}

## Dark-mode switch
Input:
```html
<div id="t" class="sw" onclick="this.dataset.on=this.dataset.on==='1'?'0':'1'">Dark mode</div>
```
Glimmer output:
```html
<button id="t" class="sw" onclick="this.dataset.on=this.dataset.on==='1'?'0':'1'">Dark mode</button>
```
Checker: {'reached': True, 'focus': True, 'focus_pixels_changed': True, 'enter': True, 'ok': True}

## Tab buttons
Input:
```html
<div id="t" class="tab" onclick="document.getElementById('p').textContent='Details shown'">Details</div><div id="p">None</div>
```
Glimmer output:
```html
<button id="t" class="tab" onclick="document.getElementById('p').textContent='Details shown'">Details</button><div id="p">None</div>
```
Checker: {'reached': True, 'focus': True, 'focus_pixels_changed': True, 'enter': True, 'ok': True}

## Accordion header
Input:
```html
<h3 id="t" class="acc" onclick="document.getElementById('b').hidden=false">Shipping info</h3><div id="b" hidden>Ships in 2 days</div>
```
Glimmer output:
```html
<button id="t" class="acc" onclick="document.getElementById('b').hidden=false">Shipping info</button><div id="b" hidden>Ships in 2 days</div>
```
Checker: {'reached': True, 'focus': True, 'focus_pixels_changed': True, 'enter': True, 'ok': True}

## Fake link
Input:
```html
<span id="t" class="lnk" onclick="document.body.dataset.went=1">Read more</span>
```
Glimmer output:
```html
<button id="t" class="lnk" onclick="document.body.dataset.went=1">Read more</button>
```
Checker: {'reached': True, 'focus': True, 'focus_pixels_changed': True, 'enter': True, 'ok': True}

## Button with focus ring removed
Input:
```html
<button id="t" class="btn" style="outline:none" onclick="this.dataset.on=1">Save</button>
```
Glimmer output:
```html
<button id="t" class="btn" onclick="this.dataset.on=1">Save</button>
```
Checker: {'reached': True, 'focus': True, 'focus_pixels_changed': True, 'enter': True, 'ok': True}

Notes: all 7 keep visible text and handlers. Tag changes only: div/span/h3 -> button. Accordion h3 -> button loses the heading element (semantic regression, not scored). Native buttons also change default visual styling (see runs/visual_before_after.png). Focus-ring case: only style="outline:none" removed.

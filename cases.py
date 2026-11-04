"""Seven small web widgets that a mouse can use but the keyboard cannot.
Each case has: id, broken HTML, hand-written fixed HTML (stand-in used only
when no model is connected), and a JS expression `done` that is true after
the control has been operated with Enter.
All cases are written by us for this project."""

CASES = [
 dict(id="menu", label="Menu button",
  broken='<div id="t" class="btn" onclick="document.getElementById(\'m\').hidden=false;this.dataset.on=1">Menu</div><ul id="m" hidden><li>Home</li><li>Help</li></ul>',
  fixed='<button id="t" class="btn" onclick="document.getElementById(\'m\').hidden=false;this.dataset.on=1">Menu</button><ul id="m" hidden><li>Home</li><li>Help</li></ul>',
  done="document.getElementById('t').dataset.on==='1'"),
 dict(id="close", label="Dialog close",
  broken='<div id="dlg">Settings <span id="t" class="x" onclick="document.getElementById(\'dlg\').dataset.closed=1">&times;</span></div>',
  fixed='<div id="dlg">Settings <button id="t" class="x" aria-label="Close" onclick="document.getElementById(\'dlg\').dataset.closed=1">&times;</button></div>',
  done="document.getElementById('dlg').dataset.closed==='1'"),
 dict(id="switch", label="Dark-mode switch",
  broken='<div id="t" class="sw" onclick="this.dataset.on=this.dataset.on===\'1\'?\'0\':\'1\'">Dark mode</div>',
  fixed='<button id="t" role="switch" aria-checked="false" class="sw" onclick="this.dataset.on=this.dataset.on===\'1\'?\'0\':\'1\';this.setAttribute(\'aria-checked\',this.dataset.on===\'1\')">Dark mode</button>',
  done="document.getElementById('t').dataset.on==='1'"),
 dict(id="tabs", label="Tab buttons",
  broken='<div id="t" class="tab" onclick="document.getElementById(\'p\').textContent=\'Details shown\'">Details</div><div id="p">None</div>',
  fixed='<button id="t" role="tab" class="tab" onclick="document.getElementById(\'p\').textContent=\'Details shown\'">Details</button><div id="p">None</div>',
  done="document.getElementById('p').textContent==='Details shown'"),
 dict(id="accordion", label="Accordion header",
  broken='<h3 id="t" class="acc" onclick="document.getElementById(\'b\').hidden=false">Shipping info</h3><div id="b" hidden>Ships in 2 days</div>',
  fixed='<h3><button id="t" class="acc" aria-expanded="false" onclick="document.getElementById(\'b\').hidden=false;this.setAttribute(\'aria-expanded\',\'true\')">Shipping info</button></h3><div id="b" hidden>Ships in 2 days</div>',
  done="!document.getElementById('b').hidden"),
 dict(id="link", label="Fake link",
  broken='<span id="t" class="lnk" onclick="document.body.dataset.went=1">Read more</span>',
  fixed='<a id="t" class="lnk" href="#more" onclick="document.body.dataset.went=1">Read more</a>',
  done="document.body.dataset.went==='1'"),
 dict(id="focusring", label="Button with focus ring removed",
  broken='<button id="t" class="btn" style="outline:none" onclick="this.dataset.on=1">Save</button>',
  fixed='<button id="t" class="btn" onclick="this.dataset.on=1">Save</button>',
  done="document.getElementById('t').dataset.on==='1'"),
]

SYSTEM = ("You repair web accessibility problems. You get one HTML fragment. The control with "
 "id=\"t\" works with a mouse but not with the keyboard. Return ONLY the corrected HTML fragment, "
 "keeping id=\"t\" and the same visible behaviour. Use native elements (button, a) where suitable. "
 "No explanation, no code fences.")


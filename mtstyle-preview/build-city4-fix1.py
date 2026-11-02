# city4 fix 1: framing (less sky), sign re-seat after reframe, guild ceiling
# (CSS timber ceiling instead of the watercolor roof crop), portal swirl
# visibility, fireplace, 320px overflow guard. Operates on the built file.
import re, sys

P = '/home/hatch/workspace/gulu-mtstyle-preview/index.html'
h = open(P, encoding='utf-8').read()
assert "APP_VERSION='2026.11.02-city4'" in h, 'version guard'
orig_len = len(h)

# 1. Shift the visible window down: less sky, buildings larger in frame.
old_bg = '.city-bg{transform:scale(1.32);transform-origin:50% 58%}'
assert h.count(old_bg) == 1
h = h.replace(old_bg, '.city-bg{transform:scale(1.32);transform-origin:50% 80%}')

# 2. Eave div: drop the watercolor roof image (it read as outdoors).
old_eave = '<div class="gh4-eave" style="background-image:url(\'+ART.hallEave+\')"></div>'
assert h.count(old_eave) == 1, h.count(old_eave)
h = h.replace(old_eave, '<div class="gh4-eave"></div>')

# 3. Remove the now-unused hallEave texture assignment (~40KB base64).
h2, n = re.subn(r"ART\.hallEave='[^']*';", '', h)
assert n == 1, n
h = h2
assert 'hallEave' not in h

# 4. Override block, appended last so it wins the cascade.
css = """
/* ==== city4 fix1: reframed signs, timber ceiling, portal glow ==== */
html,body{overflow-x:hidden}
.hs-guild{top:45%}.hs-tavern{top:42%}.hs-smith{top:42%}.hs-board{top:56%}
.chest{bottom:76px}
.gh4-eave{height:58px;background:repeating-linear-gradient(90deg,transparent 0 44px,rgba(0,0,0,.35) 44px 46px),linear-gradient(180deg,#503117 0%,#64401f 45%,#452a12 100%);border-bottom:5px solid #2c1a0c;box-shadow:0 4px 8px rgba(0,0,0,.35);-webkit-mask-image:none;mask-image:none}
.gh4-swirl{top:2px;width:100px;height:100px;opacity:.9}
.gh4-portal img{width:78px;height:78px;bottom:10px}
.gh4-fire{width:64px;height:84px;border-top:5px solid #6b4a26}
.gh4-flame{width:24px;height:32px}
@media (max-height:640px){
.hs-guild{top:41%}.hs-tavern{top:39%}.hs-smith{top:39%}.hs-board{top:50%}
.dock{top:58%}.party{bottom:128px}.cta{width:158px}.gh4-rug{bottom:2px;width:140px}
}
@media (max-width:360px){
.logo{font-size:15px}.logo svg{width:26px;height:26px}.top-acts{gap:4px}.toprow{gap:6px}
}
"""
anchor = '</style>\n</head>'
assert h.count(anchor) == 1
h = h.replace(anchor, css + anchor)

open(P, 'w', encoding='utf-8').write(h)
print('fix1 written, bytes:', orig_len, '->', len(h))

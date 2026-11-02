#!/usr/bin/env python3
"""city4 scene patch: ART textures + Taidun layers, gh4 guild interior,
vGuild rewrite, home reframe (initial values, tuned after screenshots),
Taidun layered idle in party row, version bump to city4."""
import sys, base64, os, re

D = '/home/hatch/workspace/gulu-mtstyle-preview/'
P = D + 'index.html'
html = open(P, encoding='utf-8').read()

def must(cond, msg):
    if not cond:
        print('ASSERT FAIL:', msg); sys.exit(1)

must("APP_VERSION='2026.11.02-city3'" in html, 'not city3')
must('function commit(' in html and 'function savePanelHtml(' in html, 'core patch missing')
must('function savePanelHtml' in html, 'core patch missing')

def b64(path):
    return base64.b64encode(open(path, 'rb').read()).decode()

# ---- 1. ART additions (after the ART literal line) ----
i = html.find('const ART=')
must(i >= 0, 'ART not found')
j = html.find('\n', i)
must(j > 0, 'ART line end not found')
art_line = html[i:j]
must(art_line.rstrip().endswith('};') and art_line.startswith('const ART={'), 'ART literal shape unexpected')
taidun = {k: b64(D + 'taidun-layers/' + k + '.webp') for k in
          ['body', 'leg-front', 'head', 'shield', 'arm-hammer']}
add = ("ART.hallEave='data:image/jpeg;base64," + b64(D + 'hall-eave.jpg') + "';"
       "ART.hallFloor='data:image/jpeg;base64," + b64(D + 'hall-floor.jpg') + "';"
       "ART.taidun={body:'data:image/webp;base64," + taidun['body'] + "',"
       "leg:'data:image/webp;base64," + taidun['leg-front'] + "',"
       "head:'data:image/webp;base64," + taidun['head'] + "',"
       "shield:'data:image/webp;base64," + taidun['shield'] + "',"
       "arm:'data:image/webp;base64," + taidun['arm-hammer'] + "'};")
html = html[:j + 1] + add + '\n' + html[j + 1:]

# ---- 2. version bump ----
must(html.count("APP_VERSION='2026.11.02-city3'") == 1, 'version anchor')
html = html.replace("APP_VERSION='2026.11.02-city3'", "APP_VERSION='2026.11.02-city4'", 1)
must('主城 v3 · 公会大厅' in html, 'version label')
html = html.replace('主城 v3 · 公会大厅', '主城 v4 · 公会大厅')

# ---- 3. gh3 CSS -> gh4 CSS (scene+detail only; home v3 rules after the marker stay) ----
a = html.find('/* ==== 公会大厅 v3')
b = html.find('/* ==== 主城 v3')
must(a >= 0 and b > a, 'gh3 css span not found')
gh4css = open(D + 'gh4-scene.css', encoding='utf-8').read()
html = html[:a] + gh4css + html[b:]

# ---- 3b. trailing gh3 media block (sits after the home v3 rules) ----
core_anchor = '/* ===== 主城 v4 core'
ci = html.find(core_anchor)
must(ci > 0, 'core css anchor')
mi = html.rfind('@media (max-width:360px){', 0, ci)
must(mi > 0, 'trailing gh3 media block not found')
seg = html[mi:ci]
must('gh3-' in seg, 'trailing media block has no gh3 rules')
d = 0; k = html.find('{', mi)
while True:
    c = html[k]
    if c == '{': d += 1
    elif c == '}':
        d -= 1
        if d == 0: break
    k += 1
html = html[:mi] + html[k + 1:]

# ---- 4. vGuild rewrite ----
def fn_span(src, name):
    i = src.find('function ' + name + '(')
    must(i >= 0, 'function %s not found' % name)
    j = src.find('{', i); d = 0; k = j
    while True:
        c = src[k]
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: break
        k += 1
    return i, k + 1
i, k = fn_span(html, 'vGuild')
old_vg = html[i:k]
must('gh3-scene' in old_vg and 'guildTab' in old_vg, 'vGuild shape unexpected')
new_vg = open(D + 'vguild-fragment.js', encoding='utf-8').read().strip()
html = html[:i] + new_vg + html[k:]
must(html.count('gh3-') == 0, 'gh3 references remain: %d' % html.count('gh3-'))

# ---- 5. home reframe (initial candidate values) ----
edits = [
    ('.city-bg{transform:scale(1.26);transform-origin:50% 52%}',
     '.city-bg{transform:scale(1.32);transform-origin:50% 58%}'),
    ('.hs-guild{left:calc(50% - 50px);top:50%}', '.hs-guild{left:calc(50% - 50px);top:52%}'),
    ('.hs-tavern{left:3%;top:47%}', '.hs-tavern{left:3%;top:49%}'),
    ('.hs-smith{right:2%;top:46%}', '.hs-smith{right:2%;top:49%}'),
    ('.hs-board{left:2%;top:60%}', '.hs-board{left:2%;top:63%}'),
    (' .hs-guild{top:47%}\n .hs-tavern{top:44%}\n .hs-smith{top:44%}\n .hs-board{top:54%}',
     ' .hs-guild{top:49%}\n .hs-tavern{top:46%}\n .hs-smith{top:46%}\n .hs-board{top:57%}'),
]
for old, new in edits:
    must(html.count(old) == 1, 'reframe anchor not unique: ' + old[:50])
    html = html.replace(old, new, 1)

# ---- 6. party row: Taidun layered idle ----
# File uses plain single quotes for JS string delimiters (no backslashes).
q = "'"
m = re.search(r"S\.formation\.map\(function\(id,i\)\{return .*?\}\)\.join\(\\?'\\?'\)", html)
must(m is not None, 'party map anchor')
new_map = ("S.formation.map(function(id,i){const cls=i<2?" + q + "f" + q + ":" + q + "b" + q
    + ";if(id===" + q + "taidun" + q + ")return " + q + '<div class="tidle ' + q + "+cls+" + q
    + '"><span class="tshadow"></span><img class="tl tbody" src="' + q + "+ART.taidun.body+" + q
    + '" alt=""><img class="tl tleg" src="' + q + "+ART.taidun.leg+" + q
    + '" alt=""><img class="tl thead" src="' + q + "+ART.taidun.head+" + q
    + '" alt=""><span class="tlid l1"></span><span class="tlid l2"></span><img class="tl tshield" src="' + q + "+ART.taidun.shield+" + q
    + '" alt=""><img class="tl tarm" src="' + q + "+ART.taidun.arm+" + q
    + '" alt=""></div>' + q + ";return " + q + '<img class="' + q + "+cls+" + q
    + '" src="' + q + "+ART.heroFull[id]+" + q + '" alt="">' + q + ";}).join(" + q + q + ")")
html = html[:m.start()] + new_map + html[m.end():]

# ---- 7. layered-idle CSS (appended last, wins ties) ----
css = """
/* ===== 主城 v4：苔盾分层待机（原图像素 5 层；呼吸/眨眼/头部/盾锤轻摆；脚底落地 + 阴影） ===== */
.party>img{animation:none!important}
.tidle{position:relative;flex:0 0 auto}
.tidle.f{width:80px;height:80px}
.tidle.b{width:68px;height:68px}
.party .tidle .tl{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;margin:0;filter:none;will-change:transform}
.party .tidle .tbody{transform-origin:50% 82%;animation:tidBreath 3.8s ease-in-out infinite}
.party .tidle .thead{transform-origin:36% 48%;animation:tidHead 3.8s ease-in-out infinite}
.party .tidle .tshield{transform-origin:57% 60.5%;animation:tidShield 3.8s ease-in-out infinite}
.party .tidle .tarm{transform-origin:31.5% 51%;animation:tidArm 3.8s ease-in-out infinite}
@keyframes tidBreath{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.018)}}
@keyframes tidHead{0%,100%{transform:rotate(0deg) translateY(0)}50%{transform:rotate(1.1deg) translateY(1px)}}
@keyframes tidShield{0%,100%{transform:rotate(0deg)}50%{transform:rotate(-1.4deg)}}
@keyframes tidArm{0%,100%{transform:rotate(0deg)}50%{transform:rotate(1deg) translateY(1px)}}
.tshadow{position:absolute;left:50%;bottom:1px;width:64%;height:8px;margin-left:-32%;background:radial-gradient(ellipse at center,rgba(30,20,10,.38),rgba(30,20,10,0) 70%);border-radius:50%;animation:tidShadow 3.8s ease-in-out infinite}
@keyframes tidShadow{0%,100%{transform:scaleX(1);opacity:.9}50%{transform:scaleX(1.05);opacity:.75}}
.tlid{position:absolute;background:#c6c474;border-radius:50% 50% 46% 46%;box-shadow:inset 0 -1px 0 rgba(88,108,48,.6);transform:scaleY(.08);transform-origin:50% 0;animation:tidBlink 4.8s infinite;z-index:3}
.tlid.l1{left:33.8%;top:25.8%;width:5.6%;height:7.4%}
.tlid.l2{left:52.2%;top:25.8%;width:5.6%;height:7.4%}
@keyframes tidBlink{0%,91%,100%{transform:scaleY(.08)}93.5%{transform:scaleY(1)}96%{transform:scaleY(.08)}}
@media (max-height:640px){.tidle.f{width:64px;height:64px}.tidle.b{width:54px;height:54px}}
@media (max-width:360px){.party .tidle.b{display:none}}
"""
anchor2 = '</style>\n</head>'
must(html.count(anchor2) == 1, 'css anchor')
html = html.replace(anchor2, css + anchor2, 1)

open(P, 'w', encoding='utf-8').write(html)
print('scene patch written, bytes:', len(html))

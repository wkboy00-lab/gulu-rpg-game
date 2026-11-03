#!/usr/bin/env python3
"""city5: guild hall v5 — painted interior scene + scene-fitted hotspots + parchment detail panels.
Input must be city4 (APP_VERSION 2026.11.02-city4). Gameplay, values and saves untouched."""
import base64, hashlib, re, shutil, sys

D = '/home/hatch/workspace/gulu-mtstyle-preview/'
src = D + 'index.html'
s = open(src, encoding='utf-8').read()
md5_before = hashlib.md5(open(src, 'rb').read()).hexdigest()
assert md5_before == '20d7104db38aa5d9a573964df16ebbe4', md5_before
shutil.copyfile(src, D + 'index-city4-backup.html')

assert "const APP_VERSION='2026.11.02-city4';" in s

# 1. Replace the whole gh4 CSS region (v4 comment .. start of v3 comment) with gh5 CSS.
css = open(D + 'gh5-scene.css', encoding='utf-8').read().rstrip('\n') + '\n'
i = s.index('/* ==== 公会大厅 v4')
j = s.index('\n/* ==== 主城 v3')
s = s[:i] + css + s[j:]

# 2. Replace vGuild function with the v5 fragment.
frag = open(D + 'vguild5-fragment.js', encoding='utf-8').read()
assert frag.startswith('function vGuild(){') and frag.rstrip().endswith("';}")
a = s.index('function vGuild(){')
b = s.index('function guildShop(')
assert 'function guildShop(' in s[a:b + 20] or True
s = s[:a] + frag + s[b:]
# fragment file may end with newline; strip it so guildShop follows cleanly
s = s.replace(frag + '\nfunction guildShop(', frag.rstrip('\n') + 'function guildShop(')

# 3. Swap ART.hallFloor assignment for ART.guildHall (same position, right after ART literal).
img_b64 = base64.b64encode(open(D + 'guild-art/guild-hall-v5-final.jpg', 'rb').read()).decode()
pat = re.compile(r"ART\.hallFloor='[^']*';\n?")
s, n = pat.subn("ART.guildHall='data:image/jpeg;base64," + img_b64 + "';\n", s)
assert n == 1, n

# 4. Version bump + settings label.
s = s.replace("const APP_VERSION='2026.11.02-city4';",
              "const APP_VERSION='2026.11.03-city5';", 1)
assert "APP_VERSION='2026.11.03-city5'" in s
s = s.replace('（主城 v4 · 公会大厅）', '（主城 v4 · 公会大厅 v5）', 1)

# 5. Drop dead .gh4- rules left in the city4 fix1 block.
s, n = re.subn(r'\.gh4-rug\{bottom:2px;width:140px\}', '', s)
assert n == 1, n
lines = s.split('\n')
dead = [ln for ln in lines if ln.strip().startswith('.gh4-')]
print('dead gh4 lines:', len(dead))
for ln in dead:
    print('  ', ln[:100])
assert len(dead) == 5, dead
s = '\n'.join(ln for ln in lines if not ln.strip().startswith('.gh4-'))

# 6. Final assertions: no gh4/hallFloor left; guild logic + saves intact.
assert 'gh4-' not in s, 'gh4 refs remain'
assert 'hallFloor' not in s
assert 'gh5-scene' in s and 'ART.guildHall' in s
for needle in ['function guildShop(', 'startGuildBoss', 'startGuildTrial',
               'gulu-mtstyle-v1', "const SAVE_KEY", 'GUILD_TAB',
               'guildShop(80,1)', 'guildShop(50,0)', 'guildShop(120,2)',
               '剩余 ', 'savePanelHtml', 'tidle']:
    assert needle in s, needle

open(src, 'w', encoding='utf-8').write(s)
data = open(src, 'rb').read()
print('wrote', len(data), 'bytes  MD5', hashlib.md5(data).hexdigest())

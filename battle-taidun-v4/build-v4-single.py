#!/usr/bin/env python3
"""Build the v4 single-file playable (all assets inlined as data URIs).

Icons are downscaled to 96px (displayed at 26px) to keep the file small;
all other assets are inlined byte-for-byte. The result must open standalone
with no sibling files.
"""
import base64, io, os, re

DST = os.path.expanduser('~/workspace/gulu-battle-sample-v4')
html = open(os.path.join(DST, 'index.html'), encoding='utf-8').read()

from PIL import Image

def datauri(path, mime, max_px=None):
    if max_px:
        im = Image.open(path).convert('RGBA')
        if max(im.size) > max_px:
            im.thumbnail((max_px, max_px), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'PNG', optimize=True)
        raw = buf.getvalue()
    else:
        raw = open(path, 'rb').read()
    return 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode())

ASSETS = {
    'layers/body.png': ('image/png', None),
    'layers/leg-front.png': ('image/png', None),
    'layers/head.png': ('image/png', None),
    'layers/shield.png': ('image/png', None),
    'layers/arm-hammer.png': ('image/png', None),
    'bg-forest.webp': ('image/webp', None),
    'enemy-e01.webp': ('image/webp', None),
    'flat-taidun.webp': ('image/webp', None),
    'canva-icons/icon-hammer.png': ('image/png', 96),
    'canva-icons/icon-shield.png': ('image/png', 96),
}
for rel, (mime, max_px) in ASSETS.items():
    uri = datauri(os.path.join(DST, rel), mime, max_px)
    before = html.count('src="%s"' % rel)
    assert before >= 1, 'no reference to ' + rel
    html = html.replace('src="%s"' % rel, 'src="%s"' % uri)
    print(rel, '->', len(uri), 'chars x', before)

leftover = re.findall(r'src="(?:layers/|bg-|enemy-|flat-|canva-icons/)[^"]*"', html)
assert not leftover, leftover
assert 'http://' not in html and 'https://' not in html.replace('https://www.w3.org', ''), 'external URL?'
out = os.path.join(DST, 'taidun-v4-single-file.html')
open(out, 'w', encoding='utf-8').write(html)
print('single file:', len(html), 'bytes ->', out)

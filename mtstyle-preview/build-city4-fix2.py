# city4 fix 2: Taidun blink geometry measured from the real eye pixels of the
# 628px head layer (left eye x 29.9-34.7% y 27.2-33.4%, right eye x 47.8-54.0%
# y 26.9-33.4%), lid colour sampled from the skin above the eyes (#cbc978),
# and the home chest nudged clear of Taidun's boots.
P = '/home/hatch/workspace/gulu-mtstyle-preview/index.html'
h = open(P, encoding='utf-8').read()
assert "APP_VERSION='2026.11.02-city4'" in h, 'version guard'

a = '.l1{left:33.8%;top:25.8%;width:5.6%;height:7.4%}'
b = '.l2{left:52.2%;top:25.8%;width:5.6%;height:7.4%}'
assert h.count(a) == 1 and h.count(b) == 1
h = h.replace(a, '.l1{left:28.5%;top:25.5%;width:7.2%;height:10%}')
h = h.replace(b, '.l2{left:46.5%;top:25.5%;width:8.4%;height:10%}')

c = '.tlid{position:absolute;background:#c6c474;'
assert h.count(c) == 1
h = h.replace(c, '.tlid{position:absolute;background:#cbc978;')

d = '.chest{bottom:76px}'
assert h.count(d) == 1
h = h.replace(d, '.chest{left:6px;bottom:70px}')

open(P, 'w', encoding='utf-8').write(h)
print('fix2 written')

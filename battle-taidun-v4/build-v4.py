#!/usr/bin/env python3
"""Build Taidun v4 working index.html from the v3 working file.

- Copies the v3 solo-battle base, removes the team view entirely.
- Adds core helpers (enemy contact lunge, enemy pose, hurt offsets,
  blink, split active reserve/apply) and splices in ui-v4-fragment.js.
- No banned-word text may remain in the HTML (the Node test enforces it).
"""
import os, re, shutil, sys

SRC = os.path.expanduser('~/workspace/gulu-battle-sample-v3')
DST = os.path.expanduser('~/workspace/gulu-battle-sample-v4')
FRAG = os.path.join(DST, 'ui-v4-fragment.js')

for d in ('layers', 'canva-icons'):
    os.makedirs(os.path.join(DST, d), exist_ok=True)
for f in ('layers/body.png', 'layers/leg-front.png', 'layers/head.png',
          'layers/shield.png', 'layers/arm-hammer.png',
          'bg-forest.webp', 'enemy-e01.webp', 'flat-taidun.webp',
          'canva-icons/icon-hammer.png', 'canva-icons/icon-shield.png'):
    shutil.copy2(os.path.join(SRC, f), os.path.join(DST, f))
print('assets copied')

html = open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()

def rep(old, new, count=1, must=True):
    global html
    if old not in html:
        if must:
            raise SystemExit('ANCHOR MISSING: %r' % old[:90])
        return
    html = html.replace(old, new, count)

# ---------- favicon: inline empty icon so browsers do not 404 ----------
rep('<meta charset="utf-8">', '<meta charset="utf-8"><link rel="icon" href="data:,">')

# ---------- title / header ----------
rep('<title>咕噜远征团 · 苔盾 v3 盾牌撞击样片</title>',
    '<title>咕噜远征团 · 苔盾 v4 战斗样板</title>')
rep('<header><h1>咕噜远征团 · 苔盾 v3</h1><p class="mut">只有普攻（木盾撞击）、主动（看这里）、被动（虽然害怕）。普攻由盾牌完成：接近 → 盾缘接触 → 受力缓冲 → 收盾回位。本页为隔离预览，未改动原游戏与 GitHub main。</p></header>',
    '<header><h1>咕噜远征团 · 苔盾 v4</h1><p class="mut">只有普攻（木盾撞击）、主动（看这里）、被动（虽然害怕）三种技能。分层动作：待机、普攻前摇、出手、命中、受击、回位，全部由盾缘与受击点的实时位置驱动。本页为隔离预览，不读写任何存档，未改动原游戏与 GitHub main。</p></header>')

# ---------- remove tabs ----------
rep('<div class="tabs" role="tablist"><button id="tabSolo" aria-pressed="true">单英雄精修 · 苔盾 vs 史莱姆</button><button id="tabTeam" aria-pressed="false">队伍战斗预览 · 5 vs 3</button></div>\n', '')

# ---------- head wrap with eyelids ----------
rep('<img class="lyr head" id="lyHead" src="layers/head.png" alt="头部">',
    '<span id="headWrap"><img class="lyr head" id="lyHead" src="layers/head.png" alt="头部"><span class="lid l1" id="lid1"></span><span class="lid l2" id="lid2"></span></span>')

# ---------- enemy ground shadow ----------
rep('<div class="enemy" id="enemy"><span class="tag" id="enemyTag" style="display:none">被嘲讽</span><img id="enemyImg" src="enemy-e01.webp" alt="困困史莱姆"></div>',
    '<div class="enemy" id="enemy"><div class="eshadow"></div><span class="tag" id="enemyTag" style="display:none">被嘲讽</span><img id="enemyImg" src="enemy-e01.webp" alt="困困史莱姆"></div>')

# ---------- swoosh ----------
rep('  <div id="fxLayer" style="position:absolute;inset:0;pointer-events:none;z-index:16"></div>',
    '  <div id="swoosh"></div>\n  <div id="fxLayer" style="position:absolute;inset:0;pointer-events:none;z-index:16"></div>')

# ---------- badges: version + speed ----------
rep('  <span class="badge" id="badgeTaunt">嘲讽：未触发</span>',
    '  <span class="badge">样板 v4 · 2026.11.03-taidun-v4</span>\n  <span class="badge" id="badgeTaunt">嘲讽：未触发</span>')
rep('  <span class="badge" id="badgeTime">战斗时间 0.0s</span>\n</div>',
    '  <span class="badge" id="badgeTime">战斗时间 0.0s</span>\n  <span class="badge" id="badgeSpeed">速度：1×</span>\n</div>\n<div id="resultBar"></div>')

# ---------- controls ----------
old_controls = '''<div class="controls">
  <button id="btnBasic" class="primary"><img src="canva-icons/icon-hammer.png" alt="">普攻 · 木盾撞击</button>
  <button id="btnActive"><img src="canva-icons/icon-shield.png" alt="">主动 · 看这里</button>
  <button id="btnEnemy">敌人普攻（34）</button>
  <button id="btnAuto">自动战斗：关</button>
  <button id="btnPause">暂停</button>
  <button id="btnReset">重开</button>
  <button id="btnSound">声音：开</button>
</div>'''
new_controls = '''<div class="controls">
  <button id="btnBasic" class="primary"><img src="canva-icons/icon-hammer.png" alt="">普攻 · 木盾撞击</button>
  <button id="btnActive"><img src="canva-icons/icon-shield.png" alt="">主动 · 看这里</button>
  <button id="btnEnemy">敌人普攻（34）</button>
  <button id="btnAuto">自动战斗：关</button>
  <button id="btnSpeed">速度：1×</button>
  <button id="btnSkip">跳过战斗</button>
  <button id="btnPause">暂停</button>
  <button id="btnReset">重开</button>
  <button id="btnSound">声音：开</button>
</div>'''
rep(old_controls, new_controls)

# ---------- contact note ----------
rep('<p class="mut">接触判定：每次普攻开始时，用盾牌攻击点（盾缘）与敌人受击点（史莱姆身体左侧）实时计算突进距离，窗口变化会重新计算；命中只在接触帧结算一次。连点普攻不会重复结算：动作进行中按钮不重复触发。</p>',
    '<p class="mut">接触判定：普攻与敌人攻击都在开始时用攻击点与受击点实时计算突进距离，窗口变化会重新计算；命中只在接触帧结算一次。连点不会重复结算：动作进行中按钮不重复触发。跳过战斗用同一逻辑步进快进，结果与正常播放一致。</p>')

# ---------- debug panel ----------
rep('<button id="btnStep">单帧前进 50ms</button>', '<button id="btnStep">单帧前进 20ms</button>')
rep('<p class="mut">素材与插件：身体补画用图片生成重绘无盾无臂躯干（同风格），盾牌与持锤手取原图像素并清理边缘；Figma 规范文件 AREialZ1cps0UHJ0xqt94F（颜色 Token 已用于本页）；Canva 只用于技能图标，拆分不可靠未用于图层；Runway 免费版无视频模型，未生成视频。单帧步长 50ms，暂停冻结动作、粒子、浮字、冷却与状态计时。</p>',
    '<p class="mut">素材：5 个图层全部取自原图像素（v3.1 修复版：身体、头部、前腿的遮挡区用原图扩散补画加高频纹理，静止合成与原画差异 1.1）；旧 AI 重绘层备份在 layers-ai-backup/。Figma 规范文件 AREialZ1cps0UHJ0xqt94F（颜色 Token 已用于本页）；Canva 只用于技能图标；Runway 未生成视频。逻辑步长 20ms，暂停冻结动作、粒子、浮字、冷却与状态计时；单帧前进 1 步。</p>')

# ---------- remove team section ----------
i = html.index('<section id="viewTeam"')
j = html.index('</section>', i) + len('</section>')
removed = html[i:j]
assert 'teamStage' in removed, 'team section slice wrong'
html = html[:i] + html[j:]

# ---------- remove team CSS + tabs CSS ----------
i = html.index('.teamStage{')
j = html.index('.kv{')
assert '.slot' in html[i:j], 'team css slice wrong'
html = html[:i] + html[j:]
rep('.tabs{display:flex;gap:8px;margin:8px 0}.tabs button{flex:1;padding:10px;border:2px solid var(--brass);border-radius:10px;background:var(--card);font-size:15px;cursor:pointer}\n.tabs button[aria-pressed="true"]{background:var(--brass);color:#fff;font-weight:700}\n', '')
rep('@media (max-width:400px){h1{font-size:17px}.stage{aspect-ratio:4/3}.teamStage{aspect-ratio:4/3}.controls button{flex:1 1 44%}}',
    '@media (max-width:400px){h1{font-size:17px}.stage{aspect-ratio:4/3}.controls button{flex:1 1 44%}}')

# ---------- v4 CSS additions ----------
v4css = '''
#headWrap{position:absolute;inset:0;transform-origin:36% 48%;will-change:transform}
.lid{position:absolute;background:#cbc978;border-radius:0 0 50% 50%;transform:scaleY(.08);transform-origin:50% 0%;z-index:3;pointer-events:none}
.lid.l1{left:28.5%;top:25.5%;width:7.2%;height:10%}
.lid.l2{left:46.5%;top:25.5%;width:8.4%;height:10%}
.eshadow{position:absolute;left:16%;right:16%;bottom:0;height:10%;background:radial-gradient(ellipse,#0007,#0000 70%);border-radius:50%}
#swoosh{position:absolute;top:52%;height:26px;display:none;z-index:8;pointer-events:none;background:linear-gradient(90deg,transparent,#fff8 25%,#ffe9a8 60%,#e8c98a 85%,transparent);border-radius:13px;transform:skewX(-18deg)}
#resultBar{margin:10px 0;padding:10px 12px;border-radius:10px;background:#2b1c10;color:#f6e7c3;font-size:14px;line-height:1.5}
.stage.paused *{animation-play-state:paused!important}
'''
rep('</style>', v4css + '</style>')

# ---------- core additions ----------
core_add = '''
/* 敌人接触距离：史莱姆左侧攻击点与苔盾盾缘受击点实时计算，不写死距离。 */
function computeLungeEnemy(heroRect,foeRect){
  const strikeX=foeRect.left+foeRect.width*0.11;
  const shieldX=heroRect.left+heroRect.width*0.95;
  const gap=strikeX-shieldX;
  return {gap:gap,lunge:Math.max(0,gap-4),contactX:shieldX,strikeX:strikeX};
}
/* 敌人动作姿态：t 为动作内毫秒；lungePx 为本次计算的突进像素。 */
function enemyPose(t,lungePx){
  if(t<200){ const k=easeOut(t/200); return {x:0,y:0,sx:1+0.08*k,sy:1-0.18*k,phase:'windup'}; }
  if(t<500){ const k=easeIn((t-200)/300); const arc=Math.sin(k*Math.PI)*22; return {x:-lungePx*k,y:-arc,sx:1-0.04*k,sy:1+0.04*k,phase:'lunge'}; }
  const k=easeOut(Math.min(1,(t-500)/300));
  return {x:-lungePx*(1-k),y:-Math.sin(k*Math.PI)*10,sx:1,sy:1,phase:'return'};
}
/* 受击叠加偏移：k 为 0..1 的正弦包络，作用于当前姿态之上，不打断动作。 */
function hurtOffsets(k){
  return {heroX:-7*k,bodyRot:-4*k,shieldY:-6*k,shieldRot:-8*k,headRot:-3*k};
}
/* 眨眼：4.8s 周期，闭合窗口 300..480ms；返回眼睑 scaleY（0.08=睁眼，1=闭合）。 */
function blinkScale(t){
  const p=((t%4800)+4800)%4800;
  if(p<300||p>480) return 0.08;
  const k=(p-300)/180;
  return 0.08+0.92*Math.sin(k*Math.PI);
}
/* 主动拆分：reserve 只锁定冷却（出手时），apply 在前顶帧结算嘲讽与护盾。 */
function reserveActiveTaidun(u,t){
  if(t<u.activeReadyAt) return {ok:false,reason:'cooldown'};
  u.activeReadyAt=t+8000;
  return {ok:true};
}
function applyActiveTaidun(u,foes,t){
  foes.forEach(f=>{ if(f.alive){ f.buffs=f.buffs.filter(b=>b.type!=='taunted'); f.buffs.push({type:'taunted',val:u.id,until:t+2000}); }});
  const shield=addShield(u,Math.round(u.maxHp*0.12),5000,t,'hero_taidun');
  return {shield:shield};
}
'''
old_try = '''function tryActiveTaidun(u,foes,t){
  if(t<u.activeReadyAt) return {ok:false,reason:'cooldown'};
  u.activeReadyAt=t+8000;
  foes.forEach(f=>{ if(f.alive){ f.buffs=f.buffs.filter(b=>b.type!=='taunted'); f.buffs.push({type:'taunted',val:u.id,until:t+2000}); }});
  const shield=addShield(u,Math.round(u.maxHp*0.12),5000,t,'hero_taidun');
  return {ok:true,shield:shield};
}'''
rep(old_try, core_add + '''function tryActiveTaidun(u,foes,t){
  const r=reserveActiveTaidun(u,t);
  if(!r.ok) return r;
  const a=applyActiveTaidun(u,foes,t);
  return {ok:true,shield:a.shield};
}''')
rep("module.exports={DATA,calcDamageDet,createUnit,shieldTotal,addShield,expireShields,expireBuffs,applyDamage,dealBasic,pickBasicTarget,tryActiveTaidun,computeLunge,basicPose,activePose,idlePose}",
    "module.exports={DATA,calcDamageDet,createUnit,shieldTotal,addShield,expireShields,expireBuffs,applyDamage,dealBasic,pickBasicTarget,tryActiveTaidun,reserveActiveTaidun,applyActiveTaidun,computeLunge,computeLungeEnemy,enemyPose,hurtOffsets,blinkScale,basicPose,activePose,idlePose}")

# ---------- measured contact factors (from layer alpha, v4) ----------
rep('attackX = hero 左缘 + 宽度×0.93（盾缘）；hitX = 目标左缘 + 宽度×0.15（身体左侧）',
    'attackX = hero 左缘 + 宽度×0.95（盾缘，实测图层最右不透明像素 94.9%）；hitX = 目标左缘 + 宽度×0.11（身体左侧，实测最左不透明像素 11.2%）')
rep('const attackX=heroRect.left+heroRect.width*0.93;',
    'const attackX=heroRect.left+heroRect.width*0.95;')
rep('const hitX=foeRect.left+foeRect.width*0.15;',
    'const hitX=foeRect.left+foeRect.width*0.11;')
rep('攻击点：盾缘 93% 宽度处；受击点：史莱姆左侧 15% 处。',
    '攻击点：盾缘 95% 宽度处；受击点：史莱姆左侧 11% 处。')

# ---------- splice UI fragment ----------
frag = open(FRAG, encoding='utf-8').read().strip()
marker = '/* ============ 单英雄 UI ============ */'
mi = html.index(marker)
si = html.rindex('<script>', 0, mi)
ei = html.index('newSolo(); startLoop();', mi) + len('newSolo(); startLoop();')
ei = html.index('</script>', ei) + len('</script>')
html = html[:si] + '<script>\n' + frag + '\n</script>' + html[ei:]

open(os.path.join(DST, 'index.html'), 'w', encoding='utf-8').write(html)
print('v4 index.html written:', len(html), 'bytes')
# sanity: no team code, no timers, no banned words
for bad in ('viewTeam', 'teamStage', 'tabTeam', 'setTimeout', 'setInterval'):
    assert bad not in html, 'leftover: ' + bad
import re as _re
for w in ('大招', '能量', '必杀', 'energy'):
    assert w not in html, 'banned word present: ' + w
print('sanity checks passed')

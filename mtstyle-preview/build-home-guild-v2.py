# -*- coding: utf-8 -*-
"""主城 v2 / 公会大厅重做补丁（输入：主城 v1 状态的 index.html，APP_VERSION=2026.11.01-city1）。
只改：版本号、主城构图与招牌入口、场景内小队立绘、进入过渡、公会大厅内页。
不改：玩法、数值、存档键、战斗引擎（大招机制本轮不动，待战斗轮次统一检查）。
"""
import io, base64, sys
from PIL import Image

P = '/home/hatch/workspace/gulu-mtstyle-preview/index.html'
s = open(P, encoding='utf-8').read()
assert "const APP_VERSION='2026.11.01-city1'" in s, '输入文件不是主城 v1 状态，拒绝重复打补丁'

def rep(old, new, tag):
    global s
    assert s.count(old) == 1, '锚点不唯一或缺失: ' + tag + ' count=' + str(s.count(old))
    s = s.replace(old, new, 1)
    print('patched:', tag)

# ---- 1) 版本号 ----
rep("const APP_VERSION='2026.11.01-city1'", "const APP_VERSION='2026.11.01-city2'", 'version-const')
rep('<!-- 版本 2026.11.01-city1（主城 v1） -->', '<!-- 版本 2026.11.01-city2（主城 v2 · 公会大厅） -->', 'version-comment')
rep("'+APP_VERSION+'（主城 v1）</b>", "'+APP_VERSION+'（主城 v2 · 公会大厅）</b>", 'version-settings')

# ---- 2) 全身立绘（12 名英雄，原图像素裁切，静态立绘；场景内待机仅为轻微浮动，非分层动画） ----
heroes = ['taidun', 'heling', 'yexian', 'tongshao', 'xingkui', 'maoya',
          'baoli', 'paopaoli', 'shange', 'dengyu', 'yefeng', 'qiren']
parts = []
d = '/home/hatch/workspace/gulu-handover/game/assets'
for h in heroes:
    im = Image.open(d + '/hero-' + h + '.webp').convert('RGBA').crop(
        Image.open(d + '/hero-' + h + '.webp').convert('RGBA').getbbox())
    w, hh = im.size
    nh = 240
    im = im.resize((max(1, round(w * nh / hh)), nh), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=72, method=6)
    parts.append("'%s':'data:image/webp;base64,%s'" % (h, base64.b64encode(buf.getvalue()).decode()))
rep('/* 立绘：全部取自咕噜交接包原画',
    'ART.heroFull={' + ','.join(parts) + '};\n/* 立绘：全部取自咕噜交接包原画', 'hero-full-art')

# ---- 3) 进入过渡：每次 render 后 #view 轻微淡入上浮 ----
rep("document.getElementById('view').innerHTML=fn();window.scrollTo(0,0);",
    "document.getElementById('view').innerHTML=fn();const _vw=document.getElementById('view');_vw.classList.remove('vin');void _vw.offsetWidth;_vw.classList.add('vin');window.scrollTo(0,0);",
    'view-enter-transition')

# ---- 4) 主城：招牌式入口 + 场景内小队立绘 ----
rep(r"""<span class="hs-ic">'+ICON.mug+'</span><span class="hs-lb">酒馆 · 召唤</span>""",
    r"""<span class="hs-rope"></span><span class="hs-sign">'+ICON.mug+'<span>酒馆 · 召唤</span></span>""", 'sign-tavern')
rep(r"""<span class="hs-ic">'+ICON.shield+'</span><span class="hs-lb">公会大厅</span>""",
    r"""<span class="hs-rope"></span><span class="hs-sign">'+ICON.shield+'<span>公会大厅</span></span>""", 'sign-guild')
rep(r"""<span class="hs-ic">'+ICON.anvil+'</span><span class="hs-lb">铁匠铺</span>""",
    r"""<span class="hs-rope"></span><span class="hs-sign">'+ICON.anvil+'<span>铁匠铺</span></span>""", 'sign-smith')
rep(r"""<span class="hs-ic">'+ICON.scroll+'</span><span class="hs-lb">任务板</span>""",
    r"""<span class="hs-rope"></span><span class="hs-sign">'+ICON.scroll+'<span>任务板</span></span>""", 'sign-board')
rep(r"""<button class="teamstrip" onclick="openTeam()">""",
    r"""<div class="party" aria-hidden="true">'+S.formation.map(function(id,i){return '<img class="'+(i<2?'f':'b')+'" src="'+ART.heroFull[id]+'" alt="">';}).join('')+'</div><button class="teamstrip" onclick="openTeam()">""",
    'party-in-scene')

# ---- 5) 公会大厅内页重做（保留原有 handlers 与数据） ----
start = s.index('function vGuild(){')
end = s.index('function guildShop(', start)
assert '公会 Boss' in s[start:end]
new_guild = r"""let GUILD_TAB='boss';
function guildTab(t){GUILD_TAB=t;render();}
function vGuild(){if(S.guild.day!==todayStr()){S.guild.day=todayStr();S.guild.bossDmg=0;}const bossKey='B'+((Math.floor(Date.now()/86400000)%4)+1);const boss=BOSSES[bossKey];const trialUsed=S.guild.trialDay===todayStr()?S.guild.trial:0;const sim=[['晨星小队',8200],['炉心小队',6500],['潮汐小队',5400],['星灯小队',4100]];let body='';if(GUILD_TAB==='boss'){body='<div class="panel"><b>公会 Boss · '+boss.name+'</b><div class="mut">每次挑战限时 30 秒，按伤害发公会币（伤害 ÷ 100）。今日你已造成伤害 '+fmt(S.guild.bossDmg)+'。</div><div class="btnrow"><button class="btn red" onclick="startGuildBoss()">挑战公会 Boss</button></div></div>';}else if(GUILD_TAB==='shop'){body='<div class="panel"><b>公会商店 · 公会币 '+fmt(S.res.gcoin)+'</b><div class="btnrow"><button class="btn sm" onclick="guildShop(80,1)">80 币 → 招募券 ×1</button><button class="btn sm" onclick="guildShop(50,0)">50 币 → 随机碎片 ×10</button><button class="btn sm" onclick="guildShop(120,2)">120 币 → 进阶石 ×2</button></div></div>';}else{body='<div class="panel"><b>公会试炼</b><div class="mut">多人协作推进的单机化版本：每日 2 次，今日已用 '+trialUsed+'/2 次，胜得公会币 60 + 金币 500。</div><div class="btnrow"><button class="btn" onclick="startGuildTrial()">参加试炼</button></div></div>';}return '<div class="guildhall"><div class="gh-scene"><span class="gh-win wl"></span><span class="gh-win wr"></span><span class="gh-banner bl"></span><span class="gh-banner br"></span><span class="gh-badge">单机模拟 · 本机存档</span><div class="gh-title">咕噜冒险公会</div><div class="gh-arch">'+iconSvg('boss',bossKey,96)+'</div><div class="gh-bossname">'+boss.name+' · 今日镇守</div></div><div class="gh-tiles"><button class="gh-tile '+(GUILD_TAB==='boss'?'sel':'')+'" onclick="guildTab(\'boss\')">'+iconSvg('boss',bossKey,34)+'<b>公会 Boss</b><span>今日伤害 '+fmt(S.guild.bossDmg)+'</span></button><button class="gh-tile '+(GUILD_TAB==='shop'?'sel':'')+'" onclick="guildTab(\'shop\')">'+ICON.coin+'<b>公会商店</b><span>公会币 '+fmt(S.res.gcoin)+'</span></button><button class="gh-tile '+(GUILD_TAB==='trial'?'sel':'')+'" onclick="guildTab(\'trial\')">'+ICON.sword+'<b>公会试炼</b><span>今日 '+trialUsed+'/2 次</span></button></div>'+body+'<div class="gh-rank">模拟排名 '+sim.map(function(x){return '<span class="tag">'+x[0]+' '+fmt(x[1])+'</span>';}).join('')+'<span class="tag">你 '+fmt(S.guild.bossDmg)+'</span></div><div class="mut gh-note">单机模拟：无真实玩家与在线人数，排名与成员为本地固定数据。</div></div>';}
"""
s = s[:start] + new_guild + s[end:]
print('patched: guild-hall-redo')

# ---- 6) 追加 CSS（置于原样式之后，同特异度下后置胜出；媒体查询亦后置） ----
css = r"""
/* === 主城 v2：场景放大取景 + 招牌入口 + 场景小队 + 进入过渡 === */
.city-bg{transform:scale(1.18);transform-origin:50% 38%}
#view.vin{animation:viewIn .26s ease}
@keyframes viewIn{from{opacity:.35;transform:translateY(8px)}to{opacity:1;transform:none}}
.hs{width:100px;transition:transform .12s ease}
.hs:active{transform:scale(.93)}
.hs-rope{display:block;width:30px;height:9px;border-left:2px solid #4a3018;border-right:2px solid #4a3018;margin:0 auto -1px}
.hs-sign{display:flex;align-items:center;gap:6px;background:linear-gradient(180deg,#b0814f,#7d5a36 55%,#6b4a28);border:2px solid #4a3018;border-radius:9px;padding:6px 9px;box-shadow:inset 0 2px 0 rgba(255,235,190,.35),inset 0 -3px 0 rgba(0,0,0,.22),0 4px 8px rgba(40,25,8,.4);color:#fff6dd;font-size:12.5px;font-weight:800;white-space:nowrap;text-shadow:0 1px 2px rgba(0,0,0,.45)}
.hs-sign svg{width:26px;height:26px;flex:none}
.hs-sign span{line-height:1.1}
.hs-tavern .hs-sign{transform:rotate(-1.6deg)}.hs-guild .hs-sign{transform:rotate(.6deg)}.hs-smith .hs-sign{transform:rotate(1.4deg)}.hs-board .hs-sign{transform:rotate(-1deg)}
.hs-guild{left:calc(50% - 50px);top:51%}
.hs-tavern{left:5%;top:49%}
.hs-smith{right:5%;top:51%}
.hs-board{left:3%;top:69%}
.hs .dot{top:-2px;right:4px}
.dock{top:60%}
.chest{bottom:80px}
.chest svg{width:48px;height:48px}
.party{position:absolute;left:50%;transform:translateX(-50%);bottom:148px;z-index:3;display:flex;align-items:flex-end;justify-content:center;pointer-events:none}
.party img{height:58px;width:auto;margin:0 -8px;filter:drop-shadow(0 4px 3px rgba(40,25,8,.45))}
.party img.f{height:68px}
.party img:nth-child(odd){animation:sway 3.6s ease-in-out infinite alternate}
.party img:nth-child(even){animation:sway 4.1s ease-in-out infinite alternate;animation-delay:.6s}
@keyframes sway{from{transform:translateY(0)}to{transform:translateY(-3px)}}
/* === 公会大厅内页：室内场景 === */
.guildhall{padding:10px 12px 16px}
.gh-scene{position:relative;overflow:hidden;border-radius:16px;border:2px solid #8a5a12;background:linear-gradient(180deg,#8a5f38 0%,#77522f 38%,#5f3d21 62%,#4a2d17 100%);min-height:196px;padding:12px 14px 10px;color:#fff3d0;text-align:center;box-shadow:0 6px 16px rgba(40,25,8,.35)}
.gh-scene::before{content:'';position:absolute;inset:0;background:repeating-linear-gradient(90deg,rgba(0,0,0,.13) 0 2px,transparent 2px 36px);pointer-events:none}
.gh-scene::after{content:'';position:absolute;left:0;right:0;bottom:0;height:26px;background:linear-gradient(180deg,rgba(255,214,120,.14),rgba(30,18,8,.35));pointer-events:none}
.gh-win{position:absolute;top:16px;width:34px;height:56px;border-radius:34px 34px 6px 6px;border:3px solid #4a3018;background:radial-gradient(circle at 50% 32%,#ffe9a8,#f2b63c 55%,#c9862a);box-shadow:0 0 18px 4px rgba(255,214,120,.35)}
.gh-win.wl{left:16px}.gh-win.wr{right:16px}
.gh-banner{position:absolute;top:0;width:24px;height:52px;background:linear-gradient(180deg,#b03a2c,#7c271e);border:2px solid #5a1a12;border-top:0;border-radius:0 0 5px 5px;box-shadow:0 3px 6px rgba(0,0,0,.3)}
.gh-banner.bl{left:56px}.gh-banner.br{right:56px}
.gh-badge{position:absolute;top:10px;right:10px;font-size:10.5px;font-weight:700;background:rgba(30,20,10,.55);padding:3px 8px;border-radius:999px;z-index:2}
.gh-title{position:relative;font-size:19px;font-weight:800;text-shadow:0 2px 4px rgba(0,0,0,.5);margin-top:2px}
.gh-arch{position:relative;width:112px;height:126px;margin:8px auto 0;border:3px solid #c9962f;border-bottom:0;border-radius:56px 56px 0 0;background:radial-gradient(circle at 50% 30%,#ffedbe,#e8b96a 60%,#a87c3a);display:flex;align-items:flex-end;justify-content:center;overflow:hidden;box-shadow:0 0 22px 4px rgba(255,214,120,.3)}
.gh-arch img{width:96px!important;height:96px!important}
.gh-bossname{position:relative;font-size:12.5px;font-weight:800;margin-top:6px;text-shadow:0 1px 3px rgba(0,0,0,.5)}
.gh-tiles{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:10px}
.gh-tile{display:flex;flex-direction:column;align-items:center;gap:3px;padding:9px 4px 8px;border-radius:12px;border:2px solid #8a5a12;background:linear-gradient(180deg,#fff3cd,#eed9a0);color:#2b1c10;cursor:pointer;box-shadow:0 3px 0 #8a5a12;transition:transform .12s ease}
.gh-tile:active{transform:scale(.95)}
.gh-tile.sel{border-color:#c9962f;background:linear-gradient(180deg,#ffe9a8,#f2c96a);box-shadow:0 0 0 2px #ffe9a8,0 3px 0 #8a5a12}
.gh-tile svg,.gh-tile img{width:34px;height:34px}
.gh-tile b{font-size:13px}
.gh-tile span{font-size:10.5px;color:#6b4a26;font-weight:700;white-space:nowrap}
.gh-rank{margin-top:8px}
.gh-note{margin-top:6px;font-size:11.5px}
@media (max-height:640px){
.hs-guild{top:43%}.hs-tavern{top:42%}.hs-smith{top:43%}.hs-board{top:58%}
.hs{width:80px}.hs-sign{font-size:11px;padding:4px 6px}.hs-sign svg{width:20px;height:20px}
.dock{top:54%;gap:3px;display:grid;grid-template-columns:repeat(2,34px);gap:4px}
.dock button{width:34px}
.cta{width:176px;margin-left:-88px}
.cta span{max-width:118px;font-size:10.5px}
.chest{bottom:64px}.chest svg{width:36px;height:36px}.chest .chest-sub{display:none}
.party{bottom:132px}.party img{height:48px;margin:0 -7px}.party img.f{height:56px}
.gh-scene{min-height:176px}
}
@media (max-width:360px){
.party img.b{display:none}
.party{bottom:136px}
.hs{width:80px}.hs-sign{font-size:11px;padding:4px 6px}.hs-sign svg{width:20px;height:20px}
.gh-tile span{font-size:10px}
.gh-badge{display:none}
}
"""
anchor = '</style>\n</head>'
assert s.count(anchor) == 1, 'style 块锚点异常 count=' + str(s.count(anchor))
s = s.replace(anchor, css + anchor, 1)
print('patched: css-append')

open(P, 'w', encoding='utf-8').write(s)
print('written bytes:', len(s.encode('utf-8')))

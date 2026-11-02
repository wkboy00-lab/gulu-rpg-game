# -*- coding: utf-8 -*-
"""公会大厅 v3 + 主城构图修正：city2 -> city3。

输入须为 2026.11.01-city2 状态的 index.html（已由运行前备份为
index-city2-backup.html）。只改公会大厅视图与主城场景尺寸/热点位置，
战斗引擎、玩法数值、存档键一律不动（战斗内大招机制留待战斗轮次统一处理）。

改动：
- vGuild() 整体重写为 .gh3 室内场景：墙板/石墙腰线/地板/地毯、
  火把、窗、横幅；Boss 石拱门、商店柜台、试炼布告栏三个区域本身
  就是入口按钮（木招牌 + 实时状态小字），选中态金色招牌。
- 三个功能详情全部改为完整界面：Boss（头像+伤害条+模拟排名+挑战）、
  商店（余额 + 三张商品卡）、试炼（敌方阵容头像 + 次数点 + 规则 + 参加）。
- 详情面板切换带淡入上浮动画；场景入口带 :active 按压缩放。
- 主城：场景放大取景（scale 1.26、origin 50% 52%），天空占比下降；
  招牌与 dock 位置按新取景重算；编队立绘放大（前排 80px、后排 68px）。
- 版本号 -> 2026.11.02-city3。
"""
import io, sys

SRC = '/home/hatch/workspace/gulu-mtstyle-preview/index.html'

s = io.open(SRC, encoding='utf-8').read()
assert "const APP_VERSION='2026.11.01-city2'" in s, '输入不是 city2 状态'

# ---------- 1. 版本号 ----------
s = s.replace("const APP_VERSION='2026.11.01-city2'; // 主城 v1；设置页可查，改动后须同步更新",
              "const APP_VERSION='2026.11.02-city3'; // 公会大厅 v3；设置页可查，改动后须同步更新")
s = s.replace("'+APP_VERSION+'（主城 v2 · 公会大厅）</b>",
              "'+APP_VERSION+'（主城 v3 · 公会大厅）</b>")

# ---------- 2. vGuild() 重写 ----------
start = s.index('function vGuild(){')
end = s.index('function guildShop(', start)
new_guild = (
r"""function vGuild(){if(S.guild.day!==todayStr()){S.guild.day=todayStr();S.guild.bossDmg=0;}const bossKey='B'+((Math.floor(Date.now()/86400000)%4)+1);const boss=BOSSES[bossKey];const trialUsed=S.guild.trialDay===todayStr()?S.guild.trial:0;const sim=[['晨星小队',8200],['炉心小队',6500],['潮汐小队',5400],['星灯小队',4100]];const bossPct=Math.min(100,Math.round(S.guild.bossDmg/8200*100));let body='';if(GUILD_TAB==='boss'){body='<div class="gh3-detail gh3-anim"><div class="gh3-bossrow">'+iconSvg('boss',bossKey,76)+'<div class="gh3-bossinfo"><b>公会 Boss · '+boss.name+'</b><div class="mut">每次挑战限时 30 秒，按伤害发公会币（伤害 ÷ 100）。</div><div class="gh3-bar"><i style="width:'+bossPct+'%"></i></div><div class="mut">今日你已造成伤害 <b>'+fmt(S.guild.bossDmg)+'</b> · 榜首 8,200</div></div></div><div class="gh3-rank">'+sim.map(function(x){return '<span class="tag">'+x[0]+' '+fmt(x[1])+'</span>';}).join('')+'<span class="tag me">你 '+fmt(S.guild.bossDmg)+'</span></div><button class="btn red gh3-big" onclick="startGuildBoss()">挑战公会 Boss</button></div>';}else if(GUILD_TAB==='shop'){body='<div class="gh3-detail gh3-anim"><div class="gh3-shopbal">'+ICON.coin+'<b>公会币 '+fmt(S.res.gcoin)+'</b><span class="mut">购买后即时到账</span></div><div class="gh3-cards"><div class="gh3-card">'+ICON.ticket+'<b>招募券</b><span>×1</span><button class="btn sm" onclick="guildShop(80,1)">80 币</button></div><div class="gh3-card">'+ICON.dia+'<b>随机碎片</b><span>×10</span><button class="btn sm" onclick="guildShop(50,0)">50 币</button></div><div class="gh3-card">'+ICON.stone+'<b>进阶石</b><span>×2</span><button class="btn sm" onclick="guildShop(120,2)">120 币</button></div></div><div class="mut">商店只用游戏内赚取的公会币，无真实支付。</div></div>';}else{body='<div class="gh3-detail gh3-anim"><div class="gh3-trialrow"><div class="gh3-foes">'+iconSvg('foe','E08',42)+iconSvg('foe','E09',42)+iconSvg('foe','E10',42)+iconSvg('foe','E07',42)+iconSvg('foe','E05',42)+'</div><div class="gh3-trialinfo"><b>公会试炼</b><div class="mut">胜得公会币 60 + 金币 500。</div><div class="gh3-dots"><span class="gh3-dot '+(trialUsed<1?'on':'')+'"></span><span class="gh3-dot '+(trialUsed<2?'on':'')+'"></span><span class="mut">今日剩余 '+(2-trialUsed)+'/2 次</span></div></div></div><div class="mut gh3-rules">· 多人协作推进的单机化版本，阵容为本地固定数据<br>· 试炼敌人与推图敌人共用数值与克制规则<br>· 次数每日重置，未用完不累计</div><button class="btn gh3-big" onclick="startGuildTrial()">参加试炼</button></div>';}return '<div class="guildhall3"><div class="gh3-scene"><span class="gh3-win wl"></span><span class="gh3-win wr"></span><span class="gh3-banner bl"></span><span class="gh3-banner br"></span><span class="gh3-badge">单机模拟 · 本机存档</span><div class="gh3-title">咕噜冒险公会</div><div class="gh3-floor"></div><div class="gh3-rug"></div><button class="gh3-zone gh3-boss '+(GUILD_TAB==='boss'?'sel':'')+'" onclick="guildTab(\'boss\')"><span class="gh3-torch tl"></span><span class="gh3-torch tr"></span><span class="gh3-arch">'+iconSvg('boss',bossKey,92)+'</span><span class="gh3-plate">'+ICON.sword+' 公会 Boss</span><span class="gh3-sub">今日伤害 '+fmt(S.guild.bossDmg)+'</span></button><button class="gh3-zone gh3-counter '+(GUILD_TAB==='shop'?'sel':'')+'" onclick="guildTab(\'shop\')"><span class="gh3-counterbox"><span class="gh3-mug"></span><span class="gh3-mug m2"></span><span class="gh3-coins"></span></span><span class="gh3-plate">'+ICON.coin+' 公会商店</span><span class="gh3-sub">公会币 '+fmt(S.res.gcoin)+'</span></button><button class="gh3-zone gh3-board '+(GUILD_TAB==='trial'?'sel':'')+'" onclick="guildTab(\'trial\')"><span class="gh3-boardbox"><span class="gh3-pin p1"></span><span class="gh3-pin p2"></span><span class="gh3-pin p3"></span></span><span class="gh3-plate">'+ICON.scroll+' 公会试炼</span><span class="gh3-sub">今日 '+(2-trialUsed)+'/2 次</span></button></div>'+body+'<div class="mut gh3-note">单机模拟：无真实玩家与在线人数，排名与成员为本地固定数据。</div></div>';}"""
)
s = s[:start] + new_guild + s[end:]

# ---------- 3. 追加 CSS（须放在第二 <style> 块末尾） ----------
anchor = '</style>\n</head>'
assert s.count(anchor) == 1, 'style 锚点数量异常'
css = """
/* ==== 公会大厅 v3：室内场景 ==== */
.guildhall3{position:relative}
.gh3-scene{position:relative;overflow:hidden;border-radius:16px;border:2px solid #8a5a12;box-shadow:0 8px 18px rgba(40,25,8,.35);min-height:334px;color:#fff3d0;
 background:linear-gradient(180deg,#9c6b3d 0%,#8a5c33 34%,#7a4f2b 55%,#6b4323 56%,#5a361c 100%)}
.gh3-scene::before{content:'';position:absolute;inset:0 0 56px 0;background:repeating-linear-gradient(90deg,rgba(0,0,0,.14) 0 2px,transparent 2px 40px),linear-gradient(180deg,rgba(255,220,140,.10),transparent 30%);pointer-events:none}
.gh3-floor{position:absolute;left:0;right:0;bottom:0;height:56px;background:linear-gradient(180deg,#7c5228,#5e3a18);box-shadow:inset 0 3px 0 rgba(255,215,130,.28)}
.gh3-floor::before{content:'';position:absolute;inset:0;background:repeating-linear-gradient(90deg,rgba(0,0,0,.22) 0 2px,transparent 2px 46px),repeating-linear-gradient(0deg,rgba(0,0,0,.16) 0 2px,transparent 2px 18px)}
.gh3-rug{position:absolute;left:50%;bottom:8px;width:150px;height:34px;transform:translateX(-50%);border-radius:50%;background:radial-gradient(ellipse at center,#a33b2e 0%,#8a2c20 55%,#6e2118 100%);border:2px solid #e0b45c;opacity:.9}
.gh3-win{position:absolute;top:44px;width:44px;height:58px;border-radius:22px 22px 6px 6px;border:3px solid #5a361c;background:linear-gradient(180deg,#ffe9a8,#f7c86a 55%,#e8a94e);box-shadow:0 0 18px rgba(255,205,100,.55);z-index:0}
.gh3-win.wl{left:14px}.gh3-win.wr{right:14px}
.gh3-win::before{content:'';position:absolute;left:50%;top:0;bottom:0;width:3px;background:#5a361c;transform:translateX(-50%)}
.gh3-win::after{content:'';position:absolute;left:0;right:0;top:50%;height:3px;background:#5a361c}
.gh3-banner{position:absolute;top:40px;width:30px;height:74px;background:linear-gradient(180deg,#b0402f,#8a2c20);clip-path:polygon(0 0,100% 0,100% 100%,50% 82%,0 100%);border:0;z-index:0}
.gh3-banner::before{content:'';position:absolute;left:50%;top:12px;width:14px;height:14px;transform:translateX(-50%) rotate(45deg);border:2px solid #f2d58a;background:transparent}
.gh3-banner.bl{left:74px}.gh3-banner.br{right:74px}
.gh3-badge{position:absolute;right:10px;top:10px;font-size:11px;background:rgba(30,18,8,.62);border:1px solid #d9a54a;border-radius:999px;padding:3px 8px;z-index:3}
.gh3-title{position:absolute;left:12px;top:10px;font-size:17px;font-weight:700;color:#ffe9b0;text-shadow:0 2px 4px rgba(30,18,8,.7);z-index:3}
.gh3-zone{position:absolute;z-index:2;display:flex;flex-direction:column;align-items:center;gap:3px;background:none;border:0;padding:0;color:#fff3d0;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:transform .12s ease}
.gh3-zone:active{transform:scale(.95)}
.gh3-zone:focus-visible{outline:2px solid #ffd76a;outline-offset:2px}
.gh3-boss{left:50%;top:36px;transform:translateX(-50%);width:158px}
.gh3-boss:active{transform:translateX(-50%) scale(.95)}
.gh3-arch{position:relative;display:block;width:110px;height:126px;padding-top:8px;border-radius:56px 56px 8px 8px;background:linear-gradient(180deg,#9a8f7c,#7d7263 60%,#665c4e);border:3px solid #4f453a;box-shadow:inset 0 0 0 4px rgba(255,235,180,.18),0 6px 10px rgba(0,0,0,.35)}
.gh3-arch img{display:block;margin:6px auto 0;width:92px;height:92px;object-fit:contain;filter:drop-shadow(0 4px 5px rgba(0,0,0,.45))}
.gh3-torch{position:absolute;top:52px;width:8px;height:26px;background:linear-gradient(180deg,#7a4f2b,#4a2d17);border-radius:3px}
.gh3-torch::before{content:'';position:absolute;left:50%;top:-12px;width:14px;height:16px;transform:translateX(-50%);border-radius:50% 50% 50% 50%/62% 62% 38% 38%;background:radial-gradient(circle at 50% 70%,#fff7c4 0%,#ffc93c 45%,#f07b1d 78%,rgba(240,123,29,0) 100%);animation:ghflame 1.1s ease-in-out infinite alternate}
.gh3-torch.tl{left:2px}.gh3-torch.tr{right:2px}
@keyframes ghflame{from{transform:translateX(-50%) scaleY(.92)}to{transform:translateX(-50%) scaleY(1.08)}}
.gh3-counter{left:8px;top:150px;width:104px}
.gh3-board{right:8px;top:150px;width:104px}
.gh3-counterbox{position:relative;display:block;width:96px;height:64px;border-radius:8px;background:linear-gradient(180deg,#a9743f,#7c5228 70%,#5e3a18);border:2px solid #4a2d17;box-shadow:0 5px 8px rgba(0,0,0,.35),inset 0 3px 0 rgba(255,220,140,.35)}
.gh3-counterbox::before{content:'';position:absolute;left:6px;right:6px;bottom:6px;height:24px;border-radius:4px;background:repeating-linear-gradient(90deg,rgba(0,0,0,.25) 0 2px,transparent 2px 22px)}
.gh3-mug{position:absolute;top:-14px;left:14px;width:14px;height:14px;border-radius:2px 2px 4px 4px;background:linear-gradient(180deg,#e8c47a,#b98a3e);box-shadow:inset -2px 0 0 rgba(0,0,0,.18)}
.gh3-mug::before{content:'';position:absolute;right:-4px;top:2px;width:5px;height:8px;border:2px solid #b98a3e;border-left:0;border-radius:0 4px 4px 0}
.gh3-mug.m2{left:44px}
.gh3-coins{position:absolute;top:-12px;right:10px;width:20px;height:12px}
.gh3-coins::before{content:'';position:absolute;left:0;bottom:0;width:20px;height:6px;border-radius:50%;background:#f4c93f;box-shadow:0 -4px 0 #e0a92c,0 -8px 0 #f4c93f}
.gh3-boardbox{position:relative;display:block;width:96px;height:64px;border-radius:6px;background:linear-gradient(180deg,#8a5c33,#6b4323);border:3px solid #4a2d17;box-shadow:0 5px 8px rgba(0,0,0,.35)}
.gh3-pin{position:absolute;width:24px;height:30px;background:#f7ead0;border:1px solid #cbb98f;border-radius:2px}
.gh3-pin::before{content:'';position:absolute;left:4px;right:4px;top:6px;height:2px;background:#a89a78;box-shadow:0 6px 0 #a89a78,0 12px 0 #a89a78}
.gh3-pin.p1{left:8px;top:8px;transform:rotate(-5deg)}
.gh3-pin.p2{left:36px;top:12px;transform:rotate(3deg)}
.gh3-pin.p3{left:62px;top:7px;transform:rotate(-3deg)}
.gh3-plate{display:inline-flex;align-items:center;gap:5px;white-space:nowrap;background:linear-gradient(180deg,#a9743f,#7c5228);border:2px solid #5a361c;border-radius:8px;padding:5px 9px;font-size:13px;font-weight:700;color:#ffe9b0;box-shadow:0 3px 6px rgba(0,0,0,.35)}
.gh3-plate svg{width:16px;height:16px;flex:none}
.gh3-zone.sel .gh3-plate{background:linear-gradient(180deg,#f7d878,#d9a52c);color:#3a2408;border-color:#8a5a12}
.gh3-sub{font-size:11px;color:#ffe9b0;text-shadow:0 1px 3px rgba(0,0,0,.6)}
.gh3-detail{margin-top:10px}
.gh3-anim{animation:ghIn .26s ease}
@keyframes ghIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.gh3-bossrow{display:flex;gap:10px;align-items:center}
.gh3-bossinfo{flex:1;min-width:0}
.gh3-bar{height:8px;border-radius:99px;background:rgba(0,0,0,.22);overflow:hidden;margin:6px 0}
.gh3-bar i{display:block;height:100%;background:linear-gradient(90deg,#f4c93f,#e8842c);border-radius:99px}
.gh3-rank{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.gh3-rank .tag.me{background:#fff3cf;color:#6b4323;border-color:#d9a52c}
.gh3-big{width:100%;margin-top:8px;padding:11px 0}
.gh3-shopbal{display:flex;align-items:center;gap:6px;margin-bottom:10px}
.gh3-shopbal svg{width:22px;height:22px;flex:none}
.gh3-shopbal .mut{margin-left:auto}
.gh3-cards{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}
.gh3-card{display:flex;flex-direction:column;align-items:center;gap:3px;background:#fff8e6;border:1.5px solid #d9b36a;border-radius:12px;padding:10px 4px;color:#5a3a18}
.gh3-card svg{width:28px;height:28px;flex:none}
.gh3-card b{font-size:13px}
.gh3-card span{font-size:12px;color:#8a6a34}
.gh3-card .btn{margin-top:4px;width:100%}
.gh3-trialrow{display:flex;gap:10px;align-items:center}
.gh3-foes{display:flex}
.gh3-foes img{width:42px;height:42px;margin-left:-8px;border:2px solid #fff3cf;border-radius:50%;background:#2c3b2c;object-fit:cover}
.gh3-foes img:first-child{margin-left:0}
.gh3-trialinfo{flex:1;min-width:0}
.gh3-dots{display:flex;align-items:center;gap:5px;margin-top:4px}
.gh3-dot{width:11px;height:11px;border-radius:50%;border:2px solid #8a6a34;background:transparent}
.gh3-dot.on{background:#e8842c;border-color:#e8842c}
.gh3-rules{margin:8px 0;line-height:1.7}
.gh3-note{margin-top:8px;text-align:center}
/* ==== 主城 v3：取景放大 + 角色放大 ==== */
.city-bg{transform:scale(1.26);transform-origin:50% 52%}
.hs-guild{left:calc(50% - 50px);top:50%}
.hs-tavern{left:3%;top:47%}
.hs-smith{right:2%;top:46%}
.hs-board{left:2%;top:60%}
.dock{top:57%}
.party img.f{height:80px}
.party img.b{height:68px}
.party{bottom:148px}
.party img{margin:0 -6px}
@media (max-height:640px){
 .hs-guild{top:47%}
 .hs-tavern{top:44%}
 .hs-smith{top:44%}
 .hs-board{top:54%}
 .dock{top:54%}
 .party img.f{height:64px}
 .party img.b{height:54px}
 .party{bottom:132px}
}
@media (max-width:360px){
 .gh3-boss{width:128px}
 .gh3-arch{width:88px;height:106px}
 .gh3-arch img{width:74px;height:74px}
 .gh3-counter,.gh3-board{width:86px}
 .gh3-counterbox,.gh3-boardbox{width:78px}
 .gh3-pin{width:22px}
 .gh3-pin.p1{left:4px}
 .gh3-pin.p2{left:28px}
 .gh3-pin.p3{left:50px}
 .gh3-mug{left:12px}
 .gh3-mug.m2{left:38px}
 .gh3-coins{right:4px}
 .gh3-plate{font-size:11px;padding:4px 6px}
}
"""
s = s.replace(anchor, css + anchor)

io.open(SRC, 'w', encoding='utf-8').write(s)
print('patched OK, bytes=', len(s.encode('utf-8')))
print('city3:', "APP_VERSION='2026.11.02-city3'" in s, '| gh3:', s.count('gh3-'), '| vGuild new:', 'gh3-scene' in s, '| old gh-scene markup gone:', 'gh-scene">' not in s)

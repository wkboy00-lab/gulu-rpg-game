#!/usr/bin/env python3
"""Build battle-team v1 (2026.11.03-team1) from the city5 base file."""
import hashlib, sys

BASE = 'index-city5-base.html'
OUT = 'index.html'
BASE_MD5 = 'a091ba48d17f95afa6843dfb832d1517'
L = '\u3010'
R = '\u3011'

src = open(BASE, encoding='utf-8').read()
assert hashlib.md5(src.encode('utf-8')).hexdigest() == BASE_MD5, 'base MD5 mismatch'

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'anchor count %d != %d: %r' % (n, count, old[:80])
    src = src.replace(old, new)

def cut(start_marker, end_marker):
    global src
    a = src.find(start_marker)
    assert a >= 0, 'cut start not found: %r' % start_marker[:60]
    b = src.find(end_marker, a)
    assert b > a, 'cut end not found: %r' % end_marker[:60]
    src = src[:a] + src[b:]

rep("const APP_VERSION='2026.11.03-city5'; // \u516c\u4f1a\u5927\u5385 v3\uff1b\u8bbe\u7f6e\u9875\u53ef\u67e5\uff0c\u6539\u52a8\u540e\u987b\u540c\u6b65\u66f4\u65b0",
    "const APP_VERSION='2026.11.03-team1'; // \u4e94\u4eba\u6218\u6597 v1\uff1b\u8bbe\u7f6e\u9875\u53ef\u67e5\uff0c\u6539\u52a8\u540e\u987b\u540c\u6b65\u66f4\u65b0")
rep("\uff08\u4e3b\u57ce v4 \u00b7 \u516c\u4f1a\u5927\u5385 v5\uff09",
    "\uff08\u4e3b\u57ce v4 \u00b7 \u516c\u4f1a\u5927\u5385 v5 \u00b7 \u4e94\u4eba\u6218\u6597 v1\uff09")

rep("/* base=[\u751f\u547d,\u653b\u51fb,\u62a4\u7532,\u9b54\u6297,\u901f\u5ea6,\u666e\u653b\u95f4\u9694\u79d2]\uff1bactive/ult \u6570\u503c\u5728\u672c\u539f\u578b\u6218\u6597\u5f15\u64ce\u5185\u7b80\u5316\u5b9e\u73b0\uff0c\u63cf\u8ff0\u89c1\u82f1\u96c4\u8be6\u60c5 */",
    "/* base=[\u751f\u547d,\u653b\u51fb,\u62a4\u7532,\u9b54\u6297,\u901f\u5ea6,\u666e\u653b\u95f4\u9694\u79d2]\uff1bactive \u6570\u503c\u5728\u6218\u6597\u5f15\u64ce\u5185\u7b80\u5316\u5b9e\u73b0\uff0c\u63cf\u8ff0\u89c1\u82f1\u96c4\u8be6\u60c5\uff1bult \u5b57\u6bb5\u4ec5\u4fdd\u7559\u539f\u59cb\u8d44\u6599\uff0c\u6218\u6597\u4e0e\u754c\u9762\u4e0d\u518d\u8bfb\u53d6 */")

rep("/* ===== \u6218\u6597\u5f15\u64ce\uff08\u7b80\u5316\u786e\u5b9a\u6027\u5f15\u64ce\uff1a\u666e\u653b + \u4e3b\u52a8\u51b7\u5374 + \u80fd\u91cf\u5927\u62db + \u88ab\u52a8\u7b80\u5316\uff1b\u4ec5\u672c\u539f\u578b\uff09 ===== */",
    "/* ===== \u6218\u6597\u5f15\u64ce\uff08\u786e\u5b9a\u6027\u5f15\u64ce\uff1a\u666e\u653b + \u4e3b\u52a8\u51b7\u5374 + \u88ab\u52a8\uff1b\u547d\u4e2d\u5e27\u7ed3\u7b97\uff1b\u4ec5\u4fdd\u7559\u4e09\u79cd\u6280\u80fd\uff09 ===== */")

rep("energy:0,cd:0,", "cd:0,passiveFlashUntil:0,")
rep(",acd:H.acd*1000,active:H.active,ult:H.ult,energy:H.id==='dengyu'?5:0});",
    ",acd:H.acd*1000,active:H.active});")

rep(" if(att&&att.side===0&&att.hid==='qiren'&&!tgt.alive&&!att.passiveUsed){att.energy=Math.min(100,att.energy+15);att.passiveUsed=true;setTimeout(()=>{if(att)att.passiveUsed=false;},3000);}\n", "")
rep("if(opts.burn){tgt.burn=Math.min(3,(tgt.burn||0)+1);tgt.burnUntil=BT.t+4000;if(att&&att.hid==='baoli')att.energy=Math.min(100,att.energy+2);}",
    "if(opts.burn){tgt.burn=Math.min(3,(tgt.burn||0)+1);tgt.burnUntil=BT.t+4000;}")
rep("if(att)att.energy=Math.min(100,(att.energy||0)+4);tgt.energy=Math.min(100,(tgt.energy||0)+3);", "")

rep("case 'dengyu':allies.filter(a=>a!==u).sort((a,b)=>a.energy-b.energy).slice(0,2).forEach(a=>a.energy=Math.min(100,a.energy+12));log(u.name+' \u9884\u8a00\uff1a\u4e24\u540d\u961f\u53cb +12 \u80fd\u91cf');break;",
    "case 'dengyu':log(u.name+' \u4f7f\u7528" + L + "\u4eca\u665a\u7684\u9884\u8a00" + R + "\uff08\u539f\u6548\u679c\u4f9d\u8d56\u5df2\u79fb\u9664\u7684\u673a\u5236\uff0c\u672c\u8f6e\u672a\u5b9e\u73b0\uff09');break;")

rep("case 'taidun':foes.forEach(f=>{f.tauntUntil=BT.t+2000;f.tauntBy=u;});addShield(u,u.maxHp*0.12,5000);log(u.name+' \u4f7f\u7528" + L + "\u770b\u8fd9\u91cc" + R + "\uff1a\u5632\u8bbd 2 \u79d2\uff0c\u62a4\u76fe +'+Math.round(u.maxHp*0.12));break;",
    "case 'taidun':u.actAnim={kind:'active-td',start:BT.t,hitAt:BT.t+460};BT.pending.push({hitAt:BT.t+460,run:function(){if(!u.alive||!BT)return;foes.forEach(function(f){if(f.alive){f.tauntUntil=BT.t+2000;f.tauntBy=u;}});addShield(u,u.maxHp*0.12,5000);u.passiveFlashUntil=BT.t+600;log(u.name+' \u76fe\u724c\u524d\u9876\uff1a\u5632\u8bbd 2 \u79d2\uff0c\u62a4\u76fe +'+Math.round(u.maxHp*0.12));}});log(u.name+' \u4f7f\u7528" + L + "\u770b\u8fd9\u91cc" + R + "');break;")

cut("function doUlt(u){", "function enemyAct(u){")

cut("function enemyAct(u){", "function stepBattle(dt){")
new_enemy = ("function enemyAct(u){const t=pickTarget(u);if(!t)return;scheduleStrike(u,t,1,false,{onHit:function(tgt,d){\n"
" if(u.kind==='healer'){const a=lowestAlly(1);if(a&&a.hp/a.maxHp<0.8){heal(u,a,u.atk*0.8);log(u.name+' \u6cbb\u7597 '+a.name);}}\n"
" if(u.kind==='burner'){tgt.burn=Math.min(3,(tgt.burn||0)+1);tgt.burnUntil=BT.t+4000;}\n"
" if(u.kind==='slow'){tgt.slowUntil=BT.t+3000;}\n"
" if(u.kind==='shieldbot'){addShield(u,u.maxHp*0.1,5000);}\n"
" if(u.kind==='taunt'){BT.units.filter(function(x){return x.side===0&&x.alive;}).forEach(function(a){a.tauntUntil=BT.t+1500;a.tauntBy=u;});}\n"
"}});}\nfunction stepBattle(dt){")
src = src.replace("function stepBattle(dt){", new_enemy, 1)

rep("function stepBattle(dt){BT.t+=dt;const units=BT.units;",
    "function stepBattle(dt){BT.t+=dt;const units=BT.units;\n processPending();")
rep("units.forEach(u=>{if(!u.alive||u.stunUntil>BT.t)return;if(u.side===0&&u.energy>=100){doUlt(u);return;}if(u.side===0&&u.cd<=0){const before=u.hp;doActive(u);u.cd=(u.acd||8000);}BT.t+=0;});",
    "units.forEach(u=>{if(!u.alive||u.stunUntil>BT.t)return;if(u.side===0&&u.cd<=0){doActive(u);u.cd=(u.acd||8000);}});")

rep("const r=applyDamage(u,t,m,u.role==='\u6cd5\u5e08'||u.role==='\u6cbb\u7597');log(u.name+' \u666e\u653b '+t.name+' '+r);",
    "scheduleStrike(u,t,m,u.role==='\u6cd5\u5e08'||u.role==='\u6cbb\u7597');")
rep("if(u.hid==='taidun'&&!u.passiveUsed&&u.hp/u.maxHp<0.35){u.passiveUsed=true;heal(u,u,u.maxHp*0.10);log(u.name+' 被动" + L + "虽然害怕" + R + "：恢复 10% 生命（本场一次）');}", "")
rep("function hurt(tgt,amount,att){if(amount<=0)return;tgt.hp=Math.max(0,tgt.hp-amount);if(typeof BT!=='undefined'&&BT)BT.lastHit={u:tgt,t:BT.t};if(tgt.hp<=0&&tgt.alive){tgt.alive=false;log(tgt.name+' 倒下了');}}",
    "function hurt(tgt,amount,att){if(amount<=0)return;tgt.hp=Math.max(0,tgt.hp-amount);if(typeof BT!=='undefined'&&BT)BT.lastHit={u:tgt,t:BT.t};if(tgt.hid==='taidun'&&!tgt.passiveUsed&&tgt.hp<Math.floor(tgt.maxHp*0.35)){tgt.passiveUsed=true;const pv=Math.floor(tgt.maxHp*0.10);tgt.hp=Math.min(tgt.maxHp,tgt.hp+pv);if(typeof BT!=='undefined'&&BT)tgt.passiveFlashUntil=BT.t+600;log(tgt.name+' 被动" + L + "虽然害怕" + R + "：恢复 '+pv+' 生命（本场一次）');}if(tgt.hp<=0&&tgt.alive){tgt.alive=false;log(tgt.name+' 倒下了');}}")

rep("return '<div class=\"fig '+side+(u.eid==='BOSS'?' big':'')+(u.pos>=2?' back':'')+'\" data-i=\"'+i+'\"><div class=\"figimg\">'+figIcon(u)+'</div>",
    "return '<div class=\"fig '+side+(u.eid==='BOSS'?' big':'')+(u.pos>=2?' back':'')+'\" data-i=\"'+i+'\"><div class=\"figimg\">'+((u.side===0&&u.hid==='taidun')?taidunFigHtml():figIcon(u))+'</div>")
rep('<div class="figbars"><div class="bar hp"><i></i></div>\'+(u.side===0?\'<div class="bar en"><i></i></div>\':\'\')+\'<div class="figmeta"></div></div></div>\';',
    '<div class="figbars"><div class="bar hp"><i></i></div><div class="figmeta"></div></div></div>\';')

rep("    const enBar=fig.querySelector('.bar.en>i');if(enBar)enBar.style.width=u.energy+'%';\n", "")
rep("if(meta)meta.innerHTML=fmt(Math.max(0,u.hp))+'/'+fmt(u.maxHp)+(u.shield>0?' \U0001F6E1\ufe0f'+fmt(u.shield):'')+(u.side===0?' \u00b7 \u80fd\u91cf '+Math.floor(u.energy)+' \u00b7 \u4e3b\u52a8 '+(u.cd>0?Math.ceil(u.cd/1000)+'s':'\u5c31\u7eea'):'')+statusTags(u);",
    "if(meta)meta.innerHTML=fmt(Math.max(0,u.hp))+'/'+fmt(u.maxHp)+(u.shield>0?' \U0001F6E1\ufe0f'+fmt(u.shield):'')+(u.side===0?' \u00b7 \u4e3b\u52a8 '+(u.cd>0?Math.ceil(u.cd/1000)+'s':'\u5c31\u7eea'):'')+statusTags(u);")
rep("if(BT.logs.length!==stageLogN){stageLogN=BT.logs.length;const blog=document.getElementById('blog');if(blog){blog.textContent=BT.logs.join('\\n');blog.scrollTop=blog.scrollHeight;}}",
    "const _lg=BT.logs.join('\\n');if(_lg!==stageLogN){stageLogN=_lg;const blog=document.getElementById('blog');if(blog){blog.textContent=_lg;blog.scrollTop=blog.scrollHeight;}}")
rep("    if(prev!==undefined&&u.hp<prev)spawnFloater(fig,'-'+(prev-u.hp),'');",
    "    if(prev!==undefined&&u.hp<prev)spawnFloater(fig,'-'+(prev-u.hp),'');\n    if(prev!==undefined&&u.hp>prev)spawnFloater(fig,'+'+(u.hp-prev),'heal');")
rep("    if(!u.alive)cls+=' dead';\n    else{\n      if(BT.lastHit&&BT.lastHit.u===u&&BT.t-BT.lastHit.t<600)cls+=' hit';\n      if(BT.lastAct&&BT.lastAct.u===u&&BT.t-BT.lastAct.t<500)cls+=' atk';\n    }",
    "    if(!u.alive)cls+=' dead';\n    else if(!(u.side===0&&u.hid==='taidun')){\n      if(BT.lastHit&&BT.lastHit.u===u&&BT.t-BT.lastHit.t<600)cls+=' hit';\n      if(BT.lastAct&&BT.lastAct.u===u&&BT.t-BT.lastAct.t<500)cls+=' atk';\n    }\n    updateTaidunPose(fig,u);")
rep("  const sb=document.getElementById('skillbanner');",
    "  const stg=document.getElementById('bstage');if(stg)stg.classList.toggle('paused',!!BT.paused);\n  const sb=document.getElementById('skillbanner');")
rep("if(bm)bm.textContent='MT \u5f0f\u6a21\u5f0f\uff1a\u81ea\u52a8\u6218\u6597 \u00b7 \u80fd\u91cf\u6ee1\u81ea\u52a8\u653e\u5927\u62db \u00b7 '+(BT.t/1000).toFixed(1)+'s / \u4e0a\u9650 '+(BT.limit/1000)+'s \u00b7 '+BT.speed+'\u00d7';",
    "if(bm)bm.textContent='\u81ea\u52a8\u6218\u6597 \u00b7 \u53ea\u4fdd\u7559\u666e\u653b / \u4e3b\u52a8 / \u88ab\u52a8 \u00b7 '+(BT.t/1000).toFixed(1)+'s / \u4e0a\u9650 '+(BT.limit/1000)+'s \u00b7 '+BT.speed+'\u00d7';")

rep("function startBattle(cfg){const allies=buildAllies();const foes=buildFoes(cfg.specs);BT={title:cfg.title,units:allies.concat(foes),t:0,logs:[],speed:1,paused:false,over:false,limit:cfg.limit||90000,mode:cfg.mode||'normal',onEnd:cfg.onEnd};",
    "function startBattle(cfg){if(BT){try{clearInterval(BT.timer);}catch(e){}}const allies=buildAllies();const foes=buildFoes(cfg.specs);BT={title:cfg.title,units:allies.concat(foes),t:0,logs:[],pending:[],speed:1,paused:false,over:false,limit:cfg.limit||90000,mode:cfg.mode||'normal',onEnd:cfg.onEnd};")
rep("BT={title:'\u7ade\u6280\u573a \u00b7 \u6a21\u62df\u5bf9\u6218',units:allies.concat(foes),t:0,logs:[],speed:1,paused:false,over:false,limit:90000,mode:'arena',onEnd:null};",
    "BT={title:'\u7ade\u6280\u573a \u00b7 \u6a21\u62df\u5bf9\u6218',units:allies.concat(foes),t:0,logs:[],pending:[],speed:1,paused:false,over:false,limit:90000,mode:'arena',onEnd:null};")

cut("function afterBattleWin(reward,starsEarned,stageIdx){", "function startStage(g){")
src = src.replace("function startStage(g){",
"function afterBattleWin(reward,starsEarned,stageIdx){const ok=commit(function(){addRes(reward);if(typeof stageIdx==='number'){S.stages[stageIdx]=Math.max(S.stages[stageIdx]||0,starsEarned);}S.daily.counters.battles++;if(Math.random()<0.3)S.equips.push(newEquip());});render();return ok!==false;}\nfunction startStage(g){", 1)

rep("function startStage(g){const rw=stageReward(g);startBattle({title:'\u63a8\u56fe '+(Math.floor(g/10)+1)+'-'+(g%10+1)+' \u00b7 '+STAGE_NAMES[g],specs:stageEnemies(g),onEnd:(win,result,dmg,aliveCount)=>{if(!win){render();return;}const st=aliveCount>=5?3:aliveCount>=4?2:1;afterBattleWin(rw,st,g);toast('\u80dc\u5229\uff01'+st+' \u661f\u901a\u5173\uff0c\u5956\u52b1\uff1a\u91d1\u5e01 +'+rw.gold+'\uff0c\u7ecf\u9a8c +'+rw.exp+(rw.book?'\uff0c\u6280\u80fd\u4e66 +'+rw.book:'')+(rw.dia?'\uff0c\u94bb\u77f3 +'+rw.dia:'')+(rw.ticket?'\uff0c\u62db\u52df\u5238 +'+rw.ticket:'')+(st<3?'\uff08\u5b58\u6d3b '+aliveCount+'/5 \u4eba\uff0c\u672a\u6ee1\u661f\u53ef\u91cd\u6253\uff09':''));}});}",
    "function startStage(g){const rw=stageReward(g);let settled=false;startBattle({title:'\u63a8\u56fe '+(Math.floor(g/10)+1)+'-'+(g%10+1)+' \u00b7 '+STAGE_NAMES[g],specs:stageEnemies(g),onEnd:(win,result,dmg,aliveCount)=>{if(settled)return;settled=true;if(!win){showStageResult({win:false,stageIdx:g});return;}const st=aliveCount>=5?3:aliveCount>=4?2:1;const saved=afterBattleWin(rw,st,g);showStageResult({win:true,stars:st,reward:rw,stageIdx:g,alive:aliveCount,saved:saved});}});}")


# ---- read-only debug hook (verification only, no gameplay effect) ----
rep("/* ===== \u542f\u52a8\uff1a\u652f\u6301 #view",
    "window.TEAM1_DEBUG={version:APP_VERSION,getState:function(){if(!BT)return null;return {t:BT.t,paused:BT.paused,speed:BT.speed,over:BT.over,pending:(BT.pending||[]).length,units:BT.units.map(function(u){return {hid:u.hid||u.eid,hp:u.hp,maxHp:u.maxHp,shield:u.shield,alive:u.alive,cd:u.cd,anim:u.actAnim?u.actAnim.kind:null};})};}};\n/* ===== \u542f\u52a8\uff1a\u652f\u6301 #view", 1)

rep("function spawnFloater(fig,txt,cls){",
    "let floaterN=0;\nfunction spawnFloater(fig,txt,cls){")
rep("d.style.left=(fig.offsetLeft+fig.offsetWidth*0.5-14+Math.random()*12-6)+'px';",
    "d.style.left=(fig.offsetLeft+fig.offsetWidth*0.5-14+((floaterN++%5)-2)*4)+'px';")

rep("</head>", '<link rel="icon" href="data:,">\n</head>')
frag = open('team1-fragment.js', encoding='utf-8').read()
assert 'function log(m){' in src
src = src.replace("function log(m){", frag + "\nfunction log(m){", 1)

css = open('team1-css.css', encoding='utf-8').read()
idx = src.rfind('</style>')
assert idx > 0
src = src[:idx] + css + '\n' + src[idx:]

for bad in ['\u5927\u62db', '\u80fd\u91cf', 'doUlt', 'bar en', 'u.energy', '.energy', 'energy:']:
    assert bad not in src, 'leftover marker: %r' % bad
assert "APP_VERSION='2026.11.03-team1'" in src
assert 'taidunFigHtml' in src and 'showStageResult' in src and 'processPending' in src
assert 'gh5-' in src and 'gulu-mtstyle-v1' in src, 'city5 content lost'

open(OUT, 'w', encoding='utf-8').write(src)
print('built', OUT, len(src), 'bytes, md5', hashlib.md5(src.encode('utf-8')).hexdigest())

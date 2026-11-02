#!/usr/bin/env python3
"""city4 core patch: save reliability, settings/backup UI, sheet guard,
trial wording, tap sizes, press feedback, reduce-motion.
Input must be city3. Does NOT bump version (scene script does)."""
import re, sys, subprocess, os

P = '/home/hatch/workspace/gulu-mtstyle-preview/index.html'
html = open(P, encoding='utf-8').read()

def must(cond, msg):
    if not cond:
        print('ASSERT FAIL:', msg); sys.exit(1)

must("APP_VERSION='2026.11.02-city3'" in html, 'not city3')
must("function save(){try{localStorage.setItem(SAVE_KEY,JSON.stringify(S));}catch(e){}}" in html,
     'old save() not found')

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

def replace_fn(src, name, new, *needles):
    i, k = fn_span(src, name)
    old = src[i:k]
    for n in needles:
        must(n in old, 'function %s missing expected text: %s' % (name, n))
    return src[:i] + new + src[k:]

# ---- 1. SAVE_KEY resolution + save helpers (replace the const line) ----
old_key = "const SAVE_KEY='gulu-mtstyle-v1';"
must(html.count(old_key) == 1, 'SAVE_KEY line count != 1')
new_key = """const SAVE_KEY=(function(){try{const q=new URLSearchParams(location.search).get('savekey');if(q&&/^[A-Za-z0-9][A-Za-z0-9._-]{0,60}$/.test(q))return q;}catch(e){}return 'gulu-mtstyle-v1';})();
let corruptInfo=null,corruptHold=false,saveErr=null;
function backupKey(kind){return SAVE_KEY+'.'+kind+'.'+Date.now();}
function keepPrevGood(oldRaw){if(!oldRaw)return;try{localStorage.setItem(SAVE_KEY+'.prevgood',oldRaw);}catch(e){}}
function updateSaveBadge(){const tb=document.getElementById('topbar');if(!tb)return;const bad=!!(saveErr||corruptHold);let b=document.getElementById('saveBadge');if(bad&&!b){b=document.createElement('button');b.id='saveBadge';b.className='savebadge';b.textContent=corruptHold?'存档待处理':'保存失败';b.onclick=function(){go('settings');};tb.appendChild(b);}else if(!bad&&b){b.remove();}}
function validateSave(s){const ids=(typeof HEROES!=='undefined'?Object.keys(HEROES):[]);return !!(s&&typeof s==='object'&&s.res&&typeof s.res==='object'&&Array.isArray(s.formation)&&s.formation.length>0&&s.formation.every(function(id){return ids.indexOf(id)>=0;})&&s.heroes&&typeof s.heroes==='object');}
function mergeSave(s){const d=defaultState();return Object.assign(d,s,{res:Object.assign(d.res,s.res||{}),daily:Object.assign(d.daily,s.daily||{}),arena:Object.assign(d.arena,s.arena||{}),dungeon:Object.assign(d.dungeon,s.dungeon||{}),idle:Object.assign(d.idle,s.idle||{}),guild:Object.assign(d.guild,s.guild||{}),settings:Object.assign({},d.settings||{},s.settings||{})});}
function corruptFallback(raw,reason){try{localStorage.setItem(backupKey('corrupt'),raw);}catch(e){}corruptInfo={reason:reason,at:Date.now(),len:raw?raw.length:0};corruptHold=true;return defaultState();}
function downloadText(name,text){const b=new Blob([text],{type:'application/json'});const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download=name;document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(u);a.remove();},500);}
function exportSave(){try{downloadText('gulu-save-'+SAVE_KEY+'-'+new Date().toISOString().slice(0,10)+'.json',JSON.stringify({app:'gulu-mtstyle',version:APP_VERSION,key:SAVE_KEY,exportedAt:new Date().toISOString(),state:S},null,1));toast('存档备份已导出');}catch(e){toast('导出失败：'+e.message);}}
function exportCorrupt(){let raw=null;try{raw=localStorage.getItem(SAVE_KEY);}catch(e){}if(!raw){toast('没有可导出的存档数据');return;}downloadText('gulu-save-corrupt-'+Date.now()+'.txt',raw);toast('损坏存档原文已导出');}
function recoverPrevGood(){let raw=null;try{raw=localStorage.getItem(SAVE_KEY+'.prevgood');}catch(e){}if(!raw){toast('没有上一次成功保存的备份');return;}let s;try{s=JSON.parse(raw);}catch(e){toast('备份也无法解析，请先导出损坏存档');return;}if(!validateSave(s)){toast('备份结构校验失败');return;}try{const cur=localStorage.getItem(SAVE_KEY);if(cur!==null)localStorage.setItem(backupKey('preimport'),cur);}catch(e){}S=mergeSave(s);corruptHold=false;corruptInfo=null;if(save()){render();toast('已从上一次成功保存恢复');}}
function discardCorrupt(){let raw=null;try{raw=localStorage.getItem(SAVE_KEY);}catch(e){}try{if(raw)localStorage.setItem(backupKey('corrupt'),raw);}catch(e){}corruptHold=false;corruptInfo=null;S=defaultState();if(save()){render();toast('已放弃损坏存档，开始新进度（旧档原文已另外备份）');}}
function importSaveFile(file){const rd=new FileReader();rd.onload=function(){let obj;try{obj=JSON.parse(rd.result);}catch(e){toast('导入失败：文件不是有效的 JSON');return;}const st=obj&&obj.state?obj.state:obj;if(!validateSave(st)){toast('导入失败：存档结构校验不通过，未做任何改动');return;}let cur=null;try{cur=localStorage.getItem(SAVE_KEY);}catch(e){}try{if(cur!==null)localStorage.setItem(backupKey('preimport'),cur);}catch(e){}S=mergeSave(st);corruptHold=false;corruptInfo=null;if(save()){render();toast('存档已导入（导入前已备份）');}else{toast('导入后保存失败，请导出备份');}};rd.readAsText(file);}
function applyReduceMotion(){try{document.body.classList.toggle('reduce-motion',!!(S.settings&&S.settings.reduceMotion));}catch(e){}}
function toggleReduceMotion(on){S.settings=S.settings||{};S.settings.reduceMotion=!!on;save();applyReduceMotion();render();}
function handleImportFile(input){if(input.files[0])importSaveFile(input.files[0]);input.value='';}
function discardCorruptAsk(){if(confirm('确定放弃损坏存档并开始新进度吗？旧档原文已另外备份。'))discardCorrupt();}"""
html = html.replace(old_key, new_key, 1)

# ---- 2. load() / save() ----
new_load = """function load(){let raw=null;try{raw=localStorage.getItem(SAVE_KEY);}catch(e){raw=null;}if(!raw)return defaultState();let s;try{s=JSON.parse(raw);}catch(e){return corruptFallback(raw,'存档无法解析');}if(!validateSave(s))return corruptFallback(raw,'存档结构校验失败');return mergeSave(s);}"""
html = replace_fn(html, 'load', new_load, 'JSON.parse(r)', 'Object.assign(d,s')
new_save = """function save(){if(corruptHold){toast('检测到损坏的存档，请先在设置中处理，暂不覆盖旧档');return false;}let oldRaw=null;try{oldRaw=localStorage.getItem(SAVE_KEY);}catch(e){}try{localStorage.setItem(SAVE_KEY,JSON.stringify(S));saveErr=null;keepPrevGood(oldRaw);updateSaveBadge();return true;}catch(e){saveErr={msg:String((e&&e.message)||e),at:Date.now()};updateSaveBadge();toast('保存失败：进度保留在内存中，请先在设置里导出备份');return false;}}
function commit(mut){const snap=JSON.stringify(S);let ok;try{ok=mut();}catch(e){try{S=JSON.parse(snap);}catch(_){}throw e;}if(ok===false)return false;if(!save()){try{S=JSON.parse(snap);}catch(_){}if(typeof render==='function')render();toast('保存失败，本次操作已撤销，资源与次数未变');return false;}return true;}
function lockOnce(key,ms){const now=Date.now();window.__locks=window.__locks||{};if(window.__locks[key]&&now-window.__locks[key]<(ms||400))return false;window.__locks[key]=now;return true;}"""
html = replace_fn(html, 'save', new_save, 'localStorage.setItem(SAVE_KEY')

# ---- 3. defaultState: settings field ----
old_ds = "guild:{bossDmg:0,day:'',trial:0,trialDay:''},view:'home'"
must(html.count(old_ds) == 1, 'defaultState anchor')
html = html.replace(old_ds, "guild:{bossDmg:0,day:'',trial:0,trialDay:''},settings:{reduceMotion:false},view:'home'", 1)

# ---- 4. money flows wrapped in commit() ----
html = replace_fn(html, 'claimIdle', """function claimIdle(){if(window.__idleClaiming)return;window.__idleClaiming=true;setTimeout(function(){window.__idleClaiming=false;},500);const p=idlePending();if(p.gold<1&&p.exp<1){toast('挂机收益还太少，再等一会儿');return;}const tot=S.idle.equipMin+p.mins;const n=Math.floor(tot/60);const ok=commit(function(){S.res.gold+=p.gold;S.res.exp+=p.exp;S.idle.fracG=p.fracG;S.idle.fracE=p.fracE;S.idle.equipMin=tot-n*60;S.idle.pendMin=0;S.idle.lastCalc=Date.now();for(let i=0;i<n;i++)S.equips.push(newEquip());S.daily.counters.idle++;render();});if(ok)toast('领取挂机收益：金币 +'+p.gold+'，经验 +'+p.exp+(n?'，装备 +'+n+' 件':''));}""",
    'idlePending()', 'S.idle.pendMin=0')
html = replace_fn(html, 'confirmChestClaim', """function confirmChestClaim(){
  if(chestClaiming||!chestSnap)return;
  const snap=chestSnap;if(snap.gold<1&&snap.exp<1)return;
  chestClaiming=true;const btn=document.getElementById('chestClaimBtn');if(btn)btn.disabled=true;
  const tot=(S.idle.equipMin||0)+snap.mins;const n=Math.floor(tot/60);
  const ok=commit(function(){S.res.gold+=snap.gold;S.res.exp+=snap.exp;S.idle.fracG=snap.fracG;S.idle.fracE=snap.fracE;S.idle.equipMin=tot-n*60;S.idle.pendMin=0;S.idle.lastCalc=Date.now();for(let i=0;i<n;i++)S.equips.push(newEquip());S.daily.counters.idle++;render();});
  chestClaiming=false;
  if(ok){chestSnap=null;openSheet(chestSheetHtml('claimed',{gold:snap.gold,exp:snap.exp,equip:n}),'chest');toast('挂机收益已到账');}
  else{openSheet(chestSheetHtml('ready'),'chest');}
}""", 'chestClaiming', 'chestSheetHtml')
html = replace_fn(html, 'guildShop', """function guildShop(cost,kind){if(!lockOnce('shop',400))return;if(S.res.gcoin<cost){toast('公会币不足');return;}commit(function(){S.res.gcoin-=cost;if(kind===1)S.res.ticket+=1;else if(kind===2)S.res.stone+=2;else{const id=HERO_IDS[Math.floor(Math.random()*HERO_IDS.length)];S.frags[id]=(S.frags[id]||0)+10;}render();});}""",
    'gcoin', 'save();render();')
html = replace_fn(html, 'claimQuest', """function claimQuest(id,rew){if(!lockOnce('quest'+id,400))return;if(S.daily.claimed[id])return;const ok=commit(function(){S.daily.claimed[id]=true;addRes(rew);render();});if(ok){toast('任务奖励已领取');if(sheetKind==='tasks')openTasks();}}""",
    'claimed[id]', 'addRes(rew)')
html = replace_fn(html, 'doSignin', """function doSignin(){if(!lockOnce('signin',400))return;if(S.signin.last===todayStr())return;const rewards=[{gold:300},{dia:30},{ticket:1},{book:2},{exp:500},{stone:2},{ticket:2,dia:50}];const rew=rewards[S.signin.days%7];const ok=commit(function(){addRes(rew);S.signin.days++;S.signin.last=todayStr();render();});if(ok){toast('签到成功');if(sheetKind==='signin')openSignin();}}""",
    'todayStr()', 'S.signin.days++')
html = replace_fn(html, 'doSummon', """function doSummon(n,pay){const costT=n===10?10:1,costD=n===10?2700:300;if(pay==='ticket'&&S.res.ticket<costT){toast('招募券不足');return;}if(pay==='dia'&&S.res.dia<costD){toast('钻石不足');return;}let res=[];const ok=commit(function(){if(pay==='ticket')S.res.ticket-=costT;else S.res.dia-=costD;res=[];for(let i=0;i<n;i++){const id=rollOne();if(!S.heroes[id]){S.heroes[id]={lv:1,star:1,awaken:0,sk:{active:1,ult:1,passive:1},spent:{gold:0,exp:0,book:0}};res.push({id,isNew:true});}else{S.frags[id]=(S.frags[id]||0)+FRAG_BY_RAR[HEROES[id].rar];res.push({id,isNew:false});}}S.daily.counters.summons+=n;render();});if(!ok)return;const el=document.getElementById('sumres');if(el)el.innerHTML=res.map(r=>'<div class="card rar-'+HEROES[r.id].rar+'">'+iconSvg('hero',r.id,64)+'<b>'+HEROES[r.id].name+'</b><div>'+HEROES[r.id].rar+' · '+HEROES[r.id].fac+'</div><div class="mut">'+(r.isNew?'新伙伴！':'重复 → 碎片 +'+FRAG_BY_RAR[HEROES[r.id].rar])+'</div></div>').join('');}""",
    'rollOne()', 'sumres')
html = replace_fn(html, 'skillUp', """function skillUp(id){const h=S.heroes[id];if(S.res.book<2){toast('技能书不足');return;}commit(function(){S.res.book-=2;h.spent.book+=2;h.sk.active=Math.min(5,h.sk.active+1);h.sk.passive=Math.min(5,h.sk.passive+1);render();});}""",
    'sk.active', 'save();render();')
html = replace_fn(html, 'starUp', """function starUp(id){const h=S.heroes[id];if(h.star>=5)return;if((S.frags[id]||0)<STAR_FRAG[h.star]||S.res.gold<STAR_GOLD[h.star]){toast('碎片或金币不足');return;}const ok=commit(function(){S.frags[id]-=STAR_FRAG[h.star];S.res.gold-=STAR_GOLD[h.star];h.star++;render();});if(ok)toast(HEROES[id].name+' 升至 '+h.star+' 星！');}""",
    'STAR_FRAG', 'save();render();')
html = replace_fn(html, 'levelUp', """function levelUp(id,times){const h=S.heroes[id];if(!h)return;const plan=[];let g=S.res.gold,e=S.res.exp,lv=h.lv;for(let i=0;i<times;i++){const c=upCost(lv);if(g<c.gold||e<c.exp)break;g-=c.gold;e-=c.exp;plan.push(c);lv++;}if(!plan.length){toast('金币或经验不足');return;}commit(function(){plan.forEach(function(c){S.res.gold-=c.gold;S.res.exp-=c.exp;h.spent.gold+=c.gold;h.spent.exp+=c.exp;h.lv++;});S.daily.counters.upgrades+=plan.length;render();});}""",
    'upCost', 'save();render();')
html = replace_fn(html, 'resetAll', """function resetAll(){if(!confirm('确定清空本原型（'+SAVE_KEY+'）的全部进度吗？原游戏存档不受影响。'))return;try{const keys=[];for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k===SAVE_KEY||k.indexOf(SAVE_KEY+'.')===0)keys.push(k);}keys.forEach(function(k){localStorage.removeItem(k);});}catch(e){}corruptHold=false;corruptInfo=null;saveErr=null;S=defaultState();save();render();}""",
    'removeItem(SAVE_KEY)')

# ---- 5. openSheet dedupe guard ----
html = replace_fn(html, 'openSheet', """let sheetLockAt=0;
function openSheet(html,kind){const now=Date.now();if(sheetKind===kind&&now-sheetLockAt<300)return;sheetLockAt=now;sheetKind=kind||'';const sh=document.getElementById('sheet');sh.innerHTML='<div class="sheet-card" onclick="event.stopPropagation()"><div style="text-align:right"><button class="btn sm ghost" onclick="closeSheet()">✕ 关闭</button></div>'+html+'</div>';sh.classList.add('show');}""",
    'sheet-card', "classList.add('show')")

# ---- 6. trial wording: 今日 -> 剩余 ----
old1 = "今日剩余 '+(2-trialUsed)+'/2 次"
old2 = "今日 '+(2-trialUsed)+'/2 次"
must(html.count(old1) == 1, 'trial wording 1')
must(html.count(old2) == 1, 'trial wording 2')
html = html.replace(old1, "剩余 '+(2-trialUsed)+'/2 次", 1)
html = html.replace(old2, "剩余 '+(2-trialUsed)+'/2 次", 1)

# ---- 7. vSettings: dynamic key + backup panel ----
must('键为 <b>gulu-mtstyle-v1</b>' in html, 'settings notice anchor')
html = html.replace('键为 <b>gulu-mtstyle-v1</b>', "键为 <b>'+SAVE_KEY+'</b>'+(SAVE_KEY==='gulu-mtstyle-v1'?'':'（当前为测试隔离键，与正式预览存档分开）')+'", 1)
anchor = '<div class="panel"><b>版本</b>'
must(html.count(anchor) == 1, 'version panel anchor')
html = html.replace(anchor, "'+savePanelHtml()+'" + anchor, 1)
frag = open(os.path.dirname(P) + '/save-panel-fragment.js', encoding='utf-8').read()
must('function savePanelHtml' in frag, 'fragment missing')
html = html.replace("function toggleReduceMotion(on){S.settings=S.settings||{};S.settings.reduceMotion=!!on;save();applyReduceMotion();render();}",
                    "function toggleReduceMotion(on){S.settings=S.settings||{};S.settings.reduceMotion=!!on;save();applyReduceMotion();render();}\n" + frag, 1)

# ---- 8. render() tail: apply reduce-motion + save badge ----
must(html.count('window.scrollTo(0,0);}') == 1, 'render tail anchor')
html = html.replace('window.scrollTo(0,0);}', "window.scrollTo(0,0);applyReduceMotion();updateSaveBadge();}", 1)

# ---- 9. CSS append (second style block, before </style></head>) ----
css = """
/* ===== 主城 v4 core：存档徽标 / 点按尺寸 / 按压反馈 / 减动态 ===== */
.savebadge{position:fixed;right:8px;top:104px;z-index:90;background:#b3261e;color:#fff;border:0;border-radius:999px;padding:5px 10px;font-size:11px;font-weight:700;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.35)}
.icbtn{width:44px;height:44px}
.dock button{width:44px;min-height:44px}
.hs:active{transform:scale(.94)}
.hs:active .hs-sign{filter:brightness(1.16);box-shadow:0 0 0 2px #ffd76a,0 4px 10px rgba(0,0,0,.4)}
.hs:focus-visible,.dock button:focus-visible,.icbtn:focus-visible,.cta:focus-visible,.chest:focus-visible,.teamstrip:focus-visible{outline:2px solid #ffd76a;outline-offset:2px}
@media (max-width:360px){.dock button{width:44px;min-height:44px}.dock button svg{width:20px;height:20px}}
@media (max-height:640px){.dock button{width:44px;min-height:44px}}
.reduce-motion *,.reduce-motion *::before,.reduce-motion *::after{animation-duration:.001s!important;animation-iteration-count:1!important;transition-duration:.001s!important}
@media (prefers-reduced-motion: reduce){*{animation-duration:.001s!important;animation-iteration-count:1!important;transition-duration:.001s!important}}
"""
anchor2 = '</style>\n</head>'
must(html.count(anchor2) == 1, 'css anchor')
html = html.replace(anchor2, css + anchor2, 1)

open(P, 'w', encoding='utf-8').write(html)
print('core patch written, bytes:', len(html))

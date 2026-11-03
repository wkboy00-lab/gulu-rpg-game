'use strict';
/* ============ 苔盾 v4 单英雄战斗：苔盾 vs 困困史莱姆 ============
   只有普攻、主动、被动。逻辑步长 20ms：rAF 累积、单帧、跳过快进
   走同一 logicTick，暂停冻结一切（动作、粒子、浮字、冷却、状态计时）。
   结算只在命中帧发生一次；主动的护盾与嘲讽在 ACTIVE_HIT 帧结算，
   冷却从按下时起算。跳过战斗 = 用同一 logicTick 快进到战斗结束，
   不跳过任何一次结算。 */
const SAMPLE_VERSION='2026.11.03-taidun-v4';
const $=id=>document.getElementById(id);
const stage=$('stage'), heroEl=$('hero'), enemyEl=$('enemy');
const TICK=20;
const BASIC_TOTAL=900, BASIC_HIT=560, ACTIVE_TOTAL=1000, ACTIVE_HIT=460;
const ENEMY_TOTAL=800, ENEMY_HIT=320;
let battleTime=0, acc=0, lastTs=null, running=false, paused=false, speed=1, auto=false;
let solo=null, action=null, enemyAction=null, hurtUntil=0, enemyHurtUntil=0;
let hitstopTicks=0, shakeUntil=0, shieldSince=0, crackUntil=0, breakUntil=0, expireUntil=0, shieldHitUntil=0;
let soundOn=true, audioCtx=null, fastForward=false, skipAuto=false;
let particles=[]; // {el,born,life,fn}
let lastActiveLabel='';
const C=(function(){ const s=document.getElementById('core').textContent; const m={exports:{}}; new Function('module','window',s)(m,window); return m.exports; })();

function battleOver(){ return solo&&(!solo.hero.alive||!solo.enemy.alive); }
function newSolo(){
  solo={hero:C.createUnit('taidun',0,C.DATA.heroes.taidun), enemy:C.createUnit('E01',1,C.DATA.enemies.E01),
        stats:{dealt:0,takenHp:0,absorbed:0,basics:0,actives:0,enemyHits:0}};
  solo.hero.nextAt=2200; solo.enemy.nextAt=2600;
  battleTime=0; acc=0; action=null; enemyAction=null; hurtUntil=0; enemyHurtUntil=0;
  hitstopTicks=0; shakeUntil=0; shieldSince=0; crackUntil=0; breakUntil=0; expireUntil=0; shieldHitUntil=0;
  particles.forEach(p=>{ if(p.el&&p.el!==$('fan')) p.el.remove(); }); particles=[];
  $('shieldBubble').className='shieldBubble'; $('shieldBubble').style.opacity='';
  $('crack').classList.remove('on'); $('bubble').style.display='none'; $('enemyTag').style.display='none';
  $('fan').style.display='none';
  enemyEl.style.opacity=''; $('enemyImg').style.transform=''; $('enemyImg').style.opacity='';
  stage.classList.remove('paused'); stage.style.transform='';
  $('resultBar').style.display='none'; $('resultBar').textContent='';
  $('logSolo').textContent='';
  logS('新战斗开始。苔盾 1900 血，史莱姆 700 血。普攻 91，主动护盾 228，冷却 8 秒。');
  render();
}
function logS(msg){ const el=$('logSolo'); el.textContent+='['+(battleTime/1000).toFixed(1)+'s] '+msg+'\n'; el.scrollTop=el.scrollHeight; }
function fmtHp(u){ return u.hp+' / '+u.maxHp; }
function tauntUntil(){ const b=solo.enemy.buffs.find(x=>x.type==='taunted'); return b?b.until:0; }
let lastResultText='';
function render(){
  const h=solo.hero, e=solo.enemy;
  $('hpHero').style.width=(h.hp/h.maxHp*100)+'%'; $('hpHeroTxt').textContent=fmtHp(h);
  $('hpEnemy').style.width=(e.hp/e.maxHp*100)+'%'; $('hpEnemyTxt').textContent=fmtHp(e);
  const sh=C.shieldTotal(h); $('shieldFill').style.width=(sh/h.maxHp*100)+'%'; $('shieldTxt').textContent=sh>0?'护盾 '+sh:'';
  $('badgeTaunt').textContent='嘲讽：'+(battleTime<tauntUntil()?'进行中':'未触发');
  $('badgeTaunt').className='badge'+(battleTime<tauntUntil()?' on':'');
  $('badgePassive').textContent=h.passiveUsed?'被动：本场已消耗':'被动：就绪（低于 665 触发）';
  $('badgePassive').className='badge'+(h.passiveUsed?'':' on');
  $('badgeState').textContent='状态：'+(battleOver()?(h.alive?'胜利':'苔盾倒下'):(action?action.phase:(enemyAction?'敌人行动':(paused?'已暂停':'待机'))));
  $('badgeTime').textContent='战斗时间 '+(battleTime/1000).toFixed(1)+'s';
  $('badgeSpeed').textContent='速度：'+speed+'×';
  const cd=Math.max(0,h.activeReadyAt-battleTime);
  $('btnActive').disabled=cd>0||!!action||!h.alive;
  const activeLabel=cd>0?'主动 · 冷却 '+Math.ceil(cd/1000)+'s':'主动 · 看这里';
  if(activeLabel!==lastActiveLabel){ lastActiveLabel=activeLabel; $('btnActive').innerHTML='<img src="canva-icons/icon-shield.png" alt="">'+activeLabel; }
  $('btnBasic').disabled=!!action||!e.alive||!h.alive;
  $('btnEnemy').disabled=!!enemyAction||!e.alive||!h.alive;
  $('btnSkip').disabled=battleOver();
  $('btnSpeed').textContent='速度：'+speed+'×';
  if(battleOver()){
    const win=e.alive===false&&h.alive;
    const txt=win?('胜利！用时 '+(battleTime/1000).toFixed(1)+'s · 造成伤害 '+solo.stats.dealt+' · 受到伤害 '+solo.stats.takenHp+'（护盾吸收 '+solo.stats.absorbed+'）· 主动 '+solo.stats.actives+' 次 · 被动'+(h.passiveUsed?'已触发':'未触发'))
      :('苔盾倒下了。用时 '+(battleTime/1000).toFixed(1)+'s · 造成伤害 '+solo.stats.dealt+' · 受到伤害 '+solo.stats.takenHp+'。点“重开”再打一场。');
    if(txt!==lastResultText){ lastResultText=txt; $('resultBar').textContent=txt; }
    $('resultBar').style.display='block';
  } else { lastResultText=''; $('resultBar').style.display='none'; }
}
function applyPose(P){
  // 受击叠加：敌人命中后的 300ms 内，身体后仰、盾牌上抬（与当前动作叠加，不打断动作）
  let hx=P.heroX||0, hy=P.heroY||0, bRot=P.body.rot||0, bY=P.body.y||0, bSy=P.body.sy||1;
  let hRot=P.head.rot||0, hY=P.head.y||0, sX=P.shield.x||0, sY=P.shield.y||0, sRot=P.shield.rot||0;
  if(battleTime<hurtUntil&&solo.hero.alive){
    const k=Math.sin((1-(hurtUntil-battleTime)/300)*Math.PI);
    hx-=7*k; bRot-=4*k; sY-=6*k; sRot-=8*k; hRot-=3*k;
  }
  const tf=(x,y,rot,sy)=>'translate('+x+'px,'+y+'px) rotate('+rot+'deg)'+(sy&&sy!==1?' scaleY('+sy+')':'');
  $('lyBody').style.transform=tf(P.body.x||0,bY,bRot,bSy);
  $('lyLeg').style.transform='rotate('+(P.leg.rot||0)+'deg) translate('+(P.body.x||0)+'px,'+bY+'px)';
  $('headWrap').style.transform=tf(P.head.x||0,hY,hRot,1);
  $('lyShield').style.transform=tf(sX,sY,sRot,1);
  $('lyArm').style.transform=tf(P.arm.x||0,P.arm.y||0,P.arm.rot||0,1);
  heroEl.style.transform='translate('+hx+'px,'+hy+'px)';
  $('heroShadow').style.transform='translateX('+(hx*0.6)+'px) scaleX('+(1-Math.abs(hy)*0.01)+')';
  // 眨眼：眼睑随战斗时间开合，暂停即冻结
  const bs=C.blinkScale(battleTime);
  $('lid1').style.transform='scaleY('+bs+')'; $('lid2').style.transform='scaleY('+bs+')';
}
function applyEnemyPose(){
  const e=$('enemyImg');
  if(!solo.enemy.alive){ e.style.transform='scale(1.15,0.35) translateY(18px)'; e.style.opacity='0.5'; enemyEl.style.opacity=''; return; }
  e.style.opacity='';
  if(enemyAction){
    const t=battleTime-enemyAction.start;
    const P=C.enemyPose(Math.min(t,ENEMY_TOTAL),enemyAction.lunge);
    e.style.transform='translate('+P.x+'px,'+P.y+'px) scale('+P.sx+','+P.sy+')';
    return;
  }
  if(battleTime<enemyHurtUntil){
    const k=Math.sin((1-(enemyHurtUntil-battleTime)/300)*Math.PI);
    const squash=1-0.18*k;
    e.style.transform='translateX('+(8*k)+'px) scale('+squash+','+(2-squash)+')';
    return;
  }
  const s=Math.sin(battleTime/1100*Math.PI*2);
  e.style.transform='scale('+(1+0.03*s)+','+(1-0.05*s)+')';
}
function measureLunge(){
  const hr=heroEl.getBoundingClientRect(), er=enemyEl.getBoundingClientRect();
  return C.computeLunge(hr,er,14);
}
function measureEnemyLunge(){
  const hr=heroEl.getBoundingClientRect(), er=enemyEl.getBoundingClientRect();
  return C.computeLungeEnemy(hr,er);
}
/* ---- 声音（WebAudio 合成，无音频文件；快进时不发声） ---- */
function ensureAudio(){ if(!audioCtx){ try{ audioCtx=new (window.AudioContext||window.webkitAudioContext)(); }catch(e){} } if(audioCtx&&audioCtx.state==='suspended') audioCtx.resume(); }
function thud(){
  if(!soundOn||!audioCtx||fastForward) return;
  const t0=audioCtx.currentTime, o=audioCtx.createOscillator(), g=audioCtx.createGain();
  o.type='sine'; o.frequency.setValueAtTime(95,t0); o.frequency.exponentialRampToValueAtTime(48,t0+0.11);
  g.gain.setValueAtTime(0.32,t0); g.gain.exponentialRampToValueAtTime(0.001,t0+0.13);
  o.connect(g).connect(audioCtx.destination); o.start(t0); o.stop(t0+0.14);
  const nb=audioCtx.createBuffer(1,audioCtx.sampleRate*0.08,audioCtx.sampleRate), d=nb.getChannelData(0);
  for(let i=0;i<d.length;i++) d[i]=(Math.random()*2-1)*(1-i/d.length);
  const src=audioCtx.createBufferSource(), f=audioCtx.createBiquadFilter(), g2=audioCtx.createGain();
  src.buffer=nb; f.type='lowpass'; f.frequency.value=320; g2.gain.setValueAtTime(0.16,t0); g2.gain.exponentialRampToValueAtTime(0.001,t0+0.09);
  src.connect(f).connect(g2).connect(audioCtx.destination); src.start(t0);
}
function knock(){ if(!soundOn||!audioCtx||fastForward) return; const t0=audioCtx.currentTime,o=audioCtx.createOscillator(),g=audioCtx.createGain(); o.type='triangle'; o.frequency.value=310; g.gain.setValueAtTime(0.12,t0); g.gain.exponentialRampToValueAtTime(0.001,t0+0.09); o.connect(g).connect(audioCtx.destination); o.start(t0); o.stop(t0+0.1); }
function chime(){ if(!soundOn||!audioCtx||fastForward) return; [660,880].forEach((fr,i)=>{ const t0=audioCtx.currentTime+i*0.07,o=audioCtx.createOscillator(),g=audioCtx.createGain(); o.type='sine'; o.frequency.value=fr; g.gain.setValueAtTime(0.08,t0); g.gain.exponentialRampToValueAtTime(0.001,t0+0.22); o.connect(g).connect(audioCtx.destination); o.start(t0); o.stop(t0+0.24); }); }
/* ---- 粒子与浮字：全部由 battleTime 驱动，暂停即冻结；快进时不生成 ---- */
function addParticle(el,life,fn){ if(fastForward){ return; } particles.push({el:el,born:battleTime,life:life,fn:fn}); $('fxLayer').appendChild(el); }
function spawnDust(){
  if(fastForward) return;
  const r=stage.getBoundingClientRect(), hr=heroEl.getBoundingClientRect();
  const x=hr.left-r.left+hr.width*0.45, y=hr.bottom-r.top-8;
  for(let i=0;i<2;i++){ const d=document.createElement('div'); d.className='particle'; d.style.cssText='left:'+(x+Math.random()*16-8)+'px;top:'+y+'px;width:10px;height:7px;background:#d8c9a3;opacity:.7';
    const dx=(Math.random()-0.5)*22;
    addParticle(d,420,k=>{ const p=k/420; d.style.transform='translate('+(dx*p)+'px,'+(-6*p)+'px) scale('+(1+p)+')'; d.style.opacity=String(0.7*(1-p)); }); }
}
function spawnImpact(contactX,contactY){
  if(fastForward) return;
  const fan=$('fan'); fan.style.display='block'; fan.style.left=(contactX-14)+'px'; fan.style.top=(contactY-34)+'px';
  particles.push({el:fan,born:battleTime,life:200,fn:k=>{ fan.style.opacity=String(1-k/200); if(k>=200) fan.style.display='none'; }});
  const cols=['#c89a5e','#8a6a3a','#9fbf6a','#e8d9a8'];
  for(let i=0;i<9;i++){
    const d=document.createElement('div'); d.className='particle';
    const sz=3+Math.random()*4; d.style.cssText='left:'+contactX+'px;top:'+contactY+'px;width:'+sz+'px;height:'+sz+'px;background:'+cols[i%4];
    const ang=-0.5+Math.random()*0.9, v=70+Math.random()*90, vy=-(30+Math.random()*50);
    addParticle(d,520,k=>{ const p=k/520, t=p*0.52; const x=Math.cos(ang)*v*t, y=vy*t+140*t*t; d.style.transform='translate('+x+'px,'+y+'px) rotate('+(p*220)+'deg)'; d.style.opacity=String(1-p); });
  }
  for(let i=0;i<4;i++){ const d=document.createElement('div'); d.className='particle'; d.style.cssText='left:'+(contactX-8+i*5)+'px;top:'+(contactY+8)+'px;width:8px;height:6px;background:#efe6c8;opacity:.8';
    addParticle(d,380,k=>{ const p=k/380; d.style.transform='translate('+(i*4-6)+'px,'+(4*p)+'px) scale('+(1+p*0.8)+')'; d.style.opacity=String(0.8*(1-p)); }); }
}
function spawnLeaves(){
  if(fastForward) return;
  const r=stage.getBoundingClientRect(), hr=heroEl.getBoundingClientRect();
  const x0=hr.left-r.left+hr.width*0.5, y0=hr.bottom-r.top-10;
  for(let i=0;i<10;i++){ const d=document.createElement('div'); d.className='particle'; d.style.cssText='left:'+(x0+Math.random()*40-20)+'px;top:'+y0+'px;width:8px;height:11px;background:#8fbf6a;border-radius:60% 0 60% 0';
    const dx=(Math.random()-0.5)*36;
    addParticle(d,700,k=>{ const p=k/700; d.style.transform='translate('+(dx*p)+'px,'+(-110*p)+'px) rotate('+(p*160)+'deg)'; d.style.opacity=String(1-p); }); }
}
function spawnShieldBreak(){
  if(fastForward) return;
  const r=stage.getBoundingClientRect(), hr=heroEl.getBoundingClientRect();
  const cx=hr.left-r.left+hr.width*0.55, cy=hr.top-r.top+hr.height*0.45;
  for(let i=0;i<8;i++){ const d=document.createElement('div'); d.className='particle'; d.style.cssText='left:'+cx+'px;top:'+cy+'px;width:6px;height:6px;background:#cfe8a8';
    const a=Math.random()*Math.PI*2, v=50+Math.random()*60;
    addParticle(d,450,k=>{ const p=k/450,t=p*0.45; d.style.transform='translate('+(Math.cos(a)*v*t)+'px,'+(Math.sin(a)*v*t+40*t*t)+'px)'; d.style.opacity=String(1-p); }); }
}
function spawnRing(){
  if(fastForward) return;
  const r=stage.getBoundingClientRect(), hr=heroEl.getBoundingClientRect();
  for(let i=0;i<3;i++){ const ring=document.createElement('div'); ring.className='ring';
    const cx=hr.left-r.left+hr.width*0.55, cy=hr.top-r.top+hr.height*0.5;
    ring.style.left=cx+'px'; ring.style.top=cy+'px';
    const rec={el:ring,born:battleTime,life:520,fn:k=>{ const p=k/520; const s=20+p*130; ring.style.width=s+'px'; ring.style.height=s*0.7+'px'; ring.style.transform='translate(-50%,-50%)'; ring.style.opacity=String(0.9*(1-p)); if(k>=520) ring.remove(); }};
    particles.push(rec); $('fxLayer').appendChild(ring); }
}
function floater(text,cls,x,y,delayMs){
  if(fastForward) return;
  const d=document.createElement('div'); d.className='dmg '+cls; d.textContent=text; d.style.left=x+'px'; d.style.top=y+'px'; d.style.opacity='0';
  $('floatLayer').appendChild(d);
  particles.push({el:d,born:battleTime+(delayMs||0),life:900,fn:(k)=>{ const p=Math.max(0,k)/900; d.style.transform='translateY('+(-38*p)+'px)'; d.style.opacity=String(1-p); if(k>=900) d.remove(); }});
}
function updateParticles(){
  particles=particles.filter(p=>{
    const k=battleTime-p.born; if(k<0) return true; if(k>=p.life){ if(p.el!==$('fan')) p.el.remove(); return false; }
    p.fn(k); return true;
  });
}
function updateSwoosh(){
  const sw=$('swoosh');
  if(fastForward||!action||action.kind!=='basic'){ sw.style.display='none'; return; }
  const t=battleTime-action.start;
  if(t<260||t>=BASIC_HIT){ sw.style.display='none'; return; }
  const k=(t-260)/300, op=Math.sin(k*Math.PI)*0.75;
  sw.style.display='block';
  sw.style.left=action.fromX+'px'; sw.style.width=Math.max(8,action.toX-action.fromX)+'px';
  sw.style.opacity=String(op);
}
/* ---- 命中事件：唯一结算点 ---- */
function hitEventBasic(){
  const target=solo.enemy;
  if(!solo.hero.alive){ logS('苔盾已倒下，本次盾撞未能出手。'); return; }
  if(!target.alive){ logS('目标已倒下，本次盾撞落空，不扣血。'); return; }
  const stageRect=stage.getBoundingClientRect();
  const contactX=measureLunge().contactX-stageRect.left;
  const contactY=enemyEl.getBoundingClientRect().top-stageRect.top+enemyEl.getBoundingClientRect().height*0.55;
  const res=C.dealBasic(solo.hero,target,battleTime);
  solo.stats.dealt+=res.dmg; solo.stats.basics++;
  thud(); spawnImpact(contactX,contactY);
  hitstopTicks=3; // 命中顿帧 60ms：逻辑步进暂停 3 步
  shakeUntil=battleTime+120;
  const er=enemyEl.getBoundingClientRect();
  floater('-'+res.dmg,'',er.left-stageRect.left+er.width*0.3,er.top-stageRect.top-6);
  logS('木盾撞击命中：盾缘抵达受击区，伤害 '+res.dmg+'，史莱姆 '+(target.hp+res.dmg)+' → '+target.hp+'。');
  enemyHurtUntil=battleTime+300;
  if(res.killed){ logS('史莱姆倒下了。'); }
  render();
}
function startBasic(){
  if(action||!solo.enemy.alive||!solo.hero.alive) return;
  ensureAudio();
  const r=measureLunge();
  const stageRect=stage.getBoundingClientRect();
  action={kind:'basic',start:battleTime,lunge:r.lunge,hitDone:false,phase:'windup',
          fromX:r.attackX-stageRect.left, toX:r.contactX-stageRect.left};
  spawnDust();
  logS('普攻开始：实时计算突进 '+Math.round(r.lunge)+'px（盾缘→受击区缺口 '+Math.round(r.gap)+'px）。');
  render();
}
function startActive(){
  if(action||battleTime<solo.hero.activeReadyAt||!solo.hero.alive) return;
  ensureAudio();
  const res=C.reserveActiveTaidun(solo.hero,battleTime);
  if(!res.ok){ return; }
  action={kind:'active',start:battleTime,hitDone:false,phase:'brace'};
  logS('主动「看这里」出手：前摇起盾，护盾与嘲讽在盾牌前顶帧结算，冷却 8 秒从出手起算。不造成伤害。');
  render();
}
function activeHitEvent(){
  if(!solo.hero.alive) return;
  const res=C.applyActiveTaidun(solo.hero,[solo.enemy],battleTime);
  solo.stats.actives++;
  shieldSince=battleTime;
  knock(); spawnRing(); $('bubble').style.display='block';
  logS('盾牌前顶：嘲讽 2 秒，护盾 '+res.shield+' 已立起。');
}
function enemyAttack(dmgOverride){
  if(enemyAction||!solo.enemy.alive||!solo.hero.alive) return;
  ensureAudio();
  const r=measureEnemyLunge();
  enemyAction={start:battleTime,hitDone:false,dmg:dmgOverride||null,phase:'windup',lunge:r.lunge};
  render();
}
function enemyHitEvent(){
  const dmg=enemyAction.dmg;
  const t=solo.enemy, h=solo.hero;
  if(!t.alive){ return; } // 倒下的敌人不再打出飞行中的攻击
  let res;
  if(dmg){ res=C.applyDamage(t,h,dmg,battleTime); }
  else { res=C.dealBasic(t,h,battleTime); }
  solo.stats.enemyHits++;
  const stageRect=stage.getBoundingClientRect(), hr=heroEl.getBoundingClientRect();
  if(res.absorbed>0){
    solo.stats.absorbed+=res.absorbed;
    floater('-'+res.absorbed,'absorb',hr.left-stageRect.left+hr.width*0.55,hr.top-stageRect.top+hr.height*0.18);
    shieldHitUntil=battleTime+220;
    logS('敌人攻击被护盾挡住 '+res.absorbed+'，护盾 '+(C.shieldTotal(h)+res.absorbed)+' → '+C.shieldTotal(h)+'，生命不变。');
  }
  if(res.hpDmg>0){
    solo.stats.takenHp+=res.hpDmg;
    floater('-'+res.hpDmg,'',hr.left-stageRect.left+hr.width*0.3,hr.top-stageRect.top+hr.height*0.3);
    logS('敌人攻击命中，苔盾生命 '+(h.hp+res.hpDmg)+' → '+h.hp+'。');
    hurtUntil=battleTime+300;
  }
  if(res.passive){
    chime(); spawnLeaves();
    floater('+'+res.heal,'heal',hr.left-stageRect.left+hr.width*0.62,hr.top-stageRect.top-10,120);
    logS('被动「虽然害怕」触发：低于 665，恢复 '+res.heal+'，生命 '+h.hp+'。本场不再触发。');
  }
  if(res.shieldBroken&&C.shieldTotal(h)===0){
    breakUntil=battleTime+480; crackUntil=battleTime+480;
    spawnShieldBreak();
    logS('护盾被击破。');
  }
  if(!h.alive){ logS('苔盾倒下了。'); }
  render();
}
/* 护盾气泡的全部视觉状态由战斗时间推导，不用任何 wall-clock 计时器，暂停即冻结 */
function checkShieldLifecycle(){
  const h=solo.hero;
  const ex=C.expireShields(h,battleTime);
  if(ex.expired){
    expireUntil=battleTime+520;
    logS('护盾自然到期，缓缓消散（与击破不同）。');
  }
  const total=C.shieldTotal(h);
  const b=$('shieldBubble');
  if(total===0){
    if(battleTime<breakUntil){ b.className='shieldBubble break'; }
    else if(battleTime<expireUntil){ b.className='shieldBubble expire'; b.style.opacity='0'; }
    else { b.className='shieldBubble'; b.style.opacity=''; }
    $('crack').classList.toggle('on',battleTime<crackUntil);
  } else {
    b.style.opacity='';
    $('crack').classList.remove('on');
    if(battleTime<shieldSince+300){ if(b.className!=='shieldBubble build') b.className='shieldBubble build'; }
    else if(battleTime<shieldHitUntil){ if(b.className!=='shieldBubble on hit') b.className='shieldBubble on hit'; }
    else if(b.className!=='shieldBubble on'){ b.className='shieldBubble on'; }
  }
  C.expireBuffs(solo.enemy,battleTime);
  $('enemyTag').style.display=(battleTime<tauntUntil())?'block':'none';
}
/* ---- 统一逻辑步进：rAF、单帧、跳过都走这里 ---- */
function logicTick(dt){
  if(hitstopTicks>0){ hitstopTicks--; render(); return; }
  battleTime+=dt;
  checkShieldLifecycle();
  if(action){
    const t=battleTime-action.start;
    if(action.kind==='basic'){
      if(t>=BASIC_HIT&&!action.hitDone){ action.hitDone=true; hitEventBasic(); }
      if(t>=BASIC_TOTAL){ action=null; applyPose(C.idlePose(battleTime)); }
      else applyPose(C.basicPose(t,action.lunge));
    } else {
      if(t>=ACTIVE_HIT&&!action.hitDone){ action.hitDone=true; activeHitEvent(); }
      if(t>=ACTIVE_TOTAL){ action=null; $('bubble').style.display='none'; applyPose(C.idlePose(battleTime)); }
      else { applyPose(C.activePose(t)); if(t>=ACTIVE_HIT) $('bubble').style.display='block'; }
    }
  } else { applyPose(C.idlePose(battleTime)); }
  if(enemyAction){
    const t=battleTime-enemyAction.start;
    if(t>=ENEMY_HIT&&!enemyAction.hitDone){ enemyAction.hitDone=true; enemyHitEvent(); }
    if(t>=ENEMY_TOTAL){ enemyAction=null; }
  }
  applyEnemyPose();
  updateSwoosh();
  updateParticles();
  stage.style.transform=battleTime<shakeUntil?('translate('+((Math.floor(battleTime/40)%2)?2:-2)+'px,1px)'):'';
  if((auto||skipAuto)&&solo.hero.alive&&solo.enemy.alive){
    if(battleTime>=solo.hero.nextAt&&!action){ startBasic(); solo.hero.nextAt=battleTime+2200; }
    if(battleTime>=solo.enemy.nextAt&&!enemyAction){ enemyAttack(null); solo.enemy.nextAt=battleTime+2200; }
  }
  render();
}
function frame(ts){
  if(!running) return;
  if(lastTs==null) lastTs=ts;
  let dt=ts-lastTs; lastTs=ts;
  if(!paused){
    acc+=dt*speed;
    let n=0;
    while(acc>=TICK&&n<12){ logicTick(TICK); acc-=TICK; n++; }
    if(n===12) acc=0;
  }
  requestAnimationFrame(frame);
}
function startLoop(){ if(running) return; running=true; lastTs=null; requestAnimationFrame(frame); }
$('btnBasic').addEventListener('click',()=>{ ensureAudio(); startBasic(); });
$('btnActive').addEventListener('click',()=>{ ensureAudio(); startActive(); });
$('btnEnemy').addEventListener('click',()=>{ ensureAudio(); enemyAttack(null); });
$('btnHeavy').addEventListener('click',()=>{ ensureAudio(); enemyAttack(400); logS('调试重击 400（测试用，非敌人普攻）。'); });
$('btnAuto').addEventListener('click',e=>{ auto=!auto; e.target.textContent='自动战斗：'+(auto?'开':'关'); if(auto&&!running) startLoop(); });
$('btnSpeed').addEventListener('click',()=>{ speed=speed===1?2:(speed===2?3:1); logS('速度切换到 '+speed+'×：同一逻辑步进，只是每帧步数变化。'); render(); });
$('btnSkip').addEventListener('click',()=>{
  if(battleOver()||!solo) return;
  if(paused){ paused=false; $('btnPause').textContent='暂停'; stage.classList.remove('paused'); }
  fastForward=true; skipAuto=true;
  let n=0;
  while(!battleOver()&&n<6000){ logicTick(TICK); n++; }
  skipAuto=false; fastForward=false;
  applyPose(C.idlePose(battleTime)); applyEnemyPose();
  logS('跳过战斗：同一逻辑步进快进结算完毕，未跳过任何一次伤害、治疗或护盾结算，结果与正常播放一致。');
  render();
});
$('btnPause').addEventListener('click',e=>{
  paused=!paused; acc=0;
  e.target.textContent=paused?'继续':'暂停';
  stage.classList.toggle('paused',paused);
  logS(paused?'已暂停：动作、粒子、浮字、冷却与状态计时全部冻结。':'已继续。');
  render();
});
$('btnReset').addEventListener('click',()=>{ paused=false; $('btnPause').textContent='暂停'; newSolo(); });
$('btnRevive').addEventListener('click',()=>{ solo.enemy.hp=solo.enemy.maxHp; solo.enemy.alive=true; solo.enemy.buffs=[]; enemyEl.style.opacity=''; logS('敌人已复活，旧动作与死亡标记已清除。'); render(); });
$('btnSlow').addEventListener('click',e=>{ speed=speed===0.25?1:0.25; e.target.textContent='慢动作 0.25×：'+(speed===0.25?'开':'关'); render(); });
$('btnStep').addEventListener('click',()=>{
  if(!paused){ paused=true; $('btnPause').textContent='继续'; stage.classList.add('paused'); }
  logicTick(TICK);
});
$('btnSound').addEventListener('click',e=>{ soundOn=!soundOn; e.target.textContent='声音：'+(soundOn?'开':'关'); if(soundOn) ensureAudio(); });
[['ckBody','lyBody'],['ckLeg','lyLeg'],['ckHead','headWrap'],['ckShield','lyShield'],['ckArm','lyArm']].forEach(([ck,ly])=>{
  $(ck).addEventListener('change',e=>{ $(ly).style.display=e.target.checked?'block':'none'; });
});
$('ckPivot').addEventListener('change',e=>{ $('pivotNote').style.display=e.target.checked?'block':'none'; });
$('ckFlat').addEventListener('change',e=>{ $('flatImg').style.display=e.target.checked?'block':'none'; });

/* 供浏览器实测读取的只读状态（不参与玩法） */
window.TAIDUN_DEBUG={version:SAMPLE_VERSION,getState:function(){
  return {t:battleTime,over:battleOver(),paused:paused,speed:speed,
    hero:{hp:solo.hero.hp,shield:C.shieldTotal(solo.hero),passiveUsed:solo.hero.passiveUsed,cd:Math.max(0,solo.hero.activeReadyAt-battleTime)},
    enemy:{hp:solo.enemy.hp,alive:solo.enemy.alive},
    action:action?{kind:action.kind,t:battleTime-action.start}:null,
    stats:solo.stats};
}};

newSolo(); startLoop();

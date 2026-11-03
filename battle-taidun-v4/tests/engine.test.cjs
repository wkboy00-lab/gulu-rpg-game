'use strict';
const fs=require('fs'), assert=require('assert');
const html=fs.readFileSync(__dirname+'/../index.html','utf8');
const m=/<script id="core">([\s\S]*?)<\/script>/.exec(html);
assert(m,'core script not found');
const sandbox={module:{exports:{}}};
new Function('module','window',m[1])(sandbox.module, {});
const C=sandbox.module.exports;
let n=0; const ok=(name,fn)=>{fn();n++;console.log('ok -',name);};
ok('basic damage 91 (taidun->E01), enemy 34',()=>{
  assert.strictEqual(C.calcDamageDet(100,1,10,'森芽','森芽'),91);
  assert.strictEqual(C.calcDamageDet(55,1,60,'森芽','森芽'),34);
  assert.strictEqual(C.calcDamageDet(80,1,14,'森芽','森芽'),70); // E02 bite: 80*100/114=70.17->70
});
ok('shield absorbs earliest-first, 228->194 on 34 hit, hp unchanged',()=>{
  const h=C.createUnit('taidun',0,C.DATA.heroes.taidun);
  C.addShield(h,228,5000,0,'hero_taidun');
  const r=C.applyDamage(null,h,34,1000);
  assert.strictEqual(r.absorbed,34); assert.strictEqual(r.hpDmg,0); assert.strictEqual(C.shieldTotal(h),194); assert.strictEqual(h.hp,1900);
});
ok('passive sequence: 4x400 -> 490, then 400 -> 90, no retrigger',()=>{
  const h=C.createUnit('taidun',0,C.DATA.heroes.taidun);
  const e=C.createUnit('E01',1,C.DATA.enemies.E01);
  let last;
  for(let i=0;i<4;i++) last=C.applyDamage(e,h,400,i*100);
  assert.strictEqual(last.passive,true); assert.strictEqual(h.hp,490);
  last=C.applyDamage(e,h,400,5000);
  assert.strictEqual(last.passive,false); assert.strictEqual(h.hp,90);
});
ok('passive does not fire at exactly 665, fires below',()=>{
  const h=C.createUnit('taidun',0,C.DATA.heroes.taidun);
  let r=C.applyDamage(null,h,1900-665,0);
  assert.strictEqual(h.hp,665); assert.strictEqual(r.passive,false);
  r=C.applyDamage(null,h,1,100);
  assert.strictEqual(r.passive,true); assert.strictEqual(h.hp,664+190);
});
ok('active: cooldown 8s, shield 228, no damage, taunts all foes 2s',()=>{
  const h=C.createUnit('taidun',0,C.DATA.heroes.taidun);
  const foes=[C.createUnit('E01',1,C.DATA.enemies.E01),C.createUnit('E02',1,C.DATA.enemies.E02)];
  const r=C.tryActiveTaidun(h,foes,0);
  assert.strictEqual(r.ok,true); assert.strictEqual(C.shieldTotal(h),228); assert.strictEqual(h.activeReadyAt,8000);
  assert.strictEqual(foes[0].buffs[0].type,'taunted'); assert.strictEqual(foes[0].buffs[0].until,2000);
  assert.strictEqual(C.tryActiveTaidun(h,foes,1000).ok,false);
});
ok('shield break vs expire are distinct events',()=>{
  const h=C.createUnit('taidun',0,C.DATA.heroes.taidun);
  C.addShield(h,228,5000,0,'hero_taidun');
  const r=C.applyDamage(null,h,300,1000);
  assert.strictEqual(r.shieldBroken,true); assert.strictEqual(C.shieldTotal(h),0);
  const h2=C.createUnit('taidun',0,C.DATA.heroes.taidun);
  C.addShield(h2,228,5000,0,'hero_taidun');
  const ex=C.expireShields(h2,5001);
  assert.strictEqual(ex.expired,true); assert.strictEqual(C.shieldTotal(h2),0);
});
ok('taunt redirects target: taunted > focus > front row',()=>{
  const e1=C.createUnit('E01',1,C.DATA.enemies.E01);
  const h1=C.createUnit('taidun',0,C.DATA.heroes.taidun);
  const h2=C.createUnit('xingkui',0,C.DATA.heroes.xingkui);
  const h3=C.createUnit('heling',0,C.DATA.heroes.heling);
  const foes=[h1,h2,h3];
  assert.strictEqual(C.pickBasicTarget(e1,foes,null).id,'taidun'); // front lowest pos
  assert.strictEqual(C.pickBasicTarget(e1,foes,'heling').id,'taidun'); // focus only matters for side 0
  e1.buffs.push({type:'taunted',val:'heling',until:9999});
  assert.strictEqual(C.pickBasicTarget(e1,foes,null).id,'heling'); // taunt overrides front
  // hero side: focus works when no taunt
  const hero=C.createUnit('yexian',0,C.DATA.heroes.yexian);
  const foes2=[C.createUnit('E01',1,C.DATA.enemies.E01),C.createUnit('E03',1,C.DATA.enemies.E03)];
  assert.strictEqual(C.pickBasicTarget(hero,foes2,'E03').id,'E03');
  assert.strictEqual(C.pickBasicTarget(hero,foes2,null).id,'E01');
});
ok('dead target is never picked; dead taunter ignored',()=>{
  const e1=C.createUnit('E01',1,C.DATA.enemies.E01);
  const h1=C.createUnit('taidun',0,C.DATA.heroes.taidun); h1.alive=false;
  const h2=C.createUnit('heling',0,C.DATA.heroes.heling);
  e1.buffs.push({type:'taunted',val:'taidun',until:9999});
  assert.strictEqual(C.pickBasicTarget(e1,[h1,h2],null).id,'heling');
});
ok('contact math scales: 320 / 390 / 1200 stage widths, shield edge lands within 6px of hit zone',()=>{
  const cases=[
    {hero:{left:20,width:160},foe:{left:210,width:86}},
    {hero:{left:22,width:203},foe:{left:234,width:110}},
    {hero:{left:60,width:230},foe:{left:900,width:128}}
  ];
  for(const c of cases){
    const r=C.computeLunge(c.hero,c.foe,14);
    const reach=c.hero.left+c.hero.width*0.95+r.lunge+14; // 盾缘总位移 = 初始攻击点 + heroX + 盾相对前顶
    const hitX=c.foe.left+c.foe.width*0.11;
    assert.ok(Math.abs(reach-(hitX+4))<=6, `reach ${reach} vs hit+4 ${hitX+4}`);
    assert.ok(r.lunge>0);
  }
});
ok('basic pose: windup crouch, lunge reaches lungePx at hit, recoil, return to 0',()=>{
  const p0=C.basicPose(130,60); assert.ok(p0.body.y>0&&p0.shield.x<0);
  const ph=C.basicPose(559,60); assert.ok(Math.abs(ph.heroX-60)<1); assert.strictEqual(ph.phase,'lunge');
  const pr=C.basicPose(620,60); assert.ok(pr.heroX<60&&pr.heroX>30);
  const pe=C.basicPose(900,60); assert.strictEqual(pe.heroX,0); assert.strictEqual(pe.shield.x,0);
});
ok('active pose: shield thrusts, arm braces, returns',()=>{
  const p=C.activePose(450); assert.ok(p.shield.x>=16&&p.shield.rot>=10);
  const pe=C.activePose(1000); assert.strictEqual(pe.shield.x,0);
});
ok('no ult/energy mechanics in sample html',()=>{
  assert.ok(!/大招|能量|必杀|energy/i.test(html),'sample must not contain ult/energy');
});
ok('no wall-clock timers or team view in v4',()=>{
  assert.ok(!/setTimeout|setInterval/.test(html),'no wall-clock timers: all visuals driven by battleTime');
  assert.ok(!/viewTeam|teamStage|tabTeam/.test(html),'team view removed: solo battle only');
  assert.ok(/2026\.11\.03-taidun-v4/.test(html),'version string present');
  assert.ok(/TAIDUN_DEBUG/.test(html),'debug state hook present');
});
ok('active split: reserve locks cooldown, shield+taunt settle only on apply',()=>{
  const h=C.createUnit('taidun',0,C.DATA.heroes.taidun);
  const foes=[C.createUnit('E01',1,C.DATA.enemies.E01)];
  const r=C.reserveActiveTaidun(h,1000);
  assert.strictEqual(r.ok,true); assert.strictEqual(h.activeReadyAt,9000);
  assert.strictEqual(C.shieldTotal(h),0,'no shield before the plant frame');
  assert.strictEqual(foes[0].buffs.length,0,'no taunt before the plant frame');
  const a=C.applyActiveTaidun(h,foes,1460);
  assert.strictEqual(a.shield,228); assert.strictEqual(C.shieldTotal(h),228);
  assert.strictEqual(foes[0].buffs[0].type,'taunted'); assert.strictEqual(foes[0].buffs[0].until,3460);
  assert.strictEqual(C.reserveActiveTaidun(h,2000).ok,false,'cooldown runs from the cast');
});
ok('enemy contact math scales: strike lands shield edge +4px at 3 widths',()=>{
  const cases=[
    {hero:{left:20,width:160},foe:{left:210,width:86}},
    {hero:{left:22,width:203},foe:{left:234,width:110}},
    {hero:{left:60,width:230},foe:{left:900,width:128}}
  ];
  for(const c of cases){
    const r=C.computeLungeEnemy(c.hero,c.foe);
    const reach=c.foe.left+c.foe.width*0.11-r.lunge;
    const shieldX=c.hero.left+c.hero.width*0.95;
    assert.ok(Math.abs(reach-(shieldX+4))<=6, `reach ${reach} vs shield+4 ${shieldX+4}`);
    assert.ok(r.lunge>0);
  }
});
ok('enemy pose: windup squash, lunge reaches -lungePx, returns to 0',()=>{
  const p0=C.enemyPose(100,60); assert.ok(p0.sy<1&&p0.x===0);
  const pl=C.enemyPose(499,60); assert.ok(Math.abs(pl.x+60)<2); assert.strictEqual(pl.phase,'lunge');
  const pe=C.enemyPose(800,60); assert.ok(pe.x===0); assert.strictEqual(pe.phase,'return');
});
ok('blink: open most of the cycle, closed only in the blink window',()=>{
  assert.strictEqual(C.blinkScale(0),0.08);
  assert.strictEqual(C.blinkScale(1000),0.08);
  assert.ok(C.blinkScale(390)>0.9,'eyes covered at blink peak');
  assert.ok(C.blinkScale(330)>0.08&&C.blinkScale(330)<1,'closing edge is smooth');
  assert.strictEqual(C.blinkScale(4800),0.08,'cycle repeats');
});
ok('hurt offsets: recoil overlay, shield raised, no position drift at k=0',()=>{
  const z=C.hurtOffsets(0); assert.ok(z.heroX===0); assert.ok(z.shieldY===0);
  const f=C.hurtOffsets(1); assert.strictEqual(f.heroX,-7); assert.strictEqual(f.shieldY,-6); assert.strictEqual(f.shieldRot,-8);
});
ok('layer pivots documented: shield 57% / arm 31.5%',()=>{
  assert.ok(/57%/.test(html)&&/31\.5%/.test(html));
});
console.log(n+' tests passed');

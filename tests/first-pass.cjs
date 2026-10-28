// Run: npm install --no-save playwright; node tests/first-pass.cjs
// Or provide PLAYWRIGHT_MODULE, BROWSER_CHANNEL and REVIEW_OUTPUT environment variables.
const fs=require('fs'),http=require('http'),path=require('path'),assert=require('assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..'),out=process.env.REVIEW_OUTPUT;
const results=[],errors=[];
function check(name,ok,detail){results.push({name,pass:!!ok,detail});assert.ok(ok,name+' '+JSON.stringify(detail||''));}
const server=http.createServer((req,res)=>{
 const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
 const p=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
 if(!p.startsWith(root+path.sep)){res.writeHead(403);return res.end();}
 fs.readFile(p,(err,b)=>{res.statusCode=err?404:200;res.setHeader('Content-Type',p.endsWith('.html')?'text/html;charset=utf-8':p.endsWith('.webp')?'image/webp':'text/plain');res.end(err?'missing':b);});
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL||'msedge'});
 try{
 const page=await browser.newPage({viewport:{width:390,height:844}});
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:'+server.address().port);await page.waitForTimeout(600);
 check('序章继续按钮可点击',await page.getByRole('button',{name:'继续',exact:true}).count()===1);
 await page.getByRole('button',{name:'继续',exact:true}).click();
 await page.getByRole('button',{name:'跳过',exact:true}).click();
 check('序章跳过后关闭',!await page.locator('#modalwrap').evaluate(e=>e.classList.contains('open')));
 const assets=fs.readdirSync(path.join(root,'assets')).filter(x=>x.endsWith('.webp'));
 check('44 张 WebP',assets.length===44);
 for(const file of assets){
  const a=await page.evaluate(async file=>{const img=new Image();img.src='assets/'+file;try{await img.decode();return {w:img.naturalWidth,h:img.naturalHeight};}catch(e){return null;}},file);
  check('图片解码 '+file,a&&a.w>0&&a.h>0,a);
 }
 const refs=await page.evaluate(()=>{
  const paths=new Set(['assets/city.webp',...CHAPTERS.map(c=>c.bg)]);
  const add=html=>{for(const m of html.matchAll(/src="([^"]+)"/g))paths.add(m[1]);};
  HERO_IDS.forEach(id=>{add(heroArt(id));S.skins.worn[id]=true;add(heroArt(id));delete S.skins.worn[id];});
  Object.keys(ENEMIES).forEach(id=>add(enemyArt(id)));Object.keys(BOSSES).forEach(id=>add(enemyArt(id)));
  return [...paths];
 });
 check('动态与直接游戏素材共43张',refs.length===43,refs);
 check('43个游戏资源路径均存在',refs.every(p=>fs.existsSync(path.join(root,p))));
 check('根目录icon确认缺失',!fs.existsSync(path.join(root,'icon.webp')));
 const views=['city','heroes','formation','adventure','bestiary','map','tower','dungeons','summon','bag','quests','mail','settings','expedition','docs','shop','season','arena'];
 for(const view of views){await page.evaluate(v=>{closeModal();go(v);},view);check('页面 '+view,await page.locator('#view').innerText().then(x=>x.length>0));}
 await page.evaluate(()=>go('hero','taidun'));check('英雄详情',await page.locator('#view').innerText().then(x=>x.includes('苔盾')));
 await page.evaluate(()=>go('prebattle',0));await page.getByRole('button',{name:'调整阵容',exact:true}).click();
 await page.getByRole('button',{name:'← 完成编队，返回战前',exact:true}).click();
 check('编队返回原战前',await page.evaluate(()=>V.name==='prebattle'&&V.param===0));
 await page.evaluate(()=>{go('formation');formSlotClick(0);formHeroClick('yexian');});
 check('点击编队交换',await page.evaluate(()=>S.formation[0]==='yexian'&&new Set(S.formation.filter(Boolean)).size===5));
 await page.evaluate(()=>{S=defaultState();S.storySeen.intro=true;dailyReset();go('city');});
 for(const viewport of [{width:320,height:568},{width:390,height:844},{width:460,height:900},{width:1280,height:900}]){
  await page.setViewportSize(viewport);await page.evaluate(()=>go('city'));await page.waitForTimeout(250);
  const layout=await page.evaluate(()=>{const target=document.querySelector('.objcard').getBoundingClientRect();const nav=document.querySelector('#nav').getBoundingClientRect();const title=document.querySelector('#topbar .ttl');return {overflow:document.documentElement.scrollWidth>innerWidth,targetVisible:target.bottom<=nav.top,title:getComputedStyle(title).display};});
  check('主城布局 '+viewport.width,!layout.overflow&&layout.targetVisible&&layout.title!=='none',layout);
  if(out&&viewport.width===390)await page.screenshot({path:path.join(out,'after-city.png')});
  await page.evaluate(()=>startStageBattle(0));await page.waitForTimeout(120);
  const battle=await page.evaluate(()=>{const field=document.querySelector('#bfield').getBoundingClientRect();return {buttons:[...document.querySelectorAll('.btop button')].every(b=>{const r=b.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth;}),units:[...document.querySelectorAll('.unit')].every(u=>{const r=u.getBoundingClientRect();return r.top>=field.top-1&&r.bottom<=field.bottom+1;})};});
  check('战斗控件和单位完整 '+viewport.width,battle.buttons&&battle.units,battle);
  if(out&&viewport.width===390)await page.screenshot({path:path.join(out,'after-battle.png')});
  await page.evaluate(()=>closeBattle());
 }
 await page.setViewportSize({width:390,height:844});
 await page.evaluate(()=>startStageBattle(0));
 check('连续开始不会重建正在进行的战斗',await page.evaluate(()=>{const current=B;startStageBattle(0);return B===current;}));
 await page.waitForTimeout(1050);
 const t=await page.evaluate(()=>B.t);check('1×真实计时',t>=800&&t<=1300,t);
 await page.getByRole('button',{name:'暂停',exact:true}).click();const paused=await page.evaluate(()=>B.t);await page.waitForTimeout(300);
 check('暂停不推进',await page.evaluate(()=>B.t)===paused);
 await page.getByRole('button',{name:'继续',exact:true}).click();await page.getByRole('button',{name:'1×',exact:true}).click();const t2=await page.evaluate(()=>B.t);await page.waitForTimeout(500);
 const delta2=await page.evaluate(t=>B.t-t,t2);check('2×真实计时',delta2>=700&&delta2<=1300,delta2);
 await page.getByRole('button',{name:'2×',exact:true}).click();const t3=await page.evaluate(()=>B.t);await page.waitForTimeout(400);
 const delta3=await page.evaluate(t=>B.t-t,t3);check('3×真实计时',delta3>=900&&delta3<=1500,delta3);
 await page.evaluate(()=>{const enemy=B.units.find(u=>u.side===1&&u.alive);unitEls[enemy.uid].click();});
 check('点击集火',await page.evaluate(()=>B.focus!=null));
 await page.evaluate(()=>{const u=B.units.find(u=>u.side===0);u.energy=100;manualUlt(u.uid);});check('手动大招消耗能量',await page.evaluate(()=>B.units.find(u=>u.side===0).energy<100));
 await page.getByRole('button',{name:'自动大招',exact:true}).click();check('自动大招开关',await page.evaluate(()=>B.autoUlt));
 await page.evaluate(()=>{closeBattle();});
 const deterministic=await page.evaluate(()=>{
  const cfg={kind:'stage',ref:9,title:'test',seedStr:'fixed-regression',enemies:stageEnemies(9),bossKey:'1'};
  return Array.from({length:5},()=>JSON.stringify(runHeadless({...cfg})));
 });check('同配置同种子5次逐字段一致',new Set(deterministic).size===1);
 const systems=await page.evaluate(()=>{
  function reset(){closeBattle();closeModal();S=defaultState();S.storySeen.intro=true;dailyReset();Object.values(S.heroes).forEach(h=>h.lv=60);}
  function finish(){cancelAnimationFrame(battleTimer);B.autoUlt=true;for(let i=0;i<1000&&!B.over;i++)simStep();const r=B.result;settleBattle(r);return r.win;}
  const r={};reset();const initial=S.res.gold;startStageBattle(0);r.stage=finish()&&S.stages['1-1']===3;const gained=S.res.gold;closeBattle();closeModal();startStageBattle(0);finish();r.noDuplicateStageReward=S.res.gold===gained&&gained>initial;
  reset();startTowerBattle(1);r.tower=finish()&&S.tower===1;
  reset();startDungeonBattle('gold',1);r.dungeon=finish()&&S.dungeon.used.gold===1&&S.dungeon.best.gold_1>=1&&Number.isFinite(S.res.gold);
  reset();startSeasonBattle(0);r.season=finish()&&!!S.season.cleared[SEASON_STAGES[0].id]&&S.res.stardust>0;
  reset();startArenaBattle(0);r.arena=finish()&&S.arena.wins===1&&S.arena.left===4;
  reset();startExpedition();r.expeditionStarted=S.exp.active;startExpBattle();r.expeditionBattle=finish()&&Object.keys(S.exp.hp).length>0&&S.exp.gains.gold>0;
  reset();const gold=S.res.gold;doUpgrade('taidun',1);r.upgrade=S.heroes.taidun.lv===60&&S.res.gold===gold;S.heroes.taidun.lv=1;doUpgrade('taidun',1);r.upgrade= r.upgrade&&S.heroes.taidun.lv===2&&S.res.gold<gold;
  equipTo(S.equips[0].uid,'taidun');r.equip=S.equips[0].hero==='taidun';unequip(S.equips[0].uid);r.unequip=S.equips[0].hero===null;
  const tickets=S.res.ticket;doSummon(10,"ticket");r.summon=S.res.ticket===tickets-10&&S.counters.summons===10&&S.pity.group===0;
  reset();S.idle.lastCalc=Date.now()-9*3600000;const pending=idlePending();claimIdle();r.idle=pending.mins===480&&S.equips.length===15;
  reset();const dia=S.res.dia;claimMail('m1');claimMail('m1');r.mailOnce=S.res.dia===dia+100;
  const day=gameDay();doSignin();const n=S.signin.days;doSignin();r.signOnce=S.signin.days===n&&S.signin.last===day;
  closeModal();return r;
 });for(const [name,ok]of Object.entries(systems))check('结算系统 '+name,ok);
 await page.evaluate(async()=>{closeBattle();closeModal();S=defaultState();S.storySeen.intro=true;dailyReset();S.heroes.taidun.lv=7;S.res.gold=4321;await saveNow();});
 await page.reload();await page.waitForTimeout(300);check('IndexedDB刷新恢复',await page.evaluate(()=>S.heroes.taidun.lv===7&&S.res.gold===4321));
 check('事务完成才报告成功',await page.evaluate(()=>saveNow()));
 const failed=await page.evaluate(async()=>{const old=dbOpen;dbOpen=()=>Promise.reject(Error('injected'));const ok=await saveNow();dbOpen=old;return {ok,msg:document.querySelector('#toast').textContent};});check('保存失败可见',failed.ok===false&&failed.msg.includes('保存失败'),failed);
 await page.evaluate(()=>{startStageBattle(0);endBattle(true,'win');battleFrame(performance.now());closeBattle();});
 await page.waitForTimeout(750);check('关闭战斗取消延迟结算',await page.evaluate(()=>B===null&&!document.querySelector('#modalwrap').classList.contains('open')));
 const known=await page.evaluate(()=>{const d=defaultState();return {incompleteImportAccepted:validateSave({schemaVersion:1,res:d.res})===null,stringGoldAccepted:validateSave({...d,res:{...d.res,gold:'100'}})===null,migrationMissingDefault:migrate({...d,settings:{sfx:true}}).settings.speed===undefined,soundGate:!window.S};});
 console.log('KNOWN_REMAINING',JSON.stringify(known));
 check('浏览器无未捕获异常',errors.length===0,errors);
 console.log(JSON.stringify({passed:results.length,results,known},null,2));
 if(out)fs.writeFileSync(path.join(out,'test-results.json'),JSON.stringify({passed:results.length,results,known},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>server.close());

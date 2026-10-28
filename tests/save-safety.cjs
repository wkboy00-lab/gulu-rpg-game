// See tests/README.md for the browser dependency and environment variables.
const fs=require('fs'),http=require('http'),path=require('path'),assert=require('assert/strict'),cp=require('child_process');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..'),output=process.env.REVIEW_OUTPUT,results=[],errors=[];
function check(name,ok,detail){results.push({name,pass:!!ok,detail});assert.ok(ok,name+' '+JSON.stringify(detail||''));}
const baseline=cp.execFileSync('git',['-C',root,'show','c5eca890df3464c4007294be0f199e8620a81a79:index.html']);
const server=http.createServer((req,res)=>{
 const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
 if(pathname==='/baseline'){res.setHeader('Content-Type','text/html;charset=utf-8');return res.end(baseline);}
 const file=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
 if(!file.startsWith(root+path.sep)){res.writeHead(403);return res.end();}
 fs.readFile(file,(err,data)=>{res.statusCode=err?404:200;res.setHeader('Content-Type',file.endsWith('.html')?'text/html;charset=utf-8':file.endsWith('.webp')?'image/webp':'text/plain');res.end(err?'missing':data);});
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const url='http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL||'msedge'});
 try{
  const sourceContext=await browser.newContext(),source=await sourceContext.newPage();
  await source.goto(url+'/baseline');await source.waitForTimeout(500);
  const original=await source.evaluate(()=>JSON.parse(JSON.stringify(S)));
  const progressed=await source.evaluate(()=>{
   closeModal();for(let i=0;i<10;i++)debugRes();doUpgrade('taidun',10);doSkillUp('taidun','ult');autoEquip('taidun');doEnhance(S.equips.find(e=>e.hero==='taidun').uid);doSummon(10,'ticket');closeModal();
   shopBuyTier('t6');shopBusy=false;shopBuyCard('month');shopBusy=false;shopClaimCard('month');shopBuyFund();shopBusy=false;shopBuyPass();shopBusy=false;shopClaimWallet();
   S.res.stardust=10000;seasonShopBuy(0);seasonBusy=false;unlockSkinDia('taidun');skinBusy=false;wearSkin('taidun');doSignin();claimAllMail();startExpedition();return JSON.parse(JSON.stringify(S));
  });
  await sourceContext.close();
  const context=await browser.newContext({acceptDownloads:true,viewport:{width:390,height:844}}),page=await context.newPage();
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url);await page.waitForTimeout(500);await page.evaluate(()=>closeModal());
  check('原版c5eca89导出的schema1兼容',await page.evaluate(raw=>validateSave(raw)===null,original));
  const originalCompatibility=await page.evaluate(raw=>validateSave(raw),progressed);
  check('原版养成装备招募商城外观远征进度兼容',originalCompatibility===null,originalCompatibility);
  const matrix=await page.evaluate(original=>{
   const clone=x=>JSON.parse(JSON.stringify(x)),base=clone(original),cases=[];
   function reject(name,change){const v=clone(base);change(v);const before=JSON.stringify(v),error=validateSave(v);cases.push({name,pass:typeof error==='string'&&before===JSON.stringify(v),detail:error});}
   reject('残缺档',v=>{for(const k of Object.keys(v))if(!['schemaVersion','res'].includes(k))delete v[k];});
   reject('未知版本',v=>v.schemaVersion=2);reject('字符串资源',v=>v.res.gold='100');reject('负资源',v=>v.res.gold=-1);reject('无限资源',v=>v.res.gold=Infinity);reject('小数资源',v=>v.res.gold=1.5);
   reject('缺少资源',v=>delete v.res.exp);reject('空资源',v=>v.res=null);reject('未知资源',v=>v.res.surprise=1);
   reject('未知英雄',v=>v.heroes.fake=clone(v.heroes.taidun));reject('零英雄',v=>v.heroes={});reject('等级越界',v=>v.heroes.taidun.lv=61);reject('等级小数',v=>v.heroes.taidun.lv=2.1);
   reject('技能对象缺失',v=>delete v.heroes.taidun.sk);reject('技能超过10',v=>v.heroes.taidun.sk.ult=11);reject('负投入',v=>v.heroes.taidun.spent.gold=-1);reject('英雄标记类型',v=>v.heroes.taidun.isNew=1);
   reject('重复编队',v=>v.formation[1]=v.formation[0]);reject('未拥有英雄编队',v=>v.formation[0]='dengyu');reject('编队长度',v=>v.formation=[]);reject('编队对象',v=>v.formation={});reject('预设数量',v=>v.presets=[]);reject('预设含未知英雄',v=>v.presets[0][0]='missing');
   reject('装备重复UID',v=>v.equips.push(clone(v.equips[0])));reject('装备非法归属',v=>v.equips[0].hero='missing');reject('重复穿戴',v=>{v.equips[0].hero='taidun';v.equips[1].hero='taidun';});
   reject('装备部位',v=>v.equips[0].slot='bad');reject('装备品质',v=>v.equips[0].qual='bad');reject('负装备属性',v=>v.equips[0].stats.atk=-1);reject('未知装备属性',v=>v.equips[0].stats.fake=1);
   reject('装备部位数组不能隐式转字符串',v=>v.equips[0].slot=['weapon']);
   reject('装备强化越界',v=>v.equips[0].lv=11);reject('装备UID注入',v=>v.equips[0].uid="eq');alert(1)//");reject('装备名称HTML',v=>v.equips[0].name='<img src=x onerror=alert(1)>');reject('原型字段',v=>v.extra=JSON.parse('{"__proto__":{"polluted":true}}'));
   reject('无效关卡',v=>v.stages['5-1']=1);reject('关卡星级',v=>v.stages['1-1']=4);reject('副本次数',v=>v.dungeon.used.gold=4);reject('副本星级',v=>v.dungeon.best.gold_1=4);reject('日期不存在',v=>v.lastDay='2026-02-31');
   reject('无效倍速',v=>v.settings.speed=7);reject('设置数组',v=>v.settings=[]);reject('设置字符串布尔',v=>v.settings.sfx='false');reject('负挂机时间',v=>v.idle.lastCalc=-1);reject('挂机超过上限',v=>v.idle.pendMin=481);
   reject('负碎片',v=>v.frags.taidun=-1);reject('保底计数越界',v=>v.pity.sinceSSR=50);reject('邮件ID重复',v=>v.mail.push(clone(v.mail[0])));reject('邮件HTML',v=>v.mail[0].body='<script>alert(1)</script>');
   reject('负模拟钱包',v=>v.shop.wallet=-1);reject('月卡错误结构',v=>v.shop.cards.month=[]);reject('穿未拥有外观',v=>v.skins.worn.taidun=true);reject('未知活动',v=>v.season.cleared.fake=3);
   reject('竞技场次数',v=>v.arena.left=6);reject('竞技场历史错误',v=>v.arena.hist=[null]);reject('远征越界',v=>v.exp.node=7);reject('远征生命越界',v=>v.exp.hp.taidun=1.1);reject('未知远征遗物',v=>v.exp.relics=['fake']);
   reject('进行中远征缺少生命',v=>v.exp.active=true);reject('进行中远征残缺',v=>v.exp={active:true});reject('待选遗物缺失',v=>v.exp.pendingRelic=true);
   const old=clone(base);delete old.shop;delete old.skins;delete old.season;delete old.arena;delete old.exp;delete old.res.stardust;delete old.res.skinTicket;old.settings={sfx:false};
   const before=JSON.stringify(old),m=prepareSave(old);cases.push({name:'旧档补齐嵌套默认值且不修改输入',pass:m.settings.speed===1&&!m.settings.sfx&&m.shop.cards.month.until===0&&m.res.skinTicket===0&&JSON.stringify(old)===before});
   const partial=clone(base);partial.shop={cards:{month:{until:99}},fund:{bought:true}};const p=prepareSave(partial);
   cases.push({name:'卡片基金战令深层默认值',pass:p.shop.cards.month.until===99&&p.shop.cards.month.lastClaim===''&&p.shop.cards.year.until===0&&p.shop.fund.bought&&p.shop.pass.xp===0});
   m.res.gold=1;m.heroes.taidun.lv=2;cases.push({name:'迁移结果与输入不共享引用',pass:old.res.gold!==1&&old.heroes.taidun.lv!==2});
   const subset=clone(base);delete subset.heroes.taidun;subset.formation[0]=null;subset.presets[0][0]=null;
   cases.push({name:'不重新发放默认英雄',pass:!prepareSave(subset).heroes.taidun});
   const upgraded=clone(base);upgraded.heroes.taidun.lv=60;upgraded.equips[0].stats.crit=2.3;upgraded.shop.ledger.push({ts:Date.now(),txt:'购买月卡',amt:-30});
   upgraded.arena.hist=[{day:gameDay(),tier:'正式',win:false,secs:35,delta:-2}];upgraded.skins.owned.taidun=true;upgraded.skins.worn.taidun=true;
   cases.push({name:'合法小数装备与负流水/负战绩通过',pass:validateSave(upgraded)===null,detail:validateSave(upgraded)});
   S=defaultState();S.storySeen.intro=true;dailyReset();return cases;
  },original);
  for(const row of matrix)check(row.name,row.pass,row.detail);
  async function establish(gold=111){
   await page.evaluate(async gold=>{closeModal();closeBattle();S=defaultState();S.storySeen.intro=true;dailyReset();S.res.gold=gold;saveBlocked=false;saveIssue=null;await saveNow();go('settings');},gold);
  }
  async function main(){return page.evaluate(async()=>{await saveQueue;return (await readSaveSlot('main')).value;});}
  async function slots(){return page.evaluate(async()=>({main:(await readSaveSlot('main')).value,backup:(await readSaveSlot('backup')).value}));}
  const candidate=JSON.parse(JSON.stringify(original));candidate.res.gold=222;candidate.storySeen.intro=true;
  await establish();const beforeInvalid=await main();
  await page.locator('#importfile').setInputFiles({name:'invalid.json',mimeType:'application/json',buffer:Buffer.from('{"schemaVersion":1,"res":{}}')});
  await page.waitForTimeout(100);
  check('坏档拒绝且当前内存/磁盘原样保留',await page.evaluate(()=>S.res.gold===111)&&JSON.stringify(await main())===JSON.stringify(beforeInvalid));
  check('坏档有明确反馈',await page.locator('#toast').innerText().then(t=>t.includes('导入失败')));
  await page.locator('#importfile').setInputFiles({name:'broken.json',mimeType:'application/json',buffer:Buffer.from('{')});await page.waitForTimeout(100);
  check('非法JSON保持进度',await page.evaluate(()=>S.res.gold===111)&&JSON.stringify(await main())===JSON.stringify(beforeInvalid));
  await page.locator('#importfile').setInputFiles({name:'large.json',mimeType:'application/json',buffer:Buffer.alloc(5*1024*1024+1,32)});await page.waitForTimeout(100);
  check('文件大小限制',await page.locator('#toast').innerText().then(t=>t.includes('5 MB'))&&await page.evaluate(()=>S.res.gold===111));
  const upload=()=>page.locator('#importfile').setInputFiles({name:'valid.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(candidate))});
  await upload();await page.locator('#doimport').waitFor();
  check('确认前不修改当前进度',await page.evaluate(()=>S.res.gold===111));
  await page.getByRole('button',{name:'取消',exact:true}).click();
  check('取消导入不修改磁盘',JSON.stringify(await main())===JSON.stringify(beforeInvalid));
  await upload();await page.locator('#doimport').click();await page.waitForFunction(()=>!saveBusy&&S.res.gold===222);
  let saved=await slots();check('导入提交main和独立backup',saved.main.res.gold===222&&saved.backup.state.res.gold===111&&saved.backup.reason==='import');
  const backupStable=JSON.stringify(saved.backup);
  await page.evaluate(async()=>{S.res.gold=333;await saveNow();});saved=await slots();
  check('自动保存不冲掉导入前备份',JSON.stringify(saved.backup)===backupStable&&saved.main.res.gold===333);
  await page.reload();await page.waitForFunction(()=>!!S);await page.evaluate(()=>go('settings'));
  await page.getByRole('button',{name:'恢复上次备份',exact:true}).click();await page.locator('#restorebackup').waitFor();
  const downloadPromise=page.waitForEvent('download');await page.locator('#exportbackup').click();const download=await downloadPromise;
  const exported=JSON.parse(fs.readFileSync(await download.path(),'utf8'));
  check('备份导出可用',exported.res.gold===111&&download.suggestedFilename()==='gulu-backup-save.json');
  await page.locator('#restorebackup').click();await page.waitForFunction(()=>!saveBusy&&S.res.gold===111);saved=await slots();
  check('刷新后恢复备份并保留被替换进度',saved.main.res.gold===111&&saved.backup.state.res.gold===333);
  await page.evaluate(()=>resetGame());await page.getByRole('button',{name:'确认重置',exact:true}).click();await page.waitForFunction(()=>!saveBusy&&S.res.gold===5000);saved=await slots();
  check('重置前保留可恢复进度',saved.main.res.gold===5000&&saved.backup.state.res.gold===111&&saved.backup.reason==='reset');
  await establish(444);const beforeAbort=await slots();
  await page.evaluate(()=>{window.originalPut=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(value,key){if(key==='main'){this.transaction.abort();throw new DOMException('injected abort','AbortError');}return window.originalPut.call(this,value,key);};});
  await upload();await page.locator('#doimport').click();await page.waitForFunction(()=>!saveBusy);
  await page.evaluate(()=>{IDBObjectStore.prototype.put=window.originalPut;});
  check('事务中断后main和backup均回滚',JSON.stringify(await slots())===JSON.stringify(beforeAbort));
  check('中断后内存和按钮可重试',await page.evaluate(()=>S.res.gold===444&&!document.querySelector('#doimport').disabled&&!document.querySelector('#stage').inert));
  await page.locator('#doimport').click();await page.waitForFunction(()=>!saveBusy&&S.res.gold===222);
  check('失败后的重试可成功',(await main()).res.gold===222);
  const race=await page.evaluate(async()=>{
   const realOpen=dbOpen;dbOpen=async()=>{await new Promise(r=>setTimeout(r,60));return realOpen();};
   S.res.gold=101;const first=saveNow();S.res.gold=202;const imported=saveClone(S);imported.res.gold=303;
   openModal('<h3 id="pending-save-title">正在确认</h3>');
   const replace=replaceSave(imported,'import');const during=S.res.gold;const duplicate=await replaceSave(imported,'import');const wasInert=document.querySelector('#stage').inert;go('bag');const frozen=V.name!=='bag';
   openModal('<h3>错误覆盖弹窗</h3>');closeModal();const dialogKept=!!document.querySelector('#pending-save-title')&&document.querySelector('#modalwrap').classList.contains('open');
   startStageBattle(0);const noBattle=B===null;
   await Promise.all([first,replace]);dbOpen=realOpen;
   return {during,duplicate,wasInert,frozen,dialogKept,noBattle,gold:S.res.gold,main:(await readSaveSlot('main')).value.res.gold,backup:(await readSaveSlot('backup')).value.state.res.gold};
  });check('保存与导入串行且成功前不发布状态',race.during===202&&!race.duplicate&&race.wasInert&&race.frozen&&race.dialogKept&&race.noBattle&&race.gold===303&&race.main===303&&race.backup===202,race);
  check('进行中战斗拒绝替换存档',await page.evaluate(async()=>{startStageBattle(0);togglePause();const before=JSON.stringify(S);const result=await replaceSave(defaultState(),'import');const unchanged=!result&&JSON.stringify(S)===before;closeBattle();return unchanged;}));
  await page.evaluate(async()=>{S.idle.lastCalc=Date.now()+3600000;const p=idlePending();window.futureIdleOK=p.gold>=0&&p.exp>=0;await saveNow();});
  check('系统时钟回拨不产生负挂机收益',await page.evaluate(()=>window.futureIdleOK));
  const preserved=await page.evaluate(async()=>{
   const bad={schemaVersion:2,originalProgress:'保留原档',res:{gold:9876}};
   const db=await dbOpen();await new Promise((r,j)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).put(bad,'main');tx.oncomplete=r;tx.onerror=()=>j(tx.error);});db.close();return bad;
  });
  await page.reload();await page.getByRole('heading',{name:'进度暂未载入',exact:true}).waitFor();await page.waitForTimeout(350);
  check('不兼容档启动阻止自动覆盖',JSON.stringify(await main())===JSON.stringify(preserved)&&await page.evaluate(()=>S===null&&saveBlocked));
  if(output)await page.screenshot({path:path.join(output,'save-recovery.png')});
  const rawDownloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'导出原档',exact:true}).click();const rawDownload=await rawDownloadPromise;
  check('恢复页面可导出原档',JSON.stringify(JSON.parse(fs.readFileSync(await rawDownload.path(),'utf8')))===JSON.stringify(preserved));
  await page.getByRole('button',{name:'恢复备份',exact:true}).click();await page.locator('#restorebackup').click();await page.waitForFunction(()=>!saveBusy&&!!S);
  const recovered=await page.evaluate(async()=>({gold:S.res.gold,blocked:saveBlocked,archive:(await readSaveSlot('rejected')).value,backup:(await readSaveSlot('backup')).value}));
  check('坏档恢复保留原始数据且保留好备份',recovered.gold===202&&!recovered.blocked&&JSON.stringify(recovered.archive.raw)===JSON.stringify(preserved)&&recovered.backup.state.res.gold===202);
  // Failed initial reads must not be confused with an empty database.
  await page.addInitScript(()=>{const proto=IDBFactory.prototype;window.realOpen=proto.open;proto.open=function(){throw new Error('injected read failure');};});
  const expectedGood=await main();await page.reload();await page.getByRole('heading',{name:'进度暂未载入',exact:true}).waitFor();
  await page.evaluate(()=>{IDBFactory.prototype.open=window.realOpen;});
  check('读取失败时磁盘进度不变',JSON.stringify(await main())===JSON.stringify(expectedGood));
  check('读取失败状态禁止覆盖',await page.evaluate(async()=>{const old=JSON.stringify((await readSaveSlot('main')).value);const result=await replaceSave(defaultState(),'reset');return !result&&JSON.stringify((await readSaveSlot('main')).value)===old;}));
  // Remove the injection by using a fresh page in the same storage context.
  await page.close();const fresh=await context.newPage();fresh.on('pageerror',e=>errors.push(e.message));await fresh.goto(url);await fresh.waitForFunction(()=>!!S);
  await fresh.evaluate(async()=>{
   const db=await dbOpen();await new Promise((r,j)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).put(null,'main');tx.oncomplete=r;tx.onerror=()=>j(tx.error);});db.close();
  });await fresh.reload();await fresh.getByRole('heading',{name:'进度暂未载入',exact:true}).waitFor();
  check('null坏档与空数据库明确区分',await fresh.evaluate(async()=>{const slot=await readSaveSlot('main');return slot.exists&&slot.value===null&&S===null&&saveBlocked;}));
  await fresh.evaluate(async()=>{
   const db=await dbOpen();await new Promise((r,j)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).put({schemaVersion:1,res:{}},'main');tx.oncomplete=r;tx.onerror=()=>j(tx.error);});db.close();
  });await fresh.reload();await fresh.getByRole('heading',{name:'进度暂未载入',exact:true}).waitFor();
  await fresh.getByRole('button',{name:'重新开始',exact:true}).click();await fresh.getByRole('button',{name:'确认重置',exact:true}).click();await fresh.waitForFunction(()=>!!S&&!saveBusy);
  check('坏档重新开始先保留原数据',await fresh.evaluate(async()=>{const a=(await readSaveSlot('rejected')).value;return S.res.gold===5000&&a.raw.schemaVersion===1&&Object.keys(a.raw.res).length===0;}));
  await fresh.evaluate(()=>{closeModal();go('settings');});await fresh.waitForTimeout(200);
  const preservedDownloadPromise=fresh.waitForEvent('download');await fresh.getByRole('button',{name:'导出保留的异常原档',exact:true}).click();const preservedDownload=await preservedDownloadPromise;
  check('重新开始后仍可下载异常原档',JSON.stringify(JSON.parse(fs.readFileSync(await preservedDownload.path(),'utf8')))===JSON.stringify({schemaVersion:1,res:{}}));
  await fresh.waitForTimeout(300);
  check('重置后的延迟序章不打断存档页面',await fresh.evaluate(()=>V.name==='settings'&&!document.querySelector('#modalwrap').classList.contains('open')));
  await fresh.evaluate(()=>{S.storySeen.boss1=false;go('prebattle',9);go('settings');});await fresh.waitForTimeout(150);
  check('离开战前后延迟Boss剧情不会覆盖存档页面',await fresh.evaluate(()=>V.name==='settings'&&!document.querySelector('#modalwrap').classList.contains('open')));
  await fresh.evaluate(()=>document.querySelector('#view').scrollTo(0,360));await fresh.waitForTimeout(250);
  if(output)await fresh.screenshot({path:path.join(output,'save-settings.png')});
  check('全程无浏览器未捕获异常',errors.length===0,errors);await context.close();
  const report={passed:results.length,results};console.log(JSON.stringify(report,null,2));if(output)fs.writeFileSync(path.join(output,'save-safety-results.json'),JSON.stringify(report,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>server.close());

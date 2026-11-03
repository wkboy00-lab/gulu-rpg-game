const { chromium } = require('/home/hatch/workspace/.shot/node_modules/playwright-core');
const CHROME = '/home/hatch/workspace/.shot-browsers/chrome-linux64/chrome';
const BASE = 'http://localhost:8938/index.html';
const SHOTS = '/home/hatch/workspace/.shot/shots/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const results = [];
function check(name, ok, extra) {
  results.push({ name, ok: !!ok, extra: extra || '' });
  console.log((ok ? 'PASS ' : 'FAIL ') + name + (extra ? ' :: ' + extra : ''));
}
function seedFn() { let s = 987654321; Math.random = function(){ s|=0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s>>>15, 1|s); t = t + Math.imul(t ^ t>>>7, 61|t) ^ t; return ((t ^ t>>>14)>>>0)/4294967296; }; }
async function clickSel(page, sel, idx) {
  const el = page.locator(sel).nth(idx || 0);
  await el.waitFor({ state: 'visible', timeout: 8000 });
  const box = await el.boundingBox();
  if (!box) throw new Error('no box for ' + sel);
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
}
async function newPage(browser, w, h, seed) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h } });
  if (seed) await ctx.addInitScript(seedFn);
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/favicon/i.test(m.text())) errs.push('console: ' + m.text()); });
  return { ctx, page, errs };
}
async function readSave(page, key) {
  return await page.evaluate(k => {
    const raw = localStorage.getItem(k);
    return raw ? JSON.parse(raw) : null;
  }, key);
}
async function dbg(page) {
  return await page.evaluate(() => (window.TEAM1_DEBUG ? window.TEAM1_DEBUG.getState() : null));
}
async function startStage0(page) {
  await clickSel(page, '.cta');
  await page.waitForFunction(() => document.body.innerText.includes('推图'), null, { timeout: 8000 });
  await clickSel(page, 'button[onclick="startStage(0)"]');
  await page.waitForSelector('#battle', { timeout: 8000 });
  await page.waitForFunction(() => document.querySelectorAll('.fig').length >= 8, null, { timeout: 8000 });
}
async function waitPanel(page, secs) {
  await page.waitForSelector('.result', { timeout: (secs || 90) * 1000 });
}

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  const allErrs = [];
  try {
    // ===== Test 1: version / no energy-ult text / isolated save key =====
    {
      const { ctx, page, errs } = await newPage(browser, 390, 844, false);
      await page.goto(BASE + '?savekey=team1-t1', { waitUntil: 'load' });
      await page.evaluate(() => go('settings'));
      await sleep(300);
      const txt = await page.evaluate(() => document.body.innerText);
      check('version team1 shown in settings', txt.includes('2026.11.03-team1'));
      check('settings shows isolated savekey', txt.includes('team1-t1'));
      const keys = await page.evaluate(() => Object.keys(localStorage));
      check('main save key untouched in fresh profile', !keys.includes('gulu-mtstyle-v1'), keys.join(','));
      await page.evaluate(() => go('heroes'));
      await sleep(300);
      const htxt = await page.evaluate(() => document.body.innerText);
      check('no energy/ult wording in heroes view', !htxt.includes('能量') && !htxt.includes('大招'));
      check('hero skill line lists 3 skills only', /普攻.*主动.*被动/.test(htxt));
      await page.screenshot({ path: SHOTS + 'team1-home-390.png' });
      allErrs.push(...errs);
      await ctx.close();
    }
    // ===== Test 2a: 1-1 real clicks: early active evidence + poses + panel =====
    {
      const { ctx, page, errs } = await newPage(browser, 390, 844, false);
      await page.goto(BASE + '?savekey=team1-t2', { waitUntil: 'load' });
      await startStage0(page);
      const figs = await page.evaluate(() => ({
        allies: document.querySelectorAll('.fig.ally').length,
        foes: document.querySelectorAll('.fig.foe').length,
        tfig: !!document.querySelector('[data-tfig]'),
        layers: [...document.querySelectorAll('[data-tfig] img')].filter(i => i.naturalWidth > 0).length,
        lids: document.querySelectorAll('[data-tfig] .tlid').length,
        enBar: document.querySelectorAll('.bar.en').length
      }));
      check('5 allies vs 3 foes', figs.allies === 5 && figs.foes === 3, JSON.stringify(figs));
      check('Taidun layered figure with 5 loaded layers + 2 lids', figs.tfig && figs.layers === 5 && figs.lids === 2, JSON.stringify(figs));
      check('no energy bar in battle', figs.enBar === 0);
      const bob = await page.evaluate(() => {
        const imgs = [...document.querySelectorAll('.fig.ally .figimg img')].filter(i => !i.closest('[data-tfig]'));
        return imgs.map(i => getComputedStyle(i).animationName);
      });
      check('placeholder heroes static (no float animation)', bob.every(n => n === 'none'), bob.join(','));
      const meta = await page.evaluate(() => (document.getElementById('battlemeta') || {}).textContent || '');
      check('battle meta states 3 skills only', meta.includes('只保留普攻'), meta);
      // early active evidence: poll from battle start
      let activeSeen = false, bubbleSeen = false, tauntSeen = false;
      for (let i = 0; i < 100; i++) {
        const r = await page.evaluate(() => ({
          blog: (document.getElementById('blog') || {}).textContent || '',
          disp: (() => { const b = document.querySelector('[data-bubble]'); return b ? getComputedStyle(b).display : 'none'; })(),
          taunt: [...document.querySelectorAll('.fig.foe .figmeta')].map(e => e.textContent).join('|').includes('嘲讽中'),
          over: !window.TEAM1_DEBUG || !window.TEAM1_DEBUG.getState()
        }));
        if (r.blog.includes('盾牌前顶')) activeSeen = true;
        if (r.disp === 'block') bubbleSeen = true;
        if (r.taunt) tauntSeen = true;
        if (activeSeen && bubbleSeen && tauntSeen) break;
        if (r.over) break;
        await sleep(120);
      }
      check('Taidun active settles at front-shield frame (log)', activeSeen);
      check('shield bubble visible while shield up', bubbleSeen);
      check('taunt tag on foes after active', tauntSeen);
      // pose sampling + contact measurement
      const seen = new Set(); let minGap = 999; let shotTaken = false;
      for (let i = 0; i < 60; i++) {
        const s = await page.evaluate(() => {
          const tf = document.querySelector('[data-tfig]');
          if (!tf) return { cls: '', gap: null };
          const cls = tf.className;
          let gap = null;
          if (cls.includes('contact') || cls.includes('lunge')) {
            const hr = tf.getBoundingClientRect();
            const gaps = [...document.querySelectorAll('.fig.foe .figimg')].map(el => el.getBoundingClientRect().left - hr.right);
            gap = Math.min(...gaps);
          }
          return { cls, gap };
        });
        s.cls.split(' ').forEach(c => { if (c) seen.add(c); });
        if (s.gap !== null && s.gap < minGap) minGap = s.gap;
        if (s.cls.includes('contact') && !shotTaken) { shotTaken = true; await page.screenshot({ path: SHOTS + 'team1-battle-390.png' }); }
        const st = await dbg(page);
        if (!st) break;
        await sleep(150);
      }
      check('Taidun windup pose seen', seen.has('windup'), [...seen].join(','));
      check('Taidun lunge pose seen', seen.has('lunge'), [...seen].join(','));
      check('Taidun contact pose seen', seen.has('contact'), [...seen].join(','));
      check('shield edge reaches target at contact (gap<=14px)', minGap <= 14, 'minGap=' + minGap);
      // finish via skip if battle still running
      const stMid = await dbg(page);
      if (stMid) { await clickSel(page, 'button[onclick="skipBattle()"]'); }
      await waitPanel(page, 20);
      const panelTxt = await page.evaluate(() => document.body.innerText);
      check('settlement panel shows stars + reward', panelTxt.includes('星通关') && panelTxt.includes('金币 +120'));
      await page.screenshot({ path: SHOTS + 'team1-result-390.png' });
      allErrs.push(...errs);
      await ctx.close();
    }
    // ===== Test 2b: long custom battle: pause freeze + 3x speed =====
    {
      const { ctx, page, errs } = await newPage(browser, 390, 844, false);
      await page.goto(BASE + '?savekey=team1-t2b', { waitUntil: 'load' });
      await page.evaluate(() => {
        startBattle({ title: 'test-long', specs: [{ eid: 'E01', lv: 12, mod: '', row: 0 }, { eid: 'E01', lv: 12, mod: '', row: 0 }, { eid: 'E01', lv: 12, mod: '', row: 0 }], onEnd: function () {} });
      });
      await page.waitForFunction(() => document.querySelectorAll('.fig').length >= 8, null, { timeout: 8000 });
      await sleep(1500);
      const st0 = await dbg(page);
      check('long battle running for pause/speed checks', !!st0 && st0.t > 0, JSON.stringify(st0));
      await clickSel(page, '#btnPause2');
      await sleep(200);
      const pausedCls = await page.evaluate(() => (document.getElementById('bstage') || {}).className || '');
      const t2a = (await dbg(page)).t;
      await sleep(900);
      const t2 = (await dbg(page)).t;
      check('pause freezes battle time exactly', t2a === t2, 't2a=' + t2a + ' t2=' + t2);
      check('stage gets paused class (CSS anims frozen)', pausedCls.includes('paused'), pausedCls);
      await clickSel(page, '#btnPause2');
      await sleep(600);
      const t3 = (await dbg(page)).t;
      check('resume advances battle time', t3 > t2, 't2=' + t2 + ' t3=' + t3);
      await clickSel(page, '#btnSpeed2');
      await clickSel(page, '#btnSpeed2');
      const spdTxt = await page.evaluate(() => (document.getElementById('btnSpeed2') || {}).textContent || '');
      const ta = (await dbg(page)).t;
      await sleep(900);
      const tb = (await dbg(page)).t;
      check('speed button reaches 3x', spdTxt.includes('3×'), spdTxt);
      check('3x advances ~3x battle time', (tb - ta) >= 2000 && (tb - ta) <= 3600, 'adv=' + (tb - ta));
      await clickSel(page, '#btnSpeed2');
      await clickSel(page, 'button[onclick="skipBattle()"]');
      await sleep(500);
      const ovHidden = await page.evaluate(() => document.getElementById('battle').style.display === 'none');
      check('skip ends custom battle without error', ovHidden);
      allErrs.push(...errs);
      await ctx.close();
    }
    // ===== Test 3: seeded auto vs skip consistency =====
    async function runBattle(key, doSkip) {
      const { ctx, page, errs } = await newPage(browser, 390, 844, true);
      await page.goto(BASE + '?savekey=' + key, { waitUntil: 'load' });
      await startStage0(page);
      if (doSkip) { await sleep(500); await clickSel(page, 'button[onclick="skipBattle()"]'); }
      await waitPanel(page, 90);
      const panel = await page.evaluate(() => ({
        stars: (document.querySelector('.result .stars') || {}).textContent || '',
        txt: document.body.innerText
      }));
      const sv = await readSave(page, key);
      allErrs.push(...errs);
      await ctx.close();
      return { stars: panel.stars, alive: (panel.txt.match(/存活 (\d)\/5/) || [])[1], gold: sv.res.gold, exp: sv.res.exp, stages: sv.stages, equips: sv.equips.length, battles: sv.daily.counters.battles };
    }
    const runA = await runBattle('team1-auto', false);
    const runB = await runBattle('team1-skip', true);
    console.log('auto:', JSON.stringify(runA), 'skip:', JSON.stringify(runB));
    check('seeded auto vs skip: same stars/alive/rewards', runA.stars === runB.stars && runA.alive === runB.alive && runA.gold === runB.gold && runA.exp === runB.exp && JSON.stringify(runA.stages) === JSON.stringify(runB.stages), 'auto=' + JSON.stringify(runA) + ' skip=' + JSON.stringify(runB));
    check('single settlement: gold +120 exactly', runA.gold === 5120 && runA.exp === 3060, 'gold=' + runA.gold + ' exp=' + runA.exp);
    // ===== Test 4: double-click protection + refight + refresh =====
    {
      const { ctx, page, errs } = await newPage(browser, 390, 844, true);
      await page.goto(BASE + '?savekey=team1-dbl', { waitUntil: 'load' });
      await clickSel(page, '.cta');
      await page.waitForFunction(() => document.body.innerText.includes('推图'), null, { timeout: 8000 });
      const btn = page.locator('button[onclick="startStage(0)"]');
      const box = await btn.boundingBox();
      await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
      await sleep(400);
      const st0 = await dbg(page);
      check('double-click challenge starts one battle', !!st0 && st0.t >= 0);
      const sk = page.locator('button[onclick="skipBattle()"]');
      const skb = await sk.boundingBox();
      await page.mouse.click(skb.x + skb.width / 2, skb.y + skb.height / 2);
      await page.mouse.click(skb.x + skb.width / 2, skb.y + skb.height / 2);
      await waitPanel(page, 20);
      let sv = await readSave(page, 'team1-dbl');
      check('double-click skip settles once (gold +120)', sv.res.gold === 5120, 'gold=' + sv.res.gold);
      await clickSel(page, '#bbox button[onclick="startStage(0)"]');
      await sleep(400);
      await clickSel(page, 'button[onclick="skipBattle()"]');
      await waitPanel(page, 20);
      sv = await readSave(page, 'team1-dbl');
      check('refight settles once more (gold +120 again)', sv.res.gold === 5240, 'gold=' + sv.res.gold);
      await clickSel(page, 'button[onclick="backToMap()"]');
      await sleep(300);
      const ovHidden = await page.evaluate(() => document.getElementById('battle').style.display === 'none');
      check('return button hides overlay back to map', ovHidden);
      await page.reload({ waitUntil: 'load' });
      await sleep(400);
      sv = await readSave(page, 'team1-dbl');
      check('refresh keeps rewards (no duplicate)', sv.res.gold === 5240 && (sv.stages['0'] || sv.stages[0]) >= 1, 'gold=' + sv.res.gold + ' stages=' + JSON.stringify(sv.stages));
      allErrs.push(...errs);
      await ctx.close();
    }
    // ===== Test 5: mid-battle refresh applies nothing =====
    {
      const { ctx, page, errs } = await newPage(browser, 390, 844, false);
      await page.goto(BASE + '?savekey=team1-mid', { waitUntil: 'load' });
      await startStage0(page);
      await sleep(1200);
      await page.reload({ waitUntil: 'load' });
      await sleep(400);
      const sv = await readSave(page, 'team1-mid');
      const ovHidden = await page.evaluate(() => getComputedStyle(document.getElementById('battle')).display === 'none');
      check('mid-battle refresh: no reward, no progress', sv.res.gold === 5000 && Object.keys(sv.stages).length === 0 && ovHidden, 'gold=' + sv.res.gold);
      allErrs.push(...errs);
      await ctx.close();
    }
    // ===== Test 6: defeat (no reward) + passive + defeat panel UI =====
    {
      const { ctx, page, errs } = await newPage(browser, 390, 844, false);
      await page.goto(BASE + '?savekey=team1-lose', { waitUntil: 'load' });
      await page.evaluate(() => {
        window.__res = null;
        startBattle({ title: 'test', specs: [{ eid: 'BOSS', lv: 30, mod: '', row: 0, bossKey: '1' }, { eid: 'E01', lv: 35, mod: '', row: 0 }, { eid: 'E01', lv: 35, mod: '', row: 0 }, { eid: 'E01', lv: 35, mod: '', row: 0 }, { eid: 'E01', lv: 35, mod: '', row: 0 }], onEnd: function (win) { window.__res = win; } });
      });
      let passiveSeen = false, minHp = 99999, tdMax = 0;
      for (let i = 0; i < 200; i++) {
        const r = await page.evaluate(() => ({
          blog: (document.getElementById('blog') || {}).textContent || '',
          res: window.__res,
          td: (() => { const st = window.TEAM1_DEBUG ? window.TEAM1_DEBUG.getState() : null; const u = st ? st.units.find(x => x.hid === 'taidun') : null; return u ? { hp: u.hp, maxHp: u.maxHp } : null; })()
        }));
        if (r.blog.includes('虽然害怕')) passiveSeen = true;
        if (r.td) { if (r.td.hp < minHp) minHp = r.td.hp; tdMax = r.td.maxHp; }
        if (r.res === false) break;
        await sleep(250);
      }
      const tdThresh = Math.floor(tdMax * 0.35);
      const res = await page.evaluate(() => window.__res);
      const sv = await page.evaluate(() => ({ res: S.res, stages: S.stages }));
      check('strong foes defeat the team', res === false, 'res=' + res);
      check('Taidun passive fires when first below 35% (log)', passiveSeen);
      check('Taidun actually dropped below 35% first', minHp < tdThresh, 'minHp=' + minHp + ' thresh=' + tdThresh);
      check('defeat gives no reward', sv.res.gold === 5000, 'gold=' + sv.res.gold);
      await page.evaluate(() => showStageResult({ win: false, stageIdx: 0 }));
      await sleep(200);
      const ptxt = await page.evaluate(() => document.body.innerText);
      check('defeat panel renders', ptxt.includes('战斗失败') && ptxt.includes('返回推图'));
      await clickSel(page, 'button[onclick="backToMap()"]');
      await sleep(300);
      const ovHidden = await page.evaluate(() => document.getElementById('battle').style.display === 'none');
      check('defeat panel return button works', ovHidden);
      await page.evaluate(() => showStageResult({ win: false, stageIdx: 0 }));
      await clickSel(page, '#bbox button[onclick="startStage(0)"]');
      await sleep(400);
      const st = await dbg(page);
      check('defeat panel refight starts a real battle', !!st);
      await clickSel(page, 'button[onclick="quitBattle()"]');
      allErrs.push(...errs);
      await ctx.close();
    }
    // ===== Test 7: 320x568 layout =====
    {
      const { ctx, page, errs } = await newPage(browser, 320, 568, false);
      await page.goto(BASE + '?savekey=team1-320', { waitUntil: 'load' });
      await page.screenshot({ path: SHOTS + 'team1-home-320.png' });
      await startStage0(page);
      await sleep(1500);
      const lay = await page.evaluate(() => {
        const sw = document.documentElement.scrollWidth;
        const figs = [...document.querySelectorAll('.fig')].map(f => { const r = f.getBoundingClientRect(); return { l: r.left, r: r.right }; });
        const layers = [...document.querySelectorAll('[data-tfig] img')].filter(i => i.naturalWidth > 0).length;
        const btns = [...document.querySelectorAll('#bbox .btnrow .btn')].map(b => { const r = b.getBoundingClientRect(); return Math.round(r.width) + 'x' + Math.round(r.height); });
        return { sw, figs, layers, btns };
      });
      check('320px: no horizontal overflow', lay.sw <= 320, 'scrollWidth=' + lay.sw);
      check('320px: all figures inside viewport', lay.figs.every(f => f.l >= -1 && f.r <= 321), JSON.stringify(lay.figs));
      check('320px: Taidun layers loaded', lay.layers === 5);
      console.log('320px battle buttons: ' + lay.btns.join(', '));
      await page.screenshot({ path: SHOTS + 'team1-battle-320.png' });
      allErrs.push(...errs);
      await ctx.close();
    }
  } catch (e) {
    console.log('HARNESS ERROR: ' + (e && e.stack || e));
    results.push({ name: 'harness', ok: false, extra: String(e && e.message || e) });
  } finally {
    await browser.close();
  }
  const fails = results.filter(r => !r.ok);
  console.log('==== ' + (results.length - fails.length) + '/' + results.length + ' passed; console/page errors: ' + allErrs.length);
  allErrs.slice(0, 10).forEach(e => console.log('ERR: ' + e));
  if (fails.length || allErrs.length) process.exit(1);
  console.log('ALL GREEN');
})();

// Continuous recording: home -> map 1-1 -> five-hero battle (1x) -> result -> back to map.
// Desktop Chrome simulation, 390x844.
const { chromium } = require('/home/hatch/workspace/.shot/node_modules/playwright-core');
const fs = require('fs');
const CHROME = '/home/hatch/workspace/.shot-browsers/chrome-linux64/chrome';
const URL = 'http://127.0.0.1:8938/index.html?savekey=team1-rec';
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, recordVideo: { dir: '/home/hatch/workspace/.shot/shots/', size: { width: 390, height: 844 } } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('dialog', d => { errors.push('DIALOG: ' + d.message()); d.dismiss(); });
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await page.goto(URL, { waitUntil: 'load' });
  await sleep(1800); // 主城 + 苔盾分层待机
  const clickSel = async sel => {
    const box = await page.evaluate(sel => {
      const e = document.querySelector(sel); if (!e) return null;
      e.scrollIntoView({ block: 'center' });
      const r = e.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }, sel);
    if (!box) { console.log('MISS', sel); return false; }
    await page.mouse.click(box.x, box.y);
    return true;
  };
  await clickSel('.cta'); await sleep(900); // 推图
  await clickSel('button[onclick="startStage(0)"]'); // 1-1 挑战
  await page.waitForSelector('#bstage', { timeout: 10000 });
  await page.waitForSelector('.result', { timeout: 90000 }); // 1x 打完
  const res = await page.evaluate(() => document.querySelector('.result').textContent.slice(0, 60));
  console.log('result panel:', res);
  await sleep(2500); // 结算面板停留
  await clickSel('#bbox button[onclick="backToMap()"]');
  await sleep(1500); // 回到推图
  const videoPath = await page.video().path();
  await ctx.close();
  await browser.close();
  const dest = '/home/hatch/workspace/gulu-battle-team/battle-team-v1-walkthrough.webm';
  fs.renameSync(videoPath, dest);
  const st = fs.statSync(dest);
  console.log('video:', dest, st.size, 'bytes; errors:', errors.length ? errors.join('|') : 'none');
})().catch(e => { console.error('RECORD FAIL', e); process.exit(1); });

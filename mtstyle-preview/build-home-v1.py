# -*- coding: utf-8 -*-
"""主城 v1 重做补丁：只改主城（顶栏 HUD + vHome + 弹出层 + 挂机宝箱流程）。
其它视图、战斗引擎、数值、存档键一律不动。运行前 index.html 已备份为 index-round4-backup.html。"""
import base64, io, sys
from PIL import Image

P = '/home/hatch/workspace/gulu-mtstyle-preview/index.html'
s = open(P, encoding='utf-8').read()
orig_len = len(s)

def rep(old, new, tag):
    global s
    assert old in s, 'ANCHOR MISSING: ' + tag
    s = s.replace(old, new, 1)

# ---------- 1) 场景图：城市原画全图（去纸面留白已验证不需要，整幅即场景） ----------
im = Image.open('/home/hatch/workspace/gulu-handover/game/assets/city.webp').convert('RGB')
im.thumbnail((920, 1640))
buf = io.BytesIO(); im.save(buf, 'JPEG', quality=80)
scene_b64 = base64.b64encode(buf.getvalue()).decode()
print('scene jpg bytes:', len(buf.getvalue()), 'size:', im.size)
idx = s.index('/* 立绘')
end_art = s.rfind('};', 0, idx)
assert end_art > 0
s = s[:end_art] + ',"scene":"data:image/jpeg;base64,' + scene_b64 + '"' + s[end_art:]

# ---------- 2) CSS：HUD + 城市场景 + 弹出层（追加到第二个 <style> 末尾） ----------
CSS = """
/* === 主城 v1：完整公会场景（仅主城使用；其它界面逻辑不动）=== */
#topbar{padding:6px 8px}
.toprow{display:flex;align-items:center;gap:8px}
.logo{display:flex;align-items:center;gap:6px;font-size:17px;font-weight:900;letter-spacing:1px;color:#ffe9b8;text-shadow:0 2px 0 #7a4a12,0 2px 6px rgba(0,0,0,.5);white-space:nowrap}
.logo svg{width:30px;height:30px;flex:none;filter:drop-shadow(0 2px 2px rgba(0,0,0,.4))}
.logo small{font-size:10px;color:#d5c09a;font-weight:700;letter-spacing:2px;display:block;line-height:1}
.top-acts{margin-left:auto;display:flex;gap:6px;flex:none}
.icbtn{position:relative;width:34px;height:34px;border-radius:50%;border:1.5px solid #c9962f;background:linear-gradient(180deg,#f6c453,#dda63a);display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 2px 0 #8a5a12;padding:0}
.icbtn:active{transform:translateY(1px);box-shadow:none}
.icbtn:disabled{opacity:.45;cursor:not-allowed}
.icbtn svg{width:20px;height:20px}
.resrow{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;margin-top:6px;padding-bottom:1px}
.resrow::-webkit-scrollbar{display:none}
.res{display:flex;align-items:center;gap:4px;background:rgba(0,0,0,.45);border:1px solid rgba(255,224,154,.28);border-radius:999px;padding:3px 8px 3px 4px;font-size:12.5px;font-weight:700;color:#ffe9b8;white-space:nowrap}
.res svg{width:17px;height:17px;flex:none}
.dot{position:absolute;top:-4px;right:-4px;min-width:16px;height:16px;border-radius:999px;background:#e05a4e;color:#fff;font-size:10.5px;font-weight:900;display:flex;align-items:center;justify-content:center;padding:0 4px;border:2px solid #fff3cd;box-shadow:0 1px 4px rgba(0,0,0,.4);z-index:2}
.city{position:relative;overflow:hidden;height:calc(100svh - 156px);min-height:340px;background:#d9c9a0}
.city-bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 38%}
.city-vig{position:absolute;inset:0;background:linear-gradient(180deg,rgba(60,40,15,.14),rgba(60,40,15,0) 30%,rgba(60,40,15,0) 62%,rgba(50,32,10,.40));pointer-events:none}
.glow{position:absolute;width:76px;height:76px;border-radius:50%;background:radial-gradient(circle,rgba(255,214,120,.55),rgba(255,214,120,0) 65%);animation:glowpulse 3.4s ease-in-out infinite;pointer-events:none}
.glow.g1{left:5%;top:32%}.glow.g2{right:4%;top:34%;animation-delay:1.2s}
@keyframes glowpulse{0%,100%{opacity:.5}50%{opacity:1}}
.mote{position:absolute;width:6px;height:6px;border-radius:50%;background:radial-gradient(circle,#fffbe0,#f2b63c);box-shadow:0 0 8px 2px rgba(255,220,130,.7);opacity:0;animation:mote 8s linear infinite;pointer-events:none}
@keyframes mote{0%{opacity:0;transform:translateY(14px)}18%{opacity:.9}70%{opacity:.7}100%{opacity:0;transform:translateY(-46px) translateX(10px)}}
.mote.m1{left:22%;top:58%}.mote.m2{left:38%;top:66%;animation-delay:2.2s;animation-duration:9s}.mote.m3{left:56%;top:60%;animation-delay:1.1s}.mote.m4{left:70%;top:70%;animation-delay:3.4s;animation-duration:7s}.mote.m5{left:14%;top:74%;animation-delay:4.1s}.mote.m6{left:82%;top:62%;animation-delay:5s;animation-duration:9.5s}.mote.m7{left:47%;top:72%;animation-delay:6s}.mote.m8{left:30%;top:46%;animation-delay:2.8s}
.hs{position:absolute;display:flex;flex-direction:column;align-items:center;gap:3px;background:none;border:0;padding:0;cursor:pointer;z-index:3;filter:drop-shadow(0 4px 5px rgba(40,25,8,.45));width:66px}
.hs:active{transform:scale(.92)}
.hs-ic{width:52px;height:52px;border-radius:50%;border:2.5px solid #ffe09a;background:linear-gradient(180deg,#8a5a3b,#65452e);display:flex;align-items:center;justify-content:center;box-shadow:inset 0 2px 0 rgba(255,255,255,.25),0 3px 0 #3c2716}
.hs-ic svg{width:30px;height:30px}
.hs-lb{background:linear-gradient(180deg,#fff3cd,#eed9a0);border:1.5px solid #8a5a12;color:#2b1c10;font-size:11.5px;font-weight:800;padding:2px 8px;border-radius:999px;white-space:nowrap;box-shadow:0 2px 4px rgba(0,0,0,.3)}
.hs-guild{left:calc(50% - 33px);top:37%}
.hs-tavern{left:6%;top:35%}
.hs-smith{right:6%;top:37%}
.hs-board{left:5%;top:57%}
.dock{position:absolute;right:7px;top:56%;display:flex;flex-direction:column;gap:7px;z-index:3}
.dock button{width:46px;padding:4px 0 3px;border-radius:12px;border:1.5px solid #8a5a12;background:linear-gradient(180deg,rgba(255,243,205,.96),rgba(238,217,160,.96));display:flex;flex-direction:column;align-items:center;gap:1px;cursor:pointer;color:#2b1c10;font-size:9.5px;font-weight:800;box-shadow:0 3px 6px rgba(0,0,0,.3)}
.dock button:active{transform:scale(.92)}
.dock button svg{width:22px;height:22px}
.cta{position:absolute;left:50%;margin-left:-78px;bottom:86px;width:190px;z-index:4;border:2px solid #8a5a12;border-radius:14px;background:linear-gradient(180deg,#f6c453,#dda63a);color:#2b1c10;cursor:pointer;padding:7px 10px;display:flex;align-items:center;gap:9px;box-shadow:0 4px 0 #8a5a12,0 8px 16px rgba(40,25,8,.4);text-align:left}
.cta:active{transform:translateY(3px);box-shadow:0 1px 0 #8a5a12}
.cta svg{width:30px;height:30px;flex:none}
.cta b{font-size:16px;display:block;line-height:1.15}
.cta span{font-size:11px;color:#5a3d1c;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;max-width:128px}
.chest{position:absolute;left:10px;bottom:88px;z-index:4;width:72px;background:none;border:0;padding:0;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:2px;filter:drop-shadow(0 4px 5px rgba(40,25,8,.45))}
.chest:active{transform:scale(.92)}
.chest svg{width:52px;height:52px}
.chest.ready svg{animation:chestbob 1.6s ease-in-out infinite}
@keyframes chestbob{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
.chest .hs-lb{font-size:11px}
.chest .chest-sub{font-size:10.5px;font-weight:700;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.85);white-space:nowrap}
.teamstrip{position:absolute;left:8px;right:8px;bottom:8px;z-index:5;display:flex;align-items:center;gap:8px;background:linear-gradient(180deg,rgba(73,55,40,.94),rgba(44,36,28,.95));border:1.5px solid #c9962f;border-radius:14px;padding:7px 10px;color:#ffe9b8;cursor:pointer;text-align:left;width:calc(100% - 16px)}
.teamstrip:active{transform:scale(.985)}
.teamstrip .tports{display:flex;gap:5px;flex:none}
.teamstrip .tports img{width:38px;height:38px;border-radius:10px;border:2px solid #ffe09a;box-shadow:0 2px 5px rgba(0,0,0,.4)}
.teamstrip .tinfo{flex:1;min-width:0}
.teamstrip .tinfo b{font-size:13.5px;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.teamstrip .tinfo span{font-size:11.5px;color:#d5c09a;white-space:nowrap;display:block;overflow:hidden;text-overflow:ellipsis}
.teamstrip .tpow{text-align:right;flex:none}
.teamstrip .tpow b{font-size:15px}
.teamstrip .tpow span{display:block;font-size:10.5px;color:#d5c09a}
/* === 弹出层（主城面板：宝箱 / 编队 / 任务 / 签到 / 信箱）=== */
#sheet{position:fixed;inset:0;z-index:80;display:none;align-items:flex-end;justify-content:center;background:rgba(30,20,10,.55)}
#sheet.show{display:flex}
.sheet-card{width:100%;max-width:480px;max-height:74svh;overflow:auto;background:linear-gradient(180deg,#fff9e2,#fbeec4);border:2px solid #d9ab4e;border-bottom:0;border-radius:18px 18px 0 0;padding:10px 14px calc(16px + env(safe-area-inset-bottom));animation:sheetup .25s ease-out;box-shadow:0 -8px 30px rgba(0,0,0,.4)}
@keyframes sheetup{from{transform:translateY(30px);opacity:0}to{transform:none;opacity:1}}
.sheet-card h3{margin:4px 0 8px;font-size:17px}
.sheet-card.noanim *{animation:none!important}
.rwline{display:flex;align-items:center;gap:8px;padding:6px 0;font-size:14px;border-bottom:1px dashed #e0c98f}
.rwline:last-child{border-bottom:0}
.rwline svg{width:22px;height:22px;flex:none}
.rwline b{margin-left:auto;white-space:nowrap}
.chest-big{width:76px;height:76px;margin:2px auto 6px;display:block;animation:chestbob 1.6s ease-in-out infinite}
.sheet-card .btnrow{margin-top:12px}
.mailitem{border:2px solid #e0c98f;border-radius:12px;padding:9px 10px;margin:7px 0;background:#fffdf4}
.mailitem b{font-size:14px}
.mailitem .mut{display:block;margin-top:2px;font-size:12.5px;line-height:1.5}
@media (max-height:640px){
.hs-ic{width:44px;height:44px}.hs-ic svg{width:25px;height:25px}.hs{width:58px}.hs-lb{font-size:10.5px;padding:1px 7px}
.hs-tavern{top:28%}.hs-guild{top:30%}.hs-smith{top:26%;right:9%}.hs-board{top:44%}
.dock{top:46%;gap:3px}.dock button{width:36px;padding:3px 0 2px;font-size:9px}.dock button svg{width:17px;height:17px}
.cta{bottom:78px;padding:6px 8px}.cta svg{width:26px;height:26px}.cta b{font-size:15px}
.chest{bottom:76px;width:64px}.chest svg{width:44px;height:44px}
.teamstrip .tports img{width:32px!important;height:32px!important}
}
@media (max-width:360px){
.teamstrip{gap:6px;padding:6px 8px}.teamstrip .tports{gap:4px}.teamstrip .tports img{width:30px!important;height:30px!important}.teamstrip .tinfo span{font-size:10px}.teamstrip .tpow b{font-size:13px}
}
"""
anchor = ".skillbanner{box-shadow:0 3px 10px rgba(180,130,10,.4)}\n</style>"
assert anchor in s
s = s.replace(anchor, ".skillbanner{box-shadow:0 3px 10px rgba(180,130,10,.4)}\n" + CSS + "</style>", 1)

# ---------- 3) 弹出层容器 ----------
rep('<div id="toast"></div><div id="battle">',
    '<div id="toast"></div><div id="sheet" onclick="closeSheet()"></div><div id="battle">', 'sheet-div')

# ---------- 4) 顶栏 HUD ----------
start = s.index('function renderTop(){')
end = s.index("</button>';}", start) + len("</button>';}")
new_top = """function renderTop(){const p=idlePending();const unread=mailUnread();const canSi=signinCan();const claimable=p.gold>=1||p.exp>=1;
document.getElementById('topbar').innerHTML='<div class="toprow"><span class="logo">'+logoSvg()+'<span>咕噜远征团<small>冒险公会</small></span></span><span class="top-acts">'
+'<button class="icbtn" aria-label="信箱" onclick="openMail()">'+ICON.mail+(unread?'<span class="dot">'+unread+'</span>':'')+'</button>'
+'<button class="icbtn" aria-label="签到" onclick="openSignin()">'+ICON.cal+(canSi?'<span class="dot">1</span>':'')+'</button>'
+'<button class="icbtn" aria-label="挂机宝箱" onclick="openChest()">'+ICON.chest+(claimable?'<span class="dot">!</span>':'')+'</button>'
+'<button class="icbtn" aria-label="设置" onclick="go(\\'settings\\')">'+ICON.gear+'</button></span></div>'
+'<div class="resrow">'
+'<span class="res">'+ICON.coin+fmt(S.res.gold)+'</span>'
+'<span class="res">'+ICON.exp+fmt(S.res.exp)+'</span>'
+'<span class="res">'+ICON.dia+fmt(S.res.dia)+'</span>'
+'<span class="res">'+ICON.ticket+fmt(S.res.ticket)+'</span>'
+'<span class="res">'+ICON.book+fmt(S.res.book)+'</span>'
+'<span class="res">'+ICON.stone+fmt(S.res.stone)+'</span>'
+'<span class="res">'+ICON.gcoin+fmt(S.res.gcoin)+'</span>'
+'</div>';}"""
s = s[:start] + new_top + s[end:]

# ---------- 5) 存档：信箱已读 ----------
rep("signin:{last:'',days:0},", "signin:{last:'',days:0},mailRead:[],", 'mailread-state')

# ---------- 6) 工具函数 + 图标集（插在 toast 之前） ----------
HELPERS = """
/* ===== 主城 v1：统一图标集（填充 + 描边，货币/建筑/功能同风格） ===== */
const ICON={
coin:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#f2b63c" stroke="#8a5a12" stroke-width="1.6"/><circle cx="12" cy="12" r="6.5" fill="none" stroke="#d98f1f" stroke-width="1.4"/><path d="M12 7.2 L13.5 10.6 L17 12 L13.5 13.4 L12 16.8 L10.5 13.4 L7 12 L10.5 10.6 Z" fill="#a86f14"/></svg>',
exp:'<svg viewBox="0 0 24 24"><path d="M12 2 L14 9 L21 11 L14 13.5 L12 21 L10 13.5 L3 11 L10 9 Z" fill="#57c98a" stroke="#2f7a4e" stroke-width="1.4" stroke-linejoin="round"/><circle cx="19" cy="5" r="1.6" fill="#bff0d2"/></svg>',
dia:'<svg viewBox="0 0 24 24"><path d="M12 2 L20 9 L12 22 L4 9 Z" fill="#6cb2dd" stroke="#2c6489" stroke-width="1.5" stroke-linejoin="round"/><path d="M4 9 H20 M12 2 L8.5 9 L12 22 M12 2 L15.5 9 L12 22" fill="none" stroke="#dff2ff" stroke-width="1"/></svg>',
ticket:'<svg viewBox="0 0 24 24"><path d="M3 7 Q3 5 5 5 H19 Q21 5 21 7 V9 Q19 10.5 19 12 Q19 13.5 21 15 V17 Q21 19 19 19 H5 Q3 19 3 17 V15 Q5 13.5 5 12 Q5 10.5 3 9 Z" fill="#e87a6a" stroke="#96382b" stroke-width="1.5"/><path d="M9 8 V16 M15 8 V16" stroke="#fff" stroke-width="1.4" stroke-dasharray="2 2"/></svg>',
book:'<svg viewBox="0 0 24 24"><path d="M5 4 H19 V20 H5 Q3 20 3 18 V6 Q3 4 5 4 Z" fill="#8a5a3b" stroke="#4a2f1c" stroke-width="1.5"/><path d="M6 4 H19 V20 H6" fill="#f6e7c3"/><path d="M9 8 H16 M9 11 H16 M9 14 H14" stroke="#8a6a3a" stroke-width="1.4"/></svg>',
stone:'<svg viewBox="0 0 24 24"><path d="M12 3 L19 8 L17 19 L7 19 L5 8 Z" fill="#9aa3ad" stroke="#4c545c" stroke-width="1.5" stroke-linejoin="round"/><path d="M8 9 L12 7 L16 9" stroke="#e8edf0" stroke-width="1.4" fill="none"/></svg>',
gcoin:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#b48ce0" stroke="#5e3a8a" stroke-width="1.6"/><path d="M8 16 V8 L12 5 L16 8 V16 H8 Z" fill="#f3e9ff" stroke="#5e3a8a" stroke-width="1.2"/><path d="M12 8 V13" stroke="#5e3a8a" stroke-width="1.4"/></svg>',
gear:'<svg viewBox="0 0 24 24"><g fill="#e8d3a0" stroke="#65452e" stroke-width="1"><circle cx="12" cy="12" r="7.5"/><rect x="10.6" y="1.5" width="2.8" height="4" rx="1"/><rect x="10.6" y="18.5" width="2.8" height="4" rx="1"/><rect x="1.5" y="10.6" width="4" height="2.8" rx="1"/><rect x="18.5" y="10.6" width="4" height="2.8" rx="1"/><rect x="10.6" y="1.5" width="2.8" height="4" rx="1" transform="rotate(45 12 12)"/><rect x="10.6" y="1.5" width="2.8" height="4" rx="1" transform="rotate(135 12 12)"/><rect x="10.6" y="1.5" width="2.8" height="4" rx="1" transform="rotate(225 12 12)"/><rect x="10.6" y="1.5" width="2.8" height="4" rx="1" transform="rotate(315 12 12)"/></g><circle cx="12" cy="12" r="3" fill="#65452e"/></svg>',
mail:'<svg viewBox="0 0 24 24"><rect x="2.5" y="5" width="19" height="14" rx="2" fill="#f6e7c3" stroke="#65452e" stroke-width="1.6"/><path d="M3 6 L12 13 L21 6" fill="none" stroke="#65452e" stroke-width="1.6"/></svg>',
cal:'<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2" fill="#fff9e2" stroke="#65452e" stroke-width="1.6"/><rect x="3" y="5" width="18" height="5" fill="#e05a4e"/><path d="M8 3 V6 M16 3 V6" stroke="#65452e" stroke-width="1.8"/><path d="M8.5 14.5 L11 17 L15.5 11.5" fill="none" stroke="#5d9448" stroke-width="2"/></svg>',
chest:'<svg viewBox="0 0 24 24"><path d="M3 10 Q3 6 7 6 H17 Q21 6 21 10 V11 H3 Z" fill="#a86f3a" stroke="#4a2f1c" stroke-width="1.5"/><rect x="3" y="11" width="18" height="9" rx="1.5" fill="#7a4a22" stroke="#4a2f1c" stroke-width="1.5"/><rect x="10.5" y="8" width="3" height="7" rx="1" fill="#f2b63c" stroke="#8a5a12"/><path d="M3 11 H21" stroke="#4a2f1c" stroke-width="1.2"/></svg>',
sword:'<svg viewBox="0 0 24 24"><path d="M12 2 L14.5 4 L13 15 L11 15 L9.5 4 Z" fill="#dfe9f0" stroke="#5a6268" stroke-width="1.3"/><rect x="7" y="15" width="10" height="2.4" rx="1.2" fill="#f2b63c" stroke="#8a5a12"/><rect x="10.8" y="17.4" width="2.4" height="4.6" rx="1.2" fill="#65452e"/></svg>',
mug:'<svg viewBox="0 0 24 24"><path d="M5 8 H15 V19 Q15 21 13 21 H7 Q5 21 5 19 Z" fill="#b0722e" stroke="#4a2f1c" stroke-width="1.5"/><path d="M15 10 Q19 10 19 13.5 Q19 17 15 17" fill="none" stroke="#4a2f1c" stroke-width="1.8"/><circle cx="8" cy="6.5" r="2.2" fill="#fff6dd" stroke="#d9c98f"/><circle cx="12" cy="5.5" r="2.6" fill="#fff6dd" stroke="#d9c98f"/></svg>',
helmet:'<svg viewBox="0 0 24 24"><path d="M4 13 Q4 5 12 5 Q20 5 20 13 L20 15 H4 Z" fill="#b9c6d0" stroke="#4c545c" stroke-width="1.5"/><path d="M4 15 H20" stroke="#4c545c" stroke-width="1.5"/><path d="M12 5 Q14 2 17 2.5 Q15 4.5 12 5" fill="#e05a4e"/><rect x="9" y="11" width="6" height="2.6" rx="1.3" fill="#4c545c"/></svg>',
anvil:'<svg viewBox="0 0 24 24"><path d="M4 8 H20 L18 12 H14 L13 16 H19 V19 H5 V16 H11 L10 12 H6 Z" fill="#6b7680" stroke="#3c434a" stroke-width="1.4" stroke-linejoin="round"/><rect x="3" y="19" width="18" height="2.4" rx="1" fill="#4c545c"/></svg>',
shield:'<svg viewBox="0 0 24 24"><path d="M12 2 L19 5 V13 Q19 19 12 22 Q5 19 5 13 V5 Z" fill="#5d9448" stroke="#2f5423" stroke-width="1.5"/><path d="M12 6 L13.4 9.4 L17 9.8 L14.4 12.2 L15 15.8 L12 14 L9 15.8 L9.6 12.2 L7 9.8 L10.6 9.4 Z" fill="#f2b63c"/></svg>',
tower:'<svg viewBox="0 0 24 24"><path d="M8 21 V6 L6 6 V3 H10 V6 H14 V3 H18 V6 H16 V21 Z" fill="#c9a86a" stroke="#65452e" stroke-width="1.4"/><path d="M11 12 H13 M11 16 H13" stroke="#65452e" stroke-width="1.6"/></svg>',
arena:'<svg viewBox="0 0 24 24"><path d="M5 3 L18 16" stroke="#dfe9f0" stroke-width="3" stroke-linecap="round"/><path d="M19 3 L6 16" stroke="#dfe9f0" stroke-width="3" stroke-linecap="round"/><path d="M4 18 L8 21 M20 18 L16 21" stroke="#f2b63c" stroke-width="2.4" stroke-linecap="round"/></svg>',
door:'<svg viewBox="0 0 24 24"><path d="M6 21 V8 Q6 3 12 3 Q18 3 18 8 V21 Z" fill="#7a5a3a" stroke="#3c2716" stroke-width="1.5"/><circle cx="12" cy="13" r="2" fill="#f2b63c"/><path d="M12 15 V18" stroke="#f2b63c" stroke-width="2"/></svg>',
codex:'<svg viewBox="0 0 24 24"><path d="M12 4 Q8 2 4 4 V20 Q8 18 12 20 Q16 18 20 20 V4 Q16 2 12 4 Z" fill="#fff6dd" stroke="#65452e" stroke-width="1.5"/><path d="M12 4 V20" stroke="#65452e" stroke-width="1.4"/><path d="M6.5 8 H10 M6.5 11 H10 M14 8 H17.5 M14 11 H17.5" stroke="#8a6a3a" stroke-width="1.3"/></svg>',
scroll:'<svg viewBox="0 0 24 24"><path d="M5 4 H18 Q20 4 20 6 V18 Q20 20 18 20 H5" fill="#f6e7c3" stroke="#8a6a3a" stroke-width="1.5"/><rect x="3" y="3" width="3.4" height="18" rx="1.7" fill="#c9a86a" stroke="#8a6a3a"/><path d="M8.5 8 H16 M8.5 11 H16 M8.5 14 H13" stroke="#8a6a3a" stroke-width="1.3"/></svg>'
};
function logoSvg(){return '<svg viewBox="0 0 24 24"><path d="M12 1.5 L20 4.5 V12 Q20 18.5 12 22.5 Q4 18.5 4 12 V4.5 Z" fill="#5d9448" stroke="#ffe09a" stroke-width="1.6"/><path d="M12 5.5 L13.6 9.2 L17.5 9.6 L14.6 12.2 L15.3 16 L12 14 L8.7 16 L9.4 12.2 L6.5 9.6 L10.4 9.2 Z" fill="#f2b63c" stroke="#8a5a12" stroke-width=".7"/></svg>';}
const RESNAME={gold:'金币',exp:'经验',dia:'钻石',ticket:'招募券',book:'技能书',stone:'进阶石',gcoin:'公会币'};
function fmtReward(r){return Object.keys(r||{}).map(function(k){return (RESNAME[k]||k)+' +'+fmt(r[k]);}).join(' · ');}
function signinCan(){return !(S.signin&&S.signin.last===todayStr());}
function questClaimable(){if(S.daily.date!==todayStr())return false;const q=[['battles',1],['summons',1],['upgrades',1],['idle',1]];return q.some(function(x){return (S.daily.counters[x[0]]||0)>=x[1]&&!S.daily.claimed[x[0]];});}
/* ===== 弹出层 ===== */
let sheetKind='';
function openSheet(html,kind){sheetKind=kind||'';const sh=document.getElementById('sheet');sh.innerHTML='<div class="sheet-card" onclick="event.stopPropagation()"><div style="text-align:right"><button class="btn sm ghost" onclick="closeSheet()">✕ 关闭</button></div>'+html+'</div>';sh.classList.add('show');}
function closeSheet(){const sh=document.getElementById('sheet');if(!sh)return;sh.classList.remove('show');sh.innerHTML='';sheetKind='';}
/* ===== 挂机宝箱：快照锁定，跳过演出与看完演出结果相同，连点不重复领取 ===== */
let chestSnap=null,chestClaiming=false;
function chestSnapshot(){const p=idlePending();const tot=(S.idle.equipMin||0)+p.mins;return {mins:p.mins,gold:p.gold,exp:p.exp,equip:Math.floor(tot/60),fracG:p.fracG,fracE:p.fracE};}
function openChest(){chestSnap=chestSnapshot();openSheet(chestSheetHtml('ready'), 'chest');}
function chestSheetHtml(mode,granted){
  const p=chestSnap||chestSnapshot();
  if(mode==='empty'||(p.gold<1&&p.exp<1&&mode!=='claimed')){
    return '<h3>挂机宝箱</h3><div style="text-align:center">'+ICON.chest.replace('<svg','<svg class="chest-big"')+'</div><div class="mut" style="text-align:center">宝箱还在积累中，已积累 '+Math.floor(p.mins)+' 分钟（上限 480 分钟）。<br>再等一会儿，或先去推图，回来再领。</div><div class="rwline"><span>预计金币</span><b>'+fmt(p.gold)+'</b></div><div class="rwline"><span>预计经验</span><b>'+fmt(p.exp)+'</b></div><div class="btnrow"><button class="btn ghost" onclick="closeSheet()">以后再说</button></div>';
  }
  if(mode==='claimed'){
    return '<h3>领取成功</h3><div style="text-align:center">'+ICON.chest.replace('<svg','<svg class="chest-big"')+'</div><div class="rwline"><span>'+ICON.coin+' 金币</span><b>+'+fmt(granted.gold)+'</b></div><div class="rwline"><span>'+ICON.exp+' 经验</span><b>+'+fmt(granted.exp)+'</b></div>'+(granted.equip?'<div class="rwline"><span>装备</span><b>+'+granted.equip+' 件（已放入背包）</b></div>':'')+'<div class="mut">已到账：金币 '+fmt(S.res.gold)+' · 经验 '+fmt(S.res.exp)+'。宝箱已清空，重新开始积累。</div><div class="btnrow"><button class="btn green" onclick="closeSheet();render()">收下</button></div>';
  }
  return '<div class="sheet-anim"><h3>挂机宝箱</h3><div style="text-align:center">'+ICON.chest.replace('<svg','<svg class="chest-big"')+'</div><div class="mut" style="text-align:center">已积累 '+Math.floor(p.mins)+' 分钟（上限 480 分钟）</div>'
  +'<div class="rwline"><span>'+ICON.coin+' 金币</span><b>+'+fmt(p.gold)+'</b></div>'
  +'<div class="rwline"><span>'+ICON.exp+' 经验</span><b>+'+fmt(p.exp)+'</b></div>'
  +(p.equip?'<div class="rwline"><span>装备</span><b>+'+p.equip+' 件</b></div>':'<div class="mut">每累计 60 分钟多一件装备。</div>')
  +'<div class="btnrow"><button class="btn green" id="chestClaimBtn" onclick="confirmChestClaim()">领取奖励</button><button class="btn ghost" onclick="closeSheet()">以后再说</button><button class="btn sm ghost" onclick="this.closest(\\'.sheet-card\\').classList.add(\\'noanim\\')">跳过演出</button></div></div>';
}
function confirmChestClaim(){
  if(chestClaiming||!chestSnap)return;
  const snap=chestSnap;if(snap.gold<1&&snap.exp<1)return;
  chestClaiming=true;const btn=document.getElementById('chestClaimBtn');if(btn)btn.disabled=true;
  S.res.gold+=snap.gold;S.res.exp+=snap.exp;S.idle.fracG=snap.fracG;S.idle.fracE=snap.fracE;
  const tot=(S.idle.equipMin||0)+snap.mins;const n=Math.floor(tot/60);S.idle.equipMin=tot-n*60;
  S.idle.pendMin=0;S.idle.lastCalc=Date.now();
  for(let i=0;i<n;i++)S.equips.push(newEquip());
  S.daily.counters.idle++;save();render();
  chestSnap=null;chestClaiming=false;
  openSheet(chestSheetHtml('claimed',{gold:snap.gold,exp:snap.exp,equip:n}),'chest');
  toast('挂机收益已到账');
}
/* ===== 编队详情（点开才看） ===== */
function openTeam(){
  const b=calcBonds(S.formation);
  let rows=S.formation.map(function(id,i){const H=HEROES[id];return '<div class="rwline">'+iconSvg('hero',id,34)+'<span><b>'+H.name+'</b> <span class="mut">'+H.rar+' · '+H.fac+' · '+H.role+' · '+(i<2?'前排':'后排')+'</span></span></div>';}).join('');
  openSheet('<h3>当前编队 · 战力约 '+fmt(teamPower())+'</h3>'+rows
  +'<div class="mut" style="margin-top:8px">'+(b.bonds.length?b.bonds.join('<br>'):'暂无羁绊：同阵营 2 人起生效')+'<br>克制链：森芽 → 潮汐 → 熔炉 → 星灯 → 森芽（克制 +15% 伤害）</div>'
  +'<div class="btnrow"><button class="btn" onclick="go(\\'heroes\\')">调整编队</button><button class="btn blue" onclick="go(\\'map\\')">继续推图</button></div>','team');
}
/* ===== 任务板 / 签到 / 信箱 ===== */
function openTasks(){openSheet('<h3>任务板 · 每日任务</h3>'+dailyQuestsHtml()+'<div class="btnrow"><button class="btn" onclick="openSignin()">七日签到</button></div>','tasks');}
function openSignin(){openSheet('<h3>七日签到</h3>'+signinHtml(),'signin');}
function mailLetters(){
  const list=[{id:'welcome',t:'欢迎来到咕噜远征团',b:'冒险公会欢迎你。先去推图闯过第 1 关，再到酒馆招募新伙伴。编队满 5 人后，记得看看阵营羁绊。',act:''}];
  const p=idlePending();if(p.gold>=1||p.exp>=1)list.push({id:'idle',t:'挂机收益已备好',b:'宝箱里已有金币 '+fmt(p.gold)+'、经验 '+fmt(p.exp)+'，点主城宝箱领取。',act:'chest'});
  if(signinCan())list.push({id:'signin',t:'今日签到还未领取',b:'今天的签到奖励还没领，点右上角日历或下方按钮领取。',act:'signin'});
  return list;
}
function mailUnread(){const read=S.mailRead||[];return mailLetters().filter(function(l){return read.indexOf(l.id)<0;}).length;}
function openMail(){
  const list=mailLetters();
  S.mailRead=list.map(function(l){return l.id;});save();renderTop();
  let h='<h3>公会信箱</h3>';
  list.forEach(function(l){
    h+='<div class="mailitem"><b>'+l.t+'</b><span class="mut">'+l.b+'</span>'+(l.act==='chest'?'<div class="btnrow"><button class="btn sm green" onclick="openChest()">打开宝箱</button></div>':l.act==='signin'?'<div class="btnrow"><button class="btn sm" onclick="openSignin()">去签到</button></div>':'')+'</div>';
  });
  openSheet(h,'mail');
}
"""
rep('function toast(m){', HELPERS + '\nfunction toast(m){', 'city-helpers')

# ---------- 7) go() 关闭弹出层 ----------
rep('function go(v){S.view=v;save();render();}',
    'function go(v){closeSheet();S.view=v;save();render();}', 'go-close-sheet')

# ---------- 8) claimIdle 连点保护 ----------
rep('function claimIdle(){const p=idlePending();',
    'function claimIdle(){if(window.__idleClaiming)return;window.__idleClaiming=true;setTimeout(function(){window.__idleClaiming=false;},500);const p=idlePending();',
    'claimidle-guard')

# ---------- 9) 签到/任务领取后刷新弹出层 ----------
rep("S.signin.last=todayStr();save();render();toast('签到成功');}",
    "S.signin.last=todayStr();save();render();toast('签到成功');if(sheetKind==='signin')openSignin();}",
    'signin-refresh')
rep("S.daily.claimed[id]=true;addRes(rew);save();render();toast('任务奖励已领取');}",
    "S.daily.claimed[id]=true;addRes(rew);save();render();toast('任务奖励已领取');if(sheetKind==='tasks')openTasks();}",
    'quest-refresh')

# ---------- 10) 签到面板：奖励用中文名，不再显示原始 JSON ----------
start = s.index('function signinHtml(){')
end = s.index('function doSignin', start)
new_signin = """function signinHtml(){const rewards=[{gold:300},{dia:30},{ticket:1},{book:2},{exp:500},{stone:2},{ticket:2,dia:50}];const day=S.signin.days%7;const can=signinCan();let h='';rewards.forEach((r,i)=>{h+='<span class="tag" style="'+(i===day&&can?'background:#f2b63c':'')+'">第'+(i+1)+'天'+(i<day||(i===day&&!can)?' ✓':'')+'</span>';});return '<div>'+h+'</div><div class="btnrow"><button class="btn sm" '+(can?'':'disabled')+' onclick="doSignin()">签到领取第 '+(day+1)+' 天</button></div><div class="mut">奖励：第 '+(day+1)+' 天 '+fmtReward(rewards[day])+'</div>';}
"""
s = s[:start] + new_signin + s[end:]

# ---------- 11) vHome 重写：完整场景，只保留场景内入口 ----------
start = s.index('function vHome(){')
end = s.index('function dailyQuestsHtml', start)
new_home = """function vHome(){const p=idlePending();const next=highestStage()+1;const claimable=p.gold>=1||p.exp>=1;
const stageTxt=next<40?('第 '+(Math.floor(next/10)+1)+'-'+(next%10+1)+' 关 · 推荐 Lv.'+REC_LV[next]):'已通关全部 40 关';
return '<div class="city"><img class="city-bg" src="'+(ART.scene||ART.city)+'" alt="冒险公会"><div class="city-vig"></div>'
+'<div class="glow g1"></div><div class="glow g2"></div>'
+'<span class="mote m1"></span><span class="mote m2"></span><span class="mote m3"></span><span class="mote m4"></span><span class="mote m5"></span><span class="mote m6"></span><span class="mote m7"></span><span class="mote m8"></span>'
+'<button class="hs hs-tavern" onclick="go(\\'summon\\')"><span class="hs-ic">'+ICON.mug+'</span><span class="hs-lb">酒馆 · 召唤</span></button>'
+'<button class="hs hs-guild" onclick="go(\\'guild\\')"><span class="hs-ic">'+ICON.shield+'</span><span class="hs-lb">公会大厅</span></button>'
+'<button class="hs hs-smith" onclick="go(\\'heroes\\')"><span class="hs-ic">'+ICON.anvil+'</span><span class="hs-lb">铁匠铺</span></button>'
+'<button class="hs hs-board" onclick="openTasks()"><span class="hs-ic">'+ICON.scroll+'</span><span class="hs-lb">任务板</span>'+(questClaimable()?'<span class="dot">!</span>':'')+'</button>'
+'<div class="dock"><button onclick="go(\\'tower\\')">'+ICON.tower+'爬塔</button><button onclick="go(\\'arena\\')">'+ICON.arena+'竞技场</button><button onclick="go(\\'dungeon\\')">'+ICON.door+'副本</button><button onclick="go(\\'codex\\')">'+ICON.codex+'图鉴</button></div>'
+'<button class="cta" onclick="go(\\'map\\')">'+ICON.sword+'<span><b>出发冒险</b><span>'+stageTxt+'</span></span></button>'
+'<button class="chest '+(claimable?'ready':'')+'" onclick="openChest()">'+ICON.chest+(claimable?'<span class="dot">!</span>':'')+'<span class="hs-lb">挂机宝箱</span><span class="chest-sub">'+(claimable?('金币 '+fmt(p.gold)):(Math.floor(p.mins)+' 分钟积累中'))+'</span></button>'
+'<button class="teamstrip" onclick="openTeam()"><span class="tports">'+S.formation.map(function(id){return iconSvg('hero',id,38);}).join('')+'</span><span class="tinfo"><b>当前编队</b><span>'+S.formation.length+'/5 人 · 点开查看详情</span></span><span class="tpow"><b>'+fmt(teamPower())+'</b><span>战力</span></span></button>'
+'</div>';}
"""
s = s[:start] + new_home + s[end:]


# ---------- 12) 版本号（设置页可查）+ 英雄界面去掉“大招”（只保留普攻/主动/被动） ----------
# 战斗引擎内的大招机制本轮不动，待下一轮对齐；此处只改玩家可见的英雄养成界面与设置页。
rep("const SAVE_KEY='gulu-mtstyle-v1';",
    "const SAVE_KEY='gulu-mtstyle-v1';\nconst APP_VERSION='2026.11.01-city1'; // 主城 v1；设置页可查，改动后须同步更新", 'app-version-const')
rep("</title>",
    "</title>\n<!-- 版本 2026.11.01-city1（主城 v1） -->", 'app-version-comment')
rep("<b>普攻 '+H.basic+' · 主动 '+H.active+'（冷却 '+H.acd+'s）· 大招 '+H.ult+'（仅本原型）</b>",
    "<b>普攻 '+H.basic+' · 主动 '+H.active+'（冷却 '+H.acd+'s）· 被动</b>", 'hero-skill-line')
rep("<b>主动 Lv.'+hh.sk.active+' · 大招 Lv.'+hh.sk.ult+' · 被动 Lv.'+hh.sk.passive+'</b>",
    "<b>主动 Lv.'+hh.sk.active+' · 被动 Lv.'+hh.sk.passive+'</b>", 'hero-skill-levels')
rep("h.sk.active=Math.min(5,h.sk.active+1);h.sk.ult=Math.min(5,h.sk.ult+1);",
    "h.sk.active=Math.min(5,h.sk.active+1);h.sk.passive=Math.min(5,h.sk.passive+1);", 'skillup-no-ult')
rep('<div class="panel"><b>对照与限制</b><div class="mut">见同目录 BORROWING_MAP.md：机制借鉴与不可复制内容的分界、能量/大招仅限本原型的说明、未完成清单。</div></div>',
    '<div class="panel"><b>版本</b><div class="kv"><span>版本号</span><b>' + "'+APP_VERSION+'" + '（主城 v1）</b></div><div class="mut">对照与未完成清单见同目录 BORROWING_MAP.md。</div></div>', 'settings-version-panel')

open(P, 'w', encoding='utf-8').write(s)
print('patched bytes:', len(s), 'was:', orig_len)

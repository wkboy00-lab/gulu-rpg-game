function savePanelHtml(){
  const st = corruptHold ? '损坏存档待处理（旧档已保留，未被覆盖）' : (saveErr ? '保存失败：' + saveErr.msg : '正常');
  let h = '<div class="panel"><b>存档与备份</b>';
  h += '<div class="kv"><span>保存状态</span><b>' + esc(st) + '</b></div>';
  h += '<div class="kv"><span>减少动态效果</span><label style="display:flex;align-items:center;gap:6px"><input type="checkbox" ' + ((S.settings && S.settings.reduceMotion) ? 'checked' : '') + ' onchange="toggleReduceMotion(this.checked)">关闭呼吸/浮动/闪烁动画，功能不受影响</label></div>';
  h += '<div class="btnrow"><button class="btn" onclick="exportSave()">导出存档备份</button><label class="btn ghost" style="cursor:pointer">导入存档备份<input type="file" accept=".json,application/json" style="display:none" onchange="handleImportFile(this)"></label></div>';
  if (corruptInfo) {
    h += '<div class="btnrow"><button class="btn" onclick="exportCorrupt()">导出损坏存档</button><button class="btn" onclick="recoverPrevGood()">从上次成功保存恢复</button><button class="btn red" onclick="discardCorruptAsk()">放弃损坏存档并开始新进度</button></div>';
    h += '<div class="mut">损坏原因：' + esc(corruptInfo.reason) + '。在处理之前，游戏不会覆盖旧档；刷新后仍会看到此提示。</div>';
  }
  h += '<div class="mut">导入前会自动备份当前存档；导入内容会校验结构，校验不通过不做任何改动。</div></div>';
  return h;
}

# 首轮浏览器回归

游戏仍然零运行时依赖。此测试仅供开发机运行，需要 Node.js 和 Playwright。

在临时开发环境安装 Playwright，运行 `node tests/first-pass.cjs`。默认使用已安装的 Microsoft Edge；可用 `BROWSER_CHANNEL=chrome` 切换已安装 Chrome。

可选环境变量：
- `PLAYWRIGHT_MODULE`：已有 Playwright 模块的绝对路径。
- `REVIEW_OUTPUT`：已存在的输出目录；保存两张截图及 test-results.json。

测试自行在随机本地端口启动静态服务，使用隔离浏览器上下文，不读取玩家已有浏览器存档。部分结算测试把测试英雄设为 60 级以覆盖胜利路径，这不是难度或平衡性验证。计时测试使用真实等待，繁忙机器可能需要检查容差。

覆盖：序章、18 个主页面与英雄/战前页面、编队返回、点击换位、44 图解码、43 图路径、四种视口、真实战斗倍速、暂停/手动与自动大招/集火、重复进入、同种子重复模拟、主线首通去重、塔/副本/活动/竞技场/远征首节点结算、升级/装备/十连/挂机/邮件/签到、IndexedDB 恢复、保存失败提示、关闭战斗后取消旧结算。

报告中的 KNOWN_REMAINING 是已确认的待修问题，不计为“已解决”。未覆盖真机触控、Safari、全部 Boss 机制边界、完整七节点远征与所有经济组合。

## 存档专项

运行 `node tests/save-safety.cjs`，同样支持上方环境变量。需要在Git检出目录运行，且本地历史包含原版c5eca890df3464c4007294be0f199e8620a81a79：脚本通过Git读取原版以验证真实旧档兼容，不使用网络。

96项覆盖旧档、异常输入、事务中止与回滚、保存交错、备份恢复/导出、坏档启动/保留/下载、战斗互斥及延迟剧情。全部运行在隔离浏览器上下文；不会操作用户已有存档。输出save-safety-results.json、save-recovery.png及save-settings.png。

第二轮以后首轮脚本的KNOWN_REMAINING对象仍保留早期问题的探针：前三项false表示存档缺陷已修；soundGate=true仍为待修音效问题。

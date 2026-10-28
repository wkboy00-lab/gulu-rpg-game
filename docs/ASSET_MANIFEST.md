# 素材清单（assets/）

全部为本地 `.webp`，代码按文件名硬编码引用，不得改名或移动。

## 英雄（12，透明底 628×628 量级）

hero-taidun 苔盾 / hero-heling 荷铃 / hero-yexian 叶弦 / hero-maoya 铆牙 / hero-baoli 爆栗 / hero-tongshao 铜哨 / hero-paopaoli 泡泡狸 / hero-qiren 鳍刃 / hero-shange 珊歌 / hero-dengyu 灯羽 / hero-yefeng 夜缝 / hero-xingkui 星盔

## 外观（12，与英雄一一对应）

skin-taidun 秋叶守卫 / skin-heling 夏雨药师 / skin-yexian 枫林游侠 / skin-maoya 熔火匠师 / skin-baoli 星火发明家 / skin-tongshao 冬巡修理员 / skin-paopaoli 深海学者 / skin-qiren 月潮剑客 / skin-shange 晨曦祭司 / skin-dengyu 彗星占星师 / skin-yefeng 蔷薇裁缝 / skin-xingkui 晨星骑士

## 敌人与 Boss

enemy-e01 困困史莱姆 / e02 木刺幼兽 / e03 菌伞投手 / e04 迷路药灵 / e05 铆钉巡逻机 / e06 火花投掷机 / e07 海雾水母（已重生成）/ e08 甲壳卫兵 / e09 星尘傀儡 / e10 失控灯灵
boss-b1 荆冠巨獾 / b2 熔渣锅炉王 / b3 潮眼巨蟹 / b4 失眠观星者

## 场景

city.webp 主城 / bg-forest 苔铃森林 / bg-mine 赤炉矿道 / bg-harbor 雾潮港湾 / bg-highland 星坠高地

## 其他

- `media-generation-*.json`：各批图片的生成记录（提示与来源），随素材一并归档。
- `media-generation-hero-yefeng-new-0-*.webp`：夜缝重生成原图（游戏内引用的是处理后版本 hero-yefeng.webp）。
- 根目录 `icon.webp`：应用图标。
- 图片加载失败时，代码以手绘 SVG 占位回退（非主素材）。

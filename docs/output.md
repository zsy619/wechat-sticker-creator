# 最终输出与发布

## 最终输出

详见 [project-structure.md](project-structure.md)。

- **尺寸**：1080×1440px（微信贴图标准）
- **格式**：PNG（透明或主题背景）
- **命名**：`{序号}-{贴图名称}.png`

### ZIP 打包（可选）

```bash
cd wechat-stickers/{slug}/assets-{theme}
zip -r ../output/stickers-{slug}-{theme}.zip *.png
```

### 输出汇总格式

```
═══════════════════════════════════════════
    微信贴图生成完成！
═══════════════════════════════════════════

主题: {topic}
生成方式: AI / Remotion / PIL
风格: {theme}
贴图数量: {N} 张
输出目录: wechat-stickers/{slug}/assets-{theme}/

标签推荐:
  #微信表情 #微信贴图 #AI工具 #科技感 #赛博朋克
```

## 公众号发布规格（可选）

当需要通过微信公众号发布贴图内容时，生成以下规格的图片：

### 图片规格表

| 类型 | 尺寸 | 宽高比 | 文件大小 | 格式 | 用途 |
|------|------|--------|---------|------|------|
| 贴图 | 1080×1440px | 3:4 | ≤2MB | PNG | 直接发布 |
| 封面 | 900×383px | 9:4 | ≤500KB | PNG | 公众号封面 |
| 缩略图 | 200×267px | 3:4 | ≤100KB | PNG | 文末汇总 |

### 生成贴图图片

```bash
# 使用 PIL 缩放
python3 -c "
from PIL import Image
img = Image.open('sticker.png')
img.resize((900, 1200)).save('cover-wechat.png')
img.resize((200, 267)).save('thumbnail.png')
"
```

### 公众号排版建议

1. **封面图**：使用 `cover-wechat.png`，突出主题和风格
2. **正文**：每张贴图配合 `content-{name}.png` 展示
3. **缩略图**：用于文末汇总展示，格式统一

## 标签推荐策略

自动生成 5-10 个相关标签：

| 类别 | 标签 |
|------|------|
| 平台标签 | #微信表情 #微信贴图 #WeChatStickers |
| 情感标签 | #可爱 #搞笑 #治愈 #社恐自救 #打工人 #摸鱼 |
| 主题标签 | 根据内容自动提取（如 #AI #编程 #职场 #生活） |

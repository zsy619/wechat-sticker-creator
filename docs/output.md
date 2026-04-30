# 最终输出与发布


### ZIP 打包（可选）

```bash
cd wechat-stickers/{slug}/assets
zip -r ../output/stickers-{slug}.zip *.png
```

### 输出汇总格式

```
═══════════════════════════════════════════
    微信贴图生成完成！
═══════════════════════════════════════════

主题: {topic}
输入类型: {URL链接/主题词/内容文本}
贴图数量: {N} 张
输出目录: wechat-stickers/{slug}/

生成文件:
  ✓ project.yaml          - 项目元数据
  ✓ content-analysis.md   - 内容聚合分析
  ✓ sticker-manifest.md   - 贴图设计清单
  ✓ prompts/              - {N} 个提示词文件（含专属视觉规则）
  ✓ assets/               - {N} 张PNG图片 (1080×1440)

推荐标签:
  #微信表情 #微信贴图 #可爱 #搞笑 #治愈
  #{主题相关标签1} #{主题相关标签2}

═══════════════════════════════════════════
```

## 公众号发布规格 (可选)

当需要通过微信公众号发布贴图内容时，生成以下规格的图片：

### 图片规格表

| 类型     | 尺寸          | 宽高比    | 文件大小  | 格式          | 用途     |
| ------ | ----------- | ------ | ----- | ----------- | ------ |
| 头图封面   | 900×383px   | 2.35:1 | ≤2MB  | JPG/PNG     | 文章封面   |
| 正文配图   | 1080×607px  | 16:9   | ≤2MB  | JPG/PNG/GIF | 内容展示   |
| 小图/缩略图 | 200×200px   | 1:1    | 无限制   | PNG/SVG     | 预览/缩略  |
| 贴图       | 1080×1440px | 3:4    | ≤10MB | JPG/PNG     | 单独图片消息 |

### 贴图生成（最佳选择）

贴图是微信推出的图片消息形式，适合单独发布贴图内容展示：

```bash
# 生成贴图图片
python3 ~/.agents/skills/wechat-sticker-skill/scripts/generate_cover.py \
  --output assets/xhs-post-{sticker-name}.png \
  --title "{贴图名称}" \
  --subtitle "{描述文案（最长50字）}" \
  --theme cyberpunk \
  --type sticker
```

**规格说明**：

- **最佳比例**: 3:4（竖版）
- **推荐尺寸**: 1080×1440px
- **描述文案**: 支持最长 50 字
- **适用场景**: 单独发布图片消息，类似小红书笔记风格

### 公众号封面生成

```bash
# 生成公众号头图封面
python3 ~/.agents/skills/wechat-sticker-skill/scripts/generate_cover.py \
  --output assets/cover-wechat.png \
  --title "{主题}" \
  --subtitle "{副标题}" \
  --theme cyberpunk \
  --type wechat-cover
```

### 正文配图生成

```bash
# 生成正文配图
python3 ~/.agents/skills/wechat-sticker-skill/scripts/generate_cover.py \
  --output assets/content-{sticker-name}.png \
  --title "{贴图名称}" \
  --theme cyberpunk \
  --width 1080 \
  --height 607 \
  --type content-image
```

### 缩略图生成

```bash
# 生成缩略图
python3 ~/.agents/skills/wechat-sticker-skill/scripts/generate_cover.py \
  --output assets/thumb-{sticker-name}.png \
  --title "{贴图名称}" \
  --theme cyberpunk \
  --width 200 \
  --height 200 \
  --type thumbnail
```

### 公众号发布输出

```
assets/
├── cover-wechat.png              # 公众号头图封面 (900×383)
├── content-01-{name}.png         # 正文配图 (1080×607)
├── content-02-{name}.png         # 正文配图
├── thumb-01-{name}.png           # 缩略图 (200×200)
├── 01-{sticker-name}.png         # 原始贴图 (1080×1440)
└── ...
```

### 公众号排版建议

1. **封面图**: 使用 `cover-wechat.png`，突出主题和风格
2. **正文**: 每张贴图配合 `content-{name}.png` 展示
3. **缩略图**: 用于文末汇总展示，格式统一

## 标签推荐策略

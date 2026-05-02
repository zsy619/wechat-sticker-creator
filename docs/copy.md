# 文档复制说明

## 功能说明

`copy_docs.py` 负责将技能内置的只读规范文档复制到项目 `docs/` 目录。每次运行 `run_full_pipeline.py` 时，步骤 0 会自动执行此脚本（`--with-docs`，默认开启）。

## 复制清单

技能文档分为两类：

**只读规范文档（复制到项目）**：

- `content-format.md` — 内容格式规范（content-analysis / manifest / prompts）
- `frame-design.md` — Remotion 帧设计规范
- `image-generation.md` — 两段式图像生成流程
- `output.md` — 最终输出与打包
- `project-structure.md` — 项目目录结构
- `prompts-format.md` — Prompt 生成规范
- `qa.md` — 质量检查清单
- `remotion-projects.md` — Remotion 项目完整结构
- `workflow.md` — 核心工作流程

**自动生成文档（由脚本生成，不复制）**：

- `session-log-template.md` — Token 消耗记录模板，由 `scripts/generate_session_log.py` 直接渲染到项目 `docs/session-log.md`
- `docs/session-log.md` — 由步骤 7 自动生成，记录项目级 Token 消耗
- `docs/tags.md` — 由步骤 5.5 自动生成，记录标签推荐

## 跳过方式

如需跳过文档复制，使用 `--no-docs` 参数：

```bash
python3 scripts/run_full_pipeline.py \
  --input "AI编程助手" \
  --output ~/wechat-stickers/ai-coding \
  --theme cyberpunk \
  --no-docs
```

## 手动执行

独立运行 `copy_docs.py`：

```bash
python3 scripts/copy_docs.py \
  --project ~/wechat-stickers/my-project \
  --theme neon
```

## 注意事项

- `session-log-template.md` **不**复制到项目——该文件是 `generate_session_log.py` 的模板源文件，由脚本直接渲染输出
- 每次运行 `run_full_pipeline.py` 会覆盖项目的 `docs/` 目录中的只读文档，但不会覆盖自动生成的 `session-log.md` 和 `tags.md`

---

#文档管理 #技能工作流 #项目规范 #脚本说明 #微信贴图 #自动生成

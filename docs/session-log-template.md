# Session Log - {project_name}

## 项目信息

| 字段 | 值 |
|------|-----|
| **项目名称** | {project_name} |
| **主题** | {theme} |
| **生成时间** | {generated_date} |
| **状态** | {status} |

## 模型配置

| 字段 | 值 |
|------|-----|
| **默认模型** | minimax/MiniMax-M2.7 |
| **Token 追踪** | session_status 工具 |

## Token 消耗记录

| 阶段 | 输入 Token | 输出 Token | 合计 Token | 估算费用 |
|------|-----------|-----------|-----------|---------|
| 内容聚合分析 | N | N | N | ¥N |
| sticker-manifest | N | N | N | ¥N |
| prompts × {sticker_count} | N | N | N | ¥N |
| 图片生成 × {sticker_count} | N | N | N | ¥N |
| **总计** | **{input_total}** | **{output_total}** | **{grand_total}** | **¥{cost_total}** |

> 费用估算公式：`(输入tokens + 输出tokens) / 1,000,000 × 单价（元/1M tokens）`
> MiniMax-M2.7 单价参考：输入 ¥1 / 输出 ¥1（具体以账单为准）

## 各阶段详情

### 内容聚合分析
- **输入**: {input_type}
- **处理时长**: N 秒
- **备注**:

### Manifest 生成
- **贴图数量**: {sticker_count} 张
- **处理时长**: N 秒
- **备注**:

### Prompts 生成
- **文件数**: {sticker_count}
- **处理时长**: N 秒
- **备注**:

### 图片生成
- **模式**: {generation_mode}（AI → Remotion → PIL 自动降级）
- **成功数**: N / {sticker_count}
- **处理时长**: N 秒
- **备注**:

## 问题与修复

> 如有异常或修复，记录于此

| 日期 | 问题描述 | 修复方案 |
|------|---------|---------|
| - | - | - |

## 更新日志

| 日期 | 操作 | 结果 |
|------|------|------|
| {generated_date} | 初始生成 | 贴图 N 张 |

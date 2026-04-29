---
project: {topic-slug}
created: {YYYY-MM-DD HH:mm:ss}
---

# Token 输入输出统计

## 项目信息

| 项目 | 内容 |
|-----|------|
| **主题** | {topic} |
| **贴图数量** | {N} 张 |
| **生成风格** | {style} |
| **创建时间** | {YYYY-MM-DD HH:mm:ss} |

## Token 消耗统计

| 阶段 | 输入Token | 输出Token | 备注 |
|-----|----------|----------|------|
| 内容聚合分析 | {input} | {output} | 联网搜索 + 内容整合 |
| 贴图设计 | {input} | {output} | Manifest 生成 |
| 文案生成 | {input} | {output} | copy.md 生成 |
| 提示词生成 | {input} | {output} | prompts/*.md 生成 |
| **总计** | **{total_input}** | **{total_output}** | |

## API 调用详情

| 阶段 | 调用次数 | 平均每次消耗 |
|-----|---------|-------------|
| WebSearch | {count} | {avg} tokens/次 |
| 内容分析 | {count} | {avg} tokens/次 |
| 文案生成 | {count} | {avg} tokens/次 |

## 费用估算

| 项目 | 单价 | 消耗 | 费用 |
|-----|------|------|------|
| 输入 Token | ${input_price}/1M | {input_tokens}M | ${input_cost} |
| 输出 Token | ${output_price}/1M | {output_tokens}M | ${output_cost} |
| **总计** | - | - | **${total_cost}** |

> 注：价格为参考值，实际费用以各平台账单为准

## 优化建议

### 已采取的优化措施

- [ ] 批量处理减少 API 调用次数
- [ ] 复用提示词模板降低输入 Token
- [ ] 合并相似请求优化调用效率

### 可进一步优化项

- [ ] 使用缓存避免重复搜索相同内容
- [ ] 精简提示词长度减少 Token 消耗
- [ ] 调整贴图数量平衡成本与效果
- [ ] 考虑使用更经济的模型处理简单任务

## 备注

```
在此记录本次生成过程中的重要信息、问题或改进建议
```
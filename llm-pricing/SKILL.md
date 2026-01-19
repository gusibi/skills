---
name: llm-pricing
description: 从 LLM 提供商网站提取模型定价信息，输出结构化 JSON。使用场景：(1) 提取单个 URL 的模型价格列表 (2) 合并多个提供商的数据 (3) 价格对比分析。触发词："提取定价"、"llm pricing"、"模型价格"、"/llm-pricing"。
---

# LLM 定价提取器

从各大 LLM 提供商网站提取模型定价信息，输出标准化 JSON 格式。

## 使用方式

```bash
# 提取单个 URL 的定价信息
/llm-pricing https://ppio.com/ai-computing/llm-api

# 合并所有已提取的数据
/llm-pricing --merge

# 批量提取多个 URL
/llm-pricing https://url1.com https://url2.com
```

## 输出格式

每个模型的 JSON 结构：

```json
{
  "provider": "provider-name",
  "model": "model-name",
  "input_price_per_million": 1.0,
  "output_price_per_million": 2.0,
  "currency": "CNY",
  "source_url": "https://...",
  "retrieved_at": "2026-01-19T22:35:00+08:00",
  "raw_unit": "per 1K tokens",
  "raw_text": "原始价格文本",
  "tags": ["推理模型", "满血版"]
}
```

## 规范化规则

- **模型名**：全小写，空格/下划线转 `-`
- **价格**：统一转换为"每百万 token"
- **过滤**：自动过滤无效数据行（如纯数字、价格行误识别为模型名）

## 工作流程

### 步骤 1：打开页面并获取完整列表

**优先遵循 [provider-configs.md](references/provider-configs.md) 中已定义的策略。** 如果没有定义的提供商，则执行以下通用操作：

1. **查找"所有模型"按钮**：部分页面默认显示精选模型，需点击切换
2. **滚动加载**：部分页面需滚动到底部加载完整列表
3. **展开折叠项**：部分模型可能被折叠

### 步骤 2：提取页面数据

从页面表格或卡片中提取以下信息：
- 模型名称（识别特殊标签如"满血版"、"推理模型"）
- 输入价格、输出价格
- 上下文长度（如有）
- 原始价格单位

**注意**：识别价格单位（每千/每万/每百万 token）以便后续转换。

### 步骤 3：规范化数据

运行规范化脚本：

```bash
python3 scripts/normalize_data.py output/provider.json
```

脚本自动完成：
- 模型名格式化
- 价格单位转换
- 无效数据过滤

### 步骤 4：保存结果

将 JSON 保存到 `output/` 目录：
- 文件名使用提供商名称，如 `output/ppio.json`
- 每个 URL 单独一个文件

### 步骤 5：合并数据（可选）

运行合并脚本生成汇总文件：

```bash
python3 scripts/merge_results.py --output output/all_models.json
```

## 各提供商特殊处理

详见 [provider-configs.md](references/provider-configs.md)

| Provider | 特殊处理 |
|----------|----------|
| volcengine | 表格形式，直接提取 |
| qiniu | 需点击"所有模型"标签 |
| siliconflow | 可能需滚动加载 |
| ppio | 1. 选“所有模型”；2. 展开“大语言”；3. 等待加载；4. 提取信息 |

## 输出示例

```
✅ 已提取 45 个模型，保存至 output/ppio.json

模型示例：
- deepseek-v3: 输入 ¥2.0/M, 输出 ¥8.0/M
- qwen-turbo-2025-01-25: 输入 ¥0.3/M, 输出 ¥0.6/M
```

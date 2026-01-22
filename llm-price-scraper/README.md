# LLM Price Scraper

从各大 LLM 服务提供商网站抓取模型定价数据的 AI 驱动工具。

## 功能特点

- **AI 驱动抓取**：使用 [agent-browser](https://agent-browser.dev/) 智能导航和提取数据
- **多提供商支持**：支持任意 LLM 定价页面
- **灵活定价类型**：支持 token 计费、按秒、按图片、按请求等多种定价模式
- **数据合并**：自动合并多个数据源，生成统一的 JSON 和 CSV 格式

## 已抓取数据源

| 提供商 | URL | 模型数 |
|--------|-----|--------|
| PPIO | https://ppio.com/ai-computing/llm-api | 54 |
| 七牛云 | https://www.qiniu.com/ai/models | 59 |
| 硅基流动 | https://www.siliconflow.cn/pricing | 92 |
| 火山引擎 | https://www.volcengine.com/docs/82379/1544106 | 34 |

## 使用方法

### 1. 抓取单个提供商

对 AI 助手说：

```
使用 llm-price-scraper 获取 https://example.com/pricing 的数据
```

AI 会：
1. 使用 agent-browser 打开页面
2. 智能导航找到定价信息
3. 提取并规范化数据
4. 保存到 `prices/<provider>.json`

### 2. 合并数据

```
合并
```

或运行脚本：

```bash
node scripts/merge_prices.js
```

输出：
- `prices.json` - 合并后的 JSON 数据
- `prices.csv` - CSV 格式（便于 Excel 分析）

## 数据格式

### 单个提供商 JSON (`prices/<provider>.json`)

```json
{
  "provider": "example",
  "url": "https://example.com/pricing",
  "currency": "CNY",
  "retrieved_at": "2026-01-21T10:00:00Z",
  "models": [
    {
      "model": "Example-Model-V1",
      "pricing_type": "token",
      "input_price": 2.0,
      "output_price": 8.0,
      "cache_price": 0.4,
      "context_length": 128000
    },
    {
      "model": "Example-Image-Gen",
      "pricing_type": "per_image",
      "price": 0.1,
      "price_unit": "image"
    }
  ]
}
```

### 合并后 CSV 字段

| 字段 | 说明 |
|------|------|
| `provider` | 提供商标识 |
| `model_id` | 标准化模型 ID（小写，连字符分隔） |
| `model` | 原始模型名称 |
| `pricing_type` | 定价类型：`token`, `free`, `per_image`, `per_second` 等 |
| `input_price` | 输入价格（元/百万 tokens） |
| `output_price` | 输出价格（元/百万 tokens） |
| `cache_price` | 缓存价格（元/百万 tokens） |
| `price` | 非 token 定价的单价 |
| `price_unit` | 价格单位：`image`, `second`, `request` 等 |
| `context_length` | 上下文长度限制 |
| `currency` | 货币单位 |
| `source_url` | 数据来源 URL |
| `retrieved_at` | 抓取时间 |

## 支持的定价类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `token` | 按 token 计费（输入/输出分开） | DeepSeek、GPT、Qwen |
| `free` | 免费模型 | Qwen3-8B (SiliconFlow) |
| `per_image` | 按图片计费 | Seedream、Kling |
| `per_second` | 按秒计费（视频） | Kling Video |
| `per_minute` | 按分钟计费（音频） | ASR |
| `per_request` | 按请求计费 | Search API |
| `per_chars` | 按字符计费 | TTS |

## 目录结构

```
llm-price-scraper/
├── README.md
├── SKILL.md           # AI 助手技能定义
├── prices/            # 各提供商原始数据
│   ├── ppio.json
│   ├── qiniu.json
│   ├── siliconflow.json
│   └── volcengine.json
├── prices.json        # 合并后的 JSON
├── prices.csv         # 合并后的 CSV
└── scripts/
    └── merge_prices.js
```

## 依赖

- Node.js 18+
- [agent-browser](https://agent-browser.dev/)（AI 助手使用）

## 许可

MIT

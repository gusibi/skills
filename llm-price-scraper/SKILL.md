---
name: llm-price-scraper
description: Scrape AI model pricing from provider web pages using agent-browser, extract model names and prices (token/image/video/audio), save JSON. Use when asked to (1) analyze/scrape model pricing from a given URL, (2) extract prices from a provider page, (3) merge multiple price JSON files into one.
---

# LLM Price Scraper

Scrape AI model pricing from provider pages using agent-browser. Supports multiple pricing types: token-based, per-image, per-second, per-request, and free.

## Workflow

### 1) Scrape a provider URL

When user provides a URL to analyze:

```bash
agent-browser open <url>
agent-browser snapshot -i
```

Analyze the snapshot to find pricing data. If data is hidden behind tabs/buttons (e.g., "所有模型", "All Models"), click to reveal:

```bash
agent-browser click @<ref>    # Click tab/button to show all models
agent-browser snapshot -i     # Get updated view
```

### 2) Extract pricing data

Identify the pricing type for each model and extract accordingly:

**Token-based models (LLM):**
- `pricing_type`: "token"
- `input_price`: Input price per 1M tokens
- `output_price`: Output price per 1M tokens
- `cache_price`: Cache price (optional)

**Image generation models:**
- `pricing_type`: "per_image"
- `price`: Price per image
- `price_unit`: "image"

**Video generation models:**
- `pricing_type`: "per_second"
- `price`: Price per second
- `price_unit`: "second"

**Other pricing:**
- `pricing_type`: "per_request" / "per_minute" / "per_chars" / "free"
- `price`: Unit price
- `price_unit`: "request" / "minute" / "100chars" etc.

**Price normalization for tokens:** Convert to per-1M-token:
- `/Mt` or `/M` = already per 1M tokens
- `/Kt` or `/K` = multiply by 1000

### 3) Save to JSON

Save extracted data to `prices/<provider>.json`:

```json
{
  "provider": "qiniu",
  "url": "https://www.qiniu.com/ai/models",
  "currency": "CNY",
  "retrieved_at": "2026-01-21T10:30:00Z",
  "models": [
    {
      "model": "DeepSeek-V3.2",
      "pricing_type": "token",
      "input_price": 2,
      "output_price": 3
    },
    {
      "model": "Kling-V2-1",
      "pricing_type": "per_second",
      "price": 0.4,
      "price_unit": "second"
    },
    {
      "model": "Kling-V1",
      "pricing_type": "per_image",
      "price": 0.025,
      "price_unit": "image"
    },
    {
      "model": "Mimo-V2-Flash",
      "pricing_type": "free"
    }
  ]
}
```

### 4) Merge results

When user says "merge" or "合并", run the merge script:

```bash
node scripts/merge_prices.js --in-dir prices --out prices.json --csv prices.csv
```

This combines all `prices/*.json` into a single `prices.json` and `prices.csv`.

## Output Schema

Each model object supports these fields:

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | Model name |
| `pricing_type` | string | token / per_image / per_second / per_request / per_minute / free |
| `input_price` | number | Token input price per 1M (token type only) |
| `output_price` | number | Token output price per 1M (token type only) |
| `cache_price` | number | Token cache price per 1M (optional) |
| `price` | number | Unit price (non-token types) |
| `price_unit` | string | second / image / request / minute / 100chars |
| `context_length` | number | Max context window (optional) |

## Resources

- `scripts/merge_prices.js`: Merge per-provider JSON files into consolidated output

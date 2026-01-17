# Article Image Skill

为文章生成精美的封面图及文中插图的 AI 技能。自动分析文章结构，在合适的段落插入相关的手绘风格插图，提升阅读体验。

## ✨ 功能特点

- 🎨 **多种风格**：支持 8 种视觉风格（elegant、tech、warm、bold、minimal、playful、nature、retro）
- 🤖 **智能分析**：自动识别文章结构，寻找最佳配图位置
- ☁️ **自动上传**：生成后自动上传至 Cloudflare R2 存储
- 📝 **自动插入**：将图片链接智能插入文章合适位置

## 🚀 快速开始

### 触发词

- `生成封面及插图`
- `为文章配图`  
- `美化文章`

### 基本用法

```bash
# 生成封面及建议的文中插图（默认模式）
/article-image path/to/article.md

# 仅生成封面
/article-image path/to/article.md --only-cover

# 指定风格生成全套图片
/article-image path/to/article.md --style tech
```

## 📦 依赖安装

```bash
pip install -r requirements.txt
```

## ⚙️ 配置

### ModelScope API Key

图片生成需要 ModelScope API Key，配置方式：

```bash
# 方式一：环境变量
export MODELSCOPE_API_KEY="your-api-key"

# 方式二：命令行参数
python scripts/generate_image.py --prompt "提示内容" --api-key "ms-xxx"
```

### R2 上传代理

> [!IMPORTANT]
> 上传图片至 Cloudflare R2 需要使用 [moli-tutu](https://github.com/gusibi/moli-tutu) 的 API 代理功能。

**设置步骤：**

1. 克隆 moli-tutu 项目（建议直接下载 release 版本）：
   ```bash
   git clone https://github.com/gusibi/moli-tutu.git
   ```


2. 启动 API 代理服务（默认端口 38123）

3. 确保代理服务运行后再执行上传：
   ```bash
   python scripts/upload_image.py path/to/image.png
   ```

## 📁 项目结构

```
article-image/
├── SKILL.md           # 技能详细说明
├── README.md          # 本文件
├── requirements.txt   # Python 依赖
├── scripts/
│   ├── generate_image.py   # 图片生成脚本
│   └── upload_image.py     # R2 上传脚本
└── test/              # 测试文件
```

## 📖 详细文档

完整的使用说明请参考 [SKILL.md](./SKILL.md)。

## 📄 License

MIT

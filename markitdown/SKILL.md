---
name: markitdown
description: Convert various document formats (PDF, PowerPoint, Word, Excel, Images, Audio, HTML, CSV, JSON, XML, ZIP) into text Markdown format. Use when asked to read, parse, or extract text from rich documents, slides, spreadsheets, or images, making them accessible to LLMs.
---

# MarkItDown 文档转换 Skill

基于 Microsoft 的 [MarkItDown](https://github.com/microsoft/markitdown) 库，本 Skill 可以将多种复杂格式的文件转换为易于大语言模型读取的 Markdown 格式。

支持的文件格式包括：
- PDF 文档 (PDF)
- PowerPoint 幻灯片 (PPTX)
- Word 文档 (DOCX)
- Excel 电子表格 (XLSX)
- 图片 (JPG, PNG等) 以及音频 (EXIF光元数据或语音等)
- 网页 (HTML)
- 支持基于文本的格式如 CSV, JSON, XML 等
- 压缩包 (ZIP)

## 快速使用

调用通用的转换脚本提取内容。脚本在首次执行时会自动从镜像源安装 `markitdown` 依赖。

**基本语法：**
```bash
python3 scripts/convert.py <文件路径> [--output <保存路径>]
```

**示例 1：直接预览转换结果并在 stdout 输出**
```bash
python3 scripts/convert.py /path/to/document.pdf
```

**示例 2：将转换结果保存为新的 Markdown 文件**
```bash
python3 scripts/convert.py /path/to/presentation.pptx --output /path/to/extracted_content.md
```

## 注意事项

1. 依赖库：首次运行该脚本时，将会自动安装 `markitdown`。无需手动配置您的 Python 环境。
2. 内容质量：基于原文件的复杂程度，生成的图表、排版可能会有所简化，主要适用于提取文本信息供上下文使用。
3. 如果文件内容过长，建议使用 `--output` 选项将内容保存在文件中，并通过其他大模型辅助工具读取分析（例如 `view_file` 或 `grep_search` 等工具）。

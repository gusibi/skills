# Skills Repository

This repository contains a collection of specialized "Skills" designed for Large Language Model (LLM) agents. Each skill extends the agent's capabilities with specific workflows, API integrations, and domain knowledge.

## 🌟 Available Skills

### Data & Financial
* **[AKShare Data (`akshare-data/`)](./akshare-data/)**
  * Query Chinese and global financial data using the AKShare Python library. Covers 500+ data interfaces including stock quotes (A-shares/HK/US), macroeconomic indicators (GDP/CPI/PMI), futures, options, bonds, forex, funds, indexes, and alternative data.

* **[LLM Price Scraper (`llm-price-scraper/`)](./llm-price-scraper/)**
  * Scrape AI model pricing from provider web pages using `agent-browser`, extract model names and prices (token/image/video/audio), and save to JSON. Includes utility scripts to merge multiple price files.

### Design Systems Frontend Assistants
* **[Apple Design (`design/apple-design/`)](./design/apple-design/)**
  * Apple Human Interface Guidelines (Cupertino) expert. Generates Web frontend code strictly adhering to Apple's HIG design philosophy.

* **[Google Design (`design/google-design/`)](./design/google-design/)**
  * Material Design 3 (Material You) expert. Generates Web frontend code strictly following M3 physical laws and styling.

* **[Microsoft Design (`design/microsoft-design/`)](./design/microsoft-design/)**
  * Microsoft Fluent 2 design system expert. Generates Web frontend code strictly following Fluent Design principles.

### Content & Media
* **[Article Image Generator (`article-image/`)](./article-image/)**
  * Generates beautiful cover images and inline illustrations for articles. Automatically analyzes article structure and inserts hand-drawn style illustrations at suitable paragraphs.

### Web & Information Retrieval
* **[Agent Reach (`agent-reach/`)](./agent-reach/)**
  * Use the internet: search, read, and interact with 13+ platforms including Twitter/X, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu (小红书), Douyin (抖音), WeChat Articles, LinkedIn, Boss直聘, RSS, Exa web search, and any web page.

### Document Processing
* **[MarkItDown (`markitdown/`)](./markitdown/)**
  * Convert various document formats (PDF, PowerPoint, Word, Excel, Images, Audio, HTML, CSV, JSON, XML, ZIP) into text Markdown format, making them accessible to LLMs.

### Development Utilities
* **[Git Commit Generator (`development/commit/`)](./development/commit/)**
  * Automatically analyzes current git changes and generates concise, structured commit messages in both English and Chinese.

## 🛠️ How to Use Skills

Skills are structured according to the `skill-creator` standard. A typical skill directory contains:

1. **`SKILL.md`**: The entry point for the LLM. Contains the skill's name, description (in YAML frontmatter), and core instructions or workflows.
2. **`scripts/`**: Executable scripts (Python, Node, Bash, etc.) required by the skill.
3. **`references/`** or **`resources/`**: Large documentation, context files, or templates loaded on-demand by the agent based on the prompt.

When using an agent framework that supports this skill format, the agent parses the `yaml` frontmatter in `SKILL.md` to understand *when* to trigger the skill, and reads the markdown content to know *how* to execute the task.

## 🤝 Contributing
To add a new skill:
1. Create a new directory under the root or an appropriate category folder (e.g., `development/`).
2. Add a `SKILL.md` file with clear instructions and YAML frontmatter (name, description).
3. If necessary, provide `scripts/` or `references/` for complex operations or context.

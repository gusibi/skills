---
name: xiaohongshu-operator
description: Automate Xiaohongshu (Little Red Book) through browser control using BrowserWing Executor.  Supports searching, liking, collecting (favoriting), posting, viewing comments, and viewing user profile pages  — all through a dedicated browser instance to keep your default browser safe.  Use this skill whenever the user wants to: post on xiaohongshu, search xiaohongshu,   check xiaohongshu comments, like a xiaohongshu post, save/collect a post, view a creator's page,   or perform any interactive operation on xiaohongshu (小红书) that requires a logged-in session.  Triggers: "发小红书", "小红书发帖", "搜索小红书", "search xiaohongshu", "like on xiaohongshu",  "小红书点赞", "小红书收藏", "save on xiaohongshu", "看小红书评论", "view xiaohongshu comments",  "check xiaohongshu profile", "小红书操作".
---

# Xiaohongshu Operator

Automate Xiaohongshu (小红书) interactions through browser control. This skill uses the BrowserWing
Executor HTTP API to drive a **dedicated Brave browser**. The user has a Brave installation
reserved exclusively for this skill — it is not used for personal browsing.

## Setup

The user has already logged in to Xiaohongshu in Brave. Login sessions persist in Brave's
default profile, so no special data directory is needed.

To start the service:

```bash
bash scripts/start-browser.sh
```

> Run from the `xiaohongshu-operator/` skill directory.

## Prerequisites

- **BrowserWing Executor** (`npm install -g browserwing` — auto-installed by the script)
- **Brave Browser** (dedicated for this skill, already logged in to Xiaohongshu)

## How It Works

1. `start-browser.sh` launches BrowserWing with Brave on port **9222** (shared with x-com-operator).
2. BrowserWing reuses Brave's default profile, so the existing Xiaohongshu login session is available.
3. All API calls go to `http://127.0.0.1:9222/api/v1/executor/`.

## Workflow

Before performing any Xiaohongshu operation, ensure the dedicated service is running:

```bash
bash scripts/start-browser.sh
```

Then follow the operation guides below. The API base for all operations is:

```
http://127.0.0.1:9222/api/v1/executor
```

### General Pattern

Every operation follows the same rhythm:

1. **Navigate** to the right Xiaohongshu URL
2. **Wait** for page transitions or dynamic content to load (Xiaohongshu feeds can be slow)
3. **Snapshot** the page to understand its structure and get element RefIDs
4. **Interact** with elements using their RefIDs (`@eX`)
5. **Verify** the result by taking another snapshot or extracting content

**CRITICAL NOTE ON SELECTORS:** Xiaohongshu heavily obfuscates its CSS classes (e.g., `.xg-feed-container`, randomly generated classes). It rarely uses semantic `id` or `data-testid` attributes. Therefore, **you MUST rely on the accessibility tree from `GET /snapshot`** and match elements based on their inner text (e.g., "点赞", "收藏", "发布", "评论") or their structural position rather than hardcoded CSS selectors.

### File Management

To keep the skill directory organized, follow these storage conventions:
- **Clean Root**: Do not save temporary files (snapshots, HTML dumps, screenshots) directly in the root `xiaohongshu-operator/` folder.
- **Use temp/ Directory**: Always save intermediate debugging or data files in the `temp/` subdirectory (e.g., `temp/snapshot.json`, `temp/page.html`).
- **Automation Scripts**: Store reusable automation scripts or recordings in the `scripts/` folder.

---

## Operations

### 1. Search (搜索)

Search for posts using a keyword.

```bash
# Navigate to search results using URL parameters directly
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/navigate' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://www.xiaohongshu.com/search_result?keyword=SEARCH_TERM_HERE"}'

# Wait for content to load (the feed usually takes a moment)
sleep 3
# Or use the wait API to look for a known text string if applicable, e.g.:
# curl -X POST 'http://127.0.0.1:9222/api/v1/executor/wait' ...

# Snapshot to see the loaded results
curl -X GET 'http://127.0.0.1:9222/api/v1/executor/snapshot'

# Note: Sometimes titles/text on feed pages aren't cleanly mapped in the accessibility tree.
# You can use the extract API to get all post titles directly:
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/extract' \
  -H 'Content-Type: application/json' \
  -d '{"selector": "a.title", "multiple": true, "fields": ["text", "href"]}'
```

To load more results, you can scroll down:
```bash
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/scroll-to-bottom' \
  -H 'Content-Type: application/json'
```

### 2. View a Post & Comments (查看帖子与评论)

When you want to view a post detail and its comments, navigate to its URL (usually starts with `https://www.xiaohongshu.com/explore/...`).

```bash
# Navigate to the post
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/navigate' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://www.xiaohongshu.com/explore/POST_ID"}'

# Wait for the post and comments to load
sleep 3

# Snapshot the page
curl -X GET 'http://127.0.0.1:9222/api/v1/executor/snapshot'
```

The snapshot will show the post content, images/video elements, and the comments section below or to the side. You can extract the text from the snapshot.

### 3. Like (点赞) and Collect (收藏)

To like or collect a post, first navigate to its detail page (or identify it in the feed) and take a snapshot. 

```bash
# Snapshot to find the Like or Collect button RefID
curl -X GET 'http://127.0.0.1:9222/api/v1/executor/snapshot'

# Look for elements in the snapshot whose accessible name indicates "Like" (often the count of likes) 
# or a button that represents liking/collecting. Wait for it if not immediately present.

# Click the element (replace @eXXX with actual RefID)
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/click' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "@eXXX"}'
```

Because CSS classes are obfuscated, finding the exact like/collect button may require looking at sibling elements of the post content or checking elements near the comment input box in the snapshot.

### 4. Post (发帖)

> [!WARNING]
> Xiaohongshu's Creator Center (`https://creator.xiaohongshu.com/publish/publish`) uses a complex Micro-Frontend (Qiankun) rendering architecture. Standard file input elements are deeply hidden. The most reliable automated posting method is to use Xiaohongshu's built-in **"Text-to-Image" (文字配图)** feature.

**Step 1: Navigate to Creator Center**
```bash
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/navigate' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://creator.xiaohongshu.com/publish/publish?source=official"}'
```

There are two main ways to post: **Text-to-Image (Automated)** and **Standard Image Upload (Manual Intervention Required)**.

#### Option A: Text-to-Image (Fully Automated)

1. **Click "上传图文" (Upload Graphic/Text) -> "文字配图" (Text to Image)**
```bash
# Click "上传图文"
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/evaluate' \
  -H 'Content-Type: application/json' \
  -d '{"script": "() => { Array.from(document.querySelectorAll(\"span\")).find(el => el.textContent === \"上传图文\")?.click(); return true; }"}'

sleep 1

# Click "文字配图"
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/evaluate' \
  -H 'Content-Type: application/json' \
  -d '{"script": "() => { Array.from(document.querySelectorAll(\"span\")).find(el => el.textContent === \"文字配图\")?.click(); return true; }"}'
```

2. **Generate Image from Text**
```bash
# Type the image text into the generator input
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/type' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "div[role=\"textbox\"]", "text": "自动生成的配图文字"}'

# Click "生成图片" (Generate Image)
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/evaluate' \
  -H 'Content-Type: application/json' \
  -d '{"script": "() => { document.querySelector(\"div.edit-text-button\").click(); return true; }"}'
  
# Wait 2-3 seconds for generation, then click "下一步" (Next)
sleep 3
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/evaluate' \
  -H 'Content-Type: application/json' \
  -d '{"script": "() => { Array.from(document.querySelectorAll(\"button\")).find(el => el.textContent.includes(\"下一步\"))?.click(); return true; }"}'
```

3. **Enter Posting Title and Content**
```bash
# Type Title
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/type' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "input[placeholder=\"填写标题会有更多赞哦\"]", "text": "这里是标题"}'

# Type Content (with tags)
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/type' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "div[role=\"textbox\"]", "text": "你的帖子正文内容 #话题[话题]# "}'
```

4. **Click Publish (发布)**
```bash
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/evaluate' \
  -H 'Content-Type: application/json' \
  -d '{"script": "() => { Array.from(document.querySelectorAll(\"span\")).find(el => el.textContent === \"发布\")?.click(); return true; }"}'
```

#### Option B: Standard Image Upload (Manual Intervention)
If you need to upload specific local images:
1. **Upload:** Rely on the user to manually click "上传图文" on the page and select the media file from their computer.
2. **Title/Content:** Once the user is on the text editor screen, use the `snapshot` API to locate the textboxes, or use the `type` commands from Option A.
3. **Publish:** Use the evaluate script above to find and click "发布" or "发布笔记".

### 5. View Personal Pages (查看个人主页)

```bash
# Navigate to a user's profile
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/navigate' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://www.xiaohongshu.com/user/profile/USER_ID"}'

sleep 3

# Snapshot to view their posts
curl -X GET 'http://127.0.0.1:9222/api/v1/executor/snapshot'
```

## Tips for Success

- **Wait and Retry**: Xiaohongshu uses lazy loading heavily. Elements might not be in the DOM until you scroll or wait a few seconds.
- **Login States**: If a page continuously redirects to a login portal (e.g., `/user/login`), notify the user that they might need to log in to Xiaohongshu manually in the dedicated Brave browser session.
- **DOM Inspection**: Use `evaluate` to extract parts of the DOM if the accessibility tree doesn't provide enough context to distinguish between like buttons vs other icons.
  
```bash
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/evaluate' \
  -H 'Content-Type: application/json' \
  -d '{"script": "document.body.innerHTML.substring(0, 1000)"}'
```

---
name: x-operator
description: Automate X.com (Twitter) through browser control using BrowserWing Executor.  Supports browsing timeline, viewing liked posts, composing and publishing tweets,  replying to tweets, retweeting, and liking posts — all through a dedicated browser instance  to keep your default browser safe.  Use this skill whenever the user wants to: post a tweet, browse their X/Twitter timeline,  check liked tweets, reply to someone on X, retweet something, compose a thread,  or perform any interactive operation on x.com that requires a logged-in session.  Triggers: "发推", "发推特", "推特发帖", "browsing timeline", "browse my likes on x",  "post a tweet", "reply on twitter", "retweet", "转推", "看推特", "看 timeline",  "tweet this", "post on x", "check my x timeline", "x.com 操作", "帮我发条推",  "在推特上评论", "推特点赞", "看我点赞的推文".
---

# X.com Operator

Automate X.com (Twitter) interactions through browser control. This skill uses the BrowserWing
Executor HTTP API to drive a **dedicated Brave browser**. The user has a Brave installation
reserved exclusively for this skill — it is not used for personal browsing.

## Setup

The user has already logged in to X.com in Brave. Login sessions persist in Brave's
default profile, so no special data directory is needed.

To start the service:

```bash
bash scripts/start-browser.sh
```

> Run from the `x-com-operator/` skill directory.

## Prerequisites

- **BrowserWing Executor** (`npm install -g browserwing` — auto-installed by the script)
- **Brave Browser** (dedicated for this skill, already logged in to X.com)

## How It Works

1. `start-browser.sh` launches BrowserWing with Brave on port **9222**.
2. BrowserWing reuses Brave's default profile, so the existing X.com login session is available.
3. All API calls go to `http://127.0.0.1:9222/api/v1/executor/`.

## Workflow

Before performing any X.com operation, ensure the dedicated service is running:

```bash
bash scripts/start-browser.sh
```

> Run from the `x-com-operator/` skill directory. Or use the absolute path if you know it.

Then follow the operation guides below. The API base for all operations is:

```
http://127.0.0.1:9222/api/v1/executor
```

### General Pattern

Every operation follows the same rhythm:

1. **Navigate** to the right X.com URL
2. **Snapshot** the page to understand its structure and get element RefIDs
3. **Interact** with elements using their RefIDs
4. **Wait** for page transitions or dynamic content to load
5. **Verify** the result by taking another snapshot or extracting content

The accessibility snapshot (`GET /snapshot`) is your primary tool for understanding
what's on the page. It returns element RefIDs like `@e1`, `@e2` which you use in
subsequent click/type operations. Always re-snapshot after the page changes.

---

## Operations

### 1. Browse Timeline (Home Feed)

Navigate to the home timeline and extract recent tweets.

```bash
# Navigate to home
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/navigate' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://x.com/home"}'

# Wait for timeline to load
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/wait' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"primaryColumn\"]", "state": "visible", "timeout": 15}'

# Get page structure
curl -X GET 'http://127.0.0.1:9222/api/v1/executor/snapshot'
```

To scroll and load more tweets:

```bash
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/scroll-to-bottom' \
  -H 'Content-Type: application/json'
```

After scrolling, wait a moment and re-snapshot to see newly loaded tweets.

To extract tweet content, use the snapshot output which shows tweet text, author names,
and interactive buttons. Read the snapshot text carefully — tweet content appears as
text nodes, and action buttons (reply, retweet, like) appear as clickable elements.

### 2. Browse Liked Tweets

```bash
# Navigate to your likes page (replace 'your_username' with actual username)
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/navigate' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://x.com/your_username/likes"}'

# Wait for content to load
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/wait' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"primaryColumn\"]", "state": "visible", "timeout": 15}'

# Snapshot to see liked tweets
curl -X GET 'http://127.0.0.1:9222/api/v1/executor/snapshot'
```

**Finding the username:** If you don't know the user's X handle, navigate to `https://x.com/home`
first, take a snapshot, and look for the profile link or display name in the navigation area.

### 3. Post a Tweet (Compose)

```bash
# Navigate to compose page
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/navigate' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://x.com/compose/post"}'

# Wait for the tweet compose box to appear
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/wait' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"tweetTextarea_0\"]", "state": "visible", "timeout": 10}'

# Snapshot to find the compose area RefID
curl -X GET 'http://127.0.0.1:9222/api/v1/executor/snapshot'

# Type the tweet content (use the RefID from snapshot for the text area)
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/click' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"tweetTextarea_0\"]"}'

curl -X POST 'http://127.0.0.1:9222/api/v1/executor/type' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"tweetTextarea_0\"]", "text": "YOUR TWEET TEXT HERE"}'

# Click the Post button
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/click' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"tweetButton\"]"}'
```

**Important behavior notes:**
- The compose area is a contenteditable div, not a regular input. If `type` doesn't work
  well, try clicking the area first, then using `press-key` to type character by character,
  or use `evaluate` to set content via JavaScript.
- After posting, wait ~2 seconds and verify by navigating to the user's profile.
- X.com may show a confirmation toast — check the snapshot for it.

**Fallback: Using JavaScript to insert text:**

```bash
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/evaluate' \
  -H 'Content-Type: application/json' \
  -d '{
    "expression": "const editor = document.querySelector(\"[data-testid=tweetTextarea_0]\"); if (editor) { editor.focus(); document.execCommand(\"insertText\", false, \"YOUR TWEET TEXT\"); }"
  }'
```

### 4. Reply to a Tweet

First, navigate to the specific tweet you want to reply to:

```bash
# Navigate to the tweet (use the full tweet URL)
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/navigate' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://x.com/username/status/TWEET_ID"}'

# Wait for the tweet to load
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/wait' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"tweetText\"]", "state": "visible", "timeout": 10}'

# Snapshot to find the reply area
curl -X GET 'http://127.0.0.1:9222/api/v1/executor/snapshot'

# Click the reply text area (on a tweet detail page, there's usually a reply box)
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/click' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"tweetTextarea_0\"]"}'

# Type reply content
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/type' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"tweetTextarea_0\"]", "text": "YOUR REPLY TEXT"}'

# Click the Reply button
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/click' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"tweetButton\"]"}'
```

**Alternative approach — reply from timeline:** If replying from the timeline (not the
tweet detail page), click the reply icon on the tweet first. The icon has
`data-testid="reply"`. This opens a modal with a compose area.

### 5. Retweet

```bash
# Navigate to the tweet
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/navigate' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://x.com/username/status/TWEET_ID"}'

# Wait for tweet to load
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/wait' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"tweetText\"]", "state": "visible", "timeout": 10}'

# Snapshot to find the retweet button
curl -X GET 'http://127.0.0.1:9222/api/v1/executor/snapshot'

# Click the retweet button (opens a submenu with "Repost" and "Quote")
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/click' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"retweet\"]"}'

# Wait for the dropdown menu to appear, then snapshot
sleep 1
curl -X GET 'http://127.0.0.1:9222/api/v1/executor/snapshot'

# Click "Repost" in the dropdown (use the RefID from the snapshot)
# The menu item typically has data-testid="retweetConfirm"
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/click' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"retweetConfirm\"]"}'
```

**Quote retweet:** Instead of clicking "Repost", click "Quote" in the dropdown.
This opens a compose area where you type your quote text before posting.

### 6. Like a Tweet

```bash
# Navigate to the tweet (or find the like button in the timeline)
# From tweet detail page:
curl -X POST 'http://127.0.0.1:9222/api/v1/executor/click' \
  -H 'Content-Type: application/json' \
  -d '{"identifier": "[data-testid=\"like\"]"}'
```

From the timeline, each tweet has its own like button. Use the snapshot RefIDs to identify
the correct one.

---

## Key X.com Selectors Reference

These are common `data-testid` attributes used by X.com. They may change over time —
if a selector doesn't work, take a snapshot and look for similar elements.

| Element                    | Selector                                     |
|----------------------------|----------------------------------------------|
| Main content column        | `[data-testid="primaryColumn"]`              |
| Tweet text                 | `[data-testid="tweetText"]`                  |
| Tweet compose area         | `[data-testid="tweetTextarea_0"]`            |
| Post/Reply button          | `[data-testid="tweetButton"]`                |
| Reply icon                 | `[data-testid="reply"]`                      |
| Retweet icon               | `[data-testid="retweet"]`                    |
| Retweet confirm            | `[data-testid="retweetConfirm"]`             |
| Like icon                  | `[data-testid="like"]`                       |
| Unlike icon                | `[data-testid="unlike"]`                     |
| User avatar                | `[data-testid="UserAvatar-Container-*"]`     |
| Tweet article container    | `article[data-testid="tweet"]`               |
| DM compose                 | `[data-testid="dmComposerTextInput"]`        |

## Adapting to Page Changes

X.com's interface updates frequently. When a selector doesn't work:

1. Take a snapshot (`GET /snapshot`) — the accessibility tree shows all interactive elements
   with their roles, names, and RefIDs
2. Look for elements by their visible label text (like "Post", "Reply", "Repost")
3. Try extracting raw HTML to find current `data-testid` values:
   ```bash
   curl -X POST 'http://127.0.0.1:9222/api/v1/executor/evaluate' \
     -H 'Content-Type: application/json' \
     -d '{"expression": "document.querySelector(\"article\")?.outerHTML?.substring(0, 2000)"}'
   ```
4. Use text-based identification as a fallback: `"identifier": "Post"` clicks the
   first button with text "Post"

## Rate Limiting & Safety

To avoid being rate-limited or flagged by X.com:
- Add delays between actions (1-3 seconds between operations)
- Don't scroll the timeline aggressively — load a few pages at most
- Avoid posting many tweets in rapid succession
- If you see a CAPTCHA or "something went wrong" message, stop and inform the user
- Use the `sleep` command between curl calls when doing batch operations:

```bash
sleep 2  # wait 2 seconds between actions
```

## Troubleshooting

**Service not running?**
Run `bash scripts/start-browser.sh` from the skill directory.

**Not logged in?**
Open Brave normally (outside of BrowserWing), navigate to x.com, and log in.
Then restart the service — it will reuse Brave's login session.

**Element not found?**
X.com uses dynamic loading. Add a `wait` call before interacting. Re-snapshot after
waiting to get updated RefIDs.

**Compose area doesn't accept text?**
Use the JavaScript fallback method (see "Post a Tweet" section).

**Port conflict?**
The default port is 9222. Pass `--port <number>` to the start script to use a different port.

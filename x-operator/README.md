# X.com (Twitter) Operator

An automated agent for interacting with X.com using [BrowserWing Executor](https://github.com/browserwing/browserwing).

## Prerequisites

1.  **Brave Browser**: Installed on your system.
2.  **X Account**: Logged in within the Brave browser.

## Dependencies

- **BrowserWing Executor**: `npm install -g browserwing`
- **curl**: Used for API interactions.

## Setup & Usage

### 1. Start the Browser Service
Launches BrowserWing on port **9222** (shared with xiaohongshu-operator) using your Brave profile.
```bash
bash scripts/start-browser.sh
```

### 2. Check Service Status
```bash
bash scripts/check-status.sh
```

### 3. Stop the Service
```bash
bash scripts/stop-browser.sh
```

## Operation Details
Refer to [SKILL.md](./SKILL.md) for X.com specific automation workflows (Liking, Timeline Extraction, Posting, etc.).

## Shared Instance Note
This operator shares a browser instance and PID with `xiaohongshu-operator`. Running `start-browser.sh` in either directory will attach to the same persistent browser session on port 9222.

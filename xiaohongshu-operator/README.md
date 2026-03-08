# Xiaohongshu Operator

An automated agent for interacting with Xiaohongshu (Little Red Book) using [BrowserWing Executor](https://github.com/browserwing/browserwing).

## Prerequisites

1.  **Brave Browser**: Installed on your system.
2.  **Xiaohongshu Account**: Logged in within the Brave browser.
3.  **Node.js**: Required for BrowserWing.

## Dependencies

The following tools are required and will be checked/installed by the startup scripts:
- **BrowserWing Executor**: `npm install -g browserwing`
- **Python 3**: Required for running recorded scripts.
- **curl**: Used for API interactions.

## Setup & Usage

### 1. Start the Browser Service
Launches BrowserWing on port **9222** (shared with x-operator) using your Brave profile.
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

### 4. Running Recorded Scripts
If you have JSON recordings from the BrowserWing recorder, you can run them using:
```bash
python3 scripts/run_recorded_script.py path/to/script.json
```

## Operation Details
For detailed API documentation and specific Xiaohongshu automation workflows (Search, Like, Post, etc.), refer to [SKILL.md](./SKILL.md).

## File Management
- **temp/**: All temporary snapshots, screenshots, and HTML dumps are stored here.
- **scripts/**: Core management and execution scripts.
- **evals/**: Evaluation test cases.

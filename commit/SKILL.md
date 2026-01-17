---
name: commit
description: Generate a concise commit message based on current git changes. Supports English and Chinese. Use when user asks to "commit", "write a commit message", or "summarize changes for commit".
---

# Commit Message Generator

Help the user generate a conventional commit message for their current changes.

## Instructions

1.  **Analyze Changes**:
    -   Run `git diff --cached` to see staged changes.
    -   If no output, run `git diff` to see unstaged changes.
    -   If still no output, inform the user there are no changes to commit.

2.  **Determine Language**:
    -   Check the user's request for language preference (e.g., "commit English", "commit 中文").
    -   If explicitly requested, use that language.
    -   If not specified, default to **English**.

3.  **Generate Message**:
    -   Create a **single-line** commit message following the [Conventional Commits](https://www.conventionalcommits.org/) format:
        `<type>: <description>`
    -   **Types**:
        -   `feat`: New feature
        -   `fix`: Bug fix
        -   `docs`: Documentation only
        -   `style`: Code style changes (formatting, missing semi-colons, etc.)
        -   `refactor`: Code change that neither fixes a bug nor adds a feature
        -   `perf`: A code change that improves performance
        -   `test`: Adding missing tests or correcting existing tests
        -   `chore`: Changes to the build process or auxiliary tools and libraries
    -   **Description**:
        -   Use imperative, present tense (e.g., "change" not "changed" or "changes").
        -   Be concise but descriptive.
        -   For **Chinese**, use natural technical Chinese (e.g., "feat: 新增登录功能").

4.  **Output**:
    -   Present the commit message clearly.
    -   Optionally, provide the `git commit -m "..."` command for easy copying or execution.

## Examples

**User**: "commit" (Default English)
**Agent**:
```bash
git commit -m "feat: add user authentication module"
```

**User**: "commit 中文"
**Agent**:
```bash
git commit -m "fix(auth): 修复令牌过期时的无限重定向问题"
```

**User**: "commit style changes"
**Agent**:
```bash
git commit -m "style: format code with prettier"
```

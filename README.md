# 100Hires Portfolio Project

Public portfolio documenting setup of AI dev tools in Cursor for the 100Hires application.

## Tools Installed

| Tool | Purpose |
|------|---------|
| [Cursor](https://cursor.com) | AI-native code editor |
| Claude Code (Anthropic) | Claude agent in the IDE |
| Codex (OpenAI) | OpenAI coding agent in the IDE |

## Steps Completed

1. I created a GitHub repo and cloned it locally
2. I opened the project in Cursor
3. I installed Claude Code and Codex from Extensions (`Cmd + Shift + X`)
4. I verified both extensions in the activity bar and Command Palette
5. I created this README

## Issues & Solutions

### Two Claude Code icons in the activity bar

**Problem:** After installing Claude Code once, I saw two identical icons in Cursor’s activity bar.

**Cause:** I learned it’s a known Cursor quirk, not a double install. Claude Code registers two sidebar views—the main chat panel and a sessions list. Cursor doesn’t fully support the secondary sidebar, so both views end up in the activity bar.

**How to verify:** I disabled the extension in Extensions (`Cmd + Shift + X`). Both icons disappeared together, confirming one install with two views.

**Solution:** I used either icon (chat vs. sessions) or opened Claude Code via Command Palette (`Cmd + Shift + P` → **Claude Code: Open in New Tab** or **Open in sidebar**) or the terminal (`claude`). I couldn’t hide just one icon, but it didn’t affect usage.

### GitHub README didn’t match my local file

**Problem:** The README on GitHub was missing parts of my Issues & Solutions section compared to what I had locally.

**Cause:** I edited the README after the initial commit. Cursor’s automated push failed because GitHub credentials weren’t configured in that environment, so only the earlier committed version reached GitHub until I pushed again.

**Solution:** I checked `git status`, committed my latest README changes, and pushed to `origin main`.

## Author

**Pranay** — [GitHub](https://github.com/pranaybr)

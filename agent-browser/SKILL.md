---
name: agent-browser
description: >
  Headless browser automation CLI for AI agents. Use for web automation, testing,
  taking screenshots, filling forms, clicking elements, and capturing accessibility trees.
  Triggers: browser automation, web testing, screenshots, web scraping, form filling.
---

# agent-browser Skill

Use [agent-browser](https://github.com/vercel-labs/agent-browser) for headless browser automation.

## When This Skill MUST Be Used

**Invoke this skill when the user's request involves ANY of these:**

- Browser automation (opening pages, clicking, typing)
- Taking screenshots of web pages
- Web testing or form filling
- Extracting page content (snapshots, accessibility trees)
- Web scraping or data extraction
- Any `agent-browser` command

## Installation

```bash
npm install -g agent-browser
agent-browser install  # Download Chromium
```

## Core Workflow

The optimal AI workflow uses snapshot + refs:

1. `agent-browser open <url>` - Navigate to page
2. `agent-browser snapshot -i` - Get interactive elements with refs (@e1, @e2)
3. `agent-browser click @e1` / `agent-browser fill @e2 "text"` - Interact using refs
4. Re-snapshot after page changes

## Essential Commands

### Navigation

```bash
agent-browser open <url>              # Navigate to URL
agent-browser back                    # Go back
agent-browser forward                 # Go forward
agent-browser reload                  # Reload page
agent-browser close                   # Close browser
```

### Getting Page Info

```bash
agent-browser snapshot                # Full accessibility tree with refs
agent-browser snapshot -i              # Interactive elements only
agent-browser snapshot -i -c           # Compact (no empty elements)
agent-browser get title                # Get page title
agent-browser get url                  # Get current URL
agent-browser screenshot [path]        # Take screenshot
agent-browser screenshot --annotate   # Annotated with numbered labels
```

### Interaction (using refs from snapshot)

```bash
agent-browser click @e1                # Click by ref
agent-browser fill @e2 "text"          # Clear and fill by ref
agent-browser type @e3 "text"          # Type into element
agent-browser hover @e1                # Hover element
agent-browser focus @e1               # Focus element
agent-browser get text @e1             # Get text content
```

### Traditional Selectors (if refs unavailable)

```bash
agent-browser click "#submit"
agent-browser fill "#email" "test@example.com"
agent-browser find role button click --name "Submit"
agent-browser find label "Email" fill "test@test.com"
```

### Waiting

```bash
agent-browser wait <selector>         # Wait for element
agent-browser wait <ms>                # Wait milliseconds
agent-browser wait --text "Welcome"   # Wait for text
agent-browser wait --url "**/dash"    # Wait for URL pattern
agent-browser wait --load networkidle # Wait for page load
```

## Refs (Recommended)

Refs provide deterministic element selection from snapshots:

```bash
# 1. Get snapshot with refs
agent-browser snapshot
# Output:
# - heading "Example Domain" [ref=e1] [level=1]
# - button "Submit" [ref=e2]
# - textbox "Email" [ref=e3]
# - link "Learn more" [ref=e4]

# 2. Use refs to interact
agent-browser click @e2                   # Click the button
agent-browser fill @e3 "test@example.com" # Fill the textbox
agent-browser get text @e1                # Get heading text
```

**Why use refs?**
- Deterministic: Ref points to exact element from snapshot
- Fast: No DOM re-query needed
- AI-friendly: Snapshot + ref workflow is optimal for LLMs

## Sessions

Run multiple isolated browser instances:

```bash
agent-browser --session agent1 open site-a.com
agent-browser --session agent2 open site-b.com
agent-browser tab                      # List tabs
agent-browser tab new [url]           # New tab
agent-browser tab <n>                  # Switch to tab n
```

## Persistent Profiles

Persist browser state across restarts:

```bash
agent-browser --profile ~/.myapp-profile open myapp.com
```

The profile directory stores cookies, localStorage, IndexedDB, and login sessions.

## Options

```bash
--headed        # Show browser window (not headless)
--json          # JSON output (for agents)
--full, -f      # Full page screenshot
--session <n>   # Use isolated session
```

## Example Tasks

- "Take a screenshot of example.com" -> `agent-browser open example.com && agent-browser screenshot page.png`
- "Fill out a login form" -> `agent-browser open <url> && agent-browser snapshot -i` then use refs to fill
- "Test the login flow" -> Open page, snapshot to find form fields, fill credentials, click submit
- "Get the page title" -> `agent-browser get title`

## Important Notes

- Commands can be chained with `&&` - browser persists via background daemon
- Use `--json` flag for machine-readable output in AI workflows
- The `--headed` flag shows the browser window for debugging
- Install chromium with `agent-browser install` on first use

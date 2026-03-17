---
name: opencode-dev
description: Reference for building OpenCode extensions -- skills, commands, agents, custom tools, MCP servers, plugins, and rules. Covers file locations, frontmatter schemas, configuration patterns, and working examples for each extension type.
---

# OpenCode Development Reference

Complete reference for creating and configuring all OpenCode extension types. Use this skill when the user wants to build, modify, or understand any part of the OpenCode customization system.

---

## 1. Skills

Skills are reusable instruction sets that agents load on-demand via the built-in `skill` tool.

### File layout

One folder per skill containing a `SKILL.md` file:

```
<skills-root>/<skill-name>/SKILL.md
```

### Discovery locations (checked in this order)

| Scope   | Path                                          |
|---------|-----------------------------------------------|
| Project | `.opencode/skills/<name>/SKILL.md`            |
| Global  | `~/.config/opencode/skills/<name>/SKILL.md`   |
| Project | `.claude/skills/<name>/SKILL.md`              |
| Global  | `~/.claude/skills/<name>/SKILL.md`            |
| Project | `.agents/skills/<name>/SKILL.md`              |
| Global  | `~/.agents/skills/<name>/SKILL.md`            |

For project-local paths, OpenCode walks up from the working directory to the git worktree root.

### Frontmatter schema

```yaml
---
name: my-skill            # required, 1-64 chars, lowercase alphanumeric + single hyphens
description: What it does  # required, 1-1024 chars
license: MIT               # optional
compatibility: opencode    # optional
metadata:                  # optional, string-to-string map
  audience: developers
---
```

**Name rules:**
- Lowercase alphanumeric with single hyphen separators
- Cannot start or end with `-`, no consecutive `--`
- Must match the directory name
- Regex: `^[a-z0-9]+(-[a-z0-9]+)*$`

### Body content

Everything after the frontmatter is the skill content. Structure it however you want -- the full content is injected into the conversation when the agent calls `skill({ name: "my-skill" })`.

Recommended sections:
- **When to use** -- triggers that should cause this skill to load
- **Instructions** -- the actual guidance, rules, patterns, examples
- **Examples** -- concrete usage patterns

### Permissions

Control skill access in `opencode.json`:

```json
{
  "permission": {
    "skill": {
      "*": "allow",
      "internal-*": "deny",
      "experimental-*": "ask"
    }
  }
}
```

Override per agent (in agent frontmatter):

```yaml
---
permission:
  skill:
    "my-skill": "allow"
---
```

Or disable the skill tool entirely for an agent:

```yaml
---
tools:
  skill: false
---
```

### Troubleshooting

- Verify `SKILL.md` is all caps
- Check that `name` and `description` are present in frontmatter
- Skill names must be unique across all locations
- Skills with `deny` permission are hidden from agents

### Example

```markdown
---
name: git-release
description: Create consistent releases and changelogs
license: MIT
---

## What I do
- Draft release notes from merged PRs
- Propose a version bump
- Provide a `gh release create` command

## When to use me
Use this when preparing a tagged release.
```

---

## 2. Commands

Custom slash commands that send a predefined prompt when executed.

### File layout

Markdown files in the `commands/` directory. The filename (minus `.md`) becomes the command name.

| Scope   | Path                                    |
|---------|-----------------------------------------|
| Project | `.opencode/commands/<name>.md`          |
| Global  | `~/.config/opencode/commands/<name>.md` |

### Frontmatter schema

```yaml
---
description: What this command does   # shown in TUI autocomplete
agent: build                           # optional, which agent runs it
model: anthropic/claude-sonnet-4-20250514  # optional, override model
subtask: true                          # optional, run as subagent invocation
---
```

All frontmatter fields are optional except that `description` is recommended.

### Body content (the template)

The body is the prompt sent to the LLM. It supports three special features:

**Arguments:**
- `$ARGUMENTS` -- replaced with everything after the command name
- `$1`, `$2`, `$3` ... -- positional arguments

**Shell output:**
- `` !`command` `` -- runs a bash command and injects its stdout into the prompt

**File references:**
- `@path/to/file` -- includes the file content in the prompt

### JSON alternative

Commands can also be defined in `opencode.json`:

```json
{
  "command": {
    "test": {
      "template": "Run the full test suite with coverage.",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-sonnet-4-20250514",
      "subtask": false
    }
  }
}
```

### Example

```markdown
---
description: Create a new component
agent: build
---

Create a new React component named $ARGUMENTS with TypeScript support.
Include proper typing and basic structure.

Here's the current project structure:
!`find src/components -type f -name "*.tsx" | head -20`
```

Usage: `/component Button`

---

## 3. Agents

Specialized AI assistants with custom prompts, models, tool access, and permissions.

### Types

| Mode       | Description                                  | How to invoke             |
|------------|----------------------------------------------|---------------------------|
| `primary`  | Main agents, cycle with Tab key              | Tab key                   |
| `subagent` | Invoked by primary agents or `@mention`      | `@agent-name` in message  |
| `all`      | Can be used as either (default if omitted)   | Both                      |

### File layout

Markdown files in the `agents/` directory:

| Scope   | Path                                   |
|---------|----------------------------------------|
| Project | `.opencode/agents/<name>.md`           |
| Global  | `~/.config/opencode/agents/<name>.md`  |

### Frontmatter schema

```yaml
---
description: What this agent does        # required
mode: subagent                            # primary | subagent | all (default: all)
model: anthropic/claude-sonnet-4-20250514 # optional, override model
temperature: 0.1                          # optional, 0.0-1.0
steps: 10                                 # optional, max agentic iterations
hidden: true                              # optional, hide from @ autocomplete (subagents only)
color: "#ff6b6b"                          # optional, hex or theme color name
top_p: 0.9                                # optional
disable: false                            # optional, disable the agent
prompt: "{file:./prompts/review.txt}"     # optional, load prompt from file
tools:
  write: false
  edit: false
  bash: false
  skill: true
  mymcp_*: false                          # glob patterns supported
permission:
  edit: deny
  bash:
    "*": ask
    "git diff": allow
    "git log*": allow
  webfetch: deny
  skill:
    "my-skill": allow
  task:
    "*": deny
    "my-helper-*": allow
---
```

### Body content

The body is the system prompt. Write instructions for the agent's behavior, focus areas, and constraints.

### JSON alternative

```json
{
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "temperature": 0.1,
      "tools": {
        "write": false,
        "edit": false
      },
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability."
    }
  }
}
```

### Built-in agents

| Agent       | Mode    | Purpose                              |
|-------------|---------|--------------------------------------|
| `build`     | primary | Default agent, all tools enabled     |
| `plan`      | primary | Analysis/planning, writes need approval |
| `general`   | subagent| Multi-step tasks, full tool access   |
| `explore`   | subagent| Read-only codebase exploration       |

### Permission values

- `"allow"` -- no approval needed
- `"ask"` -- user prompted before execution
- `"deny"` -- tool disabled for this agent

Bash permissions support glob patterns. Last matching rule wins:

```json
{
  "permission": {
    "bash": {
      "*": "ask",
      "git status*": "allow",
      "git push": "ask"
    }
  }
}
```

### Task permissions

Control which subagents an agent can invoke:

```yaml
---
permission:
  task:
    "*": deny
    "my-helper-*": allow
    "code-reviewer": ask
---
```

When set to `deny`, the subagent is removed from the Task tool entirely.

### Interactive creation

```bash
opencode agent create
```

This walks you through creating an agent interactively.

### Example

```markdown
---
description: Writes and maintains project documentation
mode: subagent
tools:
  bash: false
---

You are a technical writer. Create clear, comprehensive documentation.

Focus on:
- Clear explanations
- Proper structure
- Code examples
- User-friendly language
```

---

## 4. Custom Tools

Functions the LLM can call alongside built-in tools. Defined in TypeScript/JavaScript but can invoke any language.

### File layout

| Scope   | Path                              |
|---------|-----------------------------------|
| Project | `.opencode/tools/<name>.ts`       |
| Global  | `~/.config/opencode/tools/<name>.ts` |

The filename becomes the tool name.

### Structure

```typescript
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Query the project database",
  args: {
    query: tool.schema.string().describe("SQL query to execute"),
  },
  async execute(args) {
    return `Executed: ${args.query}`
  },
})
```

### Multiple tools per file

Each named export becomes a separate tool named `<filename>_<exportname>`:

```typescript
import { tool } from "@opencode-ai/plugin"

export const add = tool({
  description: "Add two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return args.a + args.b
  },
})

export const multiply = tool({
  description: "Multiply two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return args.a * args.b
  },
})
```

Creates `math_add` and `math_multiply`.

### Arguments

Use `tool.schema` (which is Zod) for argument validation:

```typescript
args: {
  query: tool.schema.string().describe("The SQL query"),
  limit: tool.schema.number().optional().describe("Max rows"),
}
```

### Context

The `execute` function receives a context object:

```typescript
async execute(args, context) {
  const { agent, sessionID, messageID, directory, worktree } = context
  // directory = session working directory
  // worktree = git worktree root
}
```

### Invoking other languages

Define the tool in TypeScript but shell out to any language:

```typescript
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Run Python analysis",
  args: {
    file: tool.schema.string().describe("File to analyze"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, ".opencode/tools/analyze.py")
    const result = await Bun.$`python3 ${script} ${args.file}`.text()
    return result.trim()
  },
})
```

### Name collisions

Custom tools with the same name as a built-in tool will override it. Prefer unique names unless you intentionally want to replace a built-in.

---

## 5. MCP Servers

External tools via the Model Context Protocol. Support both local (stdio) and remote (HTTP) servers.

### Configuration

Add to `opencode.json` under the `mcp` key:

#### Local server

```json
{
  "mcp": {
    "my-server": {
      "type": "local",
      "command": ["npx", "-y", "my-mcp-package"],
      "enabled": true,
      "environment": {
        "API_KEY": "value"
      }
    }
  }
}
```

#### Remote server

```json
{
  "mcp": {
    "my-remote": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer {env:MY_API_KEY}"
      }
    }
  }
}
```

### Local server options

| Option        | Type    | Required | Description                       |
|---------------|---------|----------|-----------------------------------|
| `type`        | string  | yes      | Must be `"local"`                 |
| `command`     | array   | yes      | Command and arguments             |
| `environment` | object  | no       | Environment variables             |
| `enabled`     | boolean | no       | Enable/disable on startup         |
| `timeout`     | number  | no       | Timeout in ms (default: 5000)     |

### Remote server options

| Option    | Type    | Required | Description                       |
|-----------|---------|----------|-----------------------------------|
| `type`    | string  | yes      | Must be `"remote"`                |
| `url`     | string  | yes      | Server URL                        |
| `enabled` | boolean | no       | Enable/disable on startup         |
| `headers` | object  | no       | HTTP headers                      |
| `oauth`   | object  | no       | OAuth config (or `false` to disable) |
| `timeout` | number  | no       | Timeout in ms (default: 5000)     |

### OAuth

Most OAuth flows are automatic. OpenCode handles discovery, dynamic client registration, and token storage.

For pre-registered credentials:

```json
{
  "mcp": {
    "my-server": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp",
      "oauth": {
        "clientId": "{env:CLIENT_ID}",
        "clientSecret": "{env:CLIENT_SECRET}",
        "scope": "tools:read tools:execute"
      }
    }
  }
}
```

CLI commands:

```bash
opencode mcp auth my-server    # authenticate
opencode mcp list              # list servers and auth status
opencode mcp logout my-server  # remove credentials
```

### Managing MCP tools

Disable globally or per-agent using glob patterns on the tool name (prefixed with server name):

```json
{
  "tools": {
    "my-server_*": false
  },
  "agent": {
    "my-agent": {
      "tools": {
        "my-server_*": true
      }
    }
  }
}
```

### Context warning

Each MCP server adds to the context window. Be selective about which servers you enable, especially ones with many tools (like the GitHub MCP server).

---

## 6. Plugins

JavaScript/TypeScript modules that hook into OpenCode events to extend behavior.

### File layout

| Scope   | Path                                   |
|---------|----------------------------------------|
| Project | `.opencode/plugins/<name>.ts`          |
| Global  | `~/.config/opencode/plugins/<name>.ts` |

### npm plugins

Specify in `opencode.json`:

```json
{
  "plugin": ["opencode-helicone-session", "@my-org/custom-plugin"]
}
```

npm plugins are auto-installed via Bun at startup, cached in `~/.cache/opencode/node_modules/`.

### Dependencies for local plugins

Add a `package.json` in the config directory:

```json
{
  "dependencies": {
    "some-package": "^1.0.0"
  }
}
```

OpenCode runs `bun install` at startup.

### Basic structure

```typescript
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    // Event hooks
  }
}
```

Context parameters:
- `project` -- current project info
- `directory` -- current working directory
- `worktree` -- git worktree path
- `client` -- OpenCode SDK client
- `$` -- Bun shell API

### Available events

| Category     | Events                                                                    |
|--------------|---------------------------------------------------------------------------|
| Command      | `command.executed`                                                         |
| File         | `file.edited`, `file.watcher.updated`                                     |
| Installation | `installation.updated`                                                    |
| LSP          | `lsp.client.diagnostics`, `lsp.updated`                                   |
| Message      | `message.part.removed`, `message.part.updated`, `message.removed`, `message.updated` |
| Permission   | `permission.asked`, `permission.replied`                                  |
| Server       | `server.connected`                                                        |
| Session      | `session.created`, `session.compacted`, `session.deleted`, `session.diff`, `session.error`, `session.idle`, `session.status`, `session.updated` |
| Todo         | `todo.updated`                                                            |
| Shell        | `shell.env`                                                               |
| Tool         | `tool.execute.before`, `tool.execute.after`                               |
| TUI          | `tui.prompt.append`, `tui.command.execute`, `tui.toast.show`              |
| Compaction   | `experimental.session.compacting`                                         |

### Hook patterns

**Before/after tool execution:**

```typescript
export const MyPlugin: Plugin = async (ctx) => {
  return {
    "tool.execute.before": async (input, output) => {
      // Modify or block tool calls
      if (input.tool === "read" && output.args.filePath.includes(".env")) {
        throw new Error("Do not read .env files")
      }
    },
    "tool.execute.after": async (input, output) => {
      // React to tool results
    },
  }
}
```

**Event subscriptions:**

```typescript
export const MyPlugin: Plugin = async ({ $ }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.idle") {
        await $`notify-send "OpenCode" "Session completed!"`
      }
    },
  }
}
```

**Inject environment variables:**

```typescript
export const MyPlugin: Plugin = async () => {
  return {
    "shell.env": async (input, output) => {
      output.env.MY_API_KEY = "secret"
    },
  }
}
```

**Register custom tools from plugins:**

```typescript
import { type Plugin, tool } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      mytool: tool({
        description: "Custom tool from plugin",
        args: { foo: tool.schema.string() },
        async execute(args, context) {
          return `Hello ${args.foo}`
        },
      }),
    },
  }
}
```

**Compaction hooks:**

```typescript
export const MyPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Add context that survives compaction
      output.context.push("## Important State\n- Current task: ...")
      // Or replace the entire compaction prompt:
      // output.prompt = "Custom compaction prompt..."
    },
  }
}
```

### Load order

1. Global config plugins (`~/.config/opencode/opencode.json`)
2. Project config plugins (`opencode.json`)
3. Global plugin directory (`~/.config/opencode/plugins/`)
4. Project plugin directory (`.opencode/plugins/`)

---

## 7. Rules (AGENTS.md)

Custom instructions injected into every LLM context.

### File locations

| Scope   | Path                              | Purpose              |
|---------|-----------------------------------|----------------------|
| Project | `AGENTS.md` in project root       | Project-specific rules |
| Global  | `~/.config/opencode/AGENTS.md`    | Personal rules       |
| Compat  | `CLAUDE.md` (fallback if no AGENTS.md) | Claude Code migration |
| Compat  | `~/.claude/CLAUDE.md` (fallback)  | Claude Code migration |

### Creating

Run `/init` in the TUI to auto-generate an `AGENTS.md` from your project structure.

Or create manually:

```markdown
# My Project

## Project Structure
- `src/` - Source code
- `tests/` - Test files

## Code Standards
- Use TypeScript strict mode
- Write tests for all new features
```

### Custom instructions via config

Reference additional instruction files in `opencode.json`:

```json
{
  "instructions": [
    "CONTRIBUTING.md",
    "docs/guidelines.md",
    ".cursor/rules/*.md",
    "https://raw.githubusercontent.com/org/rules/main/style.md"
  ]
}
```

Glob patterns and remote URLs are supported. All instruction files are combined with AGENTS.md.

### Precedence

1. Local `AGENTS.md` (traversing up from cwd)
2. Global `~/.config/opencode/AGENTS.md`
3. Fallback `CLAUDE.md` / `~/.claude/CLAUDE.md`

First match wins per category. `AGENTS.md` takes precedence over `CLAUDE.md`.

---

## 8. Built-in Tools Reference

Quick reference for the tools available to agents:

| Tool         | Purpose                            | Permission key |
|--------------|------------------------------------|---------------|
| `bash`       | Execute shell commands             | `bash`        |
| `edit`       | Modify files via string replacement| `edit`        |
| `write`      | Create/overwrite files             | `edit`        |
| `patch`      | Apply patch files                  | `edit`        |
| `read`       | Read file contents                 | `read`        |
| `grep`       | Search file contents (regex)       | `grep`        |
| `glob`       | Find files by pattern              | `glob`        |
| `list`       | List directory contents            | `list`        |
| `skill`      | Load a skill                       | `skill`       |
| `todowrite`  | Manage task lists                  | `todowrite`   |
| `todoread`   | Read task lists                    | `todoread`    |
| `webfetch`   | Fetch web content                  | `webfetch`    |
| `websearch`  | Search the web (Exa AI)            | `websearch`   |
| `question`   | Ask user questions                 | `question`    |
| `lsp`        | Code intelligence (experimental)   | `lsp`         |

---

## 9. Configuration File Reference

The main config file is `opencode.json` (or `opencode.jsonc`):

| Scope   | Path                                  |
|---------|---------------------------------------|
| Project | `opencode.json` in project root       |
| Global  | `~/.config/opencode/opencode.json`    |

### Key sections

```json
{
  "$schema": "https://opencode.ai/config.json",
  "command": { },
  "agent": { },
  "mcp": { },
  "tools": { },
  "permission": { },
  "instructions": [],
  "plugin": []
}
```

### Environment variable references

Use `{env:VAR_NAME}` in config values to reference environment variables:

```json
{
  "mcp": {
    "my-server": {
      "type": "remote",
      "url": "https://mcp.example.com",
      "headers": {
        "Authorization": "Bearer {env:MY_API_KEY}"
      }
    }
  }
}
```

### File references in prompts

Use `{file:./path/to/file}` to load content from a file:

```json
{
  "agent": {
    "review": {
      "prompt": "{file:./prompts/review.txt}"
    }
  }
}
```

---

## Quick Decision Guide

| I want to...                        | Use this          |
|-------------------------------------|-------------------|
| Inject reusable instructions        | **Skill**         |
| Run a predefined prompt             | **Command**       |
| Create a specialized AI assistant   | **Agent**         |
| Give the LLM a new callable function| **Custom Tool**   |
| Connect an external tool server     | **MCP Server**    |
| Hook into OpenCode events           | **Plugin**        |
| Set project-wide coding standards   | **Rules (AGENTS.md)** |

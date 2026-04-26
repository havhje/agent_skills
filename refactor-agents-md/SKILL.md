---
name: refactor-agents-md
disable-model-invocation: true
description: Refactor AGENTS.md files to follow progressive disclosure principles, keeping root minimal and organizing rules into separate linked files.
---

# Refactoring AGENTS.md Files

Use this skill when refactoring, creating, or auditing an AGENTS.md (or CLAUDE.md) file. The goal is a minimal root file that points to progressively disclosed documentation.

## Core Principle: Progressive Disclosure

AGENTS.md content loads on **every single request**, regardless of relevance. Frontier LLMs can follow ~150-200 instructions with reasonable consistency. Every unnecessary instruction wastes tokens and reduces the agent's ability to follow the instructions that actually matter.

The ideal root AGENTS.md should contain **only** what is relevant to every single task in the repo. Everything else goes into separate files that the agent discovers on demand.

## What Belongs in Root AGENTS.md

Be ruthless. The root file should contain at most:

1. **One-sentence project description** -- anchors the agent's understanding of scope
2. **Package manager** -- only if not npm (e.g., pnpm, yarn, bun)
3. **Non-standard build/typecheck commands** -- only if the agent can't discover them from config files
4. **Links to separate files** -- conversational references, not commands

Example of a well-structured root:

```markdown
This is a React component library for accessible data visualization.

This project uses pnpm workspaces.

For TypeScript conventions, see docs/TYPESCRIPT.md
For testing patterns, see docs/TESTING.md
For API design guidelines, see docs/API_CONVENTIONS.md
For Git workflow, see docs/GIT_WORKFLOW.md
```

That's it. Light touch, conversational references. No "ALWAYS," no all-caps forcing.

## What Does NOT Belong in Root AGENTS.md

- Language-specific coding style rules (move to `docs/TYPESCRIPT.md`, `docs/PYTHON.md`, etc.)
- Testing patterns and conventions (move to `docs/TESTING.md`)
- API design patterns (move to `docs/API_CONVENTIONS.md`)
- Git workflow rules (move to `docs/GIT_WORKFLOW.md`)
- File system structure documentation (goes stale fast -- describe capabilities instead)
- Dependency-specific instructions (move to relevant domain file)
- Anything only relevant to a subset of tasks

## Organizing Separate Files

### Suggested docs/ structure

```
docs/
├── TYPESCRIPT.md          # Language conventions, type patterns
├── PYTHON.md              # Python-specific rules
├── TESTING.md             # Test framework, patterns, coverage
├── API_CONVENTIONS.md     # API design, endpoints, error handling
├── GIT_WORKFLOW.md        # Branch strategy, commit messages, PR process
├── BUILD.md               # Build system, bundling, deployment
├── DATABASE.md            # Schema conventions, migrations, queries
└── ARCHITECTURE.md        # High-level architecture decisions
```

Only create files for categories that have meaningful content. Don't create empty placeholders.

### Nested progressive disclosure

Separate files can reference each other. `docs/TYPESCRIPT.md` can link to `docs/TESTING.md` for TypeScript-specific test patterns. The agent navigates these hierarchies efficiently.

You can also link to external resources (framework docs, library docs). The agent will follow these links when needed.

### Monorepo considerations

In monorepos, use AGENTS.md files at multiple levels:

| Level | Content |
|-------|---------|
| Root | Monorepo purpose, navigation hints, shared tools |
| Package | Package purpose, tech stack, package-specific conventions |

Each level should only contain what's relevant at that scope. The agent sees all merged AGENTS.md files in context.

## Finding Contradictions

Look for instructions that conflict with each other. Common sources:

- Different developers adding opposing preferences over time
- Rules added reactively that contradict existing rules
- Style preferences that changed but old rules weren't removed
- Broad rules that conflict with specific exceptions

For each contradiction found, present both versions to the user and ask which to keep. Do not silently resolve contradictions.

## Flagging Instructions for Deletion

Flag instructions that are:

### Redundant
Instructions the agent already follows by default. Examples:
- "Use meaningful variable names"
- "Follow language best practices"
- "Handle errors appropriately"
- Anything that restates the language's standard style guide without project-specific additions

### Too vague to be actionable
Instructions that don't give the agent enough information to act differently. Examples:
- "Write clean code"
- "Keep things simple"
- "Use best practices"
- "Make it performant"

### Overly obvious
Instructions that any competent developer (or agent) would follow without being told. Examples:
- "Don't commit secrets"
- "Test your code"
- "Use version control"

### Stale file path references
File paths change constantly. If the AGENTS.md references specific file paths, flag them. Prefer describing capabilities over documenting structure. Domain concepts (like "organization" vs "workspace") are more stable than file paths.

## Anti-Patterns to Watch For

1. **Auto-generated AGENTS.md** -- Generated files prioritize comprehensiveness over restraint. They flood context with "useful for most scenarios" content.

2. **Reactive rule accumulation** -- The pattern of "agent did X wrong -> add rule to prevent X -> repeat" creates a ball of mud over time.

3. **ALL-CAPS FORCING** -- Instructions like "ALWAYS do X" or "NEVER do Y" waste tokens on emphasis. Conversational tone works just as well.

4. **Documenting file structure** -- File paths go stale. Describe capabilities and let the agent discover structure at runtime.

5. **Duplicated instructions** -- The same rule stated in different ways across the file.

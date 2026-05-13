---
name: obsidian-note-placement
description: Manually invoked skill for inspecting the full Obsidian vault structure and suggesting where a new note should be placed.
disable-model-invocation: true
---

# Obsidian Note Placement

Use this skill only when explicitly invoked:

```text
/skill:obsidian-note-placement <new note idea>
```

Obsidian vault root:

```text
/home/havhje/Documents/mac
```

## Goal

Help decide where a new Obsidian note belongs in the vault, using the current folder and note structure as context.

The skill should:

1. Show the current vault structure.
2. Explain the apparent organization of the vault.
3. Recommend a destination folder and filename for the new note.
4. Explain why the location fits.
5. Offer alternatives when ambiguous.
6. Ask for confirmation before creating or editing any note.

Do not create, move, or edit notes unless the user explicitly confirms.

## Structure inspection

Use a structure-only listing. Do not read note contents unless the user asks.

Ignore:

- `.obsidian/`
- `.git/`

Recommended command:

```bash
python3 - <<'PY'
from pathlib import Path

root = Path('/home/havhje/Documents/mac')
max_depth = 4
ignore = {'.obsidian', '.git'}
max_entries_per_dir = 80

if not root.exists():
    raise SystemExit(f'Missing Obsidian vault root: {root}')

def walk(path, prefix='', depth=0):
    if depth > max_depth:
        return

    try:
        entries = [entry for entry in path.iterdir() if entry.name not in ignore]
    except PermissionError:
        print(prefix + '[permission denied]')
        return

    entries = sorted(entries, key=lambda entry: (not entry.is_dir(), entry.name.lower()))

    if len(entries) > max_entries_per_dir:
        shown = entries[:max_entries_per_dir]
        truncated = len(entries) - max_entries_per_dir
    else:
        shown = entries
        truncated = 0

    for index, entry in enumerate(shown):
        last = index == len(shown) - 1 and truncated == 0
        connector = '└── ' if last else '├── '
        print(prefix + connector + entry.name + ('/' if entry.is_dir() else ''))

        if entry.is_dir() and depth < max_depth:
            walk(entry, prefix + ('    ' if last else '│   '), depth + 1)

    if truncated:
        print(prefix + f'└── … {truncated} more entries')

print(root.name + '/')
walk(root)
PY
```

If the output is very large, summarize the structure and include the most relevant branches for the requested note.

## Observed top-level organization

Use these categories as placement guidance:

- `00 Privat/`
  - private life, personal administration, climbing, food, movies/series, lists, avalanche/snow safety, pension, insurance, personal tasks

- `10 Koding og KI/`
  - coding, AI, Pi, Feynman, code projects, development ideas, terminal tools, machine learning, agent best practices

- `20 Naturmangfoldskunnskap/`
  - biodiversity knowledge, species data, birds, bird sounds, sensitivity/sulnerability assessments

- `40 MC Prosjekter/`
  - work/client/project notes, project meetings, environmental assessments, military/construction/environment projects, time tracking, project-specific tasks

- `50 Verktøy/`
  - tools and workflows, GIS, ArcGIS Pro, QGIS, geospatial Python, BirdNET, Maconomy, software/how-to notes

- `60 Mac/`
  - Mac setup, Mac utilities, window managers, configuration notes

- `70 Omarchy/`
  - Omarchy/Linux setup notes

- `Bilder/`
  - attachments, pasted images, PDFs, supporting media. Avoid placing normal text notes here unless the note is specifically about media/attachments.

- `Excalidraw/`
  - drawings and visual notes. Avoid placing normal text notes here unless specifically Excalidraw-related.

Prefer existing folders over creating new folders. Suggest a new folder only when the note clearly does not fit any existing folder.

## Placement rules

When suggesting a location:

1. Match the note idea to the most specific existing folder.
2. If it relates to an existing project, place it inside that project folder.
3. If it is a reusable method/tool/how-to, prefer `50 Verktøy/` over a project folder.
4. If it is a coding/AI idea or implementation note, prefer `10 Koding og KI/`.
5. If it is general biodiversity/domain knowledge, prefer `20 Naturmangfoldskunnskap/`.
6. If it is client/work-project-specific, prefer `40 MC Prosjekter/`.
7. If it is private/personal, prefer `00 Privat/`.
8. Avoid root-level notes unless the note is broad, temporary, or intentionally uncategorized.

## Filename rules

Suggest a concise `.md` filename that matches the existing naming style.

- Preserve Norwegian titles when the topic is Norwegian.
- Use normal spaces, not underscores, unless the existing folder convention suggests otherwise.
- Avoid characters that are inconvenient in filenames.
- If a note with the suggested name already exists, suggest a distinct alternative.

Before creating a file, check whether it already exists.

## Recommendation format

Respond like this:

```text
Current structure:
<tree or relevant tree excerpt>

How I read the structure:
<short explanation>

Recommended placement:
Folder: <folder>
Filename: <filename.md>
Full path: <full path>

Reason:
<why this location fits>

Alternatives:
- <alternative folder/file if relevant>

Create this note?
```

Only create the note if the user confirms.

## Note creation

If the user confirms, create the note at the agreed path.

Use minimal initial content unless the user provides specific content. A good default is:

```markdown
# <title>

```

After creating the note, report the full path.

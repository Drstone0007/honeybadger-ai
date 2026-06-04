# USAGE GUIDE
## Honey Badger Kernel OS v1.0 — TITAN BUILD

```
═══════════════════════════════════════════════════════════════════
  HONEY BADGER KERNEL — USER GUIDE
  Elite Tech Conglomerate | Zero Compromise
═══════════════════════════════════════════════════════════════════
```

## Table of Contents

1. [Getting Started](#getting-started)
2. [Chat Interface](#chat-interface)
3. [Agent Mode](#agent-mode)
4. [Document Editor](#document-editor)
5. [Memory System](#memory-system)
6. [Email Integration](#email-integration)
7. [Calendar](#calendar)
8. [Notes & Tasks](#notes--tasks)
9. [Deep Research](#deep-research)
10. [Model Comparison](#model-comparison)
11. [Settings](#settings)
12. [Keyboard Shortcuts](#keyboard-shortcuts)
13. [Mobile Usage](#mobile-usage)
14. [Tips & Tricks](#tips--tricks)

---

## Getting Started

### First Login

1. Open browser to `http://localhost:7000`
2. Enter admin credentials (from terminal output)
3. Change password in Settings → Security
4. Configure model endpoints in Settings → Models
5. Start chatting!

### Interface Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  ┌─────────┐  ┌──────────────────────────────────────────────┐ │
│  │         │  │  HEADER: Title, Model Selector, Actions      │ │
│  │ SIDEBAR │  ├──────────────────────────────────────────────┤ │
│  │         │  │                                              │ │
│  │ Sessions│  │                                              │ │
│  │ Notes   │  │  MAIN CONTENT: Chat / Documents / Research   │ │
│  │ Calendar│  │                                              │ │
│  │ Email   │  │                                              │ │
│  │ Settings│  │                                              │ │
│  │         │  ├──────────────────────────────────────────────┤ │
│  │         │  │  INPUT: Message box, Send button, Tools      │ │
│  └─────────┘  └──────────────────────────────────────────────┘ │
│  STATUS BAR: Version, Uptime, System Status                    │
└─────────────────────────────────────────────────────────────────┘
```

### Navigation

- **Ctrl+K** — Command palette
- **Ctrl+B** — Toggle sidebar
- **Ctrl+N** — New session
- **Esc** — Close modals

---

## Chat Interface

### Basic Chat

1. Select a model from the dropdown
2. Type your message
3. Press Enter or click Send
4. Wait for response

### Chat Features

#### Web Search
- Click the 🔍 icon or type `/search`
- Enables real-time web search
- Results injected into context

#### File Attachments
- Click the 📎 icon
- Select files to upload
- Supports: images, PDFs, text files

#### Presets
- Click the 🎭 icon
- Select a preset (e.g., "Researcher", "Coder")
- System prompt changes automatically

#### Thinking Mode
- Click the 🧠 icon
- Shows AI's reasoning process
- Useful for complex problems

### Chat Commands

| Command | Description |
|---------|-------------|
| `/search` | Toggle web search |
| `/memory` | View/modify memory |
| `/preset [name]` | Switch preset |
| `/clear` | Clear context |
| `/export` | Export chat as markdown |
| `/help` | Show all commands |

### Message Actions

- **Edit** — Modify your message
- **Retry** — Regenerate response
- **Copy** — Copy message text
- **Delete** — Remove message
- **Share** — Generate shareable link

---

## Agent Mode

Agent mode gives the AI access to tools and system capabilities.

### Enabling Agent Mode

1. Click the ⚡ icon in the header
2. Or type `/agent` in chat
3. Toggle switches appear for tool access

### Available Tools

| Tool | Description | Risk Level |
|------|-------------|------------|
| `bash` | Execute shell commands | High |
| `python` | Run Python code | Medium |
| `read_file` | Read file contents | Low |
| `write_file` | Create/modify files | Medium |
| `web_search` | Search the web | Low |
| `web_fetch` | Fetch URL content | Low |
| `manage_memory` | Edit persistent memory | Low |
| `manage_notes` | Create/edit notes | Low |
| `manage_calendar` | Calendar operations | Low |
| `manage_tasks` | Task management | Low |
| `send_email` | Send email | Medium |
| `generate_image` | Create images | Low |
| `builtin_browser` | Browser automation | Medium |

### Safety Features

- **Permission gates** — High-risk tools require explicit enable
- **Path restrictions** — File access limited to safe directories
- **Command timeout** — Long-running commands auto-terminate
- **Output filtering** — Sensitive data redacted automatically

### Example: File Operations

```
User: Read the contents of config.json

Agent: I'll read that file for you.
[Tool: read_file]
[Path: config.json]
[Result: {"api_key": "xxx", ...}]

Here's the contents of config.json:
...
```

### Example: Web Research

```
User: Research the latest AI news and summarize

Agent: I'll search for the latest AI news.
[Tool: web_search]
[Query: AI news today]
[Tool: web_fetch]
[URL: https://example.com/article]

Based on my research, here are the key developments:
1. ...
```

---

## Document Editor

### Creating Documents

1. Click **Documents** in sidebar
2. Click **+ New Document**
3. Choose type: Markdown, HTML, CSV
4. Start writing

### Editor Features

- **Multi-tab** — Edit multiple documents simultaneously
- **Syntax highlighting** — Auto-detection for code blocks
- **Live preview** — Real-time rendered output
- **AI assist** — Select text → AI actions
- **Version history** — Auto-save with undo

### AI Document Actions

Select text, then:
- **Improve writing** — Enhance clarity and style
- **Fix grammar** — Correct errors
- **Expand** — Add more detail
- **Summarize** — Condense content
- **Translate** — Convert to another language
- **Format** — Apply consistent styling

### Document Types

| Type | Extension | Use Case |
|------|-----------|----------|
| Markdown | `.md` | Notes, documentation |
| HTML | `.html` | Web content |
| CSV | `.csv` | Data tables |
| JSON | `.json` | Configuration |

### Collaboration

- **Export** — Download as file
- **Share** — Generate link
- **Import** — Upload existing files
- **PDF export** — Generate PDF

---

## Memory System

### How Memory Works

Memory stores facts about you and your preferences across sessions.

### Memory Types

| Type | Description | Example |
|------|-------------|---------|
| **Pinned** | Always included | "My name is John" |
| **Recalled** | RAG-retrieved | Project details |
| **Auto-saved** | Extracted from chat | "Prefers dark mode" |

### Managing Memory

1. Click **Memory** in sidebar
2. View all stored memories
3. Add/edit/delete memories
4. Pin important facts

### Memory Commands

```
User: Remember that I prefer Python over JavaScript

AI: [Saves to memory]
✓ Memory saved: "Prefers Python over JavaScript"

User: What do you remember about me?

AI: Based on my memory:
- Name: John
- Prefers Python over JavaScript
- Working on Project X
...
```

### Memory Privacy

- **Per-user isolation** — Each user has separate memory
- **No cloud sync** — Memory stays local
- **Export/Import** — Backup your memory
- **Clear all** — Wipe memory completely

---

## Email Integration

### Setup

1. Go to **Settings → Email**
2. Add IMAP account
3. Add SMTP account
4. Configure triage rules

### Supported Providers

| Provider | IMAP | SMTP |
|----------|------|------|
| Gmail | ✓ | ✓ |
| Outlook | ✓ | ✓ |
| Yahoo | ✓ | ✓ |
| Custom | ✓ | ✓ |

### AI Triage Features

- **Auto-tag** — Categorize incoming mail
- **Urgency detection** — Flag important messages
- **Auto-summary** — Generate email summaries
- **Draft replies** — AI-powered response drafts
- **Spam detection** — Filter unwanted mail

### Reading Emails

1. Click **Email** in sidebar
2. View inbox with AI tags
3. Click email to read
4. Summary displayed at top

### Composing Emails

1. Click **Compose** button
2. Recipient auto-suggested
3. Write or let AI draft
4. Review and send

### Email Commands

```
User: Check my email for anything urgent

AI: [Scans inbox]
Found 2 urgent emails:
1. From: boss@company.com
   Subject: Q4 Report Due Tomorrow
   Urgency: HIGH — Deadline

2. From: team@project.com
   Subject: Production Issue
   Urgency: MEDIUM — Needs attention
```

---

## Calendar

### Setup

1. Go to **Settings → Calendar**
2. Add CalDAV account (Radicale, Nextcloud, etc.)
3. Or import .ics files

### Calendar Features

- **Multi-calendar** — Multiple calendar support
- **Color coding** — Custom colors per calendar
- **Agent-aware** — AI can read/create events
- **Sync** — Two-way CalDAV sync
- **Import/Export** — .ics file support

### Viewing Calendar

1. Click **Calendar** in sidebar
2. Choose view: Day, Week, Month
3. Click event for details
4. Drag to reschedule

### Creating Events

1. Click **+** or drag on calendar
2. Enter title and details
3. Set time and recurrence
4. Add reminders

### AI Calendar Commands

```
User: What's on my schedule today?

AI: [Reads calendar]
Today's schedule:
- 10:00 AM — Team standup
- 2:00 PM — Client call
- 4:00 PM — Code review

User: Schedule a meeting with John tomorrow at 3 PM

AI: [Creates event]
✓ Created: "Meeting with John"
  Tomorrow, 3:00 PM - 4:00 PM
```

---

## Notes & Tasks

### Notes

Quick notes with optional reminders.

#### Creating Notes

1. Click **Notes** in sidebar
2. Click **+ New Note**
3. Write content
4. Set reminder (optional)

#### Note Features

- **Markdown support** — Rich formatting
- **Reminders** — Browser/email/ntfy notifications
- **Search** — Full-text search
- **Tags** — Organize with tags

### Tasks

Todo lists with scheduling.

#### Creating Tasks

1. Click **Tasks** in sidebar
2. Click **+ New Task**
3. Enter task description
4. Set schedule (optional)

#### Task Features

- **Checklist** — Mark items complete
- **Scheduling** — Cron-style scheduling
- **Recurring** — Daily/weekly/monthly
- **Agent access** — AI can manage tasks

### Task Commands

```
User: Add a task to review PR #123

AI: [Creates task]
✓ Task created: "Review PR #123"
  Due: Today
  Priority: Normal

User: List my tasks

AI: [Lists tasks]
Your tasks:
- [ ] Review PR #123 (Due today)
- [x] Update documentation (Completed)
- [ ] Deploy to staging (Due tomorrow)
```

---

## Deep Research

### Starting Research

1. Click **Research** in sidebar
2. Enter research topic
3. Click **Start Research**
4. Wait for completion

### Research Process

1. **Query synthesis** — AI refines your question
2. **Source gathering** — Multiple search queries
3. **Content extraction** — Read and analyze sources
4. **Synthesis** — Combine findings
5. **Report generation** — Structured output

### Research Output

- **Executive summary** — Quick overview
- **Key findings** — Main points
- **Detailed analysis** — In-depth coverage
- **Sources** — All references
- **Visual report** — Formatted HTML output

### Research Commands

```
User: Research the impact of AI on healthcare

AI: [Starts research]
Phase 1: Synthesizing query...
Phase 2: Searching 15 sources...
Phase 3: Extracting content...
Phase 4: Analyzing findings...
Phase 5: Generating report...

[Produces visual report]
```

### Research Settings

- **Max sources** — Number of sources to check
- **Time filter** — Recent vs. all-time
- **Language** — Source language preference
- **Depth** — Quick vs. comprehensive

---

## Model Comparison

### Starting Comparison

1. Click **Compare** in sidebar
2. Select 2+ models
3. Enter test prompt
4. View side-by-side results

### Comparison Features

- **Blind test** — Hide model names
- **Multiple models** — Compare 2-6 models
- **Criteria** — Rate quality, speed, accuracy
- **Export** — Save comparison results

### Blind Comparison

1. Enable "Blind Mode"
2. Models labeled as Model A, Model B, etc.
3. Vote for best response
4. Reveal model names after voting

### Use Cases

- **Model selection** — Choose best model for your needs
- **Quality testing** — Evaluate model performance
- **Prompt optimization** — Find best prompt for each model
- **Cost analysis** — Compare price vs. quality

---

## Settings

### Accessing Settings

- Click ⚙️ in sidebar
- Or press **Ctrl+,**

### Settings Sections

#### General
- **Theme** — Dark/light/custom
- **Language** — UI language
- **Density** — Compact/comfortable
- **Font** — Mono/sans/serif

#### Models
- **Endpoints** — Add LLM servers
- **Default model** — Primary model
- **Fallbacks** — Backup models
- **Limits** — Token limits

#### Search
- **Provider** — SearXNG/Brave/DuckDuckGo
- **Safe search** — Strict/moderate/off
- **Result count** — Results per query

#### Email
- **Accounts** — IMAP/SMTP setup
- **Triage rules** — Auto-tagging
- **Notifications** — Alert preferences

#### Calendar
- **CalDAV** — Sync settings
- **Colors** — Calendar colors
- **Reminders** — Default reminders

#### Security
- **Password** — Change password
- **2FA** — Enable two-factor auth
- **Sessions** — Active sessions
- **API tokens** — Access tokens

#### Advanced
- **Debug mode** — Enable logging
- **Metrics** — Performance monitoring
- **Backup** — Export/import data

---

## Keyboard Shortcuts

### Global

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Command palette |
| `Ctrl+B` | Toggle sidebar |
| `Ctrl+N` | New session |
| `Ctrl+S` | Save current |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Esc` | Close modal |

### Chat

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Shift+Enter` | New line |
| `Ctrl+Up` | Edit previous |
| `Ctrl+Down` | Edit next |
| `Ctrl+/` | Show commands |

### Editor

| Shortcut | Action |
|----------|--------|
| `Ctrl+B` | Bold |
| `Ctrl+I` | Italic |
| `Ctrl+K` | Link |
| `Ctrl+Shift+K` | Delete line |
| `Ctrl+/` | Comment |

### Navigation

| Shortcut | Action |
|----------|--------|
| `1-9` | Switch tabs |
| `Ctrl+1-9` | Switch sections |
| `Alt+Left` | Go back |
| `Alt+Right` | Go forward |

---

## Mobile Usage

### Accessing on Mobile

1. Open browser on phone
2. Navigate to `http://your-ip:7000`
3. Login with credentials
4. Add to home screen (PWA)

### PWA Features

- **Installable** — Add to home screen
- **Offline** — Basic functionality offline
- **Push notifications** — Alert support
- **Touch gestures** — Swipe, pinch, tap

### Mobile-Optimized UI

- **Responsive layout** — Adapts to screen size
- **Touch-friendly** — Larger tap targets
- **Collapsible sidebar** — Hamburger menu
- **Bottom input** — Easy thumb access

### Mobile Tips

- **Swipe left** — Open sidebar
- **Swipe right** — Close sidebar
- **Pull down** — Refresh content
- **Long press** — Context menu

---

## Tips & Tricks

### Power User Features

1. **Slash commands** — Type `/` for quick actions
2. **Drag & drop** — Upload files by dragging
3. **Multi-select** — Ctrl+click for multiple items
4. **Quick search** — Ctrl+K for everything
5. **Preset shortcuts** — Number keys for presets

### Productivity Hacks

1. **Templates** — Save common prompts
2. **Snippets** — Reuse text blocks
3. **Bookmarks** — Save important messages
4. **Export chats** — Backup conversations
5. **Auto-naming** — Sessions auto-named

### Privacy Tips

1. **Incognito mode** — No memory saved
2. **Local models** — Run models locally
3. **No telemetry** — Zero data collection
4. **Encrypted storage** — Database encryption
5. **Secure cookies** — HTTPS-only mode

### Performance Tips

1. **Use presets** — Optimized system prompts
2. **Limit context** — Reduce token usage
3. **Clear history** — Free up memory
4. **Cache results** — Faster repeated queries
5. **Local search** — Use local SearXNG

### Troubleshooting

1. **Clear cache** — Ctrl+Shift+Delete
2. **Hard refresh** — Ctrl+F5
3. **Check logs** — Settings → Debug
4. **Restart** — Docker/native restart
5. **Reset** — Clear data folder

---

```
═══════════════════════════════════════════════════════════════════
  HONEY BADGER KERNEL — USER GUIDE COMPLETE
  All systems operational | Build TITAN
═══════════════════════════════════════════════════════════════════
```

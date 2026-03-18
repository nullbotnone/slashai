---
title: "How to Set Up OpenClaw: Complete Beginner's Guide"
description: "OpenClaw went viral in 2026. Here's how to install it, connect your tools, and run your first AI agent — no coding required."
pubDate: 2026-03-18
toolName: "OpenClaw"
difficulty: "Beginner"
timeToComplete: "30 minutes"
tags: ["openclaw", "ai agents", "setup", "automation", "beginner"]
---

OpenClaw is the open-source AI agent platform that went viral in early 2026. It connects AI models to your apps, browser, and system tools — letting you automate workflows, manage files, send emails, and control APIs with simple chat commands. Over 100,000 GitHub stars and counting.

This guide walks you through setup from zero to your first working agent.

---

## What You'll Need

- A computer (Mac, Linux, or Windows)
- Node.js 18+ installed
- An OpenAI API key (or other supported AI model)
- 30 minutes

---

## Step 1: Install OpenClaw

Open your terminal and run:

```bash
npm install -g openclaw
```

Verify installation:

```bash
openclaw --version
```

You should see a version number. If not, check your Node.js installation with `node --version`.

---

## Step 2: Initial Setup

Run the setup wizard:

```bash
openclaw setup
```

This will:
1. Create a config directory at `~/.openclaw/`
2. Ask for your AI model API key
3. Set up default permissions

**Enter your OpenAI API key** when prompted. If you don't have one:
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an account or sign in
3. Go to API Keys → Create new key
4. Copy and paste it into OpenClaw

---

## Step 3: Start the Gateway

The gateway is OpenClaw's background service:

```bash
openclaw gateway start
```

Check that it's running:

```bash
openclaw gateway status
```

You should see: `Gateway is running ✓`

---

## Step 4: Your First Command

Try a simple command to test everything works:

```bash
openclaw ask "What files are in my Documents folder?"
```

OpenClaw will use its file system skill to look at your Documents folder and answer.

---

## Step 5: Connect Skills

OpenClaw's power comes from skills — pre-built integrations. Install some useful ones:

```bash
# Web search
openclaw skills install web-search

# Email (Gmail)
openclaw skills install gmail

# Calendar
openclaw skills install google-calendar

# File management
openclaw skills install filesystem
```

Each skill adds new capabilities. After installing, you can ask things like:

```bash
openclaw ask "Search the web for the latest AI news and summarize it"
openclaw ask "Do I have any meetings tomorrow?"
openclaw ask "Draft an email to john@example.com about our project update"
```

---

## Step 6: Automate Something Real

Now let's automate a real task. Create a simple workflow:

```bash
openclaw workflow create morning-briefing
```

Add steps to your workflow:

```bash
openclaw workflow add morning-briefing "Check my calendar for today's meetings"
openclaw workflow add morning-briefing "Search for news in my industry"
openclaw workflow add morning-briefing "Compile a summary with meetings and news"
```

Run it:

```bash
openclaw workflow run morning-briefing
```

You'll get a compiled morning briefing with your schedule and relevant news.

---

## Step 7: Set Up Chat Interface (Optional)

OpenClaw includes a web chat interface:

```bash
openclaw ui start
```

Open your browser to `http://localhost:3000` and chat with your AI agent instead of using the terminal.

---

## What You Can Do Now

Now that OpenClaw is running, here are some ideas:

| Task | Command |
|------|---------|
| Research a topic | `openclaw ask "Research the best project management tools for freelancers"` |
| Manage files | `openclaw ask "Organize my Downloads folder by file type"` |
| Check email | `openclaw ask "Summarize my unread emails from today"` |
| Schedule meeting | `openclaw ask "Find a 30-minute slot tomorrow for a client call"` |
| Draft content | `openclaw ask "Write a LinkedIn post about AI productivity tools"` |

---

## Troubleshooting

**"Command not found"**
Make sure Node.js is installed and npm global bin is in your PATH.

**"API key invalid"**
Double-check your OpenAI API key at platform.openai.com.

**"Gateway not running"**
Run `openclaw gateway restart` and check status.

---

## Next Steps

- **Explore skills:** Browse available skills at the OpenClaw skill marketplace
- **Create workflows:** Automate your most repetitive tasks
- **Connect more tools:** Slack, Notion, HubSpot — the ecosystem grows daily
- **Join the community:** Discord server has tips and workflow examples

---

## Final Thoughts

OpenClaw is free, open-source, and backed by a massive community. The initial setup takes 30 minutes, but the time savings compound daily. Start with one workflow, add more as you get comfortable.

The AI agent revolution isn't coming — it's here. OpenClaw is your entry point.

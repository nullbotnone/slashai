---
title: "Build Your First AI Workflow with n8n (No Code)"
description: "n8n is the open-source Zapier alternative with native AI support. Here's how to build an automated lead processing workflow from scratch."
pubDate: 2026-03-18
toolName: "n8n"
difficulty: "Intermediate"
timeToComplete: "45 minutes"
tags: ["n8n", "automation", "workflow", "no-code", "ai agents"]
---

n8n is the open-source automation platform that's giving Zapier serious competition. It's free to self-host, has native AI agent support, and handles complex workflows Zapier can't.

This tutorial builds a real workflow: new lead comes in → AI qualifies it → CRM gets updated → personalized email goes out. All automatically.

---

## Why n8n Over Zapier?

| Feature | n8n | Zapier |
|---------|-----|--------|
| Price (self-hosted) | Free | N/A |
| Price (cloud) | €24/mo | $20/mo |
| AI agent nodes | ✅ Native | ❌ |
| Complex branching | ✅ Easy | ⚠️ Limited |
| Loops | ✅ Native | ❌ |
| Code when needed | ✅ JavaScript | ✅ (limited) |
| Integrations | 400+ | 6,000+ |

**Bottom line:** n8n wins on flexibility and AI features. Zapier wins on sheer number of integrations.

---

## What We're Building

```
New contact form submission
    ↓
AI qualifies the lead (score 1-10)
    ↓
Score ≥ 7? → Add to CRM as "Hot Lead" → Send personalized intro email
Score < 7? → Add to CRM as "Nurture" → Add to weekly newsletter
```

All automatic. You only get notified about hot leads.

---

## Step 1: Set Up n8n

**Option A: Cloud (Easiest)**
1. Go to [n8n.io](https://n8n.io)
2. Sign up for cloud plan (€24/mo, 14-day free trial)
3. You're ready — skip to Step 2

**Option B: Self-Hosted (Free)**
If you have a server or want to run locally:

```bash
# Install globally
npm install -g n8n

# Start n8n
n8n start
```

Or with Docker:

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Open `http://localhost:5678` in your browser. Create your admin account.

---

## Step 2: Create a New Workflow

1. n8n dashboard → **New Workflow**
2. Name it: "Lead Qualification Pipeline"

---

## Step 3: Add the Trigger (Form Submission)

1. Click **+** to add a node
2. Search for **Webhook**
3. Select **Webhook** → **GET** (we'll switch to POST after testing)
4. Copy the webhook URL — this is where form submissions will go

**Test it:** In a new tab, visit the webhook URL with some test data:
```
https://your-n8n-instance.com/webhook/test?name=John%20Smith&email=john@example.com&message=I%20need%20help%20with%20my%20website
```

Click "Listen for test event" in n8n first, then visit the URL. You should see the data appear.

---

## Step 4: Add AI Lead Qualification

Now the fun part — AI-powered lead scoring:

1. Click **+** after the Webhook node
2. Search for **OpenAI** (or your preferred AI provider)
3. Select **OpenAI** → **Chat** → **Message Model**
4. Configure:
   - **Model:** gpt-4
   - **System Message:**

```
You are a lead qualification expert. Score the incoming lead from 1-10 based on:
- Specificity of their request (vague = low, specific = high)
- Budget indicators
- Timeline urgency
- Fit with our services

Respond ONLY with JSON:
{"score": <number>, "reasoning": "<brief explanation>", "priority": "hot/warm/cold"}
```

   - **User Message:** Map the webhook data:
```
Name: {{ $json.name }}
Email: {{ $json.email }}
Message: {{ $json.message }}
```

---

## Step 5: Add Conditional Branching

1. Click **+** after the OpenAI node
2. Search for **IF**
3. Configure the condition:
   - **Value 1:** `{{ $json.score }}`
   - **Operation:** Greater or Equal
   - **Value 2:** `7`

This creates two branches: **True** (hot leads, score ≥ 7) and **False** (nurture leads, score < 7).

---

## Step 6: Hot Lead Branch (Score ≥ 7)

### Step 6a: Add to CRM

1. Click **+** on the True branch
2. Search for your CRM (HubSpot, Salesforce, Pipedrive)
3. Configure to create a new contact:
   - **Name:** `{{ $('Webhook').item.json.name }}`
   - **Email:** `{{ $('Webhook').item.json.email }}`
   - **Lead Score:** `{{ $json.score }}`
   - **Label:** "Hot Lead"

### Step 6b: Send Notification

1. Click **+** after CRM
2. Add **Slack** (or Email) node
3. Send yourself a notification:

```
🔥 New Hot Lead!

Name: {{ $('Webhook').item.json.name }}
Email: {{ $('Webhook').item.json.email }}
Score: {{ $json.score }}/10
Message: {{ $('Webhook').item.json.message }}

Reply within 24 hours!
```

### Step 6c: Send Personalized Intro Email

1. Click **+** after notification
2. Add **Gmail** (or Outlook) node
3. Configure to send email:

**Subject:** `Re: Your inquiry — let's chat`

**Body:**
```
Hi {{ $('Webhook').item.json.name }},

Thanks for reaching out! I read your message and I'd love to help.

{{ $json.reasoning }}

Are you free for a 20-minute call this week? Here's my calendar: [link]

Looking forward to it!
```

---

## Step 7: Nurture Branch (Score < 7)

### Step 7a: Add to CRM as Nurture

1. Click **+** on the False branch
2. Add your CRM node
3. Create contact with label "Nurture"

### Step 7b: Add to Newsletter

1. Click **+** after CRM
2. Add **Mailchimp** (or ConvertKit, Beehiiv) node
3. Add contact to your newsletter list

---

## Step 8: Test the Full Workflow

1. Click **Test Workflow** in n8n
2. Send a test webhook with sample data:
   - **Hot lead:** "I need a new website by next month, budget is $5K"
   - **Cold lead:** "Just browsing, what do you do?"
3. Watch each node execute and check the outputs

---

## Step 9: Activate

Once testing looks good:

1. Toggle **Active** in the top right
2. Update your website's contact form to POST to the webhook URL
3. Done — leads now flow through your AI pipeline automatically

---

## What You Just Built

- **AI-powered lead scoring** — no more guessing which leads are worth your time
- **Automatic CRM updates** — every lead gets logged, categorized
- **Instant hot lead response** — reply in minutes, not days
- **Newsletter pipeline** — cold leads aren't lost, they're nurtured

**Time saved:** 2-3 hours/week on lead management

---

## Next Steps

- Add more qualification criteria to the AI prompt
- Build a follow-up sequence for warm leads (score 4-6)
- Add a weekly digest email summarizing all leads
- Connect to your calendar for automatic meeting booking

---

## Final Thoughts

This workflow alone can transform a freelancer's business. No more lost leads, no more slow responses, no more guessing which inquiries are worth your time.

n8n is free to self-host and the AI nodes make it more powerful than Zapier for automation-heavy workflows. Start with this lead pipeline, then build more as you get comfortable.

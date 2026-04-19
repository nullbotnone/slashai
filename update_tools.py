import json

# Load the tools data
with open('src/data/tools.json', 'r') as f:
    tools = json.load(f)

# Helper function to find tool by slug
def find_tool(slug):
    for i, tool in enumerate(tools):
        if tool['slug'] == slug:
            return i
    return None

# Update Jasper AI
jasper_idx = find_tool('jasper-ai')
if jasper_idx is not None:
    tools[jasper_idx]['longDescription'] = "Jasper AI is the leading AI writing tool for marketers and content creators. Its Brand Voice feature learns your writing style from samples, ensuring consistent tone across all content. Jasper integrates with Surfer SEO for optimized content, offers 50+ templates, and includes a Chrome extension that works in Gmail, Google Docs, LinkedIn, and WordPress. Recent updates include $125M Series A funding (valuing company at $1.5B), new browser extension, and the \"State of AI in Marketing 2026\" report showing 91% of marketing teams now use AI (up from 63% last year). Latest product updates include Jasper Grid orchestration layer, Content Engineering Certification, Company Knowledge Hub, enhanced control features, Marketing AI Agents, advanced model options in Studio, and Studio Agent Sharing for standardized content generation. In April 2026, Jasper introduced Advanced Brand Memory and Alignment, Enhanced SEO Optimization with Optimization Agent, Autonomous AI Agents and Workflows (including Product Update Email AI Agent), Content Automation Platform, Upgraded Image Generation with Nano Banana, Enhanced Prompt Skill, Improved Integrations and Knowledge Layer, and continued focus on Enterprise Marketing."
    tools[jasper_idx]['pros'] = [
        "Best-in-class Brand Voice",
        "Surfer SEO integration",
        "Chrome extension works everywhere",
        "50+ content templates",
        "$125M Series A funding at $1.5B valuation",
        "New browser extension launched",
        "Jasper Grid orchestration layer",
        "Content Engineering Certification",
        "Company Knowledge Hub",
        "Enhanced control & execution features",
        "Marketing AI Agents",
        "Advanced model options in Studio",
        "Studio Agent Sharing",
        "Advanced Brand Memory and Alignment (April 2026)",
        "Enhanced SEO Optimization with Optimization Agent (April 2026)",
        "Autonomous AI Agents and Workflows (April 2026)",
        "Content Automation Platform (April 2026)",
        "Upgraded Image Generation with Nano Banana (April 2026)",
        "Enhanced Prompt Skill (April 2026)",
        "Improved Integrations and Knowledge Layer (April 2026)",
        "Focus on Enterprise Marketing (April 2026)"
    ]

# Update Writesonic
writesonic_idx = find_tool('writesonic')
if writesonic_idx is not None:
    tools[writesonic_idx]['longDescription'] = "Writesonic offers AI-powered writing with GPT-4 support at a fraction of competitors' prices. ChatSonic provides real-time web access for research. Features include bulk content generation, AI image creation, and 80+ templates. Recent updates include new Enterprise plan at ,000/month and evolved pricing model that charges differ based on output quality (Premium/Good/Average/Economy). No longer just a GPT-4 wrapper — now combines multiple LLMs including proprietary marketing-tuned models. In April 2026, Writesonic expanded its Generative Engine Optimization (GEO) Suite with Brand Explorer, GEO: Content Score, AI Shopping Tracker, and Portfolios; enhanced AI Article Writer (6.0/7.0) with improved brand voice consistency and SEO; Chatsonic enhancements with real-time web search, file uploads, and multiple AI models; comprehensive SEO suite; Botsonic no-code AI chatbot builder; automatic image generation; and refined pricing tiers."
    tools[writesonic_idx]['pros'] = [
        "Excellent free tier",
        "30% lifetime recurring affiliate",
        "ChatSonic with web access",
        "Bulk generation",
        "New Enterprise plan at ,000/month",
        "Quality-based pricing model (Premium/Good/Average/Economy)",
        "Proprietary marketing-tuned LLMs",
        "Generative Engine Optimization (GEO) Suite expansion (April 2026)",
        "Brand Explorer for understanding brand presence (April 2026)",
        "GEO: Content Score for optimizing content in AI search results (April 2026)",
        "AI Shopping Tracker for monitoring product visibility in AI-powered shopping recommendations (April 2026)",
        "Portfolios for organizing and showcasing work (April 2026)",
        "AI Article Writer 6.0/7.0 improvements (April 2026)",
        "Chatsonic enhancements (April 2026)",
        "SEO Suite with keyword research, content gap analysis, optimization scoring (April 2026)",
        "Botsonic: No-code AI chatbot builder for websites (April 2026)",
        "Automatic Image Generation (April 2026)",
        "Pricing Tier Updates with clearer distinctions (April 2026)"
    ]

# Update HubSpot
hubspot_idx = find_tool('hubspot')
if hubspot_idx is not None:
    tools[hubspot_idx]['longDescription'] = "HubSpot's free CRM includes contact management, deal tracking, email templates, meeting scheduler, and live chat. Email tracking shows when clients open your messages. The deal pipeline is visual and intuitive. Grows with you — paid tiers add advanced automation and reporting. Recent updates include strong Q4 2025 performance: .13B annual revenue (+19% YoY), 288,706 customers, 2026 guidance of .69-.7B revenue, Meeting Notetaker AI upgraded with \"Smart Deal Progression\" (generates follow-ups from meeting conversations), and new screen capture button in chat widget for support teams. In April 2026, HubSpot announced HubSpot AEO (Answer Engine Optimization), Smart Deal Progression, expanded AI agent capabilities (Prospecting Agent, Customer Agent), upgraded Breeze Assistant, Developer Platform v2026.03, Support Macros, and Customer Success Rooms."
    tools[hubspot_idx]['pros'] = [
        "Free tier is genuinely powerful",
        "Email open tracking",
        "Visual deal pipeline",
        "30% recurring affiliate",
        "Strong Q4 2025: .13B revenue (+19%)",
        "2026 guidance: .69-.7B revenue",
        "Meeting Notetaker AI enhanced with Smart Deal Progression",
        "HubSpot AEO (Answer Engine Optimization) - tracks brand visibility in AI-generated answers (April 2026)",
        "Smart Deal Progression - post-call agent for follow-up communications and CRM updates (April 2026)",
        "Expanded AI Agent Capabilities: Prospecting Agent (enhanced buying signals, buying committee mapping, outreach with Apollo/ZoomInfo) (April 2026)",
        "Expanded AI Agent Capabilities: Customer Agent (24/7 email handling, tone/style configuration, multi-brand support) (April 2026)",
        "Upgraded Breeze Assistant (trained on Loop Marketing data for role-aware guidance) (April 2026)",
        "Developer Platform v2026.03 (date-based versioned APIs, expanded serverless functions, Webhooks Journal API, HubSpot MCP Server) (April 2026)",
        "Support Macros (snippets + multi-step workflow actions) (April 2026)",
        "Customer Success Rooms (shared onboarding spaces) (April 2026)"
    ]

# Update Semrush
semrush_idx = find_tool('semrush')
if semrush_idx is not None:
    tools[semrush_idx]['longDescription'] = "Semrush is the most comprehensive SEO platform available. Keyword research, competitor analysis, backlink auditing, site health checks, position tracking, content optimization — it does everything. Over 10 million marketers use it. Recent updates include major brand transformation repositioning as unified \"intelligence engine\" for AI search era, new visual identity rolling out March 2026, launched \"Spotlight 2026\" AI-focused marketing conference, ChatGPT app integration released, and ongoing pursuit of Adobe acquisition. Q4/FY 2025 financial results also released. In April 2026, Semrush continued advancements of Semrush One (unifying traditional SEO with AI visibility tracking), Enterprise AI Optimization (forecasting features, persona-based prompt generation), Enterprise Site Intelligence (Crawler Profiles for AI Agents and Search Bots), regional expansion (Israel keyword database), brand identity rollout, and Spotlight 2026 conference emphasis."
    tools[semrush_idx]['pros'] = [
        "Most comprehensive SEO tool",
        "$200+ affiliate payout",
        "Excellent competitor analysis",
        "10M+ user community",
        "Major brand transformation to \"intelligence engine\" for AI search era (March 2026)",
        "ChatGPT app integration released",
        "Spotlight 2026 conference launched (AI-focused, October 2026 in London)",
        "Semrush One Advancements: unifying traditional SEO with AI visibility tracking (April 2026)",
        "Enterprise AI Optimization: new forecasting features for traffic/reach/mentions growth, persona-based prompt generation at scale (April 2026)",
        "Enterprise Site Intelligence: Crawler Profiles for AI Agents and Search Bots to analyze website interactions from AI/search engine perspectives (April 2026)",
        "Regional Expansion: Extended keyword database for Israel through premium partner Adactive (April 2026)",
        "Brand Identity Rollout: continued implementation of modernized visual identity and streamlined UI (April 2026)",
        "Spotlight 2026 Conference: ongoing emphasis on strategies for digital brand visibility amidst SEO and AI Search convergence (April 2026)"
    ]

# Update Surfer SEO
surferseo_idx = find_tool('surfer-seo')
if surferseo_idx is not None:
    tools[surferseo_idx]['longDescription'] = "Surfer SEO analyzes the top 10 Google results for your target keyword and provides a content score with specific recommendations: word count, headings, keyword density, images, and more. Integrates with Jasper, Google Docs, and WordPress. Recent updates include Workspaces (prevents brand/domain context overlap), AI Search Guidelines (recommendations for content to rank in AI answers), Gemini integration in AI Tracker for monitoring brand mentions in Google's AI ecosystem, and Mention Gap + Sentiment Analysis (identifies where brands miss from AI answers). Claim: Surfer users grew Google/AI visibility by 423% in 2025. In April 2026, Surfer SEO rolled out Optimizing from AI Tracker, Workspace Permissions, Refreshed Navigation, New Content Editor Wizard, AI Search Guidelines, Looker Studio Integration for AI Visibility, and Gemini in AI Tracker."
    tools[surferseo_idx]['pros'] = [
        "GPS for SEO content",
        "SERP analyzer shows why competitors rank",
        "Jasper integration",
        "Audit tool for existing content",
        "Workspaces feature",
        "AI Search Guidelines",
        "Gemini integration in AI Tracker",
        "Mention Gap + Sentiment Analysis",
        "423% visibility growth claimed for 2025",
        "Optimizing from AI Tracker: one-click transition to Content Editor for underperforming AI-cited pages (April 2026)",
        "Workspace Permissions: scoped access for multiple domains and user access (April 2026)",
        "Refreshed Surfer Navigation: persistent top bar, breadcrumb navigation, brand-focused dashboard (April 2026)",
        "New Content Editor Wizard: AI-powered wizard with full brand/AI/SEO context pre-generation (April 2026)",
        "AI Search Guidelines: real-time suggestions for citation-optimized writing (April 2026)",
        "Looker Studio Integration for AI Visibility: blend AI visibility scores with GA4/G Ads metrics (April 2026)",
        "Gemini in AI Tracker: monitor brand visibility in Google's AI-generated answers (April 2026)"
    ]

# Update Murf AI
murf_idx = find_tool('murf-ai')
if murf_idx is not None:
    tools[murf_idx]['longDescription'] = "Murf generates realistic AI voiceovers for videos, podcasts, and presentations. 120+ voices across accents and styles with 24-month recurring affiliate commissions. Voice cloning creates a consistent brand voice. No microphone or recording equipment needed. Recent updates include Speech Gen 3 Engine for more human-like pauses, tone shifts, and pacing; improved Indian and regional accents across 20+ languages; voice cloning features in beta; enhanced integrations with Canva, Google Slides, PowerPoint, Articulate 360, and various video editors; Agora's integration of Murf AI's text-to-speech technology into Conversational AI Engine; successful Series A funding raising $10 million; Falcon TTS Streaming Model for low-latency voice generation; Voice Changer feature to enhance raw audio quality; and ethical sourcing with models trained on real voice actors who consent and receive royalties. In April 2026, Murf AI introduced Murf Speech Gen 2, Murf Dub, expanded voice library and customization, AI Voice Changer, API updates (Falcon model), AI Dubbing & Translation, enhanced collaboration and integrations, AI Voice Cloning 2.0, and Melody Mode."
    tools[murf_idx]['pros'] = [
        "Voices sound genuinely human",
        "120+ voices and styles",
        "20% recurring affiliate (24 months)",
        "Voice cloning available",
        "Murf Speech Gen 2: most advanced speech model (44.1 kHz, >98.8% word-level accuracy) (April 2026)",
        "Murf Dub (Limited Launch): streamlines multilingual content creation while preserving original intent (April 2026)",
        "Expanded Voice Library and Customization: over 200+ voices in 20+ languages, granular control over pronunciation, emphasis, pauses, pitch, speed, volume (April 2026)",
        "AI Voice Changer: converts recorded voiceovers into professional studio-quality AI voice (April 2026)",
        "API Updates: deprecated `multiNativeLocale` field, added `model` parameter, Falcon streaming model (sub-130ms latency) (April 2026)",
        "AI Dubbing & Translation: automatic video dubbing with voice characteristics retention and lip sync (April 2026)",
        "Enhanced Collaboration and Integrations: team compatibility, integrations with Canva, Google Slides, WordPress, Notion, Webflow, Articulate 360 (April 2026)",
        "AI Voice Cloning 2.0: high-fidelity clones from as little as 10 seconds of reference audio (April 2026)",
        "\"Melody Mode\": experimental feature for AI singing (April 2026)"
    ]

# Write back the updated data
with open('src/data/tools.json', 'w') as f:
    json.dump(tools, f, indent=2)

print("Tools updated successfully.")
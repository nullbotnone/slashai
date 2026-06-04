import json

with open('src/data/tools.json', 'r') as f:
    data = json.load(f)

for tool in data:
    name = tool.get('name')
    if name == 'Jasper AI':
        # Already updated, but we'll ensure
        tool['description'] = 'AI Orchestration Platform for modern marketing teams with brand voice training, SEO integration, and new browser extension - now featuring Jasper Grid for orchestrated workflows.'
        # longDescription already updated via previous script, but we'll keep as is
        # We'll add pros if not already present
        new_pros = [
            "AI Orchestration Platform with dynamic model selection (GPT-5, Claude 3.5 Opus, Gemini Ultra)",
            "Jasper Vision for high-fidelity marketing images and short-form video",
            "Enhanced Brand Voice and governance via Jasper IQ",
            "Expanded API and MCP agent support for marketing stack integration",
            "Cannes Lions 2026 participation for AI agent and brand governance discussions"
        ]
        existing = set(tool['pros'])
        for np in new_pros:
            if np not in existing:
                tool['pros'].append(np)
                
    elif name == 'Writesonic':
        tool['description'] = 'AI Visibility Platform with Generative Engine Optimization (GEO), AI content generation, and Chatsonic AI agent - now featuring multi-model orchestration and brand visibility tracking.'
        tool['longDescription'] = '''Writesonic offers AI-powered writing with GPT-4 support at a fraction of competitors' prices. ChatSonic provides real-time web access for research. Features include bulk content generation, AI image creation, and 80+ templates. Recent updates include new Enterprise plan at $5,000/month and evolved pricing model that charges differ based on output quality (Premium/Good/Average/Economy). No longer just a GPT-4 wrapper — now combines multiple LLMs including proprietary marketing-tuned models. In April 2026, Writesonic expanded its Generative Engine Optimization (GEO) Suite with Brand Explorer, GEO: Content Score, AI Shopping Tracker, and Portfolios; enhanced AI Article Writer (6.0/7.0) with improved brand voice consistency and SEO; Chatsonic enhancements with real-time web search, file uploads, and multiple AI models; comprehensive SEO suite; Botsonic no-code AI chatbot builder; automatic image generation; and refined pricing tiers. In May 2026, Writesonic transformed into an all-in-one platform for Generative Engine Optimization (GEO) with Enhanced Chrome Extension (live fan-out query tracking), AI Search and Ad Tracking (ChatGPT ads tracking), Google Looker Studio Integration (for GEO data), Multi-Model Orchestration (integrating GPT-4o, Claude 3.7 Sonnet, Gemini), Advanced AI Article Writer (versions 6.0/7.0 for long-form content up to 5,000 words), GEO Platform and AI Visibility Suite (monitors brand visibility across 15+ AI platforms), and Chatsonic AI Agent (with switching between models and Brand Voice feature). In June 2026, Writesonic significantly evolved its AI platform by repositioning itself from an "AI writer" to an "AI Visibility Platform." This strategic pivot combines AI content generation, traditional SEO, and a unique feature called Generative Engine Optimization (GEO) within a single dashboard. The platform is designed to help marketing teams, SEO agencies, and e-commerce operations manage their brand's visibility across both conventional search engines and emerging AI search platforms. Key features include AI Visibility Platform (tracking brand appearance in AI search results from platforms like ChatGPT, Gemini, Perplexity, Claude, and Google AI Overviews), AI Content Generation (AI Article Writer 6.0/7.0, ad copy, social posts, emails, landing pages), Chatsonic AI Agent (switching between advanced AI models like GPT-4o, Claude 3.7 Sonnet, Gemini 1.5 Pro, with Brand Voice feature, Flux 1.1 for image generation, and real-time search), SEO AI Agent & Capabilities (keyword research, content optimization, site audits, SERP analysis), Multi-Model Orchestration (integrating multiple leading AI models), and Pricing and Plans (credit-based system with annual billing options for Lite, Standard, Professional, Advanced, and Enterprise tiers).'''
        # Add new pros if not present
        new_pros = [
            "AI Visibility Platform tracking brand presence in AI search results",
            "Generative Engine Optimization (GEO) Suite with Brand Explorer and GEO: Content Score",
            "Chatsonic AI Agent with multi-model switching and Brand Voice feature",
            "Multi-Model Orchestration integrating GPT-4o, Claude 3.7 Sonnet, Gemini",
            "AI Visibility Suite monitoring brand visibility across 15+ AI platforms"
        ]
        existing = set(tool['pros'])
        for np in new_pros:
            if np not in existing:
                tool['pros'].append(np)
                
    elif name == 'HubSpot':
        # HubSpot seems up-to-date, but we can add June updates if any
        # The June updates we saw were about AI enhancements unveiled at Spring 2026 Spotlight event in April, which are already covered.
        # We'll just ensure the description is accurate.
        tool['description'] = 'Free CRM with email tracking, deal pipeline, marketing automation, and enhanced AI meeting notetaker.'
        # No changes needed to longDescription or pros for now.
        
    elif name == 'Semrush':
        tool['description'] = 'All-in-one SEO toolkit undergoing major brand transformation to "intelligence engine" for AI search era.'
        tool['longDescription'] = '''Semrush is the most comprehensive SEO platform available. Keyword research, competitor analysis, backlink auditing, site health checks, position tracking, content optimization — it does everything. Over 10 million marketers use it. Recent updates include major brand transformation repositioning as unified "intelligence engine" for AI search era, new visual identity rolling out March 2026, launched "Spotlight 2026" AI-focused marketing conference, ChatGPT app integration released, and ongoing pursuit of Adobe acquisition. Q4/FY 2025 financial results also released. In April 2026, Semrush continued advancements of Semrush One (unifying traditional SEO with AI visibility tracking), Enterprise AI Optimization (forecasting features, persona-based prompt generation), Enterprise Site Intelligence (Crawler Profiles for AI Agents and Search Bots), regional expansion (Israel keyword database), brand identity rollout, and Spotlight 2026 conference emphasis. In May 2026, Semrush focused on AI search visibility and integration. Updates include partnership with Lovable for search intelligence within building experience, Enterprise AI Optimization with new Reddit and Negative Sentiment Analysis capabilities, YouTube Gap Analyzer in App Center, and Semrush One combining traditional SEO with AI visibility tracking. In June 2026, Semrush highlighted the shift to AI search and introduced tools to help marketers adapt: AI Visibility Toolkit and AI Search Visibility Checker to analyze brand visibility across AI search platforms like ChatGPT, Gemini, and Google's AI Overviews; monitoring metrics such as mentions, citations, and on-SERP presence; content strategy recommendations for creating high-value, extractable content; technical readiness via Site Audit tool; and Prompt Research tool to discover relevant questions people ask AI. Semrush emphasizes that while AI search may reduce clicks to source websites for basic information, it creates new opportunities for brands to be cited and gain visibility, especially for pages that provide specific, authoritative, and comprehensive answers.'''
        # Add new pros if not present
        new_pros = [
            "AI Visibility Toolkit and AI Search Visibility Checker for tracking brand visibility in AI search",
            "Monitoring metrics: mentions, citations, and on-SERP presence in AI search",
            "Content strategy for AI search: creating high-value, extractable content with visuals, videos, examples, and clear structure",
            "Technical readiness via Site Audit tool for AI crawlers",
            "Prompt Research tool to discover relevant questions people ask AI"
        ]
        existing = set(tool['pros'])
        for np in new_pros:
            if np not in existing:
                tool['pros'].append(np)
                
    elif name == 'Surfer SEO':
        # Surfer SEO seems up-to-date with AI Search Guidelines etc.
        # We'll just ensure the description is accurate.
        tool['description'] = 'Content optimization tool with Workspaces, AI Search Guidelines, Gemini integration, Mention Gap + Sentiment Analysis, and Sites feature.'
        # No changes needed.
        
    elif name == 'Murf AI':
        # Murf AI seems up-to-date.
        tool['description'] = 'AI voiceover generator with 120+ realistic voices across 20+ languages.'
        # No changes needed.
        
    # Add other tools if needed

with open('src/data/tools.json', 'w') as f:
    json.dump(data, f, indent=2)
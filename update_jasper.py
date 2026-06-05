import json

with open('src/data/tools.json', 'r') as f:
    data = json.load(f)

for tool in data:
    if tool.get('name') == 'Jasper AI':
        # Update description
        tool['description'] = 'AI Orchestration Platform for modern marketing teams with brand voice training, SEO integration, and new browser extension - now featuring Jasper Grid for orchestrated workflows.'
        # Update longDescription
        tool['longDescription'] = '''Jasper AI is the leading AI writing tool for marketers and content creators. Its Brand Voice feature learns your writing style from samples, ensuring consistent tone across all content. Jasper integrates with Surfer SEO for optimized content, offers 50+ templates, and includes a Chrome extension that works in Gmail, Google Docs, LinkedIn, and WordPress. Recent updates include 25M Series A funding (valuing company at .5B), new browser extension, and the "State of AI in Marketing 2026" report showing 91% of marketing teams now use AI (up from 63% last year). Latest product updates include Jasper Grid orchestration layer, Content Engineering Certification, Company Knowledge Hub, enhanced control features, Marketing AI Agents, advanced model options in Studio, and Studio Agent Sharing for standardized content generation. In April 2026, Jasper introduced Advanced Brand Memory and Alignment, Enhanced SEO Optimization with Optimization Agent, Autonomous AI Agents and Workflows (including Product Update Email AI Agent), Content Automation Platform, Upgraded Image Generation with Nano Banana, Enhanced Prompt Skill, Improved Integrations and Knowledge Layer, and continued focus on Enterprise Marketing. In May 2026, Jasper evolved into an "AI Agent Workspace for Modern Marketing Teams" with over 100 specialized AI agents, Content Pipelines for repeatable workflows, enhanced Brand Voice & Jasper IQ for brand governance, Jasper Chat + Canvas for collaboration and visual workspace, Jasper Art & Multimodal capabilities for image and visual generation, and AI Visibility Workflows in Grid for AI-native discovery and citation. Additional May 2026 updates include editor enhancements with improved speed and real-time Brand Voice application, an AI model upgrade for better long-form document context handling, expanded AI image suite capabilities, and improved integrations with Google Docs (two-way export) and HubSpot (direct blog post scheduling). In June 2026, Jasper AI solidified its position as an AI Orchestration Platform for enterprise marketing teams, featuring an orchestration layer (Jasper Grid) that dynamically selects from foundational models like GPT-5, Claude 3.5 Opus, and Google Gemini Ultra. The platform now includes Jasper Vision for generating high-fidelity marketing images and short-form video from text briefs, enhanced Brand Voice and governance through Jasper IQ, and expanded API and MCP agent support for embedding Jasper into existing marketing stacks. Jasper is also participating in Cannes Lions 2026 (June 22-26) to discuss the future of AI agents and brand governance.'''
        # Update pros: we can add June-specific pros, but let's keep the existing pros and add new ones.
        # We'll add new pros at the end of the list.
        new_pros = [
            "AI Orchestration Platform with dynamic model selection (GPT-5, Claude 3.5 Opus, Gemini Ultra)",
            "Jasper Vision for high-fidelity marketing images and short-form video",
            "Enhanced Brand Voice and governance via Jasper IQ",
            "Expanded API and MCP agent support for marketing stack integration",
            "Cannes Lions 2026 participation for AI agent and brand governance discussions"
        ]
        # Avoid duplicates: we'll check if any of these are already in pros (by checking substrings)
        # For simplicity, we'll just extend the list; duplicates are okay but we'll avoid exact duplicates.
        existing = set(tool['pros'])
        for np in new_pros:
            if np not in existing:
                tool['pros'].append(np)
        break

with open('src/data/tools.json', 'w') as f:
    json.dump(data, f, indent=2)
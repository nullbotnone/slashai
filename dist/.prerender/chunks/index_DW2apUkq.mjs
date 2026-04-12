import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { a as renderTemplate, d as defineScriptVars, r as renderComponent, m as maybeRenderHead, b as addAttribute } from './prerender_DGualgz_.mjs';
import { $ as $$BaseLayout } from './BaseLayout_rjQaa7Nu.mjs';
import { t as toolsData } from './tools_BGqMe1Zc.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(raw || cooked.slice()) }));
var _a;
const $$Index = createComponent(($$result, $$props, $$slots) => {
  const roleCategories = {
    writer: { categories: ["Writing", "Assistant", "Research"], label: "Writer / Content Creator" },
    designer: { categories: ["Design", "Video", "Assistant"], label: "Designer / Creative" },
    developer: { categories: ["Coding", "Developer", "Assistant", "Automation"], label: "Developer / Engineer" },
    marketer: { categories: ["Writing", "SEO", "Video", "AI Agents", "Assistant"], label: "Marketer / Growth" },
    consultant: { categories: ["Productivity", "AI Agents", "Assistant", "Research", "Automation"], label: "Consultant / Advisor" },
    creator: { categories: ["Video", "Audio", "Writing", "Design", "Assistant"], label: "Content Creator / Influencer" },
    freelancer: { categories: ["Productivity", "Assistant", "Writing", "Automation", "AI Agents"], label: "Freelancer (General)" },
    ecommerce: { categories: ["Writing", "Video", "Design", "SEO", "AI Agents", "Finance"], label: "E-commerce / Online Business" }
  };
  const budgets = [
    { id: "free", label: "Free only", max: 0 },
    { id: "budget", label: "Under $25/mo", max: 25 },
    { id: "mid", label: "Under $50/mo", max: 50 },
    { id: "pro", label: "Under $100/mo", max: 100 },
    { id: "unlimited", label: "No limit", max: Infinity }
  ];
  const toolsJson = JSON.stringify(toolsData);
  const rolesJson = JSON.stringify(roleCategories);
  const budgetsJson = JSON.stringify(budgets);
  return renderTemplate(_a || (_a = __template(["", "  <script>(function(){", `
  const allTools = JSON.parse(toolsJson);
  const roles = JSON.parse(rolesJson);
  const budgets = JSON.parse(budgetsJson);

  let selectedRole = null;
  let selectedBudget = null;

  document.querySelectorAll('.role-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedRole = btn.dataset.role;
      document.getElementById('step-2').classList.remove('hidden');
      document.getElementById('step-2').scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  });

  document.querySelectorAll('.budget-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.budget-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedBudget = budgets.find(b => b.id === btn.dataset.budget);
      generateStack();
    });
  });

  document.getElementById('restart-btn').addEventListener('click', () => {
    selectedRole = null;
    selectedBudget = null;
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    document.querySelectorAll('.budget-btn').forEach(b => b.classList.remove('selected'));
    document.getElementById('step-2').classList.add('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('step-1').scrollIntoView({ behavior: 'smooth' });
  });

  function parsePrice(tool) {
    if (tool.pricing === 'Free') return 0;
    const match = tool.price?.match(/\\$(\\d+(?:\\.\\d+)?)/);
    return match ? parseFloat(match[1]) : 0;
  }

  function getWhyText(tool, role) {
    const reasons = {
      writer: { 'Writing': 'Essential for your writing workflow', 'Assistant': 'Your AI research and brainstorming partner', 'Research': 'Deep research support for in-depth content' },
      designer: { 'Design': 'Core design tool — create faster', 'Video': 'Video content for your creative portfolio', 'Assistant': 'AI brainstorming and copy support' },
      developer: { 'Coding': 'Code faster with AI pair programming', 'Developer': 'Development workflow automation', 'Assistant': 'Technical documentation and research', 'Automation': 'Automate repetitive dev tasks' },
      marketer: { 'Writing': 'Content marketing at scale', 'SEO': 'Dominate search rankings', 'Video': 'Video marketing content', 'AI Agents': 'Automated lead gen and outreach', 'Assistant': 'Campaign strategy and copywriting' },
      consultant: { 'Productivity': 'Manage client work efficiently', 'AI Agents': 'Automate client communication', 'Assistant': 'Analysis and report writing', 'Research': 'Deep research for client deliverables', 'Automation': 'Streamline your workflows' },
      creator: { 'Video': 'Video creation and editing', 'Audio': 'Podcast and audio production', 'Writing': 'Script and caption writing', 'Design': 'Thumbnails and visual content', 'Assistant': 'Content ideation and planning' },
      freelancer: { 'Productivity': 'Stay organized across clients', 'Assistant': 'All-purpose AI helper', 'Writing': 'Proposals, emails, deliverables', 'Automation': 'Automate admin busywork', 'AI Agents': 'Virtual assistant that works 24/7' },
      ecommerce: { 'Writing': 'Product descriptions and emails', 'Video': 'Product videos and ads', 'Design': 'Product images and branding', 'SEO': 'Get found in search', 'AI Agents': 'Automate customer support', 'Finance': 'Track your business finances' },
    };
    return reasons[role]?.[tool.category] || 'Useful ' + tool.category.toLowerCase() + ' tool';
  }

  function generateStack() {
    const roleData = roles[selectedRole];
    const maxBudget = selectedBudget.max;

    let candidates = allTools.filter(t => roleData.categories.includes(t.category));
    candidates.sort((a, b) => {
      if (a.pricing === 'Free' && b.pricing !== 'Free') return -1;
      if (b.pricing === 'Free' && a.pricing !== 'Free') return 1;
      return parsePrice(a) - parsePrice(b);
    });

    const stack = [];
    const usedCategories = new Set();
    let totalCost = 0;

    for (const cat of roleData.categories) {
      if (usedCategories.has(cat)) continue;
      const tool = candidates.find(t => {
        if (t.category !== cat) return false;
        if (usedCategories.has(t.name)) return false;
        return (totalCost + parsePrice(t)) <= maxBudget;
      });
      if (tool) {
        stack.push({ ...tool, why: getWhyText(tool, selectedRole), monthlyCost: parsePrice(tool) });
        usedCategories.add(cat);
        usedCategories.add(tool.name);
        totalCost += parsePrice(tool);
      }
      if (stack.length >= 6) break;
    }

    const resultsEl = document.getElementById('results');
    const gridEl = document.getElementById('stack-grid');
    const totalEl = document.getElementById('stack-total');
    const metaEl = document.getElementById('results-meta');
    const emptyEl = document.getElementById('stack-empty');

    resultsEl.classList.remove('hidden');
    metaEl.innerHTML = '<strong>' + roleData.label + '</strong> · Budget: <strong>' + selectedBudget.label + '</strong> · ' + stack.length + ' tools recommended';

    if (stack.length === 0) {
      gridEl.innerHTML = '';
      totalEl.innerHTML = '';
      emptyEl.classList.remove('hidden');
      resultsEl.scrollIntoView({ behavior: 'smooth' });
      return;
    }

    emptyEl.classList.add('hidden');

    // Render cards using exact site-wide markup
    gridEl.innerHTML = stack.map(function(tool, i) {
      return '<a href="/tools/' + tool.slug + '/" class="card" style="text-decoration: none; color: inherit;">' +
        '<h3>' + tool.name + '</h3>' +
        '<p>' + tool.description + '</p>' +
        '<span class="tag">' + tool.category + '</span>' +
        '<span class="tag">' + (tool.monthlyCost === 0 ? 'Free' : '$' + tool.monthlyCost + '/mo') + '</span>' +
        '<span class="tag">' + tool.why + '</span>' +
      '</a>';
    }).join('');

    // Fade in cards one by one
    var cards = gridEl.querySelectorAll('.card');
    cards.forEach(function(card, i) {
      setTimeout(function() {
        card.classList.add('fade-in');
      }, i * 60);
    });

    totalEl.innerHTML = '<strong>' + (totalCost === 0 ? 'Free' : '$' + totalCost + '/mo') + '</strong>' +
      '<p>Total estimated monthly cost for your ' + roleData.label.toLowerCase() + ' AI stack</p>';

    resultsEl.scrollIntoView({ behavior: 'smooth' });
  }
})();<\/script>`], ["", "  <script>(function(){", `
  const allTools = JSON.parse(toolsJson);
  const roles = JSON.parse(rolesJson);
  const budgets = JSON.parse(budgetsJson);

  let selectedRole = null;
  let selectedBudget = null;

  document.querySelectorAll('.role-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedRole = btn.dataset.role;
      document.getElementById('step-2').classList.remove('hidden');
      document.getElementById('step-2').scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  });

  document.querySelectorAll('.budget-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.budget-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedBudget = budgets.find(b => b.id === btn.dataset.budget);
      generateStack();
    });
  });

  document.getElementById('restart-btn').addEventListener('click', () => {
    selectedRole = null;
    selectedBudget = null;
    document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('selected'));
    document.querySelectorAll('.budget-btn').forEach(b => b.classList.remove('selected'));
    document.getElementById('step-2').classList.add('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('step-1').scrollIntoView({ behavior: 'smooth' });
  });

  function parsePrice(tool) {
    if (tool.pricing === 'Free') return 0;
    const match = tool.price?.match(/\\\\$(\\\\d+(?:\\\\.\\\\d+)?)/);
    return match ? parseFloat(match[1]) : 0;
  }

  function getWhyText(tool, role) {
    const reasons = {
      writer: { 'Writing': 'Essential for your writing workflow', 'Assistant': 'Your AI research and brainstorming partner', 'Research': 'Deep research support for in-depth content' },
      designer: { 'Design': 'Core design tool — create faster', 'Video': 'Video content for your creative portfolio', 'Assistant': 'AI brainstorming and copy support' },
      developer: { 'Coding': 'Code faster with AI pair programming', 'Developer': 'Development workflow automation', 'Assistant': 'Technical documentation and research', 'Automation': 'Automate repetitive dev tasks' },
      marketer: { 'Writing': 'Content marketing at scale', 'SEO': 'Dominate search rankings', 'Video': 'Video marketing content', 'AI Agents': 'Automated lead gen and outreach', 'Assistant': 'Campaign strategy and copywriting' },
      consultant: { 'Productivity': 'Manage client work efficiently', 'AI Agents': 'Automate client communication', 'Assistant': 'Analysis and report writing', 'Research': 'Deep research for client deliverables', 'Automation': 'Streamline your workflows' },
      creator: { 'Video': 'Video creation and editing', 'Audio': 'Podcast and audio production', 'Writing': 'Script and caption writing', 'Design': 'Thumbnails and visual content', 'Assistant': 'Content ideation and planning' },
      freelancer: { 'Productivity': 'Stay organized across clients', 'Assistant': 'All-purpose AI helper', 'Writing': 'Proposals, emails, deliverables', 'Automation': 'Automate admin busywork', 'AI Agents': 'Virtual assistant that works 24/7' },
      ecommerce: { 'Writing': 'Product descriptions and emails', 'Video': 'Product videos and ads', 'Design': 'Product images and branding', 'SEO': 'Get found in search', 'AI Agents': 'Automate customer support', 'Finance': 'Track your business finances' },
    };
    return reasons[role]?.[tool.category] || 'Useful ' + tool.category.toLowerCase() + ' tool';
  }

  function generateStack() {
    const roleData = roles[selectedRole];
    const maxBudget = selectedBudget.max;

    let candidates = allTools.filter(t => roleData.categories.includes(t.category));
    candidates.sort((a, b) => {
      if (a.pricing === 'Free' && b.pricing !== 'Free') return -1;
      if (b.pricing === 'Free' && a.pricing !== 'Free') return 1;
      return parsePrice(a) - parsePrice(b);
    });

    const stack = [];
    const usedCategories = new Set();
    let totalCost = 0;

    for (const cat of roleData.categories) {
      if (usedCategories.has(cat)) continue;
      const tool = candidates.find(t => {
        if (t.category !== cat) return false;
        if (usedCategories.has(t.name)) return false;
        return (totalCost + parsePrice(t)) <= maxBudget;
      });
      if (tool) {
        stack.push({ ...tool, why: getWhyText(tool, selectedRole), monthlyCost: parsePrice(tool) });
        usedCategories.add(cat);
        usedCategories.add(tool.name);
        totalCost += parsePrice(tool);
      }
      if (stack.length >= 6) break;
    }

    const resultsEl = document.getElementById('results');
    const gridEl = document.getElementById('stack-grid');
    const totalEl = document.getElementById('stack-total');
    const metaEl = document.getElementById('results-meta');
    const emptyEl = document.getElementById('stack-empty');

    resultsEl.classList.remove('hidden');
    metaEl.innerHTML = '<strong>' + roleData.label + '</strong> · Budget: <strong>' + selectedBudget.label + '</strong> · ' + stack.length + ' tools recommended';

    if (stack.length === 0) {
      gridEl.innerHTML = '';
      totalEl.innerHTML = '';
      emptyEl.classList.remove('hidden');
      resultsEl.scrollIntoView({ behavior: 'smooth' });
      return;
    }

    emptyEl.classList.add('hidden');

    // Render cards using exact site-wide markup
    gridEl.innerHTML = stack.map(function(tool, i) {
      return '<a href="/tools/' + tool.slug + '/" class="card" style="text-decoration: none; color: inherit;">' +
        '<h3>' + tool.name + '</h3>' +
        '<p>' + tool.description + '</p>' +
        '<span class="tag">' + tool.category + '</span>' +
        '<span class="tag">' + (tool.monthlyCost === 0 ? 'Free' : '$' + tool.monthlyCost + '/mo') + '</span>' +
        '<span class="tag">' + tool.why + '</span>' +
      '</a>';
    }).join('');

    // Fade in cards one by one
    var cards = gridEl.querySelectorAll('.card');
    cards.forEach(function(card, i) {
      setTimeout(function() {
        card.classList.add('fade-in');
      }, i * 60);
    });

    totalEl.innerHTML = '<strong>' + (totalCost === 0 ? 'Free' : '$' + totalCost + '/mo') + '</strong>' +
      '<p>Total estimated monthly cost for your ' + roleData.label.toLowerCase() + ' AI stack</p>';

    resultsEl.scrollIntoView({ behavior: 'smooth' });
  }
})();<\/script>`])), renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Build Your AI Stack", "description": "Pick your role and budget — get a personalized AI tool stack curated for solopreneurs and freelancers.", "data-astro-cid-ea77u57b": true }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<section class="hero" data-astro-cid-ea77u57b> <div class="container" data-astro-cid-ea77u57b> <h1 data-astro-cid-ea77u57b>Build Your <span class="gradient-text" data-astro-cid-ea77u57b>AI Stack</span></h1> <p data-astro-cid-ea77u57b>Pick your role and budget. Get a personalized AI toolkit in seconds.</p> </div> </section> <section class="section-glow" data-astro-cid-ea77u57b> <div class="container" data-astro-cid-ea77u57b> <!-- Step 1: Role --> <div class="builder-step" id="step-1" data-astro-cid-ea77u57b> <div class="step-number" data-astro-cid-ea77u57b>1</div> <h2 data-astro-cid-ea77u57b>What do you do?</h2> <div class="role-grid" data-astro-cid-ea77u57b> ${Object.entries(roleCategories).map(([id, role]) => renderTemplate`<button class="role-btn"${addAttribute(id, "data-role")} data-astro-cid-ea77u57b> <span class="role-icon" data-astro-cid-ea77u57b> ${id === "writer" ? "✍️" : id === "designer" ? "🎨" : id === "developer" ? "💻" : id === "marketer" ? "📣" : id === "consultant" ? "💼" : id === "creator" ? "🎬" : id === "freelancer" ? "⚡" : "🛒"} </span> <span class="role-label" data-astro-cid-ea77u57b>${role.label}</span> </button>`)} </div> </div> <!-- Step 2: Budget --> <div class="builder-step hidden" id="step-2" data-astro-cid-ea77u57b> <div class="step-number" data-astro-cid-ea77u57b>2</div> <h2 data-astro-cid-ea77u57b>Monthly AI budget?</h2> <div class="budget-grid" data-astro-cid-ea77u57b> ${budgets.map((b) => renderTemplate`<button class="budget-btn"${addAttribute(b.id, "data-budget")}${addAttribute(b.max, "data-max")} data-astro-cid-ea77u57b> ${b.label} </button>`)} </div> </div> <!-- Results --> <div class="builder-results hidden" id="results" data-astro-cid-ea77u57b> <div class="results-header" data-astro-cid-ea77u57b> <h2 data-astro-cid-ea77u57b>Your <span class="gradient-text" data-astro-cid-ea77u57b>Recommended Stack</span></h2> <button class="restart-btn" id="restart-btn" data-astro-cid-ea77u57b>↻ Start over</button> </div> <div class="results-meta" id="results-meta" data-astro-cid-ea77u57b></div> <div class="card-grid" id="stack-grid" data-astro-cid-ea77u57b></div> <div class="stack-total" id="stack-total" data-astro-cid-ea77u57b></div> <div class="stack-empty hidden" id="stack-empty" data-astro-cid-ea77u57b> <p data-astro-cid-ea77u57b>No tools found for this combination. Try increasing your budget or choosing a different role.</p> </div> </div> </div> </section> ` }), defineScriptVars({ toolsJson, rolesJson, budgetsJson }));
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/build-your-stack/index.astro", void 0);

const $$file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/build-your-stack/index.astro";
const $$url = "/build-your-stack";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };

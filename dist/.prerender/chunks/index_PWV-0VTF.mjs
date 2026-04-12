import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { c as createRenderInstruction, r as renderComponent, a as renderTemplate, u as unescapeHTML, m as maybeRenderHead } from './prerender_DGualgz_.mjs';
import { $ as $$BaseLayout } from './BaseLayout_rjQaa7Nu.mjs';
import { t as toolsData } from './tools_BGqMe1Zc.mjs';

async function renderScript(result, id) {
  const inlined = result.inlinedScripts.get(id);
  let content = "";
  if (inlined != null) {
    if (inlined) {
      content = `<script type="module">${inlined}</script>`;
    }
  } else {
    const resolved = await result.resolve(id);
    content = `<script type="module" src="${result.userAssetsBase ? (result.base === "/" ? "" : result.base) + result.userAssetsBase : ""}${resolved}"></script>`;
  }
  return createRenderInstruction({ type: "script", id, content });
}

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$Index = createComponent(($$result, $$props, $$slots) => {
  const toolsJson = JSON.stringify(toolsData);
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Compare AI Tools", "description": "Pick two AI tools and see how they stack up." }, { "default": ($$result2) => renderTemplate(_a || (_a = __template([" ", '<section class="hero"> <div class="container"> <h1>Compare <span class="gradient-text">AI Tools</span></h1> <p>Pick two tools. See everything side by side.</p> </div> </section> <section class="section-glow"> <div class="container"> <div id="picker"> <input type="text" id="filter" placeholder="Search tools..." class="search-bar" autocomplete="off"> <div class="tool-scroll"> <div class="tool-list" id="tool-list"></div> </div> <div class="picker-action hidden" id="picker-action"> <button class="go-btn" id="go-btn">Compare →</button> </div> </div> <div class="results hidden" id="results"> <div class="results-top"> <button class="back-btn" id="back-btn">← Pick different tools</button> </div> <div class="card-grid" id="result-cards"></div> <div class="detail-wrap"> <table class="detail-table" id="detail-table"></table> </div> </div> </div> </section> <script id="tools-data" type="application/json">', "<\/script> ", " "])), maybeRenderHead(), unescapeHTML(toolsJson), renderScript($$result2, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/compare/index.astro?astro&type=script&index=0&lang.ts")) })}`;
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/compare/index.astro", void 0);

const $$file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/compare/index.astro";
const $$url = "/compare";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };

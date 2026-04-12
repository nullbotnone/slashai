import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate, m as maybeRenderHead } from './prerender_DGualgz_.mjs';
import { $ as $$BaseLayout } from './BaseLayout_rjQaa7Nu.mjs';

const $$PrivacyPolicy = createComponent(($$result, $$props, $$slots) => {
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Privacy Policy" }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<section class="hero"> <div class="container"> <h1>Privacy <span class="gradient-text">Policy</span></h1> <p>What we collect, why, and how we protect your data.</p> </div> </section> <section class="section-glow"> <div class="article-content"> <p><em>Last updated: March 2026</em></p> <h2>Information We Collect</h2> <p><strong>Analytics:</strong> We use Google Analytics to understand how visitors use our site. This includes anonymized data like pages visited, time on site, and browser type. We do not collect personally identifiable information through analytics.</p> <p><strong>Email:</strong> If you subscribe to our newsletter, we collect your email address. We use this only for sending our newsletter and never share it with third parties.</p> <p><strong>Contact Forms:</strong> If you contact us, we collect the information you provide (name, email, message) solely to respond to your inquiry.</p> <h2>Cookies</h2> <p>SlashAI uses cookies for:</p> <ul> <li>Google Analytics (site usage statistics)</li> <li>Essential site functionality</li> </ul> <p>You can disable cookies in your browser settings.</p> <h2>Affiliate Tracking</h2> <p>Some outbound links contain affiliate tracking codes. When you click these links, the third-party site may use cookies to track that you came from SlashAI. This is how affiliate commissions are attributed. We do not control third-party privacy practices.</p> <h2>Data Sharing</h2> <p>We do not sell, trade, or share your personal information with third parties except:</p> <ul> <li>Service providers (e.g., email newsletter platform, analytics)</li> <li>When required by law</li> </ul> <h2>Your Rights</h2> <p>You can:</p> <ul> <li>Unsubscribe from our newsletter at any time</li> <li>Request deletion of your data by emailing us</li> <li>Opt out of analytics using browser extensions</li> </ul> <h2>Contact</h2> <p>Questions about this policy? Email <a href="mailto:hello@slashai.app">hello@slashai.app</a>.</p> </div> </section> ` })}`;
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/privacy-policy.astro", void 0);

const $$file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/privacy-policy.astro";
const $$url = "/privacy-policy";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$PrivacyPolicy,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };

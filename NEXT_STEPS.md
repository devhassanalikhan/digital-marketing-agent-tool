# Next Steps

Roadmap for turning this from a working-but-simulated framework into a real
autonomous marketing tool. Ordered high to low priority based on what's
already agreed: free APIs first, lead capture and analytics before social,
SEMrush/X deprioritized.

## Status as of last session

- Repo is on a clean baseline: 30/30 tests passing (28 unittest + 2 pytest).
- Real, working: Knowledge Graph, Git integration (single + multi-repo),
  Background Execution framework, Operator dashboard/API, credential storage
  (AuthManager), MCP stub mounting/resolver.
- Real but not yet connected to live data: Google Analytics 4 connector
  (code is correct now that `google-auth`/`google-analytics-data` are
  installed; still needs real credentials configured).
- Simulated/fabricated (do not trust output yet): SEO Agent, Content Agent's
  performance metrics, Affiliate Agent's revenue/conversion numbers,
  Competitive Intelligence module, Revenue Optimization RL engine,
  AnalyticsEngine's `_simulate_metrics_for_source`.
- Not implemented at all: Advertising Agent, Email Agent, Social Media Agent
  (capability cards only, zero code). Lead capture (no code exists).

---

## Priority 1 — Real data foundations

1. **Wire up GA4 for real traffic/reach data**
   - Create a GCP service account, enable the Analytics Data API, grant it
     Viewer access on the GA4 property.
   - Fill in `config/google_analytics.json` with `property_id` and
     `credentials_file`.
   - Verify: call `GoogleAnalyticsConnector.get_website_traffic()` and check
     the response isn't falling back to `mock_*` values.

2. **Build lead capture (HubSpot)**
   - Create a HubSpot free-tier private app, get an access token.
   - Add a `POST /api/leads` route (e.g. in `frontend/operator_server.py`).
   - On receipt: write the lead into the Knowledge Graph, then forward it
     to HubSpot via `hubspot-api-client` (already a dependency, currently
     unused anywhere in the code).
   - Point your actual site's contact form at this endpoint once it's live.

3. **Fix the `MarketingOrchestrator` config bug**
   - `main.py` passes a config *dict* to `MarketingOrchestrator`, but it
     expects a *file path* and fails silently (falls back to defaults).
     Low blast radius today, but worth fixing before building more on top
     of the orchestrator.

---

## Priority 2 — Make SEO and content real

4. **Build a Google Search Console connector**
   - Mirror `google_analytics_connector.py`'s structure: service account
     auth, `scopes=['https://www.googleapis.com/auth/webmasters.readonly']`.
   - Add the service account as a Restricted user on the GSC property.

5. **Rewire `SEOAgent` off simulated data**
   - Replace every `_simulate_*` method in
     `core/agents/seo_agent/seo_agent.py` with calls to the new GSC
     connector (and GA4 where relevant).
   - Only trust `analyze_keywords()` / `track_rankings()` output after this.

6. **Decide the website publishing path**
   - Confirm how the target site is actually hosted/deployed.
   - If git-deployed: `core/git/` (including the new `MultiRepoGitManager`)
     works today — add the site to `core/git/git_config.json`.
   - If CMS/website-builder: build a new publisher adapter calling that
     platform's REST API, following the shape of `WebsiteUpdater`.

7. **Replace `AnalyticsEngine`'s simulated content performance**
   - `get_content_performance()` currently returns hardcoded fake data —
     swap for real data from the GA4 connector once available.

---

## Priority 3 — Sales/revenue signal

8. **Add a real payment/order webhook** (Stripe, Shopify, or whatever
   processor is in use) so the Revenue Optimization RL engine trains on
   real reward signals instead of simulated ones.
9. **Rewire `revenue_optimization/` off simulated state** once real revenue
   data is flowing — otherwise the "optimizer" is optimizing against
   fiction.

---

## Priority 4 — Social media (build from scratch)

10. **LinkedIn first** (you already have a real company Page there, and
    it's free): request Marketing Developer Platform access early — it's
    the slowest approval in the stack (days to weeks) — then implement a
    real `social_media_agent.py` with `publish_post()` and
    `get_engagement_metrics()`.
11. **Meta (Facebook + Instagram) second**: self-serve via Graph API
    Explorer, no long approval wait for posting to your own Page.
12. Do **not** build X/Twitter support under the current API pricing (no
    viable free tier as of Feb 2026) unless a specific business reason
    justifies the cost.

---

## Priority 5 — Deferred / low priority

13. **SEMrush integration** — expensive ($549/mo minimum plus metered
    units), mainly adds competitor visibility on top of what GSC already
    covers for your own site. Revisit only if competitive intelligence
    becomes a real business need.
14. **Google Ads API / Advertising Agent** — build once there's an actual
    ad budget to manage; developer token review can take 1-2 weeks, so
    apply for it ahead of when you'll need it.
15. **Email Agent (Mailchimp)** — free tier is ready to use whenever email
    marketing becomes a priority; no code exists yet.
16. **Competitive Intelligence module** — entire pipeline
    (`core/competitive_intelligence/`) is simulated data dressed as
    analysis; rebuild only if/when it's actually needed, using GSC +
    SEMrush (if adopted) as real data sources.

---

## Ongoing / housekeeping

- Keep `requirements.txt` honest — verify new dependencies are real PyPI
  packages and actually imported before adding them (this bit us twice:
  `pytorch` and `twitter-api-v2` were never valid package names).
- Run `python -m unittest discover tests` and
  `python -m pytest tests/test_integration_mcp.py` after any change to
  confirm the 30/30 baseline still holds.
- When adding a new MCP integration, prefer wiring it directly into the
  relevant agent (like the GA4 connector) over relying on the MCP stub
  layer unless multi-agent/A2A invocation is actually needed.

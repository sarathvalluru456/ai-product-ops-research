import json
from pathlib import Path
from collections import Counter
from html import escape


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

RESEARCH_FILE = DATA_DIR / "research_clean.json"
ANALYSIS_FILE = DATA_DIR / "analysis.json"
OUTPUT_FILE = BASE_DIR / "case_study.html"


GITHUB_URL = "https://github.com/sarathvalluru456/ai-product-ops-research"
LIVE_URL = "https://ai-product-ops-research-5zjv-three.vercel.app/"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_text(value):
    if value is None:
        return ""

    if isinstance(value, list):
        return ", ".join(str(x) for x in value)

    if isinstance(value, dict):
        return ", ".join(f"{k}: {v}" for k, v in value.items())

    return escape(str(value))


def main():

    research = load_json(RESEARCH_FILE)
    analysis = load_json(ANALYSIS_FILE)

    total = len(research)

    # ---------------------------------------------------------
    # HIGH-LEVEL ANALYSIS
    # ---------------------------------------------------------

    agent_ready = analysis.get("agent_ready", {})
    mcp = analysis.get("mcp_available", {})
    breadth = analysis.get("api_breadth", {})
    access = analysis.get("self_serve_status", {})
    confidence = analysis.get("confidence", {})
    categories = analysis.get("categories", {})

    ready = agent_ready.get("yes", 0)
    setup = agent_ready.get("yes_with_setup", 0)
    unclear = agent_ready.get("unclear", 0)
    not_ready = agent_ready.get("no", 0)

    mcp_yes = mcp.get("yes", 0)
    mcp_unclear = mcp.get("unclear", 0)
    mcp_no = mcp.get("no", 0)

    broad = breadth.get("broad", 0)

    self_serve = access.get("self_serve", 0)
    paid = access.get("paid_required", 0)
    sales = access.get("contact_sales", 0)
    unknown_access = access.get("unknown", 0)

    high_conf = confidence.get("high", 0)
    medium_conf = confidence.get("medium", 0)
    low_conf = confidence.get("low", 0)

    # ---------------------------------------------------------
    # NORMALIZE OAUTH FAMILY
    # ---------------------------------------------------------

    oauth_apps = 0

    for item in research:

        auth = item.get("auth_methods", [])

        if isinstance(auth, str):
            auth = [auth]

        auth_text = " ".join(
            str(x).lower()
            for x in auth
        )

        if "oauth" in auth_text:
            oauth_apps += 1

    # ---------------------------------------------------------
    # BUILD 100-APP TABLE
    # ---------------------------------------------------------

    rows = []

    for item in research:

        auth = item.get("auth_methods", [])
        api = item.get("api_type", [])

        auth_text = safe_text(auth)
        api_text = safe_text(api)

        rows.append(
            f"""
            <tr>
                <td>{safe_text(item.get("app_id", ""))}</td>

                <td>
                    <strong>{safe_text(item.get("app_name", ""))}</strong>
                </td>

                <td>{safe_text(item.get("category", ""))}</td>

                <td>{auth_text}</td>

                <td>
                    <span class="status">
                        {safe_text(item.get("self_serve_status", "unknown"))}
                    </span>
                </td>

                <td>{api_text}</td>

                <td>{safe_text(item.get("api_breadth", "unknown"))}</td>

                <td>{safe_text(item.get("mcp_available", "unknown"))}</td>

                <td>
                    <strong>
                        {safe_text(item.get("agent_ready", "unknown"))}
                    </strong>
                </td>

                <td>{safe_text(item.get("confidence", "unknown"))}</td>
            </tr>
            """
        )

    table_html = "\n".join(rows)

    # ---------------------------------------------------------
    # CATEGORY BARS
    # ---------------------------------------------------------

    category_html = ""

    for name, count in sorted(
        categories.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        percentage = min(count * 10, 100)

        category_html += f"""
        <div class="bar-row">

            <div class="bar-label">
                {safe_text(name)}
            </div>

            <div class="bar-track">

                <div
                    class="bar-fill"
                    style="width:{percentage}%"
                ></div>

            </div>

            <div class="bar-number">
                {count}
            </div>

        </div>
        """

    # ---------------------------------------------------------
    # HTML
    # ---------------------------------------------------------

    html = f"""<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
AI Product Ops Research — 100 App Agent Readiness Study
</title>

<style>

* {{
    box-sizing: border-box;
}}

html {{
    scroll-behavior: smooth;
}}

body {{

    margin: 0;

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;

    background: #f6f7fb;

    color: #172033;

    line-height: 1.55;
}}

a {{
    color: #315efb;
    text-decoration: none;
    font-weight: 700;
}}

a:hover {{
    text-decoration: underline;
}}

.container {{

    width: min(1400px, 94%);

    margin: auto;
}}

.hero {{

    background:
        radial-gradient(
            circle at top right,
            #315efb55,
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #111827,
            #253b67
        );

    color: white;

    padding: 75px 0;
}}

.hero h1 {{

    font-size: 48px;

    line-height: 1.08;

    margin:
        0 0 20px;

    max-width: 950px;
}}

.hero p {{

    max-width: 900px;

    font-size: 19px;

    color: #dbe4f5;

    margin:
        10px 0;
}}

.badge {{

    display: inline-block;

    background: #ffffff18;

    border:
        1px solid
        #ffffff35;

    padding:
        7px 14px;

    border-radius: 20px;

    margin-bottom: 20px;

    font-size: 13px;

    font-weight: 700;
}}

.hero-actions {{

    display: flex;

    gap: 12px;

    flex-wrap: wrap;

    margin-top: 28px;
}}

.hero-button {{

    display: inline-block;

    padding:
        11px 17px;

    border-radius: 9px;

    background: white;

    color: #172033;

    font-weight: 800;

    text-decoration: none;
}}

.hero-button.secondary {{

    background: #ffffff12;

    color: white;

    border:
        1px solid
        #ffffff40;
}}

section {{

    padding:
        52px 0;
}}

h2 {{

    font-size: 30px;

    line-height: 1.2;

    margin:
        0 0 12px;
}}

h3 {{

    margin-top: 0;
}}

.subtitle {{

    color: #657084;

    max-width: 900px;

    margin-bottom: 24px;
}}

.grid {{

    display: grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap: 18px;

    margin-top: 28px;
}}

.card {{

    background: white;

    border:
        1px solid
        #e4e7ee;

    border-radius: 14px;

    padding: 22px;

    box-shadow:
        0 4px 15px
        #17203308;
}}

.metric {{

    font-size: 38px;

    font-weight: 800;

    line-height: 1.1;
}}

.metric-label {{

    color: #657084;

    margin-top: 6px;

    font-size: 14px;
}}

.insight {{

    background: white;

    border-left:
        5px solid
        #315efb;

    border-radius: 12px;

    padding: 24px;

    margin:
        18px 0;

    box-shadow:
        0 4px 15px
        #17203308;
}}

.insight strong {{

    font-size: 18px;
}}

.two-col {{

    display: grid;

    grid-template-columns:
        1fr 1fr;

    gap: 24px;
}}

.bar-row {{

    display: grid;

    grid-template-columns:
        250px 1fr 40px;

    gap: 12px;

    align-items: center;

    margin:
        13px 0;
}}

.bar-track {{

    height: 12px;

    background: #edf0f5;

    border-radius: 20px;

    overflow: hidden;
}}

.bar-fill {{

    height: 100%;

    background: #315efb;

    border-radius: 20px;
}}

.bar-label {{

    font-size: 14px;
}}

.bar-number {{

    font-weight: 700;

    text-align: right;
}}

.workflow {{

    display: grid;

    grid-template-columns:
        repeat(5, 1fr);

    gap: 12px;

    margin-top: 25px;
}}

.step {{

    background: white;

    border:
        1px solid
        #e4e7ee;

    padding: 20px;

    border-radius: 12px;

    box-shadow:
        0 4px 15px
        #17203308;
}}

.step-number {{

    font-size: 12px;

    font-weight: bold;

    color: #315efb;
}}

.proof-grid {{

    display: grid;

    grid-template-columns:
        1fr 1fr;

    gap: 18px;

    margin-top: 22px;
}}

.proof-card {{

    background:
        #f8faff;

    border:
        1px solid
        #dce4ff;

    border-radius: 12px;

    padding: 20px;
}}

.code-box {{

    background: #111827;

    color: #dbe4f5;

    padding: 18px;

    border-radius: 10px;

    overflow-x: auto;

    font-family:
        Consolas,
        "Courier New",
        monospace;

    font-size: 13px;
}}

.status {{

    display: inline-block;

    padding:
        3px 8px;

    background: #f1f4f8;

    border-radius: 6px;

    font-size: 12px;
}}

table {{

    width: 100%;

    border-collapse:
        collapse;

    background: white;

    font-size: 13px;
}}

th {{

    background: #172033;

    color: white;

    padding: 12px;

    text-align: left;

    position: sticky;

    top: 0;

    z-index: 2;
}}

td {{

    padding: 11px;

    border-bottom:
        1px solid
        #e8ebf1;

    vertical-align: top;
}}

tr:hover {{

    background: #f5f7fc;
}}

.table-wrap {{

    overflow: auto;

    max-height: 680px;

    border-radius: 12px;

    border:
        1px solid
        #e4e7ee;
}}

.small {{

    font-size: 13px;

    color: #697386;
}}

.verification-good {{

    color: #087443;

    font-weight: 800;
}}

.verification-warning {{

    color: #9a6700;

    font-weight: 800;
}}

.footer-links {{

    display: flex;

    gap: 20px;

    flex-wrap: wrap;

    margin-top: 15px;
}}

footer {{

    background: #111827;

    color: #cdd5e4;

    padding:
        38px 0;

    margin-top: 30px;
}}

footer a {{

    color: white;
}}

@media(max-width: 1000px) {{

    .grid {{
        grid-template-columns:
            repeat(2, 1fr);
    }}

    .workflow {{
        grid-template-columns:
            repeat(2, 1fr);
    }}

    .proof-grid {{
        grid-template-columns:
            1fr;
    }}

}}

@media(max-width: 700px) {{

    .hero {{
        padding:
            55px 0;
    }}

    .hero h1 {{
        font-size: 36px;
    }}

    .two-col {{
        grid-template-columns:
            1fr;
    }}

    .grid {{
        grid-template-columns:
            1fr;
    }}

    .workflow {{
        grid-template-columns:
            1fr;
    }}

    .bar-row {{
        grid-template-columns:
            1fr 80px;
    }}

    .bar-track {{
        grid-column:
            1 / 2;
    }}

    .bar-number {{
        grid-column:
            2 / 3;
        grid-row:
            1 / 3;
    }}

}}

</style>

</head>


<body>


<!-- ===================================================== -->
<!-- HERO -->
<!-- ===================================================== -->

<div class="hero">

<div class="container">

<div class="badge">
AI Product Ops Intern — Take-Home Case Study
</div>

<h1>
Researching 100 Apps for AI Agent Readiness
</h1>

<p>
I built an automated research pipeline that investigates
authentication, credential access, API surface, MCP availability
and buildability across 100 real-world applications.
</p>

<p>
The objective was not simply to produce 100 rows. The pipeline was
designed to identify patterns: which apps are easy agent-toolkit
opportunities, which require setup, and which need product,
enterprise or partnership outreach.
</p>

<div class="hero-actions">

<a
    class="hero-button"
    href="{LIVE_URL}"
    target="_blank"
>
Open Live Case Study
</a>

<a
    class="hero-button secondary"
    href="{GITHUB_URL}"
    target="_blank"
>
View Source Repository
</a>

</div>

</div>

</div>


<!-- ===================================================== -->
<!-- HEADLINE -->
<!-- ===================================================== -->

<section>

<div class="container">

<h2>
The headline
</h2>

<div class="insight">

<strong>
{ready}% of the 100 researched apps are directly agent-ready.
</strong>

<p>
The final research classified
<b>{ready}</b> apps as <b>yes</b> for agent readiness,
<b>{setup}</b> as <b>yes_with_setup</b>,
<b>{unclear}</b> as unclear,
and <b>{not_ready}</b> as not ready.
</p>

<p>
<b>{broad}</b> apps have broad API surfaces. This suggests that
API breadth alone is rarely the decisive blocker. Authentication,
credential accessibility, permissions, documentation quality and
product-specific setup are often more important.
</p>

</div>


<div class="insight">

<strong>
OAuth is the dominant authentication family.
</strong>

<p>
The raw dataset contains multiple naming variants including
OAuth, OAuth 2, OAuth2 and OAuth 2.0. After normalizing those
variants, an OAuth-family authentication method appears across
<b>{oauth_apps}</b> of the 100 researched records.
</p>

<p class="small">
This normalization is used only for the headline pattern;
the detailed matrix preserves the original authentication values.
</p>

</div>


<div class="insight">

<strong>
MCP availability is meaningful but documentation coverage is uneven.
</strong>

<p>
<b>{mcp_yes}</b> apps explicitly support MCP,
<b>{mcp_unclear}</b> remain unclear,
and <b>{mcp_no}</b> were classified as not supporting MCP based
on the evidence collected.
</p>

<p>
This creates a practical opportunity: apps with broad APIs but
unclear or absent MCP support can still be strong candidates for
toolkit development.
</p>

</div>

</div>

</section>


<!-- ===================================================== -->
<!-- SNAPSHOT -->
<!-- ===================================================== -->

<section>

<div class="container">

<h2>
Research snapshot
</h2>

<p class="subtitle">
The final structured dataset contains exactly 100 researched apps
across 10 product categories.
</p>


<div class="grid">

<div class="card">

<div class="metric">
{total}
</div>

<div class="metric-label">
Apps researched
</div>

</div>


<div class="card">

<div class="metric">
{ready}
</div>

<div class="metric-label">
Directly agent-ready
</div>

</div>


<div class="card">

<div class="metric">
{mcp_yes}
</div>

<div class="metric-label">
MCP available
</div>

</div>


<div class="card">

<div class="metric">
{high_conf}
</div>

<div class="metric-label">
High-confidence records
</div>

</div>

</div>


<div class="grid">

<div class="card">

<div class="metric">
{self_serve}
</div>

<div class="metric-label">
Self-serve access
</div>

</div>


<div class="card">

<div class="metric">
{paid}
</div>

<div class="metric-label">
Paid required
</div>

</div>


<div class="card">

<div class="metric">
{sales}
</div>

<div class="metric-label">
Contact sales
</div>

</div>


<div class="card">

<div class="metric">
{broad}
</div>

<div class="metric-label">
Broad APIs
</div>

</div>

</div>

</div>

</section>


<!-- ===================================================== -->
<!-- PATTERNS -->
<!-- ===================================================== -->

<section>

<div class="container">

<h2>
What the data says
</h2>

<div class="two-col">


<div class="card">

<h3>
Access pattern
</h3>

<p>

<b>{self_serve}</b> apps were classified as self-serve.

<b>{paid}</b> required a paid plan.

<b>{sales}</b> were classified as contact-sales.

<b>{unknown_access}</b> remained unknown.

</p>

<p class="small">

The research intentionally preserves uncertainty instead of
inventing credential requirements when documentation was not
sufficient.

</p>

</div>


<div class="card">

<h3>
Confidence
</h3>

<p>

<b>{high_conf}</b> high-confidence records,

<b>{medium_conf}</b> medium-confidence records,

and <b>{low_conf}</b> low-confidence records.

</p>

<p class="small">

Confidence is based on the evidence collected by the pipeline
and is separate from the independent human verification sample.

</p>

</div>


</div>

</div>

</section>


<!-- ===================================================== -->
<!-- CATEGORY DISTRIBUTION -->
<!-- ===================================================== -->

<section>

<div class="container">

<h2>
Category distribution
</h2>

<p class="subtitle">
The research set intentionally spans different product surfaces,
authentication models and API maturity levels.
</p>

<div class="card">

{category_html}

</div>

</div>

</section>


<!-- ===================================================== -->
<!-- AGENT -->
<!-- ===================================================== -->

<section>

<div class="container">

<h2>
The research agent
</h2>

<p class="subtitle">
The 100 rows were produced through a Python research pipeline
rather than manually filling the dataset one application at a time.
</p>


<div class="insight">

<strong>
Proof of implementation
</strong>

<p>
The repository contains the research components used to build,
repair, analyze and verify the dataset.
</p>

<div class="footer-links">

<a
    href="{GITHUB_URL}"
    target="_blank"
>
GitHub source repository →
</a>

<a
    href="{LIVE_URL}"
    target="_blank"
>
Live deployed case study →
</a>

</div>

</div>


<div class="workflow">


<div class="step">

<div class="step-number">
STEP 1
</div>

<h3>
Input
</h3>

<p>
Load the canonical 100-app research set from
<code>data/apps.json</code>.
</p>

</div>


<div class="step">

<div class="step-number">
STEP 2
</div>

<h3>
Discovery
</h3>

<p>
Identify relevant official documentation for authentication,
API capabilities, pricing/access and MCP.
</p>

</div>


<div class="step">

<div class="step-number">
STEP 3
</div>

<h3>
Extraction
</h3>

<p>
Collect and structure evidence into a consistent research schema
for every application.
</p>

</div>


<div class="step">

<div class="step-number">
STEP 4
</div>

<h3>
Analysis
</h3>

<p>
Classify authentication, access, API breadth, MCP availability
and agent readiness.
</p>

</div>


<div class="step">

<div class="step-number">
STEP 5
</div>

<h3>
Repair + Verify
</h3>

<p>
Repair incorrect IDs, remove duplicates, fill missing applications,
run quality checks and perform human verification.
</p>

</div>


</div>


<div class="proof-grid">


<div class="proof-card">

<h3>
Automated components
</h3>

<ul>

<li>
Researcher / retrieval pipeline
</li>

<li>
Structured research schema
</li>

<li>
Result repair logic
</li>

<li>
Pattern analysis
</li>

<li>
Automated quality checks
</li>

<li>
Verification sampling
</li>

</ul>

</div>


<div class="proof-card">

<h3>
Human involvement
</h3>

<ul>

<li>
Reviewed a 20-app sample manually
</li>

<li>
Cross-checked claims against documentation
</li>

<li>
Investigated low-confidence records
</li>

<li>
Reviewed cross-app contamination
</li>

<li>
Validated the final 100 unique IDs
</li>

</ul>

</div>


</div>

</div>

</section>


<!-- ===================================================== -->
<!-- HUMAN IN LOOP -->
<!-- ===================================================== -->

<section>

<div class="container">

<h2>
Human-in-the-loop
</h2>


<div class="insight">

<strong>
The agent was not treated as automatically correct.
</strong>

<p>
The automated research initially contained data-quality problems,
including incorrect application references and incomplete fields.
A repair process matched records against the canonical
<code>apps.json</code> list, corrected IDs, removed duplicates and
identified missing applications.
</p>

<p>
The final structural verification reported:
<b>100 results</b>,
<b>100 unique IDs</b>,
and <b>0 missing IDs</b>.
</p>

</div>


<div class="insight">

<strong>
Failure cases were handled explicitly.
</strong>

<p>
Some official documentation endpoints returned HTTP 403 or 404
responses. Instead of silently treating these cases as successful
research, the pipeline recorded failures and handled them through
the repair and completion workflow.
</p>

<p>
This highlights an important limitation:
<b>documentation accessibility does not always equal product
accessibility.</b>
</p>

</div>


<div class="two-col">


<div class="card">

<h3>
Automated QA findings
</h3>

<ul>

<li>
4 potential cross-app references
</li>

<li>
9 missing authentication fields
</li>

<li>
8 missing API-type fields
</li>

<li>
11 low/medium-confidence records
</li>

</ul>

</div>


<div class="card">

<h3>
How QA improved trust
</h3>

<p>
Instead of hiding imperfect results, the QA layer exposed them.
Those findings were used to repair, qualify and verify the final
dataset.
</p>

<p>
This creates an auditable workflow from raw research to final
case-study output.
</p>

</div>

</div>

</div>

</section>


<!-- ===================================================== -->
<!-- VERIFICATION -->
<!-- ===================================================== -->

<section>

<div class="container">

<h2>
Verification & Accuracy
</h2>

<p class="subtitle">
The most important validation was an independent human review of
a 20-app sample against the underlying documentation.
</p>


<div class="insight">

<strong>
20-app human verification: 95% directionally correct.
</strong>

<p>
After the automated research pass, I manually checked a
20-app sample against the underlying documentation.
The sample produced:
</p>

<p>

<b>14 exact matches</b> ·
<b>5 partial matches</b> ·
<b>1 miss</b>

</p>

<p>
That gives <b>70% strict-match accuracy</b> and
<b>95% accuracy when partial matches are included</b>.
</p>

<p>
The verification loop was intentionally designed to expose
imperfect answers rather than treating agent output as ground truth.
</p>

</div>


<div class="grid">


<div class="card">

<div class="metric">
20
</div>

<div class="metric-label">
Apps manually verified
</div>

</div>


<div class="card">

<div class="metric">
14
</div>

<div class="metric-label">
Exact matches
</div>

</div>


<div class="card">

<div class="metric">
5
</div>

<div class="metric-label">
Partial matches
</div>

</div>


<div class="card">

<div class="metric">
1
</div>

<div class="metric-label">
Miss
</div>

</div>

</div>


<div class="grid">


<div class="card">

<div class="metric">
70%
</div>

<div class="metric-label">
Strict-match accuracy
</div>

</div>


<div class="card">

<div class="metric">
95%
</div>

<div class="metric-label">
Match + partial accuracy
</div>

</div>


<div class="card">

<div class="metric">
{high_conf}
</div>

<div class="metric-label">
High-confidence final records
</div>

</div>


<div class="card">

<div class="metric">
100/100
</div>

<div class="metric-label">
Unique-ID verification
</div>

</div>

</div>


<div class="insight">

<strong>
What this verification means
</strong>

<p>
The 70% strict score shows that the first-pass research was not
perfect. Including partial matches, 19 of 20 reviewed records were
directionally correct.
</p>

<p>
The result demonstrates why an agentic research system needs
verification loops, confidence scoring and human review instead of
assuming that generated research is automatically reliable.
</p>

</div>

</div>

</section>


<!-- ===================================================== -->
<!-- MATRIX -->
<!-- ===================================================== -->

<section>

<div class="container">

<h2>
100-app research matrix
</h2>

<p class="subtitle">
The detailed dataset is available below so a reviewer can inspect
the classifications across all 100 applications. Use the browser's
Find function to locate an individual app.
</p>


<div class="table-wrap">

<table>

<thead>

<tr>

<th>ID</th>

<th>App</th>

<th>Category</th>

<th>Auth</th>

<th>Access</th>

<th>API</th>

<th>Breadth</th>

<th>MCP</th>

<th>Agent Ready</th>

<th>Confidence</th>

</tr>

</thead>


<tbody>

{table_html}

</tbody>

</table>

</div>

</div>

</section>


<!-- ===================================================== -->
<!-- TAKEAWAY -->
<!-- ===================================================== -->

<section>

<div class="container">

<h2>
Key takeaway
</h2>


<div class="insight">

<strong>
The best agent-toolkit opportunities are not simply the apps
with the biggest APIs.
</strong>

<p>
The practical opportunity sits at the intersection of:
</p>

<ul>

<li>
API breadth
</li>

<li>
Credential accessibility
</li>

<li>
Authentication simplicity
</li>

<li>
MCP availability
</li>

<li>
Documentation quality
</li>

<li>
Product-specific setup complexity
</li>

</ul>

<p>
The strongest candidates are generally self-serve applications
with broad, well-documented APIs and straightforward authentication.
</p>

<p>
The harder cases are driven by enterprise permissions, paid access,
contact-sales processes, unclear documentation or product-specific
setup.
</p>

</div>


<div class="insight">

<strong>
What I would do next
</strong>

<p>
For a production version, I would prioritize the highest-value
self-serve apps first, improve the evidence-ranking and verification
loop, normalize authentication and API taxonomies, and route
contact-sales or enterprise-gated apps into a separate outreach
queue.
</p>

</div>

</div>

</section>


<!-- ===================================================== -->
<!-- FOOTER -->
<!-- ===================================================== -->

<footer>

<div class="container">

<b>
AI Product Ops Research Agent
</b>

<p>
100-app automated research case study · Generated from the final
research dataset.
</p>


<div class="footer-links">

<a
    href="{GITHUB_URL}"
    target="_blank"
>
GitHub Repository
</a>

<a
    href="{LIVE_URL}"
    target="_blank"
>
Live Case Study
</a>

</div>

</div>

</footer>


</body>

</html>
"""

    # ---------------------------------------------------------
    # WRITE FILE
    # ---------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)

    print()
    print("========================================")
    print("CASE STUDY GENERATED")
    print("========================================")
    print(f"Saved to:")
    print(OUTPUT_FILE)
    print("========================================")


if __name__ == "__main__":
    main()
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

RESEARCH_FILE = DATA_DIR / "research_clean.json"
ANALYSIS_FILE = DATA_DIR / "analysis.json"
OUTPUT_FILE = BASE_DIR / "case_study.html"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():

    research = load_json(RESEARCH_FILE)
    analysis = load_json(ANALYSIS_FILE)

    total = len(research)

    # High-level numbers
    agent_ready = analysis["agent_ready"]
    mcp = analysis["mcp_available"]
    breadth = analysis["api_breadth"]
    access = analysis["self_serve_status"]
    confidence = analysis["confidence"]

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

    categories = analysis["categories"]

    # Normalize OAuth-family authentication for the headline insight
    oauth_apps = 0

    for item in research:
        auth = item.get("auth_methods", [])

        if isinstance(auth, str):
            auth = [auth]

        auth_text = " ".join(str(x).lower() for x in auth)

        if "oauth" in auth_text:
            oauth_apps += 1

    # Build table
    rows = []

    for item in research:
        auth = item.get("auth_methods", [])
        api = item.get("api_type", [])

        if isinstance(auth, list):
            auth_text = ", ".join(str(x) for x in auth)
        else:
            auth_text = str(auth)

        if isinstance(api, list):
            api_text = ", ".join(str(x) for x in api)
        else:
            api_text = str(api)

        rows.append(
            f"""
            <tr>
                <td>{item.get("app_id", "")}</td>
                <td><strong>{item.get("app_name", "")}</strong></td>
                <td>{item.get("category", "")}</td>
                <td>{auth_text}</td>
                <td>{item.get("self_serve_status", "unknown")}</td>
                <td>{api_text}</td>
                <td>{item.get("api_breadth", "unknown")}</td>
                <td>{item.get("mcp_available", "unknown")}</td>
                <td>{item.get("agent_ready", "unknown")}</td>
                <td>{item.get("confidence", "unknown")}</td>
            </tr>
            """
        )

    table_html = "\n".join(rows)

    category_html = ""

    for name, count in sorted(
        categories.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        category_html += f"""
        <div class="bar-row">
            <div class="bar-label">{name}</div>
            <div class="bar-track">
                <div class="bar-fill" style="width:{count * 10}%"></div>
            </div>
            <div class="bar-number">{count}</div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>AI Product Ops Research — 100 App Agent Readiness Study</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Inter, Arial, sans-serif;
    background: #f6f7fb;
    color: #172033;
    line-height: 1.55;
}}

.container {{
    width: min(1400px, 94%);
    margin: auto;
}}

.hero {{
    background: linear-gradient(135deg, #111827, #253b67);
    color: white;
    padding: 70px 0;
}}

.hero h1 {{
    font-size: 46px;
    line-height: 1.1;
    margin: 0 0 18px;
}}

.hero p {{
    max-width: 850px;
    font-size: 19px;
    color: #dbe4f5;
}}

.badge {{
    display: inline-block;
    background: #ffffff20;
    border: 1px solid #ffffff35;
    padding: 7px 13px;
    border-radius: 20px;
    margin-bottom: 18px;
}}

section {{
    padding: 48px 0;
}}

h2 {{
    font-size: 30px;
    margin-bottom: 12px;
}}

.subtitle {{
    color: #657084;
    max-width: 850px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-top: 28px;
}}

.card {{
    background: white;
    border: 1px solid #e4e7ee;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 4px 15px #17203308;
}}

.metric {{
    font-size: 38px;
    font-weight: 800;
}}

.metric-label {{
    color: #657084;
}}

.insight {{
    background: white;
    border-left: 5px solid #315efb;
    border-radius: 12px;
    padding: 24px;
    margin: 18px 0;
}}

.insight strong {{
    font-size: 18px;
}}

.two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}}

.bar-row {{
    display: grid;
    grid-template-columns: 240px 1fr 40px;
    gap: 12px;
    align-items: center;
    margin: 12px 0;
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
}}

.bar-label {{
    font-size: 14px;
}}

.bar-number {{
    font-weight: 700;
}}

.workflow {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-top: 25px;
}}

.step {{
    background: white;
    border: 1px solid #e4e7ee;
    padding: 20px;
    border-radius: 12px;
}}

.step-number {{
    font-size: 12px;
    font-weight: bold;
    color: #315efb;
}}

table {{
    width: 100%;
    border-collapse: collapse;
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
}}

td {{
    padding: 11px;
    border-bottom: 1px solid #e8ebf1;
    vertical-align: top;
}}

tr:hover {{
    background: #f5f7fc;
}}

.table-wrap {{
    overflow: auto;
    max-height: 650px;
    border-radius: 12px;
    border: 1px solid #e4e7ee;
}}

.small {{
    font-size: 13px;
    color: #697386;
}}

footer {{
    background: #111827;
    color: #cdd5e4;
    padding: 35px 0;
    margin-top: 30px;
}}

@media(max-width: 900px) {{
    .grid,
    .two-col,
    .workflow {{
        grid-template-columns: 1fr 1fr;
    }}

    .hero h1 {{
        font-size: 36px;
    }}
}}

@media(max-width: 600px) {{
    .grid,
    .two-col,
    .workflow {{
        grid-template-columns: 1fr;
    }}
}}

</style>
</head>

<body>

<div class="hero">
<div class="container">

<div class="badge">AI Product Ops Intern — Take-Home Case Study</div>

<h1>Researching 100 Apps for AI Agent Readiness</h1>

<p>
I built an automated research pipeline that investigates authentication,
credential access, API surface, MCP availability and buildability across
100 real-world applications.
</p>

<p>
The goal was not just to collect rows, but to identify where an AI agent
toolkit can be built quickly, where setup is required, and where product
or partnership outreach may be necessary.
</p>

</div>
</div>


<section>
<div class="container">

<h2>The headline</h2>

<div class="insight">
<strong>{ready}% of the researched apps are classified as directly agent-ready.</strong>
<p>
The research produced {ready} apps marked <b>yes</b> for agent readiness,
{setup} requiring setup, {unclear} unclear cases, and {not_ready} not-ready
cases. {broad} apps have broad API surfaces, suggesting that API breadth
alone is rarely the main blocker; authentication, access and product-specific
setup are more important.
</p>
</div>

<div class="insight">
<strong>OAuth is the dominant authentication family.</strong>
<p>
The raw dataset contains several naming variants such as OAuth, OAuth 2,
OAuth2 and OAuth 2.0. Together, OAuth-family authentication appears across
{oauth_apps} of the 100 researched records.
</p>
</div>

<div class="insight">
<strong>MCP is growing, but documentation coverage is uneven.</strong>
<p>
{mcp_yes} apps explicitly support MCP, while {mcp_unclear} remain unclear
and {mcp_no} were classified as not supporting MCP based on the collected
evidence.
</p>
</div>

</div>
</section>


<section>
<div class="container">

<h2>Research snapshot</h2>

<div class="grid">

<div class="card">
<div class="metric">{total}</div>
<div class="metric-label">Apps researched</div>
</div>

<div class="card">
<div class="metric">{ready}</div>
<div class="metric-label">Agent-ready</div>
</div>

<div class="card">
<div class="metric">{mcp_yes}</div>
<div class="metric-label">MCP available</div>
</div>

<div class="card">
<div class="metric">{high_conf}</div>
<div class="metric-label">High-confidence results</div>
</div>

</div>

<div class="grid">

<div class="card">
<div class="metric">{self_serve}</div>
<div class="metric-label">Self-serve access</div>
</div>

<div class="card">
<div class="metric">{paid}</div>
<div class="metric-label">Paid required</div>
</div>

<div class="card">
<div class="metric">{sales}</div>
<div class="metric-label">Contact sales</div>
</div>

<div class="card">
<div class="metric">{broad}</div>
<div class="metric-label">Broad APIs</div>
</div>

</div>

</div>
</section>


<section>
<div class="container">

<h2>What the data says</h2>

<div class="two-col">

<div class="card">
<h3>Access pattern</h3>

<p>
<b>{self_serve}</b> apps were classified as self-serve.
<b>{paid}</b> required a paid plan,
<b>{sales}</b> were contact-sales,
and <b>{unknown_access}</b> remained unknown.
</p>

<p class="small">
The research intentionally treats uncertainty as a first-class result
rather than inventing access requirements.
</p>
</div>

<div class="card">
<h3>Confidence</h3>

<p>
<b>{high_conf}</b> high-confidence,
<b>{medium_conf}</b> medium-confidence,
and <b>{low_conf}</b> low-confidence records.
</p>

<p class="small">
Confidence is based on the quality and quantity of evidence collected
by the research pipeline.
</p>
</div>

</div>

</div>
</section>


<section>
<div class="container">

<h2>Category distribution</h2>

<div class="card">
{category_html}
</div>

</div>
</section>


<section>
<div class="container">

<h2>The research agent</h2>

<p class="subtitle">
The pipeline was designed to research official documentation rather than
manually filling the 100 rows.
</p>

<div class="workflow">

<div class="step">
<div class="step-number">STEP 1</div>
<h3>Input</h3>
<p>Load the 100-app research set from apps.json.</p>
</div>

<div class="step">
<div class="step-number">STEP 2</div>
<h3>Discovery</h3>
<p>Start from official documentation roots and discover relevant API,
authentication, pricing and MCP pages.</p>
</div>

<div class="step">
<div class="step-number">STEP 3</div>
<h3>Extraction</h3>
<p>Fetch and clean documentation pages before analysis.</p>
</div>

<div class="step">
<div class="step-number">STEP 4</div>
<h3>Analysis</h3>
<p>Classify auth, access, API surface, MCP and agent readiness.</p>
</div>

<div class="step">
<div class="step-number">STEP 5</div>
<h3>Repair + Verify</h3>
<p>Repair IDs, remove duplicates, fill failed apps and verify the final
dataset contains exactly 100 unique apps.</p>
</div>

</div>

</div>
</section>


<section>
<div class="container">

<h2>Human-in-the-loop</h2>

<div class="insight">
<strong>The agent was not treated as automatically correct.</strong>

<p>
The first research pass produced duplicate and incorrect app IDs.
A repair process matched records against the canonical apps.json list,
corrected IDs, removed duplicates and identified missing applications.
</p>

<p>
The final verification reported:
<b>100 results, 100 unique IDs and 0 missing IDs.</b>
</p>
</div>

<div class="insight">
<strong>Failure cases were handled explicitly.</strong>

<p>
Some official documentation endpoints returned HTTP 403 or 404 responses.
Instead of silently claiming success, these applications were identified
as missing and handled separately before the final dataset was completed.
</p>

<p>
This is an important limitation of the pipeline: documentation accessibility
does not always equal product accessibility.
</p>
</div>

</div>
</section>


<section>
<div class="container">

<h2>Verification</h2>

<div class="grid">

<div class="card">
<div class="metric">{high_conf}</div>
<div class="metric-label">High-confidence records</div>
</div>

<div class="card">
<div class="metric">{medium_conf}</div>
<div class="metric-label">Medium-confidence records</div>
</div>

<div class="card">
<div class="metric">{low_conf}</div>
<div class="metric-label">Low-confidence records</div>
</div>

<div class="card">
<div class="metric">100/100</div>
<div class="metric-label">Unique-ID verification</div>
</div>

</div>

<p class="small">
Verification included programmatic validation of result count, uniqueness
of app IDs and valid JSON structure. The research also records confidence
and evidence URLs per app so individual claims can be inspected.
</p>

</div>
</section>


<section>
<div class="container">

<h2>100-app research matrix</h2>

<p class="subtitle">
The detailed dataset is intentionally available below for inspection.
The table is searchable using the browser's Find function.
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


<section>
<div class="container">

<h2>Key takeaway</h2>

<div class="insight">

<p>
The research suggests that the opportunity is not simply to prioritize
apps with the largest APIs. The practical agent-toolkit opportunity sits
at the intersection of API breadth, credential accessibility, authentication
simplicity, MCP availability and setup complexity.
</p>

<p>
The strongest candidates are self-serve applications with broad,
well-documented APIs and straightforward authentication. The harder cases
are driven by enterprise permissions, paid access, contact-sales processes,
unclear documentation or product-specific setup.
</p>

</div>

</div>
</section>


<footer>
<div class="container">

<b>AI Product Ops Research Agent</b>

<p>
100-app automated research case study · Generated from the final verified
research dataset.
</p>

</div>
</footer>

</body>
</html>
"""

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

    print("\n========================================")
    print("CASE STUDY GENERATED")
    print("========================================")
    print(f"Saved to:\n{OUTPUT_FILE}")
    print("========================================")


if __name__ == "__main__":
    main()
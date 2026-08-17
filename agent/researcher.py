import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from agent.schemas import AppResearch
from agent.retriever import (
    retrieve_document_bundle,
    truncate_text,
)


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found in .env"
    )


client = genai.Client(
    api_key=API_KEY
)


BASE_DIR = Path(__file__).resolve().parent.parent

APPS_FILE = (
    BASE_DIR
    / "data"
    / "apps.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "research.json"
)

FAILURE_FILE = (
    BASE_DIR
    / "data"
    / "failures.json"
)


# Number of attempts for temporary API errors.
MAX_RETRIES = 3

# Wait between attempts.
RETRY_DELAY = 10

# Number of documentation pages per app.
MAX_DOCUMENTS = 6


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI Product Operations research analyst.

Your job is to research software applications for
potential integration into AI agent toolkits.

You will receive multiple documents retrieved from
official sources.

Determine:

1. What the application does.
2. Authentication methods.
3. Whether developer credentials can be obtained
   through a self-serve process.
4. Whether payment, admin approval, partnership,
   or contact-sales requirements exist.
5. API type.
6. API breadth.
7. Major API capabilities.
8. Whether MCP support is evidenced.
9. Whether the application is suitable for an
   AI agent toolkit today.
10. The main blocker.

STRICT RULES:

- Prefer official documentation.
- Use ONLY information contained in the supplied
  documents.
- Never invent authentication methods.
- Never invent API capabilities.
- Never invent pricing or access requirements.
- Never claim MCP support without evidence.
- "No evidence found" is NOT the same as "no".
- If evidence is insufficient, use "unknown" or
  "unclear".
- Distinguish product access from developer/API access.
- Distinguish a free product plan from free API credentials.
- Be conservative when determining self-serve access.
- Every important conclusion must have evidence.
- Evidence URLs must be URLs supplied in the documents.
- Evidence claims must accurately describe what the
  source supports.

MCP RULE:

Use "yes" only when there is actual evidence of an
MCP server, official MCP support, or a clearly
documented MCP integration.

Use "no" only when the supplied evidence explicitly
establishes that MCP is unavailable or unsupported.

Otherwise use "unclear".

CONFIDENCE:

high:
Strong direct evidence from official documentation.

medium:
Good evidence but some details require interpretation.

low:
Important information is missing or uncertain.
"""


# ============================================================
# LOAD APPS
# ============================================================

def load_apps():

    with open(
        APPS_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ============================================================
# URL HANDLING
# ============================================================

def get_root_url(app):

    # GitHub requires the actual REST documentation root.
    if app["name"] == "GitHub":

        return (
            "https://docs.github.com/en/rest"
        )

    root_url = app["hint"]

    if not root_url.startswith(
        "http://"
    ) and not root_url.startswith(
        "https://"
    ):

        root_url = (
            "https://" + root_url
        )

    return root_url


# ============================================================
# DOCUMENT RETRIEVAL
# ============================================================

def build_document_bundle(app):

    root_url = get_root_url(app)

    print(
        f"  Trying documentation root: "
        f"{root_url}"
    )

    documents = retrieve_document_bundle(
        root_url,
        max_links=MAX_DOCUMENTS,
        app_name=app["name"],
    )

    return documents


# ============================================================
# PROMPT CREATION
# ============================================================

def build_prompt(
    app,
    documents,
):

    document_sections = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        text = truncate_text(
            document["text"],
            max_chars=12000,
        )

        document_sections.append(
            f"""
==============================
DOCUMENT {index}
==============================

Research category:
{document["category"]}

Title:
{document["title"]}

URL:
{document["url"]}

Content:
{text}

==============================
END DOCUMENT {index}
==============================
"""
        )

    documentation_bundle = "\n".join(
        document_sections
    )

    return f"""
APPLICATION

Name:
{app["name"]}

Category:
{app["category"]}

Original research hint:
{app["hint"]}


OFFICIAL DOCUMENTATION

{documentation_bundle}


TASK

Analyze the application using the supplied
documentation.

Return a structured AppResearch result.

IMPORTANT:

Authentication should primarily use documents
classified as "authentication".

API claims should primarily use documents classified
as "api".

MCP claims require direct MCP evidence.

Access/self-serve claims require explicit evidence.

If evidence is missing, use "unknown" or "unclear".

Do not treat absence of evidence as proof of absence.

Each evidence item must:

1. Use a URL from the supplied documents.
2. State one specific claim supported by that URL.
3. Avoid unsupported conclusions.
"""


# ============================================================
# GEMINI ANALYSIS
# ============================================================

def analyze_app(
    app,
    documents,
):

    prompt = build_prompt(
        app,
        documents,
    )

    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):

        try:

            response = client.models.generate_content(

                model="gemini-3.1-flash-lite",

                contents=(
                    SYSTEM_PROMPT
                    + "\n\n"
                    + prompt
                ),

                config={
                    "response_mime_type":
                        "application/json",

                    "response_schema":
                        AppResearch,

                    "temperature":
                        0.1,
                },
            )

            return AppResearch.model_validate_json(
                response.text
            )

        except Exception as e:

            error_text = str(e)

            print(
                f"  Gemini attempt "
                f"{attempt}/{MAX_RETRIES} failed"
            )

            print(
                f"  {error_text[:500]}"
            )

            # Retry temporary quota/service errors.
            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED"
                in error_text
                or "503" in error_text
                or "UNAVAILABLE"
                in error_text
            ):

                if attempt < MAX_RETRIES:

                    print(
                        f"  Waiting "
                        f"{RETRY_DELAY} seconds..."
                    )

                    time.sleep(
                        RETRY_DELAY
                    )

                    continue

            raise


# ============================================================
# LOAD EXISTING RESULTS
# ============================================================

def load_existing_results():

    if not OUTPUT_FILE.exists():

        return []

    try:

        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

            if isinstance(
                data,
                list,
            ):

                return data

    except Exception as e:

        print(
            f"Warning: Could not read existing "
            f"research.json: {e}"
        )

    return []


# ============================================================
# LOAD FAILURES
# ============================================================

def load_failures():

    if not FAILURE_FILE.exists():

        return []

    try:

        with open(
            FAILURE_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

            if isinstance(
                data,
                list,
            ):

                return data

    except Exception:
        pass

    return []


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(results):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# SAVE FAILURES
# ============================================================

def save_failures(failures):

    FAILURE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        FAILURE_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            failures,
            f,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# REMOVE OLD FAILURE FOR SUCCESSFULLY COMPLETED APP
# ============================================================

def remove_failure_for_app(
    failures,
    app_id,
):

    return [
        failure
        for failure in failures
        if failure.get("app_id") != app_id
    ]


# ============================================================
# MAIN
# ============================================================

def main():

    apps = load_apps()

    results = load_existing_results()

    failures = load_failures()

    completed_ids = {
        item["app_id"]
        for item in results
        if "app_id" in item
    }

    print(
        "\n========================================"
    )

    print(
        "AI PRODUCT OPS RESEARCH AGENT"
    )

    print(
        "========================================"
    )

    print(
        f"Total apps: {len(apps)}"
    )

    print(
        f"Already completed: "
        f"{len(completed_ids)}"
    )

    print(
        f"Remaining: "
        f"{len(apps) - len(completed_ids)}"
    )

    print(
        "========================================\n"
    )


    for index, app in enumerate(
        apps,
        start=1,
    ):

        app_id = app["id"]

        app_name = app["name"]


        # ----------------------------------------------------
        # CHECKPOINT
        # ----------------------------------------------------

        if app_id in completed_ids:

            print(
                f"[{index}/{len(apps)}] "
                f"Skipping {app_name} "
                f"(already completed)"
            )

            continue


        print(
            f"\n[{index}/{len(apps)}]"
        )

        print(
            f"Researching: {app_name}"
        )


        # ----------------------------------------------------
        # RETRIEVE DOCUMENTATION
        # ----------------------------------------------------

        try:

            documents = build_document_bundle(
                app
            )

            print(
                f"Collected "
                f"{len(documents)} documents"
            )

            if not documents:

                raise RuntimeError(
                    "No documentation could be retrieved."
                )


        except Exception as e:

            print(
                f"✗ Retrieval failed: "
                f"{app_name}"
            )

            print(
                f"  Error: {e}"
            )

            # Avoid creating duplicate failure records
            # when the same application is retried.
            failures = [
                failure
                for failure in failures
                if failure.get("app_id") != app_id
            ]

            failures.append(
                {
                    "app_id": app_id,
                    "app_name": app_name,
                    "stage": "retrieval",
                    "error": str(e),
                }
            )

            save_failures(
                failures
            )

            continue


        # ----------------------------------------------------
        # ANALYZE
        # ----------------------------------------------------

        try:

            result = analyze_app(
                app,
                documents,
            )

            result_dict = (
                result.model_dump()
            )

            # ------------------------------------------------
            # FORCE CORRECT APP ID
            # ------------------------------------------------
            #
            # Gemini should never determine the app ID.
            # The ID comes directly from apps.json.
            # This prevents the previous problem where
            # many records were saved with app_id = 1.
            # ------------------------------------------------

            result_dict["app_id"] = app_id

            # Also keep the canonical application name.
            result_dict["app_name"] = app_name

            # ------------------------------------------------
            # PREVENT DUPLICATE RESULTS
            # ------------------------------------------------

            results = [
                existing
                for existing in results
                if existing.get("app_id") != app_id
            ]

            results.append(
                result_dict
            )

            completed_ids.add(
                app_id
            )

            # SAVE IMMEDIATELY.
            save_results(
                results
            )

            # Remove any previous failure for this app.
            failures = remove_failure_for_app(
                failures,
                app_id,
            )

            save_failures(
                failures
            )

            print(
                f"✓ Completed: "
                f"{app_name}"
            )

            print(
                f"  Auth: "
                f"{', '.join(result.auth_methods)}"
            )

            print(
                f"  Access: "
                f"{result.self_serve_status}"
            )

            print(
                f"  API: "
                f"{', '.join(result.api_type)}"
            )

            print(
                f"  MCP: "
                f"{result.mcp_available}"
            )

            print(
                f"  Agent ready: "
                f"{result.agent_ready}"
            )

            print(
                f"  Confidence: "
                f"{result.confidence}"
            )

            print(
                f"  Evidence: "
                f"{len(result.evidence)}"
            )

        except Exception as e:

            print(
                f"✗ Analysis failed: "
                f"{app_name}"
            )

            print(
                f"  Error: {e}"
            )

            # Avoid duplicate failure records.
            failures = [
                failure
                for failure in failures
                if failure.get("app_id") != app_id
            ]

            failures.append(
                {
                    "app_id": app_id,
                    "app_name": app_name,
                    "stage": "analysis",
                    "error": str(e),
                }
            )

            save_failures(
                failures
            )

            continue


        # ----------------------------------------------------
        # SMALL DELAY
        # ----------------------------------------------------

        time.sleep(2)


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print(
        "\n========================================"
    )

    print(
        "RESEARCH COMPLETE"
    )

    print(
        "========================================"
    )

    print(
        f"Successful: "
        f"{len(results)}"
    )

    print(
        f"Failures: "
        f"{len(failures)}"
    )

    print(
        f"Results saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        f"Failures saved to:"
    )

    print(
        FAILURE_FILE
    )

    print(
        "========================================"
    )


if __name__ == "__main__":

    main()
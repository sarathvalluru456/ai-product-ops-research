import json
from pathlib import Path
from copy import deepcopy


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

RESEARCH_FILE = DATA_DIR / "research_clean.json"
APPS_FILE = DATA_DIR / "apps.json"

BACKUP_FILE = DATA_DIR / "research_before_final_3_backup.json"


# ============================================================
# OFFICIAL EVIDENCE
# ============================================================

MISSING_APPS = {

    1: {
        "name": "Salesforce",

        "auth_methods": [
            "OAuth 2.0"
        ],

        "self_serve_status": "unknown",

        "api_type": [
            "REST",
            "SOAP",
            "GraphQL",
            "Bulk API"
        ],

        "mcp_available": "unclear",

        "agent_ready": "yes_with_setup",

        "confidence": "high",

        "main_blocker": "API access and permissions depend on the Salesforce edition and org configuration.",

        "evidence": [
            {
                "url": "https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/api_rest.pdf",
                "claim": "Salesforce provides a REST API for programmatic access to Salesforce data and documents OAuth 2.0 and connected-app based authorization."
            },
            {
                "url": "https://help.salesforce.com/s/articleView?id=integrate_what_is_api.htm&language=en_US",
                "claim": "Salesforce documents REST, SOAP, GraphQL, Bulk API, Metadata API, Tooling API and other API types."
            }
        ]
    },


    44: {
        "name": "Salesforce Commerce Cloud",

        "auth_methods": [
            "OAuth 2.1",
            "JWT"
        ],

        "self_serve_status": "unknown",

        "api_type": [
            "REST",
            "SCAPI",
            "SDK"
        ],

        "mcp_available": "yes",

        "agent_ready": "yes_with_setup",

        "confidence": "high",

        "main_blocker": "SCAPI access requires a B2C Commerce environment and appropriate API client configuration.",

        "evidence": [
            {
                "url": "https://developer.salesforce.com/docs/commerce/commerce-solutions/guide/scapi-get-started.html",
                "claim": "Salesforce Commerce Cloud SCAPI provides RESTful Shopper and Admin APIs for storefront, merchant and integration use cases."
            },
            {
                "url": "https://developer.salesforce.com/docs/commerce/commerce-api/guide/authorization.html",
                "claim": "SCAPI authorization uses OAuth 2.1 based client permissions and JWT access tokens."
            },
            {
                "url": "https://developer.salesforce.com/docs/commerce/commerce-solutions/guide/scapi-get-started.html",
                "claim": "Salesforce documents a B2C DX MCP Server as a developer-preview tool for exploring SCAPI from IDE AI assistants."
            }
        ]
    },


    52: {
        "name": "SE Ranking",

        "auth_methods": [
            "API Key"
        ],

        "self_serve_status": "self_serve",

        "api_type": [
            "REST"
        ],

        "mcp_available": "yes",

        "agent_ready": "yes_with_setup",

        "confidence": "high",

        "main_blocker": "API usage depends on the account plan, API credits and subscription limits.",

        "evidence": [
            {
                "url": "https://seranking.com/api/how-to-get-api/",
                "claim": "SE Ranking provides Data API and Project API access through a single API key generated from the API Dashboard."
            },
            {
                "url": "https://seranking.com/api/data/getting-started/",
                "claim": "SE Ranking Data API requests require an API key and support authentication through the Authorization header."
            },
            {
                "url": "https://help.seranking.com/hc/en-us/sections/21701343953180-API",
                "claim": "SE Ranking provides API documentation and a documented SE Ranking MCP Server resource."
            }
        ]
    }
}


# ============================================================
# LOAD
# ============================================================

def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# SAVE
# ============================================================

def save_json(path, data):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# FIND APP
# ============================================================

def find_app(apps, app_id):

    for app in apps:

        if app.get("id") == app_id:

            return app

    return None


# ============================================================
# CREATE RESULT
# ============================================================

def create_result(app, info, template):

    result = deepcopy(template)

    # --------------------------------------------------------
    # Basic fields
    # --------------------------------------------------------

    result["app_id"] = app["id"]

    result["app_name"] = app["name"]

    # --------------------------------------------------------
    # Known research fields
    # --------------------------------------------------------

    fields = [
        "auth_methods",
        "self_serve_status",
        "api_type",
        "mcp_available",
        "agent_ready",
        "confidence",
        "main_blocker",
    ]

    for field in fields:

        if field in result or field in info:

            result[field] = deepcopy(
                info[field]
            )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    if "evidence" in result:

        result["evidence"] = deepcopy(
            info["evidence"]
        )

    # --------------------------------------------------------
    # Handle possible alternate blocker field names
    # --------------------------------------------------------

    alternate_blocker_fields = [
        "blocker",
        "main_blocker",
        "primary_blocker",
        "access_blocker",
    ]

    for field in alternate_blocker_fields:

        if field in result:

            result[field] = info["main_blocker"]

    # --------------------------------------------------------
    # Handle possible name fields
    # --------------------------------------------------------

    for field in [
        "name",
        "application_name",
    ]:

        if field in result:

            result[field] = app["name"]

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("========================================")
    print("FINAL 3 APP RESEARCH REPAIR")
    print("========================================")

    if not RESEARCH_FILE.exists():

        print("ERROR: research_clean.json not found")
        print(RESEARCH_FILE)
        return

    if not APPS_FILE.exists():

        print("ERROR: apps.json not found")
        print(APPS_FILE)
        return

    research = load_json(
        RESEARCH_FILE
    )

    apps = load_json(
        APPS_FILE
    )

    print(
        f"Current results: {len(research)}"
    )

    # --------------------------------------------------------
    # Backup
    # --------------------------------------------------------

    save_json(
        BACKUP_FILE,
        research
    )

    print()
    print("Backup created:")
    print(BACKUP_FILE)

    # --------------------------------------------------------
    # Existing IDs
    # --------------------------------------------------------

    existing_ids = {
        item.get("app_id")
        for item in research
        if item.get("app_id") is not None
    }

    missing = [
        app_id
        for app_id in MISSING_APPS
        if app_id not in existing_ids
    ]

    print()
    print(
        f"Missing apps to add: {len(missing)}"
    )

    # --------------------------------------------------------
    # Use an existing valid result as structure template
    # --------------------------------------------------------

    if not research:

        print(
            "ERROR: research_clean.json is empty."
        )

        return

    template = research[0]

    # --------------------------------------------------------
    # Add missing apps
    # --------------------------------------------------------

    for app_id in missing:

        app = find_app(
            apps,
            app_id
        )

        if not app:

            print(
                f"ERROR: App ID {app_id} "
                f"not found in apps.json"
            )

            continue

        info = MISSING_APPS[app_id]

        result = create_result(
            app,
            info,
            template
        )

        research.append(
            result
        )

        print()
        print(
            f"Added: {app['name']} "
            f"(ID {app_id})"
        )

    # --------------------------------------------------------
    # Remove duplicate IDs
    # --------------------------------------------------------

    unique = {}

    for item in research:

        app_id = item.get("app_id")

        if app_id is None:
            continue

        if app_id not in unique:

            unique[app_id] = item

    research = list(
        unique.values()
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    research.sort(
        key=lambda x: x["app_id"]
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_json(
        RESEARCH_FILE,
        research
    )

    # --------------------------------------------------------
    # Verify
    # --------------------------------------------------------

    expected_ids = {
        app["id"]
        for app in apps
    }

    actual_ids = {
        item["app_id"]
        for item in research
    }

    missing_ids = sorted(
        expected_ids - actual_ids
    )

    extra_ids = sorted(
        actual_ids - expected_ids
    )

    print()
    print("========================================")
    print("FINAL VERIFICATION")
    print("========================================")

    print(
        f"Results: {len(research)}"
    )

    print(
        f"Expected apps: {len(apps)}"
    )

    print()
    print(
        f"Missing IDs: {missing_ids}"
    )

    print(
        f"Extra IDs: {extra_ids}"
    )

    if len(research) == len(apps) and not missing_ids:

        print()
        print("SUCCESS: 100/100 COMPLETE")

    else:

        print()
        print("WARNING: Results are not yet 100/100")

    print()
    print("Saved:")
    print(RESEARCH_FILE)

    print("========================================")


if __name__ == "__main__":

    main()
import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent
RESEARCH_FILE = BASE_DIR / "data" / "research_clean.json"
ANALYSIS_FILE = BASE_DIR / "data" / "analysis.json"


def count_list_field(records, field):
    counter = Counter()

    for item in records:
        values = item.get(field, [])

        if isinstance(values, list):
            for value in values:
                if value:
                    counter[str(value)] += 1
        elif values:
            counter[str(values)] += 1

    return counter


def count_field(records, field):
    counter = Counter()

    for item in records:
        value = item.get(field)

        if value is None or value == "":
            value = "unknown"

        counter[str(value)] += 1

    return counter


def main():

    print("=" * 50)
    print("AI PRODUCT OPS RESEARCH ANALYSIS")
    print("=" * 50)

    with open(RESEARCH_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"\nTotal apps: {len(records)}")

    # --------------------------------------------------
    # CATEGORY
    # --------------------------------------------------

    categories = count_field(records, "category")

    print("\nCATEGORIES")
    for name, count in categories.most_common():
        print(f"  {name}: {count}")

    # --------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------

    auth = count_list_field(records, "auth_methods")

    print("\nAUTH METHODS")
    for name, count in auth.most_common():
        print(f"  {name}: {count}")

    # --------------------------------------------------
    # SELF SERVE
    # --------------------------------------------------

    self_serve = count_field(
        records,
        "self_serve_status"
    )

    print("\nSELF-SERVE / ACCESS")
    for name, count in self_serve.most_common():
        print(f"  {name}: {count}")

    # --------------------------------------------------
    # API TYPE
    # --------------------------------------------------

    api_types = count_list_field(
        records,
        "api_type"
    )

    print("\nAPI TYPES")
    for name, count in api_types.most_common():
        print(f"  {name}: {count}")

    # --------------------------------------------------
    # API BREADTH
    # --------------------------------------------------

    api_breadth = count_field(
        records,
        "api_breadth"
    )

    print("\nAPI BREADTH")
    for name, count in api_breadth.most_common():
        print(f"  {name}: {count}")

    # --------------------------------------------------
    # MCP
    # --------------------------------------------------

    mcp = count_field(
        records,
        "mcp_available"
    )

    print("\nMCP AVAILABILITY")
    for name, count in mcp.most_common():
        print(f"  {name}: {count}")

    # --------------------------------------------------
    # AGENT READINESS
    # --------------------------------------------------

    agent_ready = count_field(
        records,
        "agent_ready"
    )

    print("\nAGENT READINESS")
    for name, count in agent_ready.most_common():
        print(f"  {name}: {count}")

    # --------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------

    confidence = count_field(
        records,
        "confidence"
    )

    print("\nCONFIDENCE")
    for name, count in confidence.most_common():
        print(f"  {name}: {count}")

    # --------------------------------------------------
    # MAIN BLOCKERS
    # --------------------------------------------------

    blockers = Counter()

    for item in records:
        blocker = item.get("main_blocker")

        if blocker:
            blockers[str(blocker)] += 1

    print("\nTOP BLOCKERS")

    for blocker, count in blockers.most_common(15):
        print(f"  {count}: {blocker}")

    # --------------------------------------------------
    # EASY WINS
    # --------------------------------------------------

    easy_wins = []

    for item in records:

        agent = str(
            item.get("agent_ready", "")
        ).lower()

        confidence_value = str(
            item.get("confidence", "")
        ).lower()

        if (
            agent == "yes"
            and confidence_value in ["high", "medium"]
        ):
            easy_wins.append(
                {
                    "id": item.get("app_id"),
                    "name": item.get("app_name"),
                    "category": item.get("category"),
                    "auth": item.get("auth_methods"),
                    "api": item.get("api_type"),
                    "mcp": item.get("mcp_available"),
                    "confidence": item.get("confidence"),
                }
            )

    # --------------------------------------------------
    # NEEDS SETUP / BLOCKED
    # --------------------------------------------------

    needs_setup = []

    for item in records:

        agent = str(
            item.get("agent_ready", "")
        ).lower()

        if agent != "yes":
            needs_setup.append(
                {
                    "id": item.get("app_id"),
                    "name": item.get("app_name"),
                    "agent_ready": item.get(
                        "agent_ready"
                    ),
                    "blocker": item.get(
                        "main_blocker"
                    ),
                }
            )

    # --------------------------------------------------
    # SAVE ANALYSIS
    # --------------------------------------------------

    analysis = {
        "total_apps": len(records),

        "categories": dict(
            categories
        ),

        "auth_methods": dict(
            auth
        ),

        "self_serve_status": dict(
            self_serve
        ),

        "api_types": dict(
            api_types
        ),

        "api_breadth": dict(
            api_breadth
        ),

        "mcp_available": dict(
            mcp
        ),

        "agent_ready": dict(
            agent_ready
        ),

        "confidence": dict(
            confidence
        ),

        "top_blockers": [
            {
                "blocker": blocker,
                "count": count
            }
            for blocker, count
            in blockers.most_common(15)
        ],

        "easy_wins": easy_wins,

        "needs_setup_or_blocked": needs_setup,
    }

    with open(
        ANALYSIS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            analysis,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE")
    print("=" * 50)

    print(
        f"Easy wins: {len(easy_wins)}"
    )

    print(
        f"Needs setup / blocked: "
        f"{len(needs_setup)}"
    )

    print(
        f"\nSaved:\n{ANALYSIS_FILE}"
    )


if __name__ == "__main__":
    main()
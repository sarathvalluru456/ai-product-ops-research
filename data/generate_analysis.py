import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent
INPUT = BASE_DIR / "data" / "research_clean.json"
OUTPUT = BASE_DIR / "data" / "analysis.json"


def values(data, key):
    result = []

    for item in data:
        value = item.get(key)

        if isinstance(value, list):
            result.extend(str(x) for x in value)
        elif value:
            result.append(str(value))

    return result


def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("=" * 50)
    print("AI PRODUCT OPS RESEARCH ANALYSIS")
    print("=" * 50)

    print(f"\nTotal apps: {len(data)}")

    auth = Counter(values(data, "auth_methods"))
    access = Counter(values(data, "access"))
    api = Counter(values(data, "api_surface"))
    mcp = Counter(values(data, "mcp"))
    verdict = Counter(values(data, "buildability"))

    analysis = {
        "total_apps": len(data),
        "auth_methods": dict(auth),
        "access": dict(access),
        "api_surface": dict(api),
        "mcp": dict(mcp),
        "buildability": dict(verdict),
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(
            analysis,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("\nAUTH METHODS")
    for key, value in auth.most_common():
        print(f"  {key}: {value}")

    print("\nACCESS")
    for key, value in access.most_common():
        print(f"  {key}: {value}")

    print("\nAPI SURFACE")
    for key, value in api.most_common():
        print(f"  {key}: {value}")

    print("\nMCP")
    for key, value in mcp.most_common():
        print(f"  {key}: {value}")

    print("\nBUILDABILITY")
    for key, value in verdict.most_common():
        print(f"  {key}: {value}")

    print("\nSaved:")
    print(OUTPUT)


if __name__ == "__main__":
    main()
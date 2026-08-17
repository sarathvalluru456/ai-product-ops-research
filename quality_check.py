import json
from collections import Counter

with open("data/research.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 60)
print("AI PRODUCT OPS — DATA QUALITY CHECK")
print("=" * 60)

print(f"\nTotal records: {len(data)}")

# ---------------------------------------------------------
# 1. Check cross-app references
# ---------------------------------------------------------

app_names = [x["app_name"] for x in data]

print("\n" + "=" * 60)
print("POTENTIAL CROSS-APP REFERENCES")
print("=" * 60)

cross_app = []

for item in data:
    text = (
        str(item.get("buildability_reason", "")) + " " +
        str(item.get("research_notes", ""))
    ).lower()

    current_app = item["app_name"].lower()

    for other_app in app_names:
        if other_app.lower() == current_app:
            continue

        if other_app.lower() in text:
            cross_app.append(
                (
                    item["app_id"],
                    item["app_name"],
                    other_app
                )
            )

            print(
                f'{item["app_id"]}. {item["app_name"]} '
                f'→ mentions "{other_app}"'
            )

print(f"\nPotential cross-app references: {len(cross_app)}")


# ---------------------------------------------------------
# 2. Distribution checks
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("FIELD DISTRIBUTIONS")
print("=" * 60)

print("\nSelf-serve status:")
print(Counter(x.get("self_serve_status") for x in data))

print("\nMCP availability:")
print(Counter(x.get("mcp_available") for x in data))

print("\nAgent readiness:")
print(Counter(x.get("agent_ready") for x in data))

print("\nConfidence:")
print(Counter(x.get("confidence") for x in data))


# ---------------------------------------------------------
# 3. Missing evidence
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("MISSING EVIDENCE")
print("=" * 60)

missing_evidence = [
    x for x in data
    if not x.get("evidence")
]

print(f"Apps without evidence: {len(missing_evidence)}")

for x in missing_evidence:
    print(f'{x["app_id"]}. {x["app_name"]}')


# ---------------------------------------------------------
# 4. Missing important fields
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("MISSING IMPORTANT FIELDS")
print("=" * 60)

fields = [
    "category",
    "description",
    "auth_methods",
    "self_serve_status",
    "credential_access",
    "api_type",
    "api_breadth",
    "mcp_available",
    "agent_ready",
    "main_blocker",
    "buildability_reason",
    "evidence",
    "confidence",
]

for field in fields:
    missing = sum(
        1 for x in data
        if not x.get(field)
    )

    print(f"{field:25} {missing}")


# ---------------------------------------------------------
# 5. Low-confidence records
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("LOW-CONFIDENCE RECORDS")
print("=" * 60)

low_confidence = [
    x for x in data
    if str(x.get("confidence", "")).lower()
    in ["low", "medium"]
]

print(f"Low/medium confidence: {len(low_confidence)}")

for x in low_confidence:
    print(
        f'{x["app_id"]}. {x["app_name"]} '
        f'→ {x.get("confidence")}'
    )


print("\n" + "=" * 60)
print("QUALITY CHECK COMPLETE")
print("=" * 60)
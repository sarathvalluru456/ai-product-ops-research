import json

with open("data/research.json", "r", encoding="utf-8") as f:
    data = json.load(f)

categories = {}

for app in data:
    categories.setdefault(app["category"], []).append(app)

print("=" * 80)
print("20-APP HUMAN VERIFICATION SAMPLE")
print("=" * 80)

sample = []

for category, apps in categories.items():
    selected = apps[:2]

    print(f"\n### {category}")

    for app in selected:
        sample.append(app)

        print(f'\n{app["app_id"]}. {app["app_name"]}')
        print(f'Category: {app["category"]}')
        print(f'Auth: {app.get("auth_methods")}')
        print(f'Self-serve: {app.get("self_serve_status")}')
        print(f'API: {app.get("api_type")}')
        print(f'MCP: {app.get("mcp_available")}')
        print(f'Ready: {app.get("agent_ready")}')
        print(f'Confidence: {app.get("confidence")}')

        print("Evidence:")
        for evidence in app.get("evidence", []):
            print(f'  {evidence.get("url")}')

print("\n" + "=" * 80)
print(f"TOTAL SAMPLE: {len(sample)}")
print("=" * 80)
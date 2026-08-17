import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

RESEARCH_FILE = BASE_DIR / "data" / "research.json"
APPS_FILE = BASE_DIR / "data" / "apps.json"

BACKUP_FILE = BASE_DIR / "data" / "research_backup.json"
CLEAN_FILE = BASE_DIR / "data" / "research_clean.json"


def main():

    print("========================================")
    print("RESEARCH RESULTS REPAIR TOOL")
    print("========================================")

    if not RESEARCH_FILE.exists():
        print("ERROR: research.json not found")
        return

    if not APPS_FILE.exists():
        print("ERROR: apps.json not found")
        return

    with open(RESEARCH_FILE, "r", encoding="utf-8") as f:
        research = json.load(f)

    with open(APPS_FILE, "r", encoding="utf-8") as f:
        apps = json.load(f)

    print(f"Research records found: {len(research)}")
    print(f"Apps in apps.json: {len(apps)}")

    # Backup original
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(research, f, indent=2, ensure_ascii=False)

    print(f"Backup created: {BACKUP_FILE}")

    # Map expected apps
    expected_by_id = {
        app["id"]: app
        for app in apps
    }

    expected_by_name = {
        app["name"].strip().lower(): app
        for app in apps
    }

    valid = []

    print()
    print("Checking records...")

    for item in research:

        app_name = str(
            item.get("app_name", "")
        ).strip()

        if not app_name:
            continue

        matching_app = expected_by_name.get(
            app_name.lower()
        )

        if not matching_app:
            print(
                f"Unknown app skipped: {app_name}"
            )
            continue

        correct_id = matching_app["id"]

        if item.get("app_id") != correct_id:

            print(
                f"Fixing ID: {app_name} "
                f"{item.get('app_id')} -> {correct_id}"
            )

        item["app_id"] = correct_id

        valid.append(item)

    # Remove duplicates
    print()
    print("Removing duplicates...")

    unique = {}

    for item in valid:

        app_id = item["app_id"]

        if app_id not in unique:

            unique[app_id] = item

        else:

            print(
                f"Duplicate removed: "
                f"{item['app_name']} "
                f"(ID {app_id})"
            )

    clean_results = list(
        unique.values()
    )

    clean_results.sort(
        key=lambda x: x["app_id"]
    )

    # Find missing
    completed_ids = {
        item["app_id"]
        for item in clean_results
    }

    expected_ids = set(
        expected_by_id.keys()
    )

    missing_ids = sorted(
        expected_ids - completed_ids
    )

    # Save cleaned results
    with open(
        CLEAN_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            clean_results,
            f,
            indent=2,
            ensure_ascii=False
        )

    # Summary
    print()
    print("========================================")
    print("REPAIR COMPLETE")
    print("========================================")

    print(
        f"Original records: {len(research)}"
    )

    print(
        f"Valid records: {len(valid)}"
    )

    print(
        f"Unique results: {len(clean_results)}"
    )

    print(
        f"Duplicates removed: "
        f"{len(valid) - len(clean_results)}"
    )

    print(
        f"Missing apps: {len(missing_ids)}"
    )

    print()
    print("Missing apps:")

    if missing_ids:

        for app_id in missing_ids:

            print(
                f"  {app_id}: "
                f"{expected_by_id[app_id]['name']}"
            )

    else:

        print("  None")

    print()
    print("Clean file:")
    print(CLEAN_FILE)

    print()
    print("Backup file:")
    print(BACKUP_FILE)

    print("========================================")


if __name__ == "__main__":
    main()
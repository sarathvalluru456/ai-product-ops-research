import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

RESEARCH_FILE = BASE_DIR / "data" / "research.json"
APPS_FILE = BASE_DIR / "data" / "apps.json"

BACKUP_FILE = BASE_DIR / "data" / "research_backup.json"
CLEAN_FILE = BASE_DIR / "data" / "research_clean.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():

    print()
    print("========================================")
    print("RESEARCH RESULTS REPAIR TOOL")
    print("========================================")

    # Check files
    if not RESEARCH_FILE.exists():
        print("ERROR: research.json not found")
        print(RESEARCH_FILE)
        return

    if not APPS_FILE.exists():
        print("ERROR: apps.json not found")
        print(APPS_FILE)
        return

    # Load files
    research = load_json(RESEARCH_FILE)
    apps = load_json(APPS_FILE)

    print(f"Research records found: {len(research)}")
    print(f"Apps in apps.json: {len(apps)}")

    # Backup original
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(
            research,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Backup created:")
    print(BACKUP_FILE)

    # Expected apps
    expected_by_id = {
        app["id"]: app
        for app in apps
    }

    # Match results by app name
    valid = []
    invalid = []

    for index, item in enumerate(research, start=1):

        app_name = item.get("app_name")

        if not app_name:
            invalid.append(item)
            continue

        matching_app = None

        for app in apps:

            if (
                app["name"].strip().lower()
                == str(app_name).strip().lower()
            ):
                matching_app = app
                break

        if matching_app:

            correct_id = matching_app["id"]

            if item.get("app_id") != correct_id:

                print(
                    f"Fixing ID: {app_name} "
                    f"{item.get('app_id')} -> {correct_id}"
                )

            item["app_id"] = correct_id

            valid.append(item)

        else:

            print(
                f"Unknown app ignored: {app_name}"
            )

            invalid.append(item)

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
                f"{item.get('app_name')} "
                f"(ID {app_id})"
            )

    clean_results = list(unique.values())

    # Sort
    clean_results.sort(
        key=lambda x: x["app_id"]
    )

    # Find missing apps
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

    # Save clean file
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
        f"Invalid records: {len(invalid)}"
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
    print("Clean results saved to:")
    print(CLEAN_FILE)

    print()
    print("Original backup saved to:")
    print(BACKUP_FILE)

    print("========================================")


if __name__ == "__main__":
    main()
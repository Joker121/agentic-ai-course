"""Validate all A2A Agent Card JSON files against the expected schema."""

import json
import os
import sys
from pathlib import Path

AGENT_CARDS_DIR = Path(__file__).parent.parent / "modules" / "m5-a2a" / "agent-cards"

REQUIRED_FIELDS = [
    "name",
    "version",
    "description",
    "endpoint",
    "capabilities",
    "input_schema",
    "output_schema",
    "authentication",
    "owner",
]

REQUIRED_CAPABILITIES = {
    "orchestrator": ["task-routing", "load-balancing"],
    "researcher-a2a": ["web-search", "document-analysis"],
    "writer-a2a": ["content-generation", "style-adaptation"],
}


def validate_card(card_path: Path) -> tuple[bool, list[str]]:
    """Validate a single Agent Card file."""
    errors = []

    try:
        with open(card_path) as f:
            card = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return False, [f"Failed to parse: {e}"]

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in card:
            errors.append(f"Missing required field: {field}")

    # Check capabilities match expected
    name = card.get("name", "")
    expected_caps = REQUIRED_CAPABILITIES.get(name, [])
    for cap in expected_caps:
        if cap not in card.get("capabilities", []):
            errors.append(f"Missing expected capability '{cap}' for {name}")

    # Check input_schema has type and properties
    input_schema = card.get("input_schema", {})
    if "type" not in input_schema:
        errors.append(f"input_schema missing 'type' for {name}")
    if "properties" not in input_schema:
        errors.append(f"input_schema missing 'properties' for {name}")

    # Check output_schema
    output_schema = card.get("output_schema", {})
    if "type" not in output_schema:
        errors.append(f"output_schema missing 'type' for {name}")

    # Check endpoint format
    endpoint = card.get("endpoint", "")
    if not endpoint.startswith("http"):
        errors.append(f"Invalid endpoint format for {name}: {endpoint}")

    return len(errors) == 0, errors


def main():
    print("🔍 Validating A2A Agent Cards...")
    print("=" * 60)

    all_valid = True
    card_files = sorted(AGENT_CARDS_DIR.glob("*.json"))

    if not card_files:
        print("❌ No agent card files found!")
        sys.exit(1)

    for card_path in card_files:
        valid, errors = validate_card(card_path)
        status = "✅" if valid else "❌"
        print(f"\n{status} {card_path.name}")
        for error in errors:
            print(f"   - {error}")
        if not valid:
            all_valid = False

    print("\n" + "=" * 60)
    if all_valid:
        print("✅ All Agent Cards are valid!")
        sys.exit(0)
    else:
        print("❌ Some Agent Cards have validation errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path

from skillopt.datasets.base import SplitDataLoader


REQUIRED_FIELDS = [
    "id",
    "platform",
    "brand",
    "target_audience",
    "objective",
    "topic",
    "brand_tone",
    "ground_truth_checks",
]


def _normalize(raw: dict) -> dict:
    missing = [key for key in REQUIRED_FIELDS if key not in raw]
    if missing:
        raise ValueError(f"Dataset item missing required fields: {missing}")

    return {
        "id": str(raw["id"]),
        "platform": str(raw["platform"]),
        "brand": str(raw["brand"]),
        "target_audience": str(raw["target_audience"]),
        "objective": str(raw["objective"]),
        "topic": str(raw["topic"]),
        "brand_tone": str(raw["brand_tone"]),
        "constraints": list(raw.get("constraints", [])),
        "task_type": str(raw.get("task_type", "social_strategy")),
        "ground_truth_checks": dict(raw["ground_truth_checks"]),
    }


class SocialMediaDataLoader(SplitDataLoader):
    """Load social media benchmark items from split-specific JSONL files."""

    def load_split_items(self, split_path: str) -> list[dict]:
        path = Path(split_path) / "items.jsonl"

        if not path.exists():
            raise FileNotFoundError(f"Expected {path}")

        items: list[dict] = []

        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                try:
                    raw = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON on line {line_number} of {path}"
                    ) from exc

                items.append(_normalize(raw))

        if not items:
            raise ValueError(f"No items found in {path}")

        ids = [item["id"] for item in items]

        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate IDs detected in {path}")

        return items
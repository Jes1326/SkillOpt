"""Dataloader for Test Data Generator environment."""
from __future__ import annotations

import json
import os

from skillopt.datasets.base import SplitDataLoader


class TestDataGenDataLoader(SplitDataLoader):

    def load_split_items(self, split_path: str) -> list[dict]:
        path = os.path.join(split_path, "items.jsonl")
        if not os.path.exists(path):
            return []
        items = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
        return items

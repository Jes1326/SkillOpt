#!/usr/bin/env python3
"""Generate a before/after benchmark report for a social_media SkillOpt run.

Usage
-----
    python scripts/social_media_report.py --out_root outputs/skillopt_social_media_gpt-4o_YYYYMMDD_HHMMSS
    python scripts/social_media_report.py --out_root outputs/... --split val
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path


def _load_rollouts(out_root: str, split: str) -> list[dict]:
    root = Path(out_root)
    records: list[dict] = []
    # Step-level rollouts (train split)
    for step_dir in sorted(root.glob("steps/step_*")):
        step_num = int(step_dir.name.split("_")[1])
        rollouts_file = step_dir / "rollout" / "rollouts.json"
        if rollouts_file.exists():
            with open(rollouts_file, encoding="utf-8") as f:
                for item in json.load(f):
                    item["_epoch"] = (step_num - 1) // 3 + 1  # 3 steps/epoch
                    item["_step"] = step_num
                    records.append(item)
    # Val/test evals
    for eval_dir_name in ("final_selection_eval", "selection_eval_baseline", "test_eval", "test_eval_baseline"):
        rollouts_file = root / eval_dir_name / "rollouts.json"
        if rollouts_file.exists() and split in eval_dir_name:
            with open(rollouts_file, encoding="utf-8") as f:
                for item in json.load(f):
                    item["_epoch"] = 0 if "baseline" in eval_dir_name else 99
                    records.append(item)
    return records


def _epoch0_scores(out_root: str, split: str) -> dict[str, float]:
    root = Path(out_root)
    rollouts_file = root / "selection_eval_baseline" / "rollouts.json"
    if rollouts_file.exists():
        with open(rollouts_file, encoding="utf-8") as f:
            return {r["id"]: r.get("hard", 0) for r in json.load(f)}
    # Fall back to first step
    for step_dir in sorted(root.glob("steps/step_*")):
        rollouts_file = step_dir / "rollout" / "rollouts.json"
        if rollouts_file.exists():
            with open(rollouts_file, encoding="utf-8") as f:
                return {r["id"]: r.get("hard", 0) for r in json.load(f)}
    return {}



def _last_epoch_scores(records: list[dict]) -> dict[str, float]:
    """Return {item_id: hard_score} from the highest epoch seen."""
    by_id: dict[str, dict] = {}
    for r in records:
        prev = by_id.get(r["id"])
        if prev is None or r["_epoch"] > prev["_epoch"]:
            by_id[r["id"]] = r
    return {k: v.get("hard", 0) for k, v in by_id.items()}


def _epoch_progression(records: list[dict]) -> dict[int, float]:
    """Return {epoch: mean_hard} across all items."""
    by_epoch: dict[int, list[float]] = defaultdict(list)
    for r in records:
        by_epoch[r["_epoch"]].append(r.get("hard", 0))
    return {e: sum(v) / len(v) for e, v in sorted(by_epoch.items())}


def _per_platform(records: list[dict]) -> dict[str, dict]:
    """Return {platform: {epoch: mean_hard}} grouped by item metadata."""
    by_platform: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in records:
        platform = (r.get("metadata") or {}).get("platform", "unknown")
        by_platform[platform][r["_epoch"]].append(r.get("hard", 0))
    return {
        p: {e: sum(v) / len(v) for e, v in sorted(epochs.items())}
        for p, epochs in by_platform.items()
    }


def _per_check(records: list[dict]) -> dict[str, float]:
    """Return {check_name: pass_rate} across the last epoch only."""
    last_epoch = max((r["_epoch"] for r in records), default=0)
    last = [r for r in records if r["_epoch"] == last_epoch]
    check_counts: dict[str, list[int]] = defaultdict(list)
    for r in last:
        for check, passed in (r.get("checks") or {}).items():
            check_counts[check].append(int(bool(passed)))
    return {c: sum(v) / len(v) for c, v in check_counts.items()}


def _fmt_pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def build_report(out_root: str, split: str) -> dict:
    records = _load_rollouts(out_root, split)
    if not records:
        print(f"[warn] No rollouts found under {out_root} for split={split}", file=sys.stderr)
        return {}

    before = _epoch0_scores(out_root, split)
    after = _last_epoch_scores(records)
    progression = _epoch_progression(records)
    per_platform = _per_platform(records)
    per_check = _per_check(records)

    all_ids = sorted(set(before) | set(after))
    before_mean = sum(before.get(i, 0) for i in all_ids) / max(len(all_ids), 1)
    after_mean = sum(after.get(i, 0) for i in all_ids) / max(len(all_ids), 1)

    return {
        "split": split,
        "n_items": len(all_ids),
        "before_mean": before_mean,
        "after_mean": after_mean,
        "delta": after_mean - before_mean,
        "epoch_progression": progression,
        "per_platform": per_platform,
        "per_check_pass_rate": per_check,
        "per_item": {i: {"before": before.get(i, 0), "after": after.get(i, 0)} for i in all_ids},
    }


def print_report(report: dict) -> None:
    if not report:
        return
    print(f"\n{'='*60}")
    print(f"  Social Media Benchmark Report  (split={report['split']})")
    print(f"{'='*60}")
    print(f"  Items:   {report['n_items']}")
    print(f"  Before:  {_fmt_pct(report['before_mean'])}")
    print(f"  After:   {_fmt_pct(report['after_mean'])}")
    delta = report['delta']
    sign = "+" if delta >= 0 else ""
    print(f"  Delta:   {sign}{_fmt_pct(delta)}")

    print(f"\n  Epoch progression:")
    for epoch, score in report["epoch_progression"].items():
        print(f"    epoch {epoch:>2}: {_fmt_pct(score)}")

    print(f"\n  Per-platform (final epoch):")
    for platform, epochs in sorted(report["per_platform"].items()):
        last_score = list(epochs.values())[-1] if epochs else 0
        print(f"    {platform:<15} {_fmt_pct(last_score)}")

    print(f"\n  Per-check pass rate (final epoch):")
    for check, rate in sorted(report["per_check_pass_rate"].items(), key=lambda x: x[1]):
        bar = "█" * int(rate * 20)
        print(f"    {check:<40} {_fmt_pct(rate):>6}  {bar}")

    print(f"\n  Per-item before → after:")
    for item_id, scores in sorted(report["per_item"].items()):
        arrow = "✓" if scores["after"] >= scores["before"] else "✗"
        print(f"    {arrow} {item_id:<45} {_fmt_pct(scores['before'])} → {_fmt_pct(scores['after'])}")
    print()


def write_markdown(report: dict, path: str) -> None:
    lines = [
        "# Social Media Benchmark Report",
        "",
        f"**Split**: `{report['split']}`  |  **Items**: {report['n_items']}",
        "",
        f"| Metric | Score |",
        f"|--------|-------|",
        f"| Before (epoch 0) | {_fmt_pct(report['before_mean'])} |",
        f"| After (final epoch) | {_fmt_pct(report['after_mean'])} |",
        f"| Delta | {'+' if report['delta'] >= 0 else ''}{_fmt_pct(report['delta'])} |",
        "",
        "## Epoch Progression",
        "",
        "| Epoch | Hard Score |",
        "|-------|-----------|",
    ]
    for epoch, score in report["epoch_progression"].items():
        lines.append(f"| {epoch} | {_fmt_pct(score)} |")

    lines += ["", "## Per-Platform (Final Epoch)", "", "| Platform | Hard Score |", "|----------|-----------|"]
    for platform, epochs in sorted(report["per_platform"].items()):
        last_score = list(epochs.values())[-1] if epochs else 0
        lines.append(f"| {platform} | {_fmt_pct(last_score)} |")

    lines += ["", "## Per-Check Pass Rate (Final Epoch)", "", "| Check | Pass Rate |", "|-------|----------|"]
    for check, rate in sorted(report["per_check_pass_rate"].items(), key=lambda x: x[1]):
        lines.append(f"| `{check}` | {_fmt_pct(rate)} |")

    lines += ["", "## Per-Item Results", "", "| Item | Before | After |", "|------|--------|-------|"]
    for item_id, scores in sorted(report["per_item"].items()):
        lines.append(f"| `{item_id}` | {_fmt_pct(scores['before'])} | {_fmt_pct(scores['after'])} |")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Social Media SkillOpt benchmark report")
    p.add_argument("--out_root", required=True, help="Path to SkillOpt output directory")
    p.add_argument("--split", default="val", choices=["train", "val", "test"])
    args = p.parse_args()

    report = build_report(args.out_root, args.split)
    if not report:
        sys.exit(1)

    print_report(report)

    report_json = os.path.join(args.out_root, "report.json")
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"  Saved: {report_json}")

    report_md = os.path.join(args.out_root, "report.md")
    write_markdown(report, report_md)
    print(f"  Saved: {report_md}\n")


if __name__ == "__main__":
    main()

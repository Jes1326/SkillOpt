from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from skillopt.model import chat_target
from skillopt.prompts import load_prompt

from .evaluator import evaluate_prediction


def _build_user_prompt(item: dict) -> str:
    constraints = item.get("constraints") or []

    constraint_text = (
        "\n".join(
            f"- {constraint}"
            for constraint in constraints
        )
        if constraints
        else "- None"
    )

    return f"""
Create a social media content strategy for this brief.

PLATFORM:
{item["platform"]}

BRAND:
{item["brand"]}

TARGET AUDIENCE:
{item["target_audience"]}

OBJECTIVE:
{item["objective"]}

TOPIC:
{item["topic"]}

BRAND TONE:
{item["brand_tone"]}

CONSTRAINTS:
{constraint_text}

Return ONLY one valid JSON object.
Do not use Markdown.
Do not use ``` fences.
""".strip()


def _run_one(
    item: dict,
    skill_content: str,
    *,
    prediction_dir: Path,
    max_completion_tokens: int,
) -> dict:

    rollout_wrapper = load_prompt(
        "rollout_system",
        env="social_media",
    )

    system = (
        f"{rollout_wrapper.rstrip()}\n\n"
        f"--- EVOLVING SKILL ---\n"
        f"{skill_content.strip()}"
    )

    user = _build_user_prompt(item)

    try:

        prediction, usage = chat_target(
            system=system,
            user=user,
            max_completion_tokens=max_completion_tokens,
        )

        prediction = prediction or ""
        usage_dict = (
            usage
            if isinstance(usage, dict)
            else {}
        )

        evaluation = evaluate_prediction(
            prediction,
            item["ground_truth_checks"],
        )

        hard = evaluation.hard
        soft = evaluation.soft
        fail_reason = evaluation.fail_reason

    except Exception as exc:

        prediction = ""
        usage_dict = {}

        hard = 0
        soft = 0.0

        evaluation = None

        fail_reason = (
            f"target_model_error:"
            f"{type(exc).__name__}:"
            f"{exc}"
        )

    # ---------------------------------------------------------
    # Mandatory trajectory persistence
    # ---------------------------------------------------------

    task_dir = prediction_dir / str(item["id"])

    task_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    conversation = [
        {
            "role": "system",
            "content": system,
        },
        {
            "role": "user",
            "content": user,
        },
        {
            "role": "assistant",
            "content": prediction,
        },
    ]

    (
        task_dir / "conversation.json"
    ).write_text(
        json.dumps(
            conversation,
            ensure_ascii=True,
            indent=2,
        ),
        encoding="utf-8",
    )

    result = {
        "id": str(item["id"]),
        "hard": hard,
        "soft": soft,
        "predicted_answer": prediction,
        "task_type": item.get(
            "task_type",
            "social_strategy",
        ),
        "task_description": item["topic"],
        "target_system_prompt": system,
        "target_user_prompt": user,
        "fail_reason": fail_reason,
        "platform": item["platform"],
        "objective": item["objective"],
        "ground_truth_checks": item[
            "ground_truth_checks"
        ],
        "usage": usage_dict,
    }

    if evaluation is not None:

        result["failed_checks"] = (
            evaluation.fail_reasons
        )

        result["passed_checks"] = (
            evaluation.passed_checks
        )

    return result


def run_batch(
    *,
    items: list[dict],
    skill_content: str,
    out_root: str,
    workers: int = 4,
    max_completion_tokens: int = 4096,
) -> list[dict]:

    os.makedirs(
        out_root,
        exist_ok=True,
    )

    prediction_dir = (
        Path(out_root) / "predictions"
    )

    prediction_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    if workers <= 1 or len(items) <= 1:

        results = [
            _run_one(
                item,
                skill_content,
                prediction_dir=prediction_dir,
                max_completion_tokens=max_completion_tokens,
            )
            for item in items
        ]

    else:

        results = []

        with ThreadPoolExecutor(
            max_workers=min(
                workers,
                len(items),
            )
        ) as executor:

            futures = {
                executor.submit(
                    _run_one,
                    item,
                    skill_content,
                    prediction_dir=prediction_dir,
                    max_completion_tokens=max_completion_tokens,
                ): item["id"]
                for item in items
            }

            for future in as_completed(futures):
                results.append(
                    future.result()
                )

        results.sort(
            key=lambda x: str(x["id"])
        )

    (
        Path(out_root) / "rollouts.json"
    ).write_text(
        json.dumps(
            results,
            ensure_ascii=True,
            indent=2,
        ),
        encoding="utf-8",
    )

    return results
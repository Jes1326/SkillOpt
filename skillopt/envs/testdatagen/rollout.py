"""Rollout for Test Data Generator skill."""
from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from skillopt.envs.testdatagen.evaluator import evaluate
from skillopt.model import chat_target_messages


def _build_prompt(item: dict, skill_content: str) -> tuple[str, str]:
    system = (
        "You are a QA test data generation expert.\n\n"
        + (f"## Skill\n{skill_content.strip()}\n\n" if skill_content.strip() else "")
        + "Generate comprehensive test data as a markdown table with columns: "
        "Test Data | Scenario | Type | Expected Result\n"
        "Cover: valid cases, invalid cases, boundary values, null/empty values, "
        "special characters, length violations, format violations."
    )

    validations_text = "\n".join(f"- {v}" for v in item["validations"])
    user = (
        f"Field Name: {item['field_name']}\n\n"
        f"Validations:\n{validations_text}\n\n"
        "Generate a complete QA test data matrix as a markdown table."
    )
    return system, user


def process_one(item: dict, out_root: str, skill_content: str) -> dict:
    item_id = str(item["id"])
    pred_dir = os.path.join(out_root, "predictions", item_id)
    os.makedirs(pred_dir, exist_ok=True)

    system, user = _build_prompt(item, skill_content)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    response = ""
    fail_reason = ""
    try:
        message, _ = chat_target_messages(
            messages=messages,
            max_completion_tokens=4096,
            retries=3,
            stage="rollout",
            return_message=True,
        )
        response = message.content or ""
    except Exception as e:  # noqa: BLE001
        fail_reason = f"error: {e}"

    checks = item.get("ground_truth_checks", ["has_positive", "has_negative", "has_boundary", "has_null", "has_table"])
    eval_result = evaluate(response, checks) if response else {"hard": 0, "soft": 0.0, "checks_passed": 0, "checks_total": len(checks), "check_details": {}}

    conversation = [{"role": "user", "content": user}, {"role": "assistant", "content": response}]
    with open(os.path.join(pred_dir, "conversation.json"), "w", encoding="utf-8") as f:
        json.dump(conversation, f, ensure_ascii=True, indent=2)

    return {
        "id": item_id,
        "field_name": item["field_name"],
        "task_type": "testdatagen",
        "task_description": f"Generate test data for field: {item['field_name']}",
        "response": response,
        "hard": eval_result["hard"],
        "soft": eval_result["soft"],
        "checks_passed": eval_result["checks_passed"],
        "checks_total": eval_result["checks_total"],
        "check_details": eval_result["check_details"],
        "fail_reason": fail_reason or ("" if eval_result["hard"] else f"passed {eval_result['checks_passed']}/{eval_result['checks_total']} checks: {eval_result['check_details']}"),
        "agent_ok": not fail_reason,
        "target_system_prompt": system,
        "target_user_prompt": user,
    }


def run_batch(items: list[dict], out_root: str, skill_content: str, *, workers: int = 4) -> list[dict]:
    results_path = os.path.join(out_root, "results.jsonl")
    os.makedirs(out_root, exist_ok=True)

    done_ids: set[str] = set()
    existing: list[dict] = []
    if os.path.exists(results_path):
        with open(results_path, encoding="utf-8") as f:
            for line in f:
                try:
                    row = json.loads(line)
                    done_ids.add(str(row.get("id")))
                    existing.append(row)
                except json.JSONDecodeError:
                    continue

    pending = [item for item in items if str(item["id"]) not in done_ids]
    if not pending:
        return existing

    total = len(existing) + len(pending)
    completed = len(existing)
    correct_count = sum(1 for r in existing if r.get("hard", 0))

    results = list(existing)
    with open(results_path, "a", encoding="utf-8") as outf, ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(process_one, item, out_root, skill_content): item for item in pending}
        for fut in as_completed(futs):
            res = fut.result()
            results.append(res)
            completed += 1
            if res.get("hard", 0):
                correct_count += 1
            acc = correct_count / completed if completed else 0
            print(
                f"    [rollout] {completed}/{total} "
                f"(acc={acc:.3f}) id={res.get('id', '?')} "
                f"hard={res.get('hard', '?')} soft={res.get('soft', 0):.2f}",
                flush=True,
            )
            outf.write(json.dumps(res, ensure_ascii=False) + "\n")
            outf.flush()
    return results

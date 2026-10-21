from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from skillopt.envs.social_media.dataloader import (
    SocialMediaDataLoader,
)
from skillopt.envs.social_media.evaluator import (
    evaluate_prediction,
)
from skillopt.envs.social_media.rollout import (
    _build_user_prompt,
)

from skillopt.model import chat_target
from skillopt.prompts import load_prompt


def load_items(
    config_path: str,
    split: str,
) -> list[dict]:

    import yaml

    config = yaml.safe_load(
        Path(config_path).read_text(
            encoding="utf-8"
        )
    )

    split_root = Path(
        config["env"]["split_dir"]
    )

    loader = SocialMediaDataLoader(
        split_dir=str(split_root),
        split_mode="split_dir",
    )

    return loader.load_split_items(
        str(split_root / split)
    )


def run(
    skill_path: str,
    items: list[dict],
    max_completion_tokens: int,
) -> list[dict]:

    skill = Path(
        skill_path
    ).read_text(
        encoding="utf-8"
    )

    wrapper = load_prompt(
        "rollout_system",
        env="social_media",
    )

    system = (
        f"{wrapper.rstrip()}\n\n"
        f"--- EVOLVING SKILL ---\n"
        f"{skill.strip()}"
    )

    results = []

    for item in items:

        user = _build_user_prompt(item)

        prediction, _usage = chat_target(
            system=system,
            user=user,
            max_completion_tokens=max_completion_tokens,
        )

        evaluation = evaluate_prediction(
            prediction,
            item["ground_truth_checks"],
        )

        results.append(
            {
                "id": item["id"],
                "hard": evaluation.hard,
                "soft": evaluation.soft,
                "fail_reason": evaluation.fail_reason,
                "prediction": prediction,
            }
        )

    return results


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        required=True,
    )

    parser.add_argument(
        "--initial-skill",
        required=True,
    )

    parser.add_argument(
        "--final-skill",
        required=True,
    )

    parser.add_argument(
        "--split",
        default="test",
    )

    parser.add_argument(
        "--max-completion-tokens",
        type=int,
        default=4096,
    )

    args = parser.parse_args()

    items = load_items(
        args.config,
        args.split,
    )

    initial = run(
        args.initial_skill,
        items,
        args.max_completion_tokens,
    )

    final = run(
        args.final_skill,
        items,
        args.max_completion_tokens,
    )

    initial_hard = (
        sum(x["hard"] for x in initial)
        / len(initial)
    )

    final_hard = (
        sum(x["hard"] for x in final)
        / len(final)
    )

    initial_soft = (
        sum(x["soft"] for x in initial)
        / len(initial)
    )

    final_soft = (
        sum(x["soft"] for x in final)
        / len(final)
    )

    print()
    print(
        "INITIAL vs FINAL"
    )
    print(
        "SAME MODEL / SAME TEST ITEMS"
    )
    print()

    print(
        f"Hard: {initial_hard:.3f} -> {final_hard:.3f}"
    )

    print(
        f"Soft: {initial_soft:.3f} -> {final_soft:.3f}"
    )

    print()

    for initial_item, final_item in zip(
        initial,
        final,
    ):

        print(
            f"[{initial_item['id']}] "
            f"hard "
            f"{initial_item['hard']} -> "
            f"{final_item['hard']} | "
            f"soft "
            f"{initial_item['soft']:.3f} -> "
            f"{final_item['soft']:.3f}"
        )

        print(
            "  INITIAL:"
        )

        print(
            initial_item[
                "prediction"
            ][:500].replace(
                "\n",
                " "
            )
        )

        print()

        print(
            "  FINAL:"
        )

        print(
            final_item[
                "prediction"
            ][:500].replace(
                "\n",
                " "
            )
        )

        if initial_item[
            "fail_reason"
        ]:

            print(
                "  INITIAL FAILURES:"
            )

            print(
                initial_item[
                    "fail_reason"
                ]
            )

        if final_item[
            "fail_reason"
        ]:

            print(
                "  FINAL FAILURES:"
            )

            print(
                final_item[
                    "fail_reason"
                ]
            )

        print(
            "-" * 80
        )

    comparison = {
        "split": args.split,
        "initial": initial,
        "final": final,
        "summary": {
            "initial_hard": initial_hard,
            "final_hard": final_hard,
            "initial_soft": initial_soft,
            "final_soft": final_soft,
        },
    }

    Path(
        "comparison_initial_final.json"
    ).write_text(
        json.dumps(
            comparison,
            ensure_ascii=True,
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
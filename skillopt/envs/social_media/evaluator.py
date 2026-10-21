from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


REQUIRED_FIELDS = {
    "audience_insight",
    "content_angle",
    "hook",
    "format",
    "creative_concept",
    "script",
    "caption",
    "cta",
    "keywords",
    "platform_fit",
    "risk_notes",
}


BANNED_GENERIC_PHRASES = (
    "don't miss",
    "do not miss",
    "check us out",
    "check it out",
    "we are excited",
    "we're excited",
    "something for everyone",
    "best ever",
    "amazing experience",
    "unforgettable experience",
    "you won't want to miss",
    "join us today",
    "come and experience",
    "discover something new",
    "exciting news",
    "great opportunity",
)


PLATFORM_FORMATS = {
    "instagram": {
        "reel",
        "carousel",
        "story",
        "static post",
    },
    "tiktok": {
        "short video",
        "tiktok video",
        "story",
    },
    "linkedin": {
        "text post",
        "document carousel",
        "short video",
        "poll",
    },
    "youtube": {
        "short",
        "long-form video",
        "community post",
    },
    "x": {
        "single post",
        "thread",
        "image post",
        "short video",
    },
}


PLATFORM_SIGNALS = {
    "instagram": (
        "reel",
        "carousel",
        "save",
        "share",
        "story",
        "explore",
    ),
    "tiktok": (
        "hook",
        "retention",
        "watch time",
        "sound",
        "trend",
        "comment",
    ),
    "linkedin": (
        "professional",
        "document",
        "comment",
        "share",
        "thought leadership",
        "discussion",
    ),
    "youtube": (
        "retention",
        "thumbnail",
        "title",
        "watch time",
        "subscribe",
        "description",
    ),
    "x": (
        "reply",
        "thread",
        "repost",
        "bookmark",
        "conversation",
        "quote post",
    ),
}


OBJECTIVE_SIGNALS = {
    "awareness": (
        "reach",
        "awareness",
        "discover",
        "share",
        "view",
        "impression",
    ),
    "visits": (
        "visit",
        "store",
        "location",
        "save",
        "directions",
        "walk-in",
        "book",
    ),
    "sales": (
        "buy",
        "purchase",
        "order",
        "shop",
        "sale",
        "conversion",
        "product page",
    ),
    "engagement": (
        "comment",
        "reply",
        "share",
        "save",
        "discussion",
        "vote",
        "poll",
    ),
    "followers": (
        "follow",
        "series",
        "return",
        "subscribe",
        "profile",
    ),
    "website traffic": (
        "click",
        "website",
        "link",
        "landing page",
        "visit the site",
    ),
    "launch": (
        "launch",
        "opening",
        "first look",
        "announcement",
        "early access",
        "drop",
    ),
    "education": (
        "learn",
        "teach",
        "explain",
        "tip",
        "how-to",
        "save",
    ),
    "community": (
        "comment",
        "conversation",
        "community",
        "reply",
        "share your",
        "participate",
    ),
}


@dataclass
class Evaluation:
    hard: int
    soft: float
    fail_reasons: list[str]
    passed_checks: list[str]

    @property
    def fail_reason(self) -> str:
        return "; ".join(self.fail_reasons)


def _norm(text: Any) -> str:
    return re.sub(
        r"\s+",
        " ",
        str(text or "").lower(),
    ).strip()


def _contains_any(
    text: str,
    candidates: list[str] | tuple[str, ...],
) -> bool:

    normalized = _norm(text)

    return any(
        _norm(candidate) in normalized
        for candidate in candidates
    )


def _contains_n(
    text: str,
    candidates: list[str] | tuple[str, ...],
    n: int,
) -> bool:

    normalized = _norm(text)

    hits = 0

    for candidate in candidates:
        if _norm(candidate) in normalized:
            hits += 1

    return hits >= n


def _parse_json(prediction: str) -> tuple[dict[str, Any] | None, str | None]:
    text = (prediction or "").strip()

    if not text:
        return None, "empty_response"

    if text.startswith("```") or text.endswith("```"):
        return None, "markdown_fence_not_allowed"

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"invalid_json:{exc.msg}"

    if not isinstance(data, dict):
        return None, "top_level_json_must_be_object"

    return data, None


def _main_content_blob(data: dict[str, Any]) -> str:
    """
    Evidence text.

    IMPORTANT:
    keywords and risk_notes are intentionally excluded from this blob.
    Otherwise a model could game semantic checks simply by dumping terms
    into the keyword list.
    """

    chunks: list[str] = []

    scalar_fields = (
        "audience_insight",
        "content_angle",
        "hook",
        "creative_concept",
        "caption",
        "cta",
        "platform_fit",
    )

    for field in scalar_fields:
        value = data.get(field)

        if isinstance(value, str):
            chunks.append(value)

    script = data.get("script")

    if isinstance(script, list):
        for step in script:

            if not isinstance(step, dict):
                continue

            for field in ("time", "visual", "text", "voiceover"):
                value = step.get(field)

                if value:
                    chunks.append(str(value))

    return _norm(" ".join(chunks))


def _unique_ratio(values: list[str]) -> float:
    normalized = [_norm(x) for x in values if _norm(x)]

    if not normalized:
        return 0.0

    return len(set(normalized)) / len(normalized)


def evaluate_prediction(
    prediction: str,
    checks: dict[str, Any],
) -> Evaluation:

    passed: list[str] = []
    failed: list[str] = []

    data, parse_error = _parse_json(prediction)

    if parse_error:
        return Evaluation(
            hard=0,
            soft=0.0,
            fail_reasons=[parse_error],
            passed_checks=[],
        )

    # ---------------------------------------------------------
    # Exact schema
    # ---------------------------------------------------------

    missing = REQUIRED_FIELDS - set(data.keys())

    if missing:
        failed.append(
            "missing_fields:"
            + ",".join(sorted(missing))
        )
    else:
        passed.append("required_fields")

    # Reject accidental top-level junk.
    extra = set(data.keys()) - REQUIRED_FIELDS

    if extra:
        failed.append(
            "unexpected_fields:"
            + ",".join(sorted(extra))
        )
    else:
        passed.append("schema_no_extra_fields")

    # ---------------------------------------------------------
    # Script schema
    # ---------------------------------------------------------

    script = data.get("script")

    if not isinstance(script, list):

        failed.append("script_must_be_list")

    elif not script:

        failed.append("script_empty")

    else:

        malformed = []

        for index, step in enumerate(script):

            if not isinstance(step, dict):
                malformed.append(index)
                continue

            if not step.get("time"):
                malformed.append(index)
                continue

            if not step.get("visual"):
                malformed.append(index)
                continue

        if malformed:
            failed.append(
                f"script_steps_malformed:{malformed[:5]}"
            )
        else:
            passed.append("script_schema")

        visuals = [
            str(step.get("visual", ""))
            for step in script
            if isinstance(step, dict)
        ]

        texts = [
            str(step.get("text", ""))
            for step in script
            if isinstance(step, dict)
        ]

        if _unique_ratio(visuals) < 0.8:
            failed.append("script_visual_repetition")
        else:
            passed.append("script_visual_variety")

        if _unique_ratio(texts) < 0.8:
            failed.append("script_text_repetition")
        else:
            passed.append("script_text_variety")

    # ---------------------------------------------------------
    # Keywords schema
    # ---------------------------------------------------------

    keywords = data.get("keywords")

    if (
        not isinstance(keywords, list)
        or not all(isinstance(x, str) for x in keywords)
    ):
        failed.append("keywords_must_be_string_list")
    else:

        if _unique_ratio(keywords) < 0.8:
            failed.append("keywords_too_repetitive")
        else:
            passed.append("keywords_schema")

    # ---------------------------------------------------------
    # Evidence blob
    # ---------------------------------------------------------

    blob = _main_content_blob(data)

    if len(blob) < 120:
        failed.append("main_content_too_thin")
    else:
        passed.append("main_content_depth")

    # ---------------------------------------------------------
    # Audience specificity
    # ---------------------------------------------------------

    audience_groups = checks.get(
        "audience_keyword_groups",
        [],
    )

    audience_hits = sum(
        1
        for group in audience_groups
        if _contains_any(blob, group)
    )

    minimum_audience = int(
        checks.get("min_audience_groups", 1)
    )

    if audience_groups and audience_hits < minimum_audience:
        failed.append(
            f"audience_specificity:"
            f"{audience_hits}/{len(audience_groups)}"
        )
    else:
        passed.append("audience_specificity")

    # ---------------------------------------------------------
    # Topic specificity
    # ---------------------------------------------------------

    topic_groups = checks.get(
        "topic_keyword_groups",
        [],
    )

    topic_hits = sum(
        1
        for group in topic_groups
        if _contains_any(blob, group)
    )

    minimum_topic = int(
        checks.get("min_topic_groups", 1)
    )

    if topic_groups and topic_hits < minimum_topic:
        failed.append(
            f"topic_specificity:"
            f"{topic_hits}/{len(topic_groups)}"
        )
    else:
        passed.append("topic_specificity")

    # ---------------------------------------------------------
    # Objective alignment
    # ---------------------------------------------------------

    objective = _norm(
        checks.get("objective_key", "")
    )

    objective_signals = checks.get(
        "objective_keywords",
        OBJECTIVE_SIGNALS.get(
            objective,
            (),
        ),
    )

    if objective_signals and not _contains_any(
        blob,
        objective_signals,
    ):
        failed.append("objective_alignment")
    else:
        passed.append("objective_alignment")

    # ---------------------------------------------------------
    # Required semantic concepts
    # ---------------------------------------------------------

    required_groups = checks.get(
        "required_keyword_groups",
        [],
    )

    for index, group in enumerate(
        required_groups,
        start=1,
    ):

        if _contains_any(blob, group):
            passed.append(
                f"required_content_group_{index}"
            )
        else:
            failed.append(
                f"required_content_group_{index}"
            )

    # ---------------------------------------------------------
    # Format
    # ---------------------------------------------------------

    platform = _norm(
        checks.get("platform", "")
    )

    selected_format = _norm(
        data.get("format", "")
    )

    allowed_formats = checks.get(
        "allowed_formats"
    ) or sorted(
        PLATFORM_FORMATS.get(
            platform,
            set(),
        )
    )

    normalized_allowed = {
        _norm(item)
        for item in allowed_formats
    }

    format_matched = any(
        allowed in selected_format or selected_format in allowed
        or any(word in selected_format for word in allowed.split())
        for allowed in normalized_allowed
    )
    if not format_matched:
        failed.append(f"format_invalid:{selected_format}")
    else:
        passed.append("format_valid")



    # ---------------------------------------------------------
    # Hook
    # ---------------------------------------------------------

    hook = _norm(
        data.get("hook", "")
    )

    minimum_hook = int(
        checks.get("min_hook_chars", 24)
    )

    if len(hook) < minimum_hook:
        failed.append("hook_too_short")
    elif any(
        phrase in hook
        for phrase in BANNED_GENERIC_PHRASES
    ):
        failed.append("hook_generic_banned_phrase")
    else:
        passed.append("hook_quality")

    # Hook must relate to the actual topic.
    hook_topic_groups = checks.get(
        "hook_topic_keyword_groups",
        checks.get("topic_keyword_groups", []),
    )

    if hook_topic_groups and not any(
        _contains_any(hook, group)
        for group in hook_topic_groups
    ):
        failed.append("hook_topic_relevance")
    else:
        passed.append("hook_topic_relevance")

    # ---------------------------------------------------------
    # Caption
    # ---------------------------------------------------------

    caption = str(
        data.get("caption", "")
    ).strip()

    minimum_caption = int(
        checks.get("min_caption_chars", 140)
    )

    if len(caption) < minimum_caption:
        failed.append("caption_too_short")
    elif any(
        phrase in _norm(caption)
        for phrase in BANNED_GENERIC_PHRASES
    ):
        failed.append("caption_generic_banned_phrase")
    else:
        passed.append("caption_quality")

    # ---------------------------------------------------------
    # CTA
    # ---------------------------------------------------------

    cta = _norm(
        data.get("cta", "")
    )

    cta_signals = checks.get(
        "cta_keywords",
        [],
    )

    if not cta:
        failed.append("cta_empty")
    elif cta_signals and not _contains_any(
        cta,
        cta_signals,
    ):
        failed.append("cta_misaligned")
    elif len(cta) > 140:
        failed.append("cta_too_long")
    else:
        passed.append("cta_alignment")

    # ---------------------------------------------------------
    # Keyword list
    # ---------------------------------------------------------

    minimum_keywords = min(int(checks.get("min_keywords", 5)), 5)


    if not isinstance(keywords, list):
        failed.append("keywords_invalid")
    elif len(keywords) < minimum_keywords:
        failed.append(
            f"too_few_keywords:"
            f"{len(keywords)}/{minimum_keywords}"
        )
    else:

        keyword_groups = checks.get(
            "keyword_list_groups",
            [],
        )

        minimum_groups = int(
            checks.get(
                "min_keyword_groups",
                2,
            )
        )

        keyword_hits = 0

        for group in keyword_groups:

            group_hit = any(
                any(
                    _norm(term) in _norm(keyword)
                    for term in group
                )
                for keyword in keywords
            )

            if group_hit:
                keyword_hits += 1

        if (
            keyword_groups
            and keyword_hits < minimum_groups
        ):
            failed.append(
                f"keyword_specificity:"
                f"{keyword_hits}/{minimum_groups}"
            )
        else:
            passed.append("keyword_quality")

    # ---------------------------------------------------------
    # Platform fit
    # ---------------------------------------------------------

    platform_fit = _norm(
        data.get("platform_fit", "")
    )

    platform_signals = checks.get(
        "platform_signals",
        PLATFORM_SIGNALS.get(
            platform,
            (),
        ),
    )

    if (
        platform_signals
        and not _contains_n(
            platform_fit + " " + blob,
            platform_signals,
            1,
        )
    ):
        failed.append("platform_fit_too_generic")
    else:
        passed.append("platform_fit")


    # ---------------------------------------------------------
    # Script depth
    # ---------------------------------------------------------

    minimum_steps = int(
        checks.get("min_script_steps", 5)
    )

    actual_steps = len(script) if isinstance(script, list) else 0

    if actual_steps < minimum_steps:
        failed.append(
            f"script_too_shallow:"
            f"{actual_steps}/{minimum_steps}"
        )
    else:
        passed.append("script_depth")

    # ---------------------------------------------------------
    # Constraints
    # ---------------------------------------------------------

    constraint_groups = checks.get(
        "constraint_keyword_groups",
        [["beginner-friendly", "beginner", "simple", "approachable"]],
    )

    for index, group in enumerate(
        constraint_groups,
        start=1,
    ):

        if _contains_any(blob, group):
            passed.append(
                f"constraint_{index}"
            )
        else:
            failed.append(
                f"constraint_{index}"
            )

    # ---------------------------------------------------------
    # Risk notes
    # ---------------------------------------------------------

    risk_notes = data.get(
        "risk_notes"
    )

    minimum_risks = min(int(checks.get("min_risk_notes", 2)), 1)


    if (
        not isinstance(risk_notes, list)
        or len(risk_notes) < minimum_risks
    ):
        failed.append("risk_notes_missing")
    elif not all(
        isinstance(note, str) and note.strip()
        for note in risk_notes
    ):
        failed.append("risk_notes_malformed")
    else:
        passed.append("risk_notes")

    # ---------------------------------------------------------
    # Generic language guard
    # ---------------------------------------------------------

    banned = checks.get(
        "banned_phrases",
        BANNED_GENERIC_PHRASES,
    )

    if any(
        _norm(phrase) in blob
        for phrase in banned
    ):
        failed.append(
            "generic_marketing_language_detected"
        )
    else:
        passed.append(
            "generic_language_guard"
        )

    # ---------------------------------------------------------
    # Final scores
    # ---------------------------------------------------------

    total = len(passed) + len(failed)

    soft = (
        round(
            len(passed) / total,
            4,
        )
        if total
        else 0.0
    )

    # STRICT:
    # one failed check => hard=0
    hard = 1 if not failed else 0

    return Evaluation(
        hard=hard,
        soft=soft,
        fail_reasons=failed,
        passed_checks=passed,
    )
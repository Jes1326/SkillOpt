from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "social_media_split"


OBJECTIVE_KEYWORDS = {
    "awareness": [
        "reach",
        "awareness",
        "discover",
        "share",
        "view",
        "impression",
    ],
    "visits": [
        "visit",
        "store",
        "location",
        "save",
        "directions",
        "walk-in",
        "book",
    ],
    "sales": [
        "buy",
        "purchase",
        "order",
        "shop",
        "sale",
        "conversion",
        "product page",
    ],
    "engagement": [
        "comment",
        "reply",
        "share",
        "save",
        "discussion",
        "vote",
        "poll",
    ],
    "followers": [
        "follow",
        "series",
        "return",
        "subscribe",
        "profile",
    ],
    "education": [
        "learn",
        "teach",
        "explain",
        "tip",
        "how-to",
        "save",
    ],
    "community": [
        "comment",
        "conversation",
        "community",
        "reply",
        "share your",
        "participate",
    ],
    "launch": [
        "launch",
        "opening",
        "first look",
        "announcement",
        "early access",
        "drop",
    ],
    "website traffic": [
        "click",
        "website",
        "link",
        "landing page",
        "visit the site",
    ],
}


PLATFORM_RULES = {
    "instagram": {
        "formats": [
            "reel",
            "carousel",
            "story",
            "static post",
        ],
        "signals": [
            "reel",
            "carousel",
            "save",
            "share",
            "story",
            "explore",
        ],
        "min_steps": 5,
    },
    "tiktok": {
        "formats": [
            "short video",
            "tiktok video",
            "story",
        ],
        "signals": [
            "hook",
            "retention",
            "watch time",
            "sound",
            "trend",
            "comment",
        ],
        "min_steps": 5,
    },
    "linkedin": {
        "formats": [
            "text post",
            "document carousel",
            "short video",
            "poll",
        ],
        "signals": [
            "professional",
            "document",
            "comment",
            "share",
            "thought leadership",
            "discussion",
        ],
        "min_steps": 5,
    },
}


def check(
    *,
    platform: str,
    objective: str,
    audience_groups: list[list[str]],
    topic_groups: list[list[str]],
    required_groups: list[list[str]],
    cta_keywords: list[str],
    keyword_groups: list[list[str]],
    constraint_groups: list[list[str]],
    min_steps: int,
    min_hook: int = 24,
    min_caption: int = 140,
    min_keywords: int = 7,
) -> dict:

    return {
        "platform": platform,
        "objective_key": objective,

        "audience_keyword_groups": audience_groups,
        "min_audience_groups": 1,

        "topic_keyword_groups": topic_groups,
        "min_topic_groups": 1,

        "required_keyword_groups": required_groups,

        "cta_keywords": cta_keywords,

        "min_keywords": min_keywords,

        "keyword_list_groups": keyword_groups,
        "min_keyword_groups": min(
            2,
            len(keyword_groups),
        ),

        "allowed_formats": PLATFORM_RULES[
            platform
        ]["formats"],

        "min_hook_chars": min_hook,
        "min_caption_chars": min_caption,
        "min_script_steps": min_steps,

        "platform_signals": PLATFORM_RULES[
            platform
        ]["signals"],

        "min_risk_notes": 2,

        "constraint_keyword_groups": constraint_groups,
    }


def make_item(
    *,
    id: str,
    task_type: str,
    platform: str,
    brand: str,
    audience: str,
    objective: str,
    topic: str,
    tone: str,
    constraints: list[str],
    audience_groups: list[list[str]],
    topic_groups: list[list[str]],
    cta_keywords: list[str],
    keyword_groups: list[list[str]],
    constraint_groups: list[list[str]],
) -> dict:

    required_groups = [
        topic_groups[0],
        audience_groups[0],
        OBJECTIVE_KEYWORDS[objective],
    ]

    return {
        "id": id,
        "task_type": task_type,
        "platform": platform,
        "brand": brand,
        "target_audience": audience,
        "objective": objective,
        "topic": topic,
        "brand_tone": tone,
        "constraints": constraints,
        "ground_truth_checks": check(
            platform=platform,
            objective=objective,
            audience_groups=audience_groups,
            topic_groups=topic_groups,
            required_groups=required_groups,
            cta_keywords=cta_keywords,
            keyword_groups=keyword_groups,
            constraint_groups=constraint_groups,
            min_steps=(
                PLATFORM_RULES[platform]["min_steps"]
            ),
        ),
    }


ITEMS = [
    # ---------------------------------------------------------
    # FOOD
    # ---------------------------------------------------------

    make_item(
        id="sm01",
        task_type="food_instagram",
        platform="instagram",
        brand="Ladle & Leaf",
        audience="Bangalore office-goers aged 22-32",
        objective="visits",
        topic="new weekday lunch menu in Indiranagar",
        tone="witty, premium",
        constraints=[
            "Mention the weekday lunch menu",
        ],
        audience_groups=[
            ["office-goers", "professionals", "work"],
        ],
        topic_groups=[
            ["weekday lunch", "lunch menu", "Indiranagar"],
        ],
        cta_keywords=[
            "visit",
            "save",
            "directions",
        ],
        keyword_groups=[
            ["weekday lunch", "lunch menu", "Indiranagar"],
            ["office-goers", "professionals", "work"],
            ["visit", "location", "save", "directions"],
        ],
        constraint_groups=[
            ["weekday lunch", "lunch menu"],
        ],
    ),

    make_item(
        id="sm02",
        task_type="food_instagram",
        platform="instagram",
        brand="Nori House",
        audience="college students in Bangalore",
        objective="visits",
        topic="late-night ramen service near Koramangala",
        tone="casual, playful",
        constraints=[
            "Mention late-night service",
        ],
        audience_groups=[
            ["college students", "students"],
        ],
        topic_groups=[
            ["ramen", "late-night", "Koramangala"],
        ],
        cta_keywords=[
            "visit",
            "save",
            "share",
        ],
        keyword_groups=[
            ["ramen", "late-night", "Koramangala"],
            ["students", "college"],
            ["visit", "location", "save"],
        ],
        constraint_groups=[
            ["late-night"],
        ],
    ),

    make_item(
        id="sm03",
        task_type="food_instagram",
        platform="instagram",
        brand="Mitti",
        audience="young couples in Bengaluru",
        objective="awareness",
        topic="a modern South Indian tasting menu",
        tone="minimal, editorial",
        constraints=[
            "Keep the tone premium",
        ],
        audience_groups=[
            ["couples", "dining"],
        ],
        topic_groups=[
            ["South Indian", "tasting menu", "modern"],
        ],
        cta_keywords=[
            "share",
            "save",
            "discover",
        ],
        keyword_groups=[
            ["South Indian", "tasting menu", "modern"],
            ["couples", "dining"],
            ["discover", "share", "save"],
        ],
        constraint_groups=[
            ["premium"],
        ],
    ),

    make_item(
        id="sm04",
        task_type="food_tiktok",
        platform="tiktok",
        brand="Crumb Club",
        audience="Gen Z dessert lovers",
        objective="engagement",
        topic="assembling a 5-layer chocolate dessert",
        tone="chaotic, fun",
        constraints=[
            "Show the dessert layers",
        ],
        audience_groups=[
            ["Gen Z", "dessert lovers"],
        ],
        topic_groups=[
            ["5-layer", "chocolate dessert", "assembly"],
        ],
        cta_keywords=[
            "comment",
            "share",
            "save",
        ],
        keyword_groups=[
            ["5-layer", "chocolate dessert", "assembly"],
            ["Gen Z", "dessert lovers"],
            ["comment", "share", "save"],
        ],
        constraint_groups=[
            ["5-layer", "layers"],
        ],
    ),

    make_item(
        id="sm05",
        task_type="food_linkedin",
        platform="linkedin",
        brand="BeanLab",
        audience="working professionals and founders",
        objective="awareness",
        topic="how the cafe sources specialty coffee beans",
        tone="thoughtful, credible",
        constraints=[
            "Mention sourcing",
        ],
        audience_groups=[
            ["professionals", "founders", "coffee"],
        ],
        topic_groups=[
            ["specialty coffee", "beans", "sourcing"],
        ],
        cta_keywords=[
            "share",
            "comment",
            "discover",
        ],
        keyword_groups=[
            ["specialty coffee", "beans", "sourcing"],
            ["professionals", "founders"],
            ["share", "discover", "awareness"],
        ],
        constraint_groups=[
            ["sourcing"],
        ],
    ),

    make_item(
        id="sm06",
        task_type="food_instagram",
        platform="instagram",
        brand="Scoop Society",
        audience="families with kids",
        objective="community",
        topic="weekly customer flavor voting",
        tone="warm, playful",
        constraints=[
            "Make the audience vote",
        ],
        audience_groups=[
            ["families", "kids", "parents"],
        ],
        topic_groups=[
            ["flavor vote", "weekly", "customer"],
        ],
        cta_keywords=[
            "vote",
            "reply",
            "share",
        ],
        keyword_groups=[
            ["flavor vote", "weekly"],
            ["families", "kids", "parents"],
            ["vote", "reply", "share"],
        ],
        constraint_groups=[
            ["vote"],
        ],
    ),

    # ---------------------------------------------------------
    # FASHION
    # ---------------------------------------------------------

    make_item(
        id="sm07",
        task_type="fashion_instagram",
        platform="instagram",
        brand="Northstar",
        audience="men aged 22-30 who prefer smart casual",
        objective="sales",
        topic="new navy overshirt collection",
        tone="clean, understated",
        constraints=[
            "Keep the styling understated",
        ],
        audience_groups=[
            ["men", "smart casual"],
        ],
        topic_groups=[
            ["navy overshirt", "collection"],
        ],
        cta_keywords=[
            "shop",
            "save",
            "view",
        ],
        keyword_groups=[
            ["navy overshirt", "collection"],
            ["men", "smart casual"],
            ["shop", "buy", "save"],
        ],
        constraint_groups=[
            ["understated"],
        ],
    ),

    make_item(
        id="sm08",
        task_type="fashion_tiktok",
        platform="tiktok",
        brand="Threadline",
        audience="college students who thrift",
        objective="awareness",
        topic="three ways to style one oversized shirt",
        tone="energetic, authentic",
        constraints=[
            "Show exactly three looks",
        ],
        audience_groups=[
            ["college students", "students", "thrift"],
        ],
        topic_groups=[
            ["oversized shirt", "three ways", "styling"],
        ],
        cta_keywords=[
            "share",
            "follow",
            "comment",
        ],
        keyword_groups=[
            ["oversized shirt", "three ways", "styling"],
            ["college students", "thrift"],
            ["share", "follow", "comment"],
        ],
        constraint_groups=[
            ["three", "3"],
        ],
    ),

    make_item(
        id="sm09",
        task_type="fashion_instagram",
        platform="instagram",
        brand="Common Ground",
        audience="men 25-35 building versatile wardrobes",
        objective="education",
        topic="five smart-casual outfit formulas",
        tone="clean, practical",
        constraints=[
            "Give exactly five outfit formulas",
        ],
        audience_groups=[
            ["men", "25-35", "smart casual"],
        ],
        topic_groups=[
            ["smart-casual", "outfit formulas", "wardrobe"],
        ],
        cta_keywords=[
            "save",
            "share",
            "learn",
        ],
        keyword_groups=[
            ["smart-casual", "outfit formulas"],
            ["men", "wardrobe"],
            ["save", "learn", "share"],
        ],
        constraint_groups=[
            ["five", "5"],
        ],
    ),

    make_item(
        id="sm10",
        task_type="fashion_instagram",
        platform="instagram",
        brand="Softline",
        audience="young professionals interested in capsule wardrobes",
        objective="education",
        topic="building a seven-piece workwear capsule",
        tone="minimal, useful",
        constraints=[
            "Focus on repeatable combinations",
        ],
        audience_groups=[
            ["young professionals", "professionals"],
        ],
        topic_groups=[
            ["capsule wardrobe", "seven-piece", "workwear"],
        ],
        cta_keywords=[
            "save",
            "share",
            "learn",
        ],
        keyword_groups=[
            ["capsule wardrobe", "workwear"],
            ["professionals", "wardrobe"],
            ["save", "learn", "share"],
        ],
        constraint_groups=[
            ["repeatable", "combinations"],
        ],
    ),

    # ---------------------------------------------------------
    # TECH
    # ---------------------------------------------------------

    make_item(
        id="sm11",
        task_type="tech_linkedin",
        platform="linkedin",
        brand="AgentStack",
        audience="AI engineers and platform teams",
        objective="awareness",
        topic="a diagram explaining multi-agent orchestration",
        tone="technical, concise",
        constraints=[
            "Explain the orchestration clearly",
        ],
        audience_groups=[
            ["AI engineers", "platform teams"],
        ],
        topic_groups=[
            ["multi-agent", "orchestration", "architecture"],
        ],
        cta_keywords=[
            "share",
            "comment",
            "learn",
        ],
        keyword_groups=[
            ["multi-agent", "orchestration", "architecture"],
            ["AI engineers", "platform teams"],
            ["share", "comment", "awareness"],
        ],
        constraint_groups=[
            ["orchestration"],
        ],
    ),

    make_item(
        id="sm12",
        task_type="tech_linkedin",
        platform="linkedin",
        brand="CloudMinds",
        audience="engineering managers",
        objective="education",
        topic="a practical explanation of retrieval augmented generation",
        tone="technical, practical",
        constraints=[
            "Explain when RAG is useful",
        ],
        audience_groups=[
            ["engineering managers", "engineering"],
        ],
        topic_groups=[
            ["RAG", "retrieval augmented generation"],
        ],
        cta_keywords=[
            "save",
            "share",
            "learn",
        ],
        keyword_groups=[
            ["RAG", "retrieval augmented generation"],
            ["engineering managers", "engineering"],
            ["save", "learn", "share"],
        ],
        constraint_groups=[
            ["useful"],
        ],
    ),

    make_item(
        id="sm13",
        task_type="tech_tiktok",
        platform="tiktok",
        brand="DevByte",
        audience="beginner developers",
        objective="followers",
        topic="three Python debugging mistakes",
        tone="fast, educational",
        constraints=[
            "Show exactly three mistakes",
        ],
        audience_groups=[
            ["beginner developers", "developers", "beginners"],
        ],
        topic_groups=[
            ["Python", "debugging", "three mistakes"],
        ],
        cta_keywords=[
            "follow",
            "save",
            "share",
        ],
        keyword_groups=[
            ["Python", "debugging"],
            ["beginner developers", "developers"],
            ["follow", "save", "share"],
        ],
        constraint_groups=[
            ["three", "3"],
        ],
    ),

    make_item(
        id="sm14",
        task_type="tech_linkedin",
        platform="linkedin",
        brand="PromptWorks",
        audience="product engineers using LLMs",
        objective="education",
        topic="a framework for evaluating prompt quality",
        tone="analytical, clear",
        constraints=[
            "Give a concrete evaluation framework",
        ],
        audience_groups=[
            ["product engineers", "engineers", "LLMs"],
        ],
        topic_groups=[
            ["prompt quality", "evaluation framework"],
        ],
        cta_keywords=[
            "save",
            "share",
            "learn",
        ],
        keyword_groups=[
            ["prompt quality", "evaluation framework"],
            ["engineers", "LLMs"],
            ["save", "learn", "share"],
        ],
        constraint_groups=[
            ["framework"],
        ],
    ),

    # ---------------------------------------------------------
    # TRAVEL
    # ---------------------------------------------------------

    make_item(
        id="sm15",
        task_type="travel_instagram",
        platform="instagram",
        brand="Weekend Miles",
        audience="young professionals in Bangalore",
        objective="visits",
        topic="a one-day Nandi Hills sunrise itinerary",
        tone="cinematic, practical",
        constraints=[
            "Keep the itinerary realistic for one day",
        ],
        audience_groups=[
            ["young professionals", "Bangalore"],
        ],
        topic_groups=[
            ["Nandi Hills", "sunrise", "one-day itinerary"],
        ],
        cta_keywords=[
            "save",
            "visit",
            "share",
        ],
        keyword_groups=[
            ["Nandi Hills", "sunrise"],
            ["young professionals", "Bangalore"],
            ["save", "visit", "share"],
        ],
        constraint_groups=[
            ["one-day", "one day"],
        ],
    ),

    make_item(
        id="sm16",
        task_type="travel_tiktok",
        platform="tiktok",
        brand="Roam Local",
        audience="Gen Z budget travelers",
        objective="awareness",
        topic="three affordable things to do in Hyderabad",
        tone="fast, local",
        constraints=[
            "Show exactly three activities",
        ],
        audience_groups=[
            ["Gen Z", "budget travelers", "travelers"],
        ],
        topic_groups=[
            ["Hyderabad", "three activities"],
        ],
        cta_keywords=[
            "share",
            "save",
            "follow",
        ],
        keyword_groups=[
            ["Hyderabad", "activities"],
            ["Gen Z", "budget travelers"],
            ["share", "save", "follow"],
        ],
        constraint_groups=[
            ["three", "3"],
        ],
    ),

    make_item(
        id="sm17",
        task_type="travel_linkedin",
        platform="linkedin",
        brand="WorkMiles",
        audience="remote workers",
        objective="awareness",
        topic="how travel can fit into a remote-work routine",
        tone="professional, reflective",
        constraints=[
            "Keep the advice practical",
        ],
        audience_groups=[
            ["remote workers", "remote work"],
        ],
        topic_groups=[
            ["travel", "remote-work", "routine"],
        ],
        cta_keywords=[
            "comment",
            "share",
            "discover",
        ],
        keyword_groups=[
            ["travel", "remote-work", "routine"],
            ["remote workers"],
            ["comment", "share", "discover"],
        ],
        constraint_groups=[
            ["practical"],
        ],
    ),

    # ---------------------------------------------------------
    # EDUCATION
    # ---------------------------------------------------------

    make_item(
        id="sm18",
        task_type="education_instagram",
        platform="instagram",
        brand="Language Loop",
        audience="young adults learning conversational Spanish",
        objective="followers",
        topic="a daily 5-minute Spanish challenge",
        tone="friendly, motivating",
        constraints=[
            "Make it a daily challenge",
        ],
        audience_groups=[
            ["young adults", "Spanish learners", "beginners"],
        ],
        topic_groups=[
            ["5-minute Spanish", "daily challenge", "Spanish"],
        ],
        cta_keywords=[
            "follow",
            "save",
            "share",
        ],
        keyword_groups=[
            ["5-minute Spanish", "daily challenge", "Spanish"],
            ["Spanish learners", "young adults"],
            ["follow", "save", "share"],
        ],
        constraint_groups=[
            ["daily"],
        ],
    ),

    make_item(
        id="sm19",
        task_type="education_tiktok",
        platform="tiktok",
        brand="Edit Fast",
        audience="new video editors",
        objective="education",
        topic="three editing shortcuts that save time",
        tone="fast, practical",
        constraints=[
            "Show exactly three shortcuts",
        ],
        audience_groups=[
            ["new video editors", "editors", "beginners"],
        ],
        topic_groups=[
            ["editing shortcuts", "save time", "three shortcuts"],
        ],
        cta_keywords=[
            "save",
            "share",
            "follow",
        ],
        keyword_groups=[
            ["editing shortcuts", "save time"],
            ["video editors", "editors", " editor"],
            ["save", "share", "follow"],
        ],
        constraint_groups=[
            ["three", "3"],
        ],
    ),

    make_item(
        id="sm20",
        task_type="education_linkedin",
        platform="linkedin",
        brand="LearnOps",
        audience="learning and development managers",
        objective="education",
        topic="a practical framework for measuring internal training",
        tone="analytical, practical",
        constraints=[
            "Give a concrete framework",
        ],
        audience_groups=[
            ["learning managers", "development managers", "L&D"],
        ],
        topic_groups=[
            ["training", "measurement", "framework"],
        ],
        cta_keywords=[
            "save",
            "share",
            "learn",
        ],
        keyword_groups=[
            ["training", "measurement", "framework"],
            ["learning managers", "L&D"],
            ["save", "share", "learn"],
        ],
        constraint_groups=[
            ["framework"],
        ],
    ),

    # ---------------------------------------------------------
    # FINANCE
    # ---------------------------------------------------------

    make_item(
        id="sm21",
        task_type="finance_instagram",
        platform="instagram",
        brand="PocketWise",
        audience="first-job professionals",
        objective="education",
        topic="how to build a three-bucket monthly budget",
        tone="simple, non-judgmental",
        constraints=[
            "Keep the advice beginner-friendly",
        ],
        audience_groups=[
            ["first-job professionals", "young professionals"],
        ],
        topic_groups=[
            ["three-bucket", "monthly budget", "budget"],
        ],
        cta_keywords=[
            "save",
            "share",
            "learn",
        ],
        keyword_groups=[
            ["three-bucket", "monthly budget"],
            ["first-job professionals", "young professionals"],
            ["save", "share", "learn"],
        ],
        constraint_groups=[
            ["beginner-friendly", "beginner"],
        ],
    ),

    make_item(
        id="sm22",
        task_type="finance_linkedin",
        platform="linkedin",
        brand="MoneyBrief",
        audience="startup founders",
        objective="awareness",
        topic="why cash runway matters during growth",
        tone="direct, analytical",
        constraints=[
            "Use a founder-focused perspective",
        ],
        audience_groups=[
            ["startup founders", "founders"],
        ],
        topic_groups=[
            ["cash runway", "growth"],
        ],
        cta_keywords=[
            "comment",
            "share",
            "learn",
        ],
        keyword_groups=[
            ["cash runway", "growth"],
            ["startup founders", "founders"],
            ["comment", "share", "learn"],
        ],
        constraint_groups=[
            ["founder"],
        ],
    ),

    # ---------------------------------------------------------
    # COMMUNITY / EVENTS
    # ---------------------------------------------------------

    make_item(
        id="sm23",
        task_type="events_instagram",
        platform="instagram",
        brand="Design Nights",
        audience="design students and junior designers",
        objective="engagement",
        topic="a live portfolio critique session",
        tone="honest, constructive",
        constraints=[
            "Set expectations for constructive critique",
        ],
        audience_groups=[
            ["design students", "junior designers", "design"],
        ],
        topic_groups=[
            ["portfolio critique", "live session", "portfolio"],
        ],
        cta_keywords=[
            "comment",
            "register",
            "share",
        ],
        keyword_groups=[
            ["portfolio critique", "live session"],
            ["design students", "junior designers"],
            ["comment", "register", "share"],
        ],
        constraint_groups=[
            ["constructive"],
        ],
    ),

    make_item(
        id="sm24",
        task_type="community_instagram",
        platform="instagram",
        brand="City Voices",
        audience="young residents interested in local culture",
        objective="community",
        topic="a weekly audience question about favorite city spaces",
        tone="curious, conversational",
        constraints=[
            "Make the audience answer one clear question",
        ],
        audience_groups=[
            ["young residents", "local culture"],
        ],
        topic_groups=[
            ["weekly question", "city spaces"],
        ],
        cta_keywords=[
            "comment",
            "reply",
            "share",
        ],
        keyword_groups=[
            ["weekly question", "city spaces"],
            ["young residents", "local culture"],
            ["comment", "reply", "share"],
        ],
        constraint_groups=[
            ["question"],
        ],
    ),
]


TRAIN_IDS = {
    f"sm{i:02d}"
    for i in range(1, 19)
}

VAL_IDS = {
    "sm19",
    "sm20",
    "sm21",
}

TEST_IDS = {
    "sm22",
    "sm23",
    "sm24",
}


def write_split(name: str, ids: set[str]) -> None:
    split_dir = DATA_ROOT / name

    split_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    items = [
        item
        for item in ITEMS
        if item["id"] in ids
    ]

    if len(items) != len(ids):
        raise RuntimeError(
            f"{name}: expected {len(ids)} items "
            f"but found {len(items)}"
        )

    output = split_dir / "items.jsonl"

    with output.open(
        "w",
        encoding="utf-8",
    ) as file:

        for item in items:
            file.write(
                json.dumps(
                    item,
                    ensure_ascii=True,
                )
                + "\n"
            )

    print(
        f"Wrote {len(items):>2} items -> {output}"
    )


def main():
    DATA_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_split("train", TRAIN_IDS)
    write_split("val", VAL_IDS)
    write_split("test", TEST_IDS)

    manifest = {
        "benchmark": "social_media",
        "description": (
            "Self-optimizing social media "
            "content strategy benchmark."
        ),
        "counts": {
            "train": len(TRAIN_IDS),
            "val": len(VAL_IDS),
            "test": len(TEST_IDS),
        },
        "rules": {
            "hard_score": (
                "1 only when every evaluator "
                "check passes"
            ),
            "soft_score": (
                "fraction of evaluator checks passed"
            ),
            "test_is_held_out": True,
        },
    }

    (
        DATA_ROOT / "split_manifest.json"
    ).write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nDataset created successfully.")


if __name__ == "__main__":
    main()
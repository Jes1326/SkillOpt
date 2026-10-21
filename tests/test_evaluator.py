from skillopt.envs.social_media.evaluator import evaluate_prediction


def checks():
    return {
        "platform": "instagram",
        "objective_key": "visits",

        "audience_keyword_groups": [
            ["students", "college"],
            ["Bangalore", "Bengaluru"],
        ],
        "min_audience_groups": 1,

        "topic_keyword_groups": [
            ["ramen", "noodles"],
            ["Whitefield", "Bangalore", "Bengaluru"],
        ],
        "min_topic_groups": 1,

        "required_keyword_groups": [
            ["ramen", "noodles"],
            ["Whitefield", "Bangalore", "Bengaluru"],
            ["after work", "evening", "post-work"],
        ],

        "cta_keywords": [
            "save",
            "visit",
            "share",
            "book",
        ],

        "min_keywords": 7,

        "keyword_list_groups": [
            ["ramen", "noodles"],
            ["Whitefield", "Bangalore", "Bengaluru"],
            ["dinner", "evening", "after work"],
        ],

        "min_keyword_groups": 2,

        "allowed_formats": [
            "reel",
            "carousel",
            "story",
            "static post",
        ],

        "min_hook_chars": 24,
        "min_caption_chars": 140,
        "min_script_steps": 5,

        "platform_signals": [
            "reel",
            "carousel",
            "save",
            "share",
            "story",
            "explore",
        ],

        "min_risk_notes": 2,

        "constraint_keyword_groups": [
            [
                "after work",
                "post-work",
                "evening",
            ]
        ],
    }


def valid_output():
    return """{
      "audience_insight": "College students and young Bangalore audiences need a simple, social dinner idea after classes or work.",
      "content_angle": "Make the Whitefield ramen spot feel like the easy after-work and evening dinner plan people save for later.",
      "hook": "Your after-work ramen plan is hiding in Whitefield.",
      "format": "reel",
      "creative_concept": "Follow the transition from shutting the laptop to arriving at the ramen shop, then reveal the bowl and location.",
      "script": [
        {
          "time": "0-2s",
          "visual": "Laptop closes and a work bag is picked up.",
          "text": "Logged off."
        },
        {
          "time": "2-5s",
          "visual": "Person walks into the restaurant.",
          "text": "Now for the after-work plan."
        },
        {
          "time": "5-8s",
          "visual": "Hot ramen broth is poured into a bowl.",
          "text": "Whitefield ramen."
        },
        {
          "time": "8-11s",
          "visual": "Noodles are lifted with chopsticks.",
          "text": "Dinner sorted."
        },
        {
          "time": "11-15s",
          "visual": "Friends eat together and the location appears.",
          "text": "Save this for your next evening out."
        }
      ],
      "caption": "Work done, notifications muted, and dinner finally has a plan. This Whitefield ramen spot is built for the kind of evening when you want something warm, social and easy without spending half the night deciding where to go. Save the Reel for your next after-work dinner and send it to the friend who always asks where everyone should eat.",
      "cta": "Save this Reel and send it to your post-work dinner person.",
      "keywords": [
        "ramen",
        "Whitefield",
        "Bangalore",
        "after-work dinner",
        "Japanese food",
        "noodles",
        "evening plan"
      ],
      "platform_fit": "Instagram Reel works here because the opening visual acts as a fast hook, the short scene changes support retention, and the final location card encourages saves and shares.",
      "risk_notes": [
        "Do not invent prices, offers or opening hours that were not supplied.",
        "Keep the location and product claims limited to the information in the brief."
      ]
    }"""


def test_valid_output_passes():
    result = evaluate_prediction(
        valid_output(),
        checks(),
    )

    assert result.hard == 1
    assert result.soft > 0.95
    assert not result.fail_reasons


def test_generic_output_fails():
    bad = """{
      "audience_insight": "Everyone loves great food.",
      "content_angle": "An amazing restaurant experience.",
      "hook": "Don't miss this amazing experience!",
      "format": "reel",
      "creative_concept": "Show the restaurant.",
      "script": [
        {
          "time": "0-3s",
          "visual": "Restaurant",
          "text": "Come visit"
        }
      ],
      "caption": "We are excited to welcome you to an amazing experience. Check us out today!",
      "cta": "Join us today.",
      "keywords": ["food", "fun", "restaurant", "amazing", "Bangalore"],
      "platform_fit": "This works on social media.",
      "risk_notes": []
    }"""

    result = evaluate_prediction(
        bad,
        checks(),
    )

    assert result.hard == 0
    assert result.soft < 0.8
    assert result.fail_reasons


def test_keyword_dump_does_not_game_content():
    bad = """{
      "audience_insight": "A generic content idea for users.",
      "content_angle": "A social media post about food.",
      "hook": "A new idea worth seeing tonight in Bangalore.",
      "format": "reel",
      "creative_concept": "Create a simple food video.",
      "script": [
        {
          "time": "0-3s",
          "visual": "Food shot",
          "text": "Ramen"
        },
        {
          "time": "3-6s",
          "visual": "Food shot",
          "text": "Whitefield"
        },
        {
          "time": "6-9s",
          "visual": "Food shot",
          "text": "Dinner"
        },
        {
          "time": "9-12s",
          "visual": "Food shot",
          "text": "Evening"
        },
        {
          "time": "12-15s",
          "visual": "Food shot",
          "text": "Save"
        }
      ],
      "caption": "This is a generic food caption that has enough length but does not meaningfully discuss the audience, intent, or actual content strategy for the requested experience.",
      "cta": "Save this.",
      "keywords": ["ramen", "Whitefield", "Bangalore", "evening", "dinner", "noodles", "food"],
      "platform_fit": "Instagram Reel uses save behavior and visual content.",
      "risk_notes": [
        "Do not invent facts.",
        "Keep claims accurate."
      ]
    }"""

    result = evaluate_prediction(
        bad,
        checks(),
    )

    assert result.hard == 0
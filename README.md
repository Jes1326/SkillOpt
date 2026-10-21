# 🚀 SkillOpt: Autonomous LLM Skill & Prompt Optimization

> An empirical study applying **Textual Gradient Descent** to automate prompt engineering for real-world domains: **Social Media Strategy Generation** and **Software QA Test Data Generation**.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Framework](https://img.shields.io/badge/Framework-Microsoft%20SkillOpt-8dbb3c)](https://github.com/microsoft/SkillOpt)
[![Target Model](https://img.shields.io/badge/Target%20Model-GPT--4o-purple)](https://openai.com)

---

## 📌 Overview

Traditional prompt engineering is manual, heuristic, and brittle: you tweak a sentence, test it on a couple of examples, and inadvertently cause regressions on other edge cases.

This project experiments with [Microsoft's SkillOpt](https://github.com/microsoft/SkillOpt) framework, which treats **the System Prompt (a Markdown file) as the trainable parameter** of an LLM agent—optimizing it iteratively through **natural language gradient descent**.

### 🧠 How It Works Under the Hood

```
                  ┌──────────────────────────────┐
                  │   Current Skill (Prompt)     │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                    [ Target Model Rollout ]
                    (GPT-4o runs batch tasks)
                                 │
                                 ▼
                   [ Programmatic Evaluator ]
                    (800+ lines of assertions)
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
             [ Passes ]                     [ Failures ]
                 │                               │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                     [ Multi-Worker Analysts ]
                (Diagnose root-cause failure modes)
                                 │
                                 ▼
                    [ Textual Gradient Patch ]
                 (Targeted edits to Skill Markdown)
                                 │
                                 ▼
                       [ Validation Gate ]
               Is candidate score > current score?
                    /                        \
                 [YES]                       [NO]
                   │                           │
          Accept New Skill               Reject & Re-try
```

1. **Target Rollout:** The frozen target model (`gpt-4o`) executes task briefs using the current skill document.
2. **Deterministic Evaluation:** A multi-check evaluator tests schema validity, domain constraints, platform signals, and banned phrases.
3. **Analyst Reflection:** Parallel LLM workers analyze execution trajectories and diagnose why the prompt fell short.
4. **Textual Gradient Patch:** The optimizer proposes minimal, targeted Markdown edits to the prompt.
5. **Validation Gate:** The candidate prompt is evaluated against a held-out validation set. If it doesn't strictly improve performance, it is rejected.

---

## 📊 Key Results at a Glance

| Environment | Baseline Pass Score | Evolved Skill Pass Score | Key Improvement |
| :--- | :---: | :---: | :--- |
| **Social Media Strategist** | `66.7%` | **`100.0%`** | Replaced generic fluff with split-screen hooks, objective-aligned CTAs, and algorithm retention mechanics. |
| **QA Test Data Generator** | `26.7%` | **`60.0%`** | Transformed basic tables into comprehensive SDET matrices covering positive, negative, boundary, and null cases. |

---

## 🔬 Case Study 1: Social Media Strategy Generator

### The Problem
Prompting an LLM to generate platform-native marketing strategies (TikTok, Instagram, LinkedIn) usually results in generic marketing cliches (*"don't miss out"*, *"something for everyone"*), weak hooks, and self-promotional calls-to-action.

### The Evaluator
We built a strict **800+ line programmatic evaluator** ([`skillopt/envs/social_media/evaluator.py`](skillopt/envs/social_media/evaluator.py)) that enforces:
* 11 mandatory JSON schema fields
* 16+ banned marketing cliches
* Platform-native signal checks (Instagram Reel retention, TikTok audio/split-screen, LinkedIn carousels)
* Objective-to-CTA semantic alignment

---

### 📝 System Prompt Evolution (Before vs. After)

#### ❌ Before: Initial Prompt (`initial.md`)
```markdown
# Social Media Content Strategist

You are a social media content strategist.
Your job is to turn a content brief into a useful social media content package.

Consider:
- target audience, objective, topic, brand tone, platform, constraints

Try to make the content engaging and specific.
Think about what would work on the selected platform.

Return exactly one JSON object with these fields:
{
  "audience_insight": "...", "content_angle": "...", "hook": "...",
  "format": "...", "creative_concept": "...", "script": [...],
  "caption": "...", "cta": "...", "keywords": [], "platform_fit": "...", "risk_notes": []
}

Avoid generic filler and follow the supplied constraints.
Do not use Markdown fences.
```

#### ✅ After: Evolved Prompt (`ckpt/social_media/gpt4o_best_skill.md`)
*SkillOpt analyzed failing rollouts and automatically synthesized these specific behavioral guidelines:*
```markdown
Strengthen hooks by ensuring a direct connection to the audience's interests
and the content brief's specific topic. Incorporate urgency or exclusivity
as appropriate to motivate immediate engagement.

Align CTAs closely with the stated objectives in the brief, emphasizing actionable
and specific outcomes that resonate with the platform's audience and purpose.

- Highlight relatable audience challenges or needs to foster a sense of connection upfront.
- Provide actionable insights or practical solutions aligned with audience goals.
- Use platform-native strengths, such as visual storytelling on Instagram or concise technical explanations on LinkedIn.
- Structure scripts progressively or in step-by-step formats to maintain engagement and clarity.
- Address all task constraints fully and directly, ensuring comprehensive coverage without over-simplification.
- Identify potential risks in content reception and propose ways to mitigate them effectively to maintain audience trust.

Enhance script depth by introducing storytelling elements and ensuring structured content delivery that resonates with the audience while explaining concepts clearly.
```

---

### ⚡ Real LLM Output Showdown (Task `sm19`)

**Brief:** TikTok video for *Edit Fast* targeting new video editors. Objective: *education*. Topic: *three editing shortcuts that save time*. Constraint: *Show exactly three shortcuts*.

| Dimension | ❌ Baseline Skill Output (Failed) | ✅ Optimized Skill Output (100% Pass) |
| :--- | :--- | :--- |
| **01. The Hook** | `"'Want to save HOURS editing? Here are 3 time-saving shortcuts every beginner needs!'"` *(Generic, quoted)* | `"Stop wasting time on video edits – here are 3 pro shortcuts you'll wish you knew yesterday!"` *(Direct pain-point + urgency)* |
| **02. The Script** | Generic shots of someone at a desk, smiling, and ending with a static logo screen. | **Split-screen format** showing the "slow manual way" vs the "fast shortcut way" with real hotkeys (`C` razor tool, `S` snap to timeline, `Alt + Drag` duplicate). |
| **03. Caption** | Generic hashtag dump: `🚀 Ready to edit faster? These 3 simple shortcuts will save you HOURS ⏳...` | **Interactive question**: `⏱️ Stop wasting time! Which one do YOU use the most? 👇💻 #VideoEditingTips` |
| **04. Call to Action** | `"Follow Edit Fast for more practical editing tips!"` ❌ *(Failed: Self-promotional follower pitch, failed objective check)* | `"Learn these shortcuts today and save time on your next edit – start now!"` ✅ *(Passed: Action-oriented & educational)* |
| **Hard Pass Score** | **66.7%** | **100.0%** |

---

## 🛠️ Case Study 2: QA Test Data Generator

### The Problem
Asking an LLM to generate test data for software testing typically yields superficial tables with only happy-path values, missing boundary conditions, empty strings, and special characters.

### The Evaluator
We built an SDET evaluator ([`skillopt/envs/testdatagen/evaluator.py`](skillopt/envs/testdatagen/evaluator.py)) that strictly inspects generated markdown tables for:
* Minimum 3 positive examples
* Minimum 2 negative examples (format, length, invalid character violations)
* Explicit boundary tests (min/max range limits)
* Null, empty string, and whitespace cases

---

### ⚡ Real Output Showdown (Field: `Aadhaar Number`)

**Requirements:** Mandatory, exactly 12 digits, numeric only, must not start with 0 or 1.

#### ❌ Baseline Output (Loosely structured):
```markdown
| Test Data    | Scenario              | Type    | Expected Result |
|--------------|-----------------------|---------|-----------------|
| 123456789012 | Valid Aadhaar Number  | Valid   | Accepted        |
| 123456789    | Less than 12 digits   | Invalid | Rejected        |
| 012345678901 | Starts with 0         | Invalid | Rejected        |
|              | Null/Empty value      | Invalid | Rejected        |
```

#### ✅ Optimized Output (Comprehensive SDET Matrix):
```markdown
| **Test Data**      | **Scenario**                                   | **Type**                    | **Expected Result** |
|---------------------|------------------------------------------------|-----------------------------|---------------------|
| **Positive Tests**  |                                                |                             |                     |
| 234567890123        | Valid Aadhaar, 12 digits, doesn't start with 0 | Positive Test               | Pass                |
| 345678901234        | Valid Aadhaar, 12 digits, doesn't start with 1 | Positive Test               | Pass                |
| **Boundary Tests**  |                                                |                             |                     |
| 200000000000        | Lower boundary: Starts with 2, 12 digits       | Boundary Test               | Pass                |
| 999999999999        | Upper boundary: Largest valid 12-digit number  | Boundary Test               | Pass                |
| **Negative Tests**  |                                                |                             |                     |
| 123456              | Length violation: Less than 12 digits          | Length Violation            | Fail                |
| 1234567890123       | Length violation: More than 12 digits          | Length Violation            | Fail                |
| 023456789012        | Starts with 0                                  | Format Violation            | Fail                |
| 98765@#$%^123       | Contains special characters                    | Special Character Violation | Fail                |
| NULL                | Explicit Null value                            | Null/Empty Violation        | Fail                |
| "   "               | Whitespace only string                         | Null/Empty Violation        | Fail                |
| +912345678901       | Contains plus sign prefix                      | Format Violation            | Fail                |
```

---

## 📂 Repository Structure

```
├── ckpt/                             # Saved Best Skill Checkpoints
│   ├── social_media/                 # Evolved Social Media Skill (gpt4o_best_skill.md)
│   └── testdatagen/                  # Evolved Test Data Gen Skill (gpt4o_best_skill.md)
├── configs/                          # Experiment YAML Configs
│   ├── social_media/default.yaml
│   └── testdatagen/default.yaml
├── data/                             # Train / Val / Test Splits
│   ├── social_media_split/
│   └── testdatagen/
├── skillopt/                         # Core SkillOpt Framework
│   └── envs/
│       ├── social_media/             # 800+ line Evaluator, Dataloader & Adapter
│       └── testdatagen/              # SDET Evaluator, Dataloader & Adapter
├── scripts/
│   ├── social_media_report.py        # Benchmark progression report generator
│   └── train.py                      # SkillOpt training entrypoint
├── tools/
│   ├── build_social_media_dataset.py # Synthetic benchmark dataset generator
│   └── compare_initial_final.py      # Pairwise before/after inference comparator
├── linkedin_carousel.html            # Interactive 3-Slide Visual Deck (1-Click PDF Export)
├── EXPERIMENT_SHOWCASE.md            # Deep-dive Case Study and Trajectory Logs
└── README.md
```

---

## ⚡ Quickstart & Reproduction

### 1. Installation
```bash
git clone https://github.com/Jes1326/SkillOpt.git
cd SkillOpt
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Credentials
Copy `.env.example` to `.env` and configure your LLM backend:
```env
OPENAI_API_KEY=your_key_here
# Or Azure OpenAI:
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

### 3. Run Evaluator Tests
```bash
python -m pytest tests/test_evaluator.py
```

### 4. Inspect Benchmark Report
```bash
python scripts/social_media_report.py --out_root outputs/skillopt_social_media_gpt-4o_20261007_181822 --split val
```

### 5. View Interactive Carousel Deck
Open [`linkedin_carousel.html`](linkedin_carousel.html) in your browser to view the 3-slide visual deck with 1-click PDF export for LinkedIn.

---

## 🙏 Acknowledgments

This research is built on top of Microsoft's open-source [SkillOpt](https://github.com/microsoft/SkillOpt) framework:
* *Paper:* "SkillOpt: Executive Strategy for Self-Evolving Agent Skills" (arXiv:2605.23904)
* *Authors:* Microsoft Research

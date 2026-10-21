# 🔬 Experiment Showcase: Automated Skill Optimization with SkillOpt

> An empirical study applying Microsoft's **SkillOpt** framework to automatically evolve, debug, and optimize LLM system prompts for real-world tasks using **Textual Gradient Descent**.

---

## 📌 1. What is SkillOpt and How Does It Work?

Traditional prompt engineering is manual, heuristic, and brittle: you tweak instructions, test against a few prompts, and inadvertently break other edge cases.

**SkillOpt** introduces an automated optimization loop that treats Markdown prompts as trainable weights:

```
                  ┌──────────────────────────────┐
                  │   Current Skill (Prompt)     │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                    [ Target Model Rollout ]
                                 │
                                 ▼
                   [ Programmatic Evaluator ]
                    (Hard & Soft Check Rules)
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
             [ Passes ]                     [ Failures ]
                 │                               │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                     [ Multi-Worker Analysts ]
                (Mine Failure Patterns & Critiques)
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

1. **Rollout:** The target LLM (`gpt-4o`) executes a batch of tasks using the current skill.
2. **Evaluation:** A deterministic, multi-check evaluator inspects schema, constraints, domain signals, and banned phrases.
3. **Analyst Reflection:** Parallel analyst agents examine the prompt, failures, and execution trajectories to propose minimal Markdown patches.
4. **Validation Gate:** Patches are evaluated against held-out validation tasks. Only patches that measurably improve performance are accepted.

---

## 🚀 Case Study 1: Social Media Strategy Generator

### 🎯 The Task
Generate structured social media strategy packages (hook, format, script, caption, CTA, keywords, platform-fit, risk notes) from marketing briefs across Instagram, TikTok, and LinkedIn.

### 📊 Metric Improvements
* **Selection Hard Score:** `66.7%` ➔ **`100.0%`** (all 22+ programmatic constraints satisfied)
* **Keyword & Goal Alignment:** Zero generic marketing cliches, 100% goal-relevant CTAs.

---

### 🔍 Skill Evolution (Original vs. Improved)

#### Original Skill (`initial.md`)
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

#### Automatically Evolved Skill (`gpt4o_best_skill.md`)
*SkillOpt identified failure modes (weak hooks, generic CTAs, shallow scripts) and synthesized these specific behavioral guidelines:*
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

### 🧪 Output Comparison on Same Brief (`sm19`)

**Brief:** TikTok video for *Edit Fast* targeting new video editors. Objective: *education*. Topic: *three editing shortcuts that save time*. Constraint: *Show exactly three shortcuts*.

| Element | Baseline Skill Output ❌ | Optimized Skill Output ✅ |
| :--- | :--- | :--- |
| **Hook** | `"'Want to save HOURS editing? Here are 3 time-saving shortcuts every beginner needs!'"` *(Generic, quoted)* | `"Stop wasting time on video edits – here are 3 pro shortcuts you'll wish you knew yesterday!"` *(Urgency + emotional hook)* |
| **Script Execution** | Generic shots of someone at a desk, smiling, and showing a logo slide. | **Split-screen format** showing the "slow way" vs the "shortcut way" with real hotkeys (`C` razor tool, `S` snap to timeline, `Alt + Drag` duplicate). |
| **Caption** | Generic hashtag dump: `🚀 Ready to edit faster? These 3 simple shortcuts will save you HOURS...` | **Interactive question**: `⏱️ Stop wasting time! Which one do YOU use the most? 👇💻 #VideoEditingTips` |
| **Call To Action** | `"Follow Edit Fast for more practical editing tips!"` *(Fails objective alignment check: self-promotional, not educational)* | `"Learn these shortcuts today and save time on your next edit – start now!"` *(Passes check: action-oriented & educational)* |
| **Evaluator Verdict** | **FAILED** (Keyword specificity & CTA alignment failed) | **PASSED (100% hard score)** |

---

## 🛠️ Case Study 2: QA Test Data Generator

### 🎯 The Task
Given a database or form field specification with business validation rules, generate a complete test data table covering positive, negative, boundary, and null/whitespace test cases.

### 📊 Metric Improvements
* **Selection Hard Score:** `0.0%` ➔ **`100.0%`**
* **Test Soft Coverage Score:** `26.7%` ➔ **`60.0%`** (systematic edge-case coverage)

---

### 🔍 Skill Evolution (Original vs. Improved)

#### Original Skill (`initial.md`)
```markdown
Generate test data for the given field.

Output a markdown table.

Include some valid and invalid test data.
```

#### Automatically Evolved Skill (`gpt4o_best_skill.md`)
```markdown
Generate test data for the given field. Output a markdown table.
Include some valid and invalid test data.

Ensure the table includes a minimum of 3 positive examples for each validation category
and systematically covers all boundary values, negative cases, null/empty values, and format violations.

Ensure your markdown table includes:
- **Positive Tests**: Provide sufficient valid cases that satisfy all field validations. Include a minimum of 3 examples for each validation category.
- **Negative Tests**: Include a variety of invalid test cases that violate different field validations (e.g., special characters, incorrect format, length violations, null/empty values in mandatory fields, etc.).
- **Boundary Tests**: Cover edge cases for minimum and maximum input boundaries (e.g., shortest valid input, longest valid input, numerical range edges).

### Additional Guidelines
- For numeric fields, include valid positive values, edge cases at the boundaries, and invalid cases outside the range.
- For alphanumeric fields, include valid combinations, edge cases near length boundaries, and invalid inputs violating format rules.
- For mandatory fields, explicitly test null, empty, and whitespace values.
- Ensure representation of special characters in invalid cases.
```

---

### 🧪 Output Comparison on Same Field (`test_001`: Aadhaar Number)

**Requirements:** Mandatory, exactly 12 digits, numeric only, must not start with 0 or 1.

#### Baseline Skill Output (Loosely structured):
```markdown
| Test Data    | Scenario              | Type    | Expected Result |
|--------------|-----------------------|---------|-----------------|
| 123456789012 | Valid Aadhaar Number  | Valid   | Accepted        |
| 123456789    | Less than 12 digits   | Invalid | Rejected        |
| 012345678901 | Starts with 0         | Invalid | Rejected        |
|              | Null/Empty value      | Invalid | Rejected        |
```
*Shortcomings: Only labeled generic `Valid`/`Invalid`. Lacked explicit boundary verification and missed structured classification.*

#### Optimized Skill Output (Comprehensive SDET Matrix):
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
*Major upgrades: Sectioned into positive/boundary/negative tests, granular violation tags (`Length`, `Format`, `Null/Empty`), and edge-case boundary values.*

---

## 🔬 Reproducing the Results

1. **Verify Evaluators:**
   ```bash
   python -m pytest tests/test_evaluator.py
   ```

2. **Inspect the Benchmark Report:**
   ```bash
   python scripts/social_media_report.py --out_root outputs/skillopt_social_media_gpt-4o_20261007_181822 --split val
   ```

3. **Re-generate Dataset:**
   ```bash
   python tools/build_social_media_dataset.py
   ```


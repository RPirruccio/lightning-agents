---
name: slides-review
description: Use when reviewing presentations for quality issues. Covers visual design, content clarity, flow, and technical accuracy.
---

# Slides Review

Expert presentation review workflow with parallel per-slide analysis capabilities.

## Quick Start

1. **Extract slide images** using `extract_slide_images` tool
2. **Review each slide** for visual, content, and design issues
3. **Report findings** with prioritized recommendations

## When to Use This Skill

- Reviewing presentation PDFs for AIMUG lightning talks
- Quality-checking slide decks before delivery
- Identifying visual design problems
- Validating technical content accuracy
- Ensuring consistent styling across slides

## Two Review Modes

### Mode 1: Quick Review
For fast feedback on a complete presentation:
- Use `Read` tool on the PDF directly
- Provide high-level assessment
- Good for initial checks or simple decks

### Mode 2: Deep Parallel Analysis (Orchestration Mode)
For thorough per-slide review:

1. **Extract slides to images**
   ```
   extract_slide_images(pdf_path="presentation/output/lightning-agents.pdf")
   ```
   This converts the PDF to individual PNG files for detailed analysis.

2. **Parallel per-slide checking**
   Use `run_agent` to spawn multiple review instances, each focusing on one slide:
   ```
   run_agent(
     agent_id="slides_checker",
     prompt="Review slide image at presentation/output/slides/slide_3.png.
             Focus on visual clarity, content accuracy, and design quality.
             Be specific about issues found."
   )
   ```

3. **Synthesize feedback**
   Combine all sub-agent reports into a unified assessment with:
   - Overall rating
   - Strengths found
   - Issues categorized by priority
   - Top 3 priority fixes

## Review Framework

Evaluate each slide across three dimensions:

### 1. Visual Clarity
- **Text readability**: Font size, contrast, density
- **Layout**: Whitespace usage, element alignment
- **Image/chart quality**: Resolution, relevance, clarity
- **Consistency**: Styling across slides

### 2. Content Quality
- **Clear messaging**: Each slide has a focused point
- **Accuracy**: Information is correct and up-to-date
- **Detail level**: Appropriate depth for audience
- **Completeness**: No missing or broken elements

### 3. Design Quality
- **Professional appearance**: Clean, polished look
- **Theme consistency**: Colors, fonts, styles aligned
- **Visual effectiveness**: Diagrams/images enhance understanding
- **Accessibility**: Color contrast, font legibility

For detailed visual design criteria, see [VISUAL_GUIDE.md](references/VISUAL_GUIDE.md).

## Output Format

Structure your review as:

```
## Overall Assessment
[2-3 sentence summary with rating: Excellent/Good/Needs Work/Major Revision]

## Strengths
- What works well (3-5 bullet points)

## Issues Found
Categorized by priority:

### Critical (Must Fix)
- [SLIDE N] Specific issue description
- [SLIDE M] Another issue

### Important (Should Fix)
- [SLIDE X] Layout problem
- [SLIDE Y] Content clarity issue

### Minor (Nice to Fix)
- [SLIDE Z] Suggestion for improvement

## Priority Fixes
Top 3 changes for biggest impact:
1. [Fix description with slide numbers]
2. [Second priority fix]
3. [Third priority fix]
```

## Common Issues Checklist

When reviewing, look for:

- [ ] Missing or broken images/icons
- [ ] Text too small to read from distance
- [ ] Inconsistent fonts or colors
- [ ] Cluttered layouts with too much content
- [ ] Poor contrast between text and background
- [ ] Typos or spelling errors
- [ ] Inaccurate technical information
- [ ] Misaligned elements
- [ ] Unclear diagrams or charts
- [ ] Missing slide titles
- [ ] Inconsistent footer/header styling

## Review Guidelines

1. **Be constructive and specific**
   - Bad: "Slide 3 looks bad"
   - Good: "[SLIDE 3] Text density too high - reduce bullet points from 8 to 4 key points"

2. **Prioritize by audience impact**
   - Fix critical issues (broken content, errors) first
   - Then address important issues (clarity, layout)
   - Finally consider minor improvements

3. **Check for technical accuracy**
   - Verify code snippets are syntactically correct
   - Ensure diagrams accurately represent concepts
   - Validate claims and statistics

4. **Consider the presentation context**
   - AIMUG lightning talks: 5-10 minutes (5-10 slides)
   - Technical depth appropriate for audience
   - Code examples are relevant and clear

## Orchestration Tips

When using Mode 2 (parallel analysis):

1. **Distribute work efficiently**: Assign one slide per sub-agent call
2. **Use specific prompts**: Tell each sub-agent which slide number to focus on
3. **Track progress**: Label runs clearly (e.g., "check_slide_3", "check_slide_7")
4. **Synthesize thoughtfully**: Don't just concatenate - prioritize and group similar issues

## Example Workflow

```
User: "Review presentation/output/lightning-agents.pdf"

You:
1. extract_slide_images(pdf_path="presentation/output/lightning-agents.pdf")
2. Spawn 13 parallel reviews (one per slide)
3. Collect feedback from all sub-agents
4. Synthesize into structured report
5. Output: Overall assessment + categorized issues + priority fixes
```

## Integration with Other Agents

This skill works best when combined with:

- **presentation_slide_writer**: Apply fixes based on review findings
- **slides_quality_loop**: Automate review → fix → regenerate cycles
- **tool_architect**: Create new review tools for specific checks

## References

- [VISUAL_GUIDE.md](references/VISUAL_GUIDE.md) - Detailed visual design criteria
- `/Users/riccardopirruccio/CODE_PROJECTS/lightning-agents/db/agents.json` - `slides_checker` agent definition
- AIMUG presentation guidelines: 5-10 minute lightning talks

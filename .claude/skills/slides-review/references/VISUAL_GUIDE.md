# Visual Design Guide for Slide Review

Detailed criteria for evaluating presentation visual quality.

## Typography

### Font Size
- **Title text**: Minimum 36pt, ideally 44pt+
- **Body text**: Minimum 24pt, ideally 28pt+
- **Code snippets**: Minimum 18pt, ideally 20pt+
- **Footer/attribution**: Minimum 14pt

**Why it matters**: Slides must be readable from the back of a room. Small text fails.

### Font Readability
✅ **Good choices**: Sans-serif fonts (Arial, Helvetica, Calibri, Open Sans)
❌ **Avoid**: Script fonts, decorative fonts, narrow condensed fonts

### Text Density
- **Maximum bullet points per slide**: 4-6
- **Maximum words per bullet**: 10-15
- **Maximum lines per slide**: 6-8

**Red flags**:
- Paragraphs of text
- More than 7 bullets on a slide
- Bullets wrapping to 3+ lines

### Text Hierarchy
Clear visual hierarchy using:
- Font size variation (title > subtitle > body)
- Weight variation (bold for emphasis)
- Color variation (consistent with theme)

## Color Contrast

### Text Contrast Ratios
Per WCAG 2.1 guidelines:
- **Normal text**: Minimum 4.5:1 contrast ratio
- **Large text** (18pt+): Minimum 3:1 contrast ratio
- **Optimal**: 7:1 or higher for maximum readability

### Common Problems
❌ Light gray text on white background
❌ Dark blue text on black background
❌ Yellow text on white background
❌ Low-opacity overlays obscuring text

✅ **Safe combinations**:
- Black on white
- White on dark blue/navy
- Dark gray (#333) on light gray (#F5F5F5)
- White on teal/green (dark shades)

### Testing Contrast
Ask yourself: "Can I read this in bright room lighting or on a projector?"

## Layout Balance

### Whitespace Usage
Good slides have **breathing room**:
- Margins: Minimum 0.5" on all sides
- Space between elements: At least 0.25"
- Don't fill every pixel

**Rule of thumb**: 40-50% of slide should be empty space

### Element Alignment
All elements should align to a grid:
- Titles aligned consistently (usually left or center)
- Bullets aligned with consistent indentation
- Images aligned to slide edges or center
- Consistent positioning across slides

**Red flags**:
- Text boxes slightly misaligned between slides
- Images floating randomly
- Inconsistent title positions

### Visual Weight Distribution
Avoid:
- All content crammed to one side
- Bottom-heavy slides
- Unbalanced text-to-image ratios

Aim for:
- Centered or evenly distributed content
- Focal point in upper-left to center area
- Balanced use of text and visuals

## Image Quality

### Resolution Standards
- **Minimum**: 72 DPI for screen presentations
- **Optimal**: 150 DPI for crisp display
- **Size**: Images should not appear pixelated when projected

**Test**: Zoom to 100% in PowerPoint - if blurry, resolution is too low

### Image Relevance
Every image should:
- Directly support the content
- Add understanding (not just decoration)
- Be clearly visible and recognizable

❌ **Avoid**:
- Tiny icons that don't convey meaning
- Decorative clip art
- Low-quality screenshots
- Watermarked stock photos

### Image Integration
✅ **Good practices**:
- Images have consistent styling (borders, shadows)
- Screenshots are cropped to relevant area
- Diagrams use consistent color palette
- Icons are similar style (all flat, all outlined, etc.)

## Diagram Clarity

### Diagram Elements
Effective diagrams have:
- **Clear labels**: Large enough to read, positioned logically
- **Visual hierarchy**: Important elements stand out
- **Directional flow**: Arrows or connectors show relationships
- **Color coding**: Consistent colors for related concepts

### Common Diagram Issues
❌ Too many elements (aim for 3-7 main components)
❌ Unclear connections between elements
❌ Inconsistent shapes/styles
❌ Missing labels or legends
❌ Overlapping text or arrows

### Diagram Types to Consider

**Flow diagrams**: Show process or sequence
- Use arrows to indicate direction
- Keep to 4-6 steps maximum
- Highlight key decision points

**Architecture diagrams**: Show system structure
- Group related components
- Use boxes/shapes consistently
- Show clear boundaries/layers

**Comparison diagrams**: Show differences
- Side-by-side layout
- Highlight contrasting elements
- Use color to distinguish categories

## Code Presentation

### Code Readability
- **Font**: Monospace (Courier New, Consolas, Monaco)
- **Size**: 18-20pt minimum
- **Lines**: Maximum 10-12 lines per slide
- **Width**: Maximum 70-80 characters per line

### Syntax Highlighting
✅ **Use syntax highlighting** for:
- Python, JavaScript, etc.
- Consistent color scheme (e.g., Monokai, VS Code Dark)

❌ **Avoid**:
- Plain black text with no highlighting
- Light color schemes on white background
- Too many colors (keep it simple)

### Code Context
Every code slide should:
- Have a descriptive title
- Show only relevant code (trim boilerplate)
- Include comments for non-obvious parts
- Fit on one slide (no scrolling needed)

## Consistency Checks

### Theme Consistency
Verify across all slides:
- [ ] Same background color/pattern
- [ ] Same font family throughout
- [ ] Same title positioning
- [ ] Same footer/header style
- [ ] Same bullet point style
- [ ] Same code block styling

### Color Palette
Stick to 3-5 main colors:
- Primary: Main brand or theme color
- Secondary: Accent color
- Neutral: Text color (black/dark gray)
- Background: White or light color
- Highlight: For emphasis (sparingly)

**Red flag**: Using 10+ different colors randomly

### Slide Template
All slides should follow the same template:
- Title placement
- Content area boundaries
- Footer information
- Logo/branding position

## Accessibility Guidelines

### Color Blindness
Don't rely on color alone to convey meaning:
- Use patterns or shapes in addition to color
- Label chart elements explicitly
- Test with color blindness simulator if possible

### Readability
- High contrast text
- Large, clear fonts
- Avoid all-caps for body text (harder to read)
- Use bullet points, not dense paragraphs

### Cognitive Load
- One main idea per slide
- Progressive disclosure (reveal info step by step)
- Clear visual hierarchy guides the eye

## Presentation Context: AIMUG Lightning Talks

### Time Constraints
5-10 minute talks = 5-10 slides:
- Title slide
- 3-7 content slides
- Closing/thank you slide

### Technical Audience Considerations
- Code examples should be production-quality
- Diagrams should be technically accurate
- Avoid oversimplification that misleads
- Include references/links for further reading

### Engagement Elements
- Use diagrams to explain complex concepts
- Show code snippets, not walls of text
- Include visual examples or demos
- Keep text minimal, speak to the details

## Common Visual Anti-Patterns

### 1. The "Wall of Text" Slide
**Problem**: Entire paragraphs on a slide
**Fix**: Extract 3-4 key bullet points, speak the rest

### 2. The "Tiny Font" Slide
**Problem**: Font too small to read from distance
**Fix**: Increase to 24pt minimum, reduce content

### 3. The "Rainbow Explosion" Slide
**Problem**: Too many colors with no purpose
**Fix**: Limit to 3-5 colors, use consistently

### 4. The "Pixelated Image" Slide
**Problem**: Low-resolution images look unprofessional
**Fix**: Use higher-res images or vector graphics

### 5. The "Cluttered Diagram" Slide
**Problem**: 15+ boxes with tiny text and crossing arrows
**Fix**: Simplify to 5-7 main elements, split into multiple slides

### 6. The "Invisible Code" Slide
**Problem**: Light gray code on white background
**Fix**: Use dark background with light text or proper syntax highlighting

### 7. The "Misaligned Mess" Slide
**Problem**: Elements randomly positioned
**Fix**: Use alignment guides, snap to grid

## Quick Visual Checklist

Before approving a presentation, verify:

**Typography**
- [ ] All text is 24pt or larger (except footer)
- [ ] Fonts are consistent throughout
- [ ] No more than 6 bullets per slide
- [ ] Text hierarchy is clear

**Color & Contrast**
- [ ] Text has high contrast with background
- [ ] Color palette is consistent (3-5 colors)
- [ ] Colors serve a purpose, not decoration

**Layout**
- [ ] Elements are aligned to grid
- [ ] Adequate whitespace (40-50%)
- [ ] Consistent positioning across slides

**Images & Diagrams**
- [ ] All images are high resolution
- [ ] Diagrams are clear and labeled
- [ ] Visual style is consistent

**Code**
- [ ] Code is 18pt+ with syntax highlighting
- [ ] Maximum 10-12 lines per slide
- [ ] Code is relevant and readable

**Consistency**
- [ ] All slides follow same template
- [ ] Theme is consistent throughout
- [ ] Styling is uniform

**Accessibility**
- [ ] Color is not the only way to convey meaning
- [ ] High contrast for all text
- [ ] One main idea per slide

## Tools & Resources

### Contrast Checkers
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Coolors Contrast Checker: https://coolors.co/contrast-checker

### Color Palette Tools
- Adobe Color: https://color.adobe.com
- Coolors: https://coolors.co

### Design References
- Presentation Zen (book by Garr Reynolds)
- WCAG 2.1 Accessibility Guidelines
- Google Material Design Guidelines

## Summary

Great presentation visuals are:
1. **Readable**: Large fonts, high contrast, clear hierarchy
2. **Balanced**: Good use of whitespace, aligned elements
3. **Consistent**: Same theme, colors, and styling throughout
4. **Clear**: Simple diagrams, relevant images, focused content
5. **Accessible**: Works for color blindness, readable from distance

When in doubt, simplify. Less is more in presentation design.

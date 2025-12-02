"""
Generate PowerPoint presentation for Lightning Agents talk.

Usage:
    uv sync --extra presentation
    uv run python -m presentation.generate_slides
"""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from .slide_content import SLIDES, DIAGRAMS
from .styles import COLORS, FONTS, SIZES, DIMS


def rgb(color_key: str) -> RGBColor:
    """Convert color key to RGBColor."""
    hex_color = COLORS.get(color_key, color_key)
    return RGBColor.from_string(hex_color)


def add_slide_title(slide, title_text: str) -> None:
    """Add a consistent title to any slide."""
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.4),
        Inches(DIMS["width"] - 1), Inches(1)
    )
    tf = title_box.text_frame
    tf.paragraphs[0].text = title_text
    tf.paragraphs[0].font.size = Pt(SIZES["heading"])
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = rgb("text_dark")
    tf.paragraphs[0].font.name = FONTS["title"]


def add_title_slide(prs: Presentation, data: dict) -> None:
    """Add a centered title slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

    # Main title
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(2.5),
        Inches(DIMS["width"] - 1), Inches(1.5)
    )
    tf = title_box.text_frame
    tf.paragraphs[0].text = data["title"]
    tf.paragraphs[0].font.size = Pt(SIZES["title"])
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = rgb("primary")
    tf.paragraphs[0].font.name = FONTS["title"]
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Subtitle
    if "subtitle" in data:
        sub_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(4.2),
            Inches(DIMS["width"] - 1), Inches(1)
        )
        tf = sub_box.text_frame
        tf.paragraphs[0].text = data["subtitle"]
        tf.paragraphs[0].font.size = Pt(SIZES["subtitle"])
        tf.paragraphs[0].font.color.rgb = rgb("text_light")
        tf.paragraphs[0].font.name = FONTS["body"]
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Footer
    if "footer" in data:
        footer_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(6.5),
            Inches(DIMS["width"] - 1), Inches(0.5)
        )
        tf = footer_box.text_frame
        tf.paragraphs[0].text = data["footer"]
        tf.paragraphs[0].font.size = Pt(SIZES["small"])
        tf.paragraphs[0].font.color.rgb = rgb("secondary")
        tf.paragraphs[0].font.name = FONTS["body"]
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER


def add_bullet_slide(prs: Presentation, data: dict) -> None:
    """Add a slide with bullet points."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    add_slide_title(slide, data["title"])

    # Bullets
    bullet_box = slide.shapes.add_textbox(
        Inches(1), Inches(1.6),
        Inches(DIMS["width"] - 2), Inches(5.5)
    )
    tf = bullet_box.text_frame
    tf.word_wrap = True

    for i, bullet in enumerate(data["bullets"]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"  {bullet}"
        p.font.size = Pt(SIZES["body"])
        p.font.color.rgb = rgb("text_dark")
        p.font.name = FONTS["body"]
        p.space_before = Pt(16)
        p.level = 0


def add_code_slide(prs: Presentation, data: dict) -> None:
    """Add a slide with a code block."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_title(slide, data["title"])

    # Code box background
    code_bg = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.8), Inches(1.6),
        Inches(DIMS["width"] - 1.6), Inches(5.4)
    )
    code_bg.fill.solid()
    code_bg.fill.fore_color.rgb = rgb("code_bg")
    code_bg.line.color.rgb = rgb("text_light")

    # Code text
    code_box = slide.shapes.add_textbox(
        Inches(1.0), Inches(1.8),
        Inches(DIMS["width"] - 2), Inches(5)
    )
    tf = code_box.text_frame
    tf.word_wrap = False

    lines = data["code"].split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = FONTS["code"]
        p.font.size = Pt(SIZES["code"])
        p.font.color.rgb = rgb("text_dark")


def add_code_comparison_slide(prs: Presentation, data: dict) -> None:
    """Add a slide with side-by-side code comparison."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_title(slide, data["title"])

    half_width = (DIMS["width"] - 1.5) / 2

    # Left side
    left_title = slide.shapes.add_textbox(
        Inches(0.5), Inches(1.5),
        Inches(half_width), Inches(0.5)
    )
    tf = left_title.text_frame
    tf.paragraphs[0].text = data["left_title"]
    tf.paragraphs[0].font.size = Pt(SIZES["body"])
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = rgb("text_light")
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    left_bg = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.5), Inches(2.0),
        Inches(half_width), Inches(4.5)
    )
    left_bg.fill.solid()
    left_bg.fill.fore_color.rgb = rgb("code_bg")
    left_bg.line.color.rgb = rgb("text_light")

    left_code = slide.shapes.add_textbox(
        Inches(0.7), Inches(2.2),
        Inches(half_width - 0.4), Inches(4.1)
    )
    tf = left_code.text_frame
    for i, line in enumerate(data["left_code"].split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = FONTS["code"]
        p.font.size = Pt(SIZES["code"])
        p.font.color.rgb = rgb("text_dark")

    # Right side
    right_x = 0.5 + half_width + 0.5

    right_title = slide.shapes.add_textbox(
        Inches(right_x), Inches(1.5),
        Inches(half_width), Inches(0.5)
    )
    tf = right_title.text_frame
    tf.paragraphs[0].text = data["right_title"]
    tf.paragraphs[0].font.size = Pt(SIZES["body"])
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = rgb("secondary")
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    right_bg = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(right_x), Inches(2.0),
        Inches(half_width), Inches(4.5)
    )
    right_bg.fill.solid()
    right_bg.fill.fore_color.rgb = rgb("code_bg")
    right_bg.line.color.rgb = rgb("secondary")

    right_code = slide.shapes.add_textbox(
        Inches(right_x + 0.2), Inches(2.2),
        Inches(half_width - 0.4), Inches(4.1)
    )
    tf = right_code.text_frame
    for i, line in enumerate(data["right_code"].split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = FONTS["code"]
        p.font.size = Pt(SIZES["code"])
        p.font.color.rgb = rgb("text_dark")


def add_diagram_slide(prs: Presentation, data: dict) -> None:
    """Add a slide with a flow diagram."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_title(slide, data["title"])

    diagram = DIAGRAMS[data["diagram_id"]]

    # Draw boxes
    for box in diagram["boxes"]:
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(box["x"]), Inches(box["y"]),
            Inches(2.2), Inches(1.4)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(box["color"])
        shape.line.color.rgb = rgb(box["color"])

        # Text in box
        tf = shape.text_frame
        tf.paragraphs[0].text = box["label"]
        tf.paragraphs[0].font.size = Pt(16)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = rgb("white")
        tf.paragraphs[0].font.name = FONTS["body"]
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        tf.anchor = MSO_ANCHOR.MIDDLE

    # Draw arrows between boxes
    for start_idx, end_idx in diagram["arrows"]:
        start_box = diagram["boxes"][start_idx]
        end_box = diagram["boxes"][end_idx]

        # Horizontal arrow
        if abs(start_box["y"] - end_box["y"]) < 0.5:
            arrow = slide.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW,
                Inches(start_box["x"] + 2.3),
                Inches(start_box["y"] + 0.55),
                Inches(end_box["x"] - start_box["x"] - 2.5),
                Inches(0.3)
            )
        else:
            # Vertical arrow (down)
            arrow = slide.shapes.add_shape(
                MSO_SHAPE.DOWN_ARROW,
                Inches(start_box["x"] + 0.95),
                Inches(start_box["y"] + 1.5),
                Inches(0.3),
                Inches(end_box["y"] - start_box["y"] - 1.6)
            )

        arrow.fill.solid()
        arrow.fill.fore_color.rgb = rgb("text_light")
        arrow.line.fill.background()


def add_closing_slide(prs: Presentation, data: dict) -> None:
    """Add a closing slide with resources."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(1.5),
        Inches(DIMS["width"] - 1), Inches(1.5)
    )
    tf = title_box.text_frame
    tf.paragraphs[0].text = data["title"]
    tf.paragraphs[0].font.size = Pt(SIZES["title"])
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = rgb("primary")
    tf.paragraphs[0].font.name = FONTS["title"]
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Bullets (centered)
    bullet_box = slide.shapes.add_textbox(
        Inches(2), Inches(3.0),
        Inches(DIMS["width"] - 4), Inches(3)
    )
    tf = bullet_box.text_frame

    for i, bullet in enumerate(data["bullets"]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = bullet
        p.font.size = Pt(SIZES["body"])
        p.font.color.rgb = rgb("text_dark")
        p.font.name = FONTS["body"]
        p.space_before = Pt(16)
        p.alignment = PP_ALIGN.CENTER

    # Footer
    if "footer" in data:
        footer_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(6.5),
            Inches(DIMS["width"] - 1), Inches(0.5)
        )
        tf = footer_box.text_frame
        tf.paragraphs[0].text = data["footer"]
        tf.paragraphs[0].font.size = Pt(SIZES["small"])
        tf.paragraphs[0].font.color.rgb = rgb("secondary")
        tf.paragraphs[0].font.name = FONTS["body"]
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER


def create_presentation() -> Path:
    """Generate the complete presentation."""
    prs = Presentation()
    prs.slide_width = Inches(DIMS["width"])
    prs.slide_height = Inches(DIMS["height"])

    for slide_data in SLIDES:
        slide_type = slide_data["type"]

        if slide_type == "title":
            add_title_slide(prs, slide_data)
        elif slide_type == "bullets":
            add_bullet_slide(prs, slide_data)
        elif slide_type == "diagram":
            add_diagram_slide(prs, slide_data)
        elif slide_type == "code":
            add_code_slide(prs, slide_data)
        elif slide_type == "code_comparison":
            add_code_comparison_slide(prs, slide_data)
        elif slide_type == "closing":
            add_closing_slide(prs, slide_data)

    # Save
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "lightning-agents.pptx"
    prs.save(output_path)

    print(f"Presentation saved to: {output_path}")
    return output_path


def main():
    """CLI entry point."""
    create_presentation()


if __name__ == "__main__":
    main()

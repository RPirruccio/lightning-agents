"""
Presentation tools - Create and manage PPTX slides.

These tools let agents work on presentations directly:
- Generate PPTX from slide_content.py
- List, add, update, delete slides
- Manipulate the SLIDES list in slide_content.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from claude_agent_sdk import tool


def get_presentation_dir() -> Path:
    """Get the presentation directory."""
    return Path(__file__).parent.parent.parent.parent / "presentation"


def get_slide_content_path() -> Path:
    """Get path to slide_content.py."""
    return get_presentation_dir() / "slide_content.py"


def load_slides_and_diagrams() -> tuple[list[dict], dict]:
    """Load SLIDES and DIAGRAMS from slide_content.py using importlib."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("slide_content", get_slide_content_path())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, "SLIDES", []), getattr(module, "DIAGRAMS", {})


def save_slides(slides: list[dict], diagrams: dict) -> None:
    """Save SLIDES list back to slide_content.py."""
    path = get_slide_content_path()

    # Helper to format Python dicts nicely
    def format_value(v, indent=0):
        spaces = "    " * indent
        if isinstance(v, dict):
            if not v:
                return "{}"
            items = []
            for k, val in v.items():
                items.append(f'{spaces}    "{k}": {format_value(val, indent + 1)}')
            return "{\n" + ",\n".join(items) + f"\n{spaces}}}"
        elif isinstance(v, list):
            if not v:
                return "[]"
            if all(isinstance(x, str) for x in v):
                # Short string list on one line
                return "[" + ", ".join(f'"{x}"' for x in v) + "]"
            items = [f"{spaces}    {format_value(x, indent + 1)}" for x in v]
            return "[\n" + ",\n".join(items) + f"\n{spaces}]"
        elif isinstance(v, str):
            if "\n" in v:
                return f"'''{v}'''"
            return f'"{v}"'
        elif isinstance(v, bool):
            return "True" if v else "False"
        elif v is None:
            return "None"
        else:
            return str(v)

    # Format SLIDES
    slides_items = []
    for slide in slides:
        slides_items.append(format_value(slide, 1))
    slides_str = "[\n" + ",\n".join(slides_items) + "\n]"

    # Format DIAGRAMS
    diagrams_str = format_value(diagrams, 0)

    output = f'''"""
Slide content definitions.

Edit this file to update presentation content.
Run `uv run python -m presentation.generate_slides` to regenerate.
"""

SLIDES = {slides_str}

# Diagram definitions for visual slides
DIAGRAMS = {diagrams_str}
'''

    path.write_text(output)


@tool("generate_pptx", "Generate PowerPoint presentation and PDF from current slides", {})
async def generate_pptx(args: dict) -> dict:
    """Run the slide generator to create PPTX and PDF."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "presentation.generate_slides"],
            cwd=str(get_presentation_dir().parent),
            capture_output=True,
            text=True,
            timeout=120,  # PDF conversion can take longer
        )

        if result.returncode != 0:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error generating presentation:\n{result.stderr}"
                }],
                "isError": True
            }

        output_dir = get_presentation_dir() / "output"
        pptx_path = output_dir / "lightning-agents.pptx"
        pdf_path = output_dir / "lightning-agents.pdf"

        output_text = "Generated presentation successfully!\n\n"
        output_text += f"PPTX: {pptx_path}\n"
        if pdf_path.exists():
            output_text += f"PDF: {pdf_path}\n"
        else:
            output_text += "PDF: skipped (install LibreOffice or use Keynote)\n"
        output_text += f"\n{result.stdout}"

        return {
            "content": [{
                "type": "text",
                "text": output_text
            }]
        }
    except subprocess.TimeoutExpired:
        return {
            "content": [{"type": "text", "text": "Timeout generating presentation"}],
            "isError": True
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {e}"}],
            "isError": True
        }


@tool("list_slides", "List all slides with their titles and types", {})
async def list_slides(args: dict) -> dict:
    """List current slides."""
    try:
        slides, _ = load_slides_and_diagrams()

        result = f"Current presentation has {len(slides)} slides:\n\n"
        for i, slide in enumerate(slides):
            slide_type = slide.get("type", "unknown")
            title = slide.get("title", slide.get("subtitle", "Untitled"))

            # Show preview based on type
            preview = ""
            if slide_type == "bullets" and "bullets" in slide:
                preview = f" ({len(slide['bullets'])} bullets)"
            elif slide_type == "code":
                preview = f" ({slide.get('language', 'code')})"
            elif slide_type == "diagram":
                preview = f" (diagram: {slide.get('diagram_id', '?')})"

            result += f"  [{i}] {slide_type}: {title}{preview}\n"

        return {"content": [{"type": "text", "text": result}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error reading slides: {e}"}],
            "isError": True
        }


@tool(
    "add_slide",
    "Add a new slide at a specific position",
    {
        "position": int,
        "slide_type": str,
        "title": str,
        "content": dict,
    }
)
async def add_slide(args: dict) -> dict:
    """Add a new slide.

    Args:
        position: Index to insert at (0 = first, -1 = last)
        slide_type: One of: title, bullets, code, code_comparison, diagram, closing
        title: Slide title
        content: Additional fields based on type:
            - bullets: {"bullets": ["point1", "point2"]}
            - code: {"code": "...", "language": "python"}
            - code_comparison: {"left_title": "", "left_code": "", "right_title": "", "right_code": ""}
            - diagram: {"diagram_id": "my_diagram"}
            - title: {"subtitle": "", "footer": ""}
            - closing: {"bullets": [], "footer": ""}
    """
    try:
        slides, diagrams = load_slides_and_diagrams()
        position = args["position"]

        # Build slide dict
        slide = {
            "type": args["slide_type"],
            "title": args["title"],
        }

        # Merge additional content
        content = args.get("content", {})
        slide.update(content)

        # Insert at position
        if position == -1 or position >= len(slides):
            slides.append(slide)
            position = len(slides) - 1
        else:
            slides.insert(position, slide)

        save_slides(slides, diagrams)

        return {
            "content": [{
                "type": "text",
                "text": f"Added {args['slide_type']} slide at position {position}:\n\n{json.dumps(slide, indent=2)}\n\nRun generate_pptx to create the updated presentation."
            }]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error adding slide: {e}"}],
            "isError": True
        }


@tool(
    "update_slide",
    "Update an existing slide by index",
    {
        "index": int,
        "updates": dict,
    }
)
async def update_slide(args: dict) -> dict:
    """Update a slide's content.

    Args:
        index: Slide index (0-based)
        updates: Dict of fields to update (e.g., {"title": "New Title", "bullets": [...]})
    """
    try:
        slides, diagrams = load_slides_and_diagrams()
        index = args["index"]

        if index < 0 or index >= len(slides):
            return {
                "content": [{"type": "text", "text": f"Invalid index {index}. Have {len(slides)} slides (0-{len(slides)-1})"}],
                "isError": True
            }

        # Update the slide
        slides[index].update(args["updates"])
        save_slides(slides, diagrams)

        return {
            "content": [{
                "type": "text",
                "text": f"Updated slide {index}:\n\n{json.dumps(slides[index], indent=2)}\n\nRun generate_pptx to create the updated presentation."
            }]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error updating slide: {e}"}],
            "isError": True
        }


@tool("delete_slide", "Delete a slide by index", {"index": int})
async def delete_slide(args: dict) -> dict:
    """Delete a slide."""
    try:
        slides, diagrams = load_slides_and_diagrams()
        index = args["index"]

        if index < 0 or index >= len(slides):
            return {
                "content": [{"type": "text", "text": f"Invalid index {index}. Have {len(slides)} slides (0-{len(slides)-1})"}],
                "isError": True
            }

        deleted = slides.pop(index)
        save_slides(slides, diagrams)

        return {
            "content": [{
                "type": "text",
                "text": f"Deleted slide {index} ({deleted.get('type')}: {deleted.get('title')})\n\nNow have {len(slides)} slides. Run generate_pptx to update."
            }]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error deleting slide: {e}"}],
            "isError": True
        }

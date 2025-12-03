"""Extract Slide Images Tool - Converts PDF pages to PNG images."""

from pathlib import Path

from claude_agent_sdk import tool


@tool("extract_slide_images", "Extract slide images from a PDF file, saving each page as a PNG", {
    "pdf_path": str,
    "output_dir": str,
})
async def extract_slide_images(args: dict) -> dict:
    """Convert each PDF page to a PNG image and save to output directory.

    Args:
        args: Dictionary containing:
            - pdf_path: Path to the PDF file to extract slides from
            - output_dir: Directory to save extracted slide images (default: presentation/output/slides/)

    Returns:
        MCP-style response with list of extracted image paths or error.
    """
    pdf_path = args["pdf_path"]
    output_dir = args.get("output_dir", "presentation/output/slides/")

    # Validate PDF path
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        return {
            "content": [{
                "type": "text",
                "text": f"Error: PDF file not found: {pdf_path}"
            }],
            "isError": True
        }

    if not pdf_file.suffix.lower() == ".pdf":
        return {
            "content": [{
                "type": "text",
                "text": f"Error: File is not a PDF: {pdf_path}"
            }],
            "isError": True
        }

    # Create output directory
    output_path = Path(output_dir)
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error: Failed to create output directory: {e}"
            }],
            "isError": True
        }

    # Import pdf2image (handle import error gracefully)
    try:
        from pdf2image import convert_from_path
    except ImportError:
        return {
            "content": [{
                "type": "text",
                "text": "Error: pdf2image library is not installed. Install with: pip install pdf2image"
            }],
            "isError": True
        }

    # Convert PDF to images
    try:
        images = convert_from_path(str(pdf_file))
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error: Failed to convert PDF to images: {e}"
            }],
            "isError": True
        }

    if not images:
        return {
            "content": [{
                "type": "text",
                "text": "Error: No pages found in PDF"
            }],
            "isError": True
        }

    # Save each page as PNG
    saved_paths = []
    try:
        for i, image in enumerate(images, start=1):
            image_filename = f"slide_{i}.png"
            image_path = output_path / image_filename
            image.save(str(image_path), "PNG")
            saved_paths.append(str(image_path))
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error: Failed to save image: {e}"
            }],
            "isError": True
        }

    # Return success with list of paths
    paths_list = "\n".join(f"  - {p}" for p in saved_paths)
    return {
        "content": [{
            "type": "text",
            "text": f"Successfully extracted {len(saved_paths)} slide images:\n{paths_list}"
        }]
    }

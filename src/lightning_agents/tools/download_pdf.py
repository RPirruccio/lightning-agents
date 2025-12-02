"""PDF Download Tool - Downloads papers from URLs."""

import re
from pathlib import Path
from urllib.parse import urlparse, unquote

import httpx
from claude_agent_sdk import tool


def sanitize_filename(name: str) -> str:
    """Convert string to safe filename."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s+', '_', name)
    return name[:100]


@tool("download_pdf", "Download a PDF from a URL and save it to the downloads folder", {
    "url": str,
    "filename": str,
})
async def download_pdf(args: dict) -> dict:
    """Download a PDF from URL to downloads folder."""
    url = args["url"]
    filename = args.get("filename")

    # Create downloads folder relative to project root
    downloads_dir = Path(__file__).parent.parent.parent.parent / "downloads"
    downloads_dir.mkdir(exist_ok=True)

    # Determine filename
    if filename:
        safe_name = sanitize_filename(filename)
    else:
        parsed = urlparse(url)
        path_name = unquote(parsed.path.split('/')[-1])
        if path_name.endswith('.pdf'):
            safe_name = sanitize_filename(path_name[:-4])
        else:
            safe_name = sanitize_filename(path_name) or "paper"

    output_path = downloads_dir / f"{safe_name}.pdf"

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            output_path.write_bytes(response.content)

            return {
                "content": [{
                    "type": "text",
                    "text": f"Downloaded successfully!\nPath: {output_path}\nSize: {len(response.content)} bytes"
                }]
            }

    except httpx.HTTPStatusError as e:
        return {
            "content": [{
                "type": "text",
                "text": f"HTTP error {e.response.status_code}: {e.response.reason_phrase}"
            }],
            "isError": True
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Download failed: {str(e)}"
            }],
            "isError": True
        }

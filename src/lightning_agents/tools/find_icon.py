"""Find and Download Icon Tool - Downloads icons from LobeHub's icon library."""

from pathlib import Path

import httpx
from claude_agent_sdk import tool


# LobeHub icons package version (for stable URLs)
LOBEHUB_VERSION = "1.74.0"


@tool("find_icon", "Search and download icons/logos from LobeHub's icon library. Downloads the icon to the presentation/images/ directory and returns the local file path.", {
    "icon_name": str,
    "mode": str,
    "size": str,
})
async def find_icon(args: dict) -> dict:
    """Download an icon from LobeHub's icon library.

    Args:
        icon_name: Name of the icon (e.g., 'claude', 'openai', 'langchain'). Case-insensitive.
        mode: Color mode - 'light' or 'dark'. Defaults to 'dark'.
        size: Icon size - '16', '32', '64', '128', or '256'. Defaults to '128'.
              Note: LobeHub provides one size per icon, so this is used only for filename.

    Returns:
        The local file path where the icon was saved.
    """
    icon_name = args["icon_name"].lower().strip()
    mode = args.get("mode", "dark").lower().strip()
    size = args.get("size", "128").strip()

    # Validate mode
    if mode not in ("light", "dark"):
        return {
            "content": [{
                "type": "text",
                "text": f"Invalid mode '{mode}'. Must be 'light' or 'dark'."
            }],
            "isError": True
        }

    # Validate size (kept for API compatibility even though LobeHub has one size)
    valid_sizes = ("16", "32", "64", "128", "256")
    if size not in valid_sizes:
        return {
            "content": [{
                "type": "text",
                "text": f"Invalid size '{size}'. Must be one of: {', '.join(valid_sizes)}."
            }],
            "isError": True
        }

    # Build URL - LobeHub actual pattern: /{mode}/{icon_name}.png
    # Using versioned URL for stability
    url = f"https://unpkg.com/@lobehub/icons-static-png@{LOBEHUB_VERSION}/{mode}/{icon_name}.png"

    # Create presentation/images directory relative to project root
    images_dir = Path(__file__).parent.parent.parent.parent / "presentation" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Output filename: {icon_name}_{mode}_{size}.png
    output_filename = f"{icon_name}_{mode}_{size}.png"
    output_path = images_dir / output_filename

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Verify we got an image
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type and not response.content[:8].startswith(b'\x89PNG'):
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Icon '{icon_name}' not found in LobeHub library. The URL returned non-image content."
                    }],
                    "isError": True
                }

            # Save the icon
            output_path.write_bytes(response.content)

            return {
                "content": [{
                    "type": "text",
                    "text": f"Icon downloaded successfully!\nPath: {output_path}\nSize: {len(response.content)} bytes\nURL: {url}"
                }]
            }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Icon '{icon_name}' not found in LobeHub library. Check the icon name and try again.\nAttempted URL: {url}"
                }],
                "isError": True
            }
        return {
            "content": [{
                "type": "text",
                "text": f"HTTP error {e.response.status_code}: {e.response.reason_phrase}\nURL: {url}"
            }],
            "isError": True
        }
    except httpx.TimeoutException:
        return {
            "content": [{
                "type": "text",
                "text": f"Request timed out while downloading icon '{icon_name}'. Please try again."
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

"""
Markdown to DOCX Converter
Converts Markdown files to Word documents using pandoc.
"""

import subprocess
from pathlib import Path


def pandoc_exists() -> bool:
    """Check if pandoc is installed and available."""
    try:
        subprocess.run(
            ["pandoc", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except Exception:
        return False


def convert_md_to_docx(md_path: Path, docx_path: Path) -> None:
    """
    Convert Markdown to DOCX using pandoc with landscape orientation.
    Preserves anchors/ids as Word bookmarks for comment mapping to story IDs (dst_*).

    Args:
        md_path: Path to input markdown file
        docx_path: Path to output DOCX file

    Raises:
        FileNotFoundError: If markdown file doesn't exist
        RuntimeError: If pandoc is not installed or conversion fails
    """
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    if not pandoc_exists():
        raise RuntimeError(
            "Pandoc was not found on PATH. Please install pandoc:\n"
            "  - macOS: brew install pandoc\n"
            "  - Windows: choco install pandoc\n"
            "  - Linux:   apt-get install pandoc or dnf install pandoc\n"
        )

    # Ensure output directory exists
    docx_path.parent.mkdir(parents=True, exist_ok=True)

    # Get reference template path (landscape orientation)
    import os
    template_path = Path(__file__).parent / "templates" / "landscape-reference.docx"

    # --extract-media ensures embedded images are preserved into a media folder if present.
    # --standalone helps pandoc structure the document well.
    # --reference-doc sets landscape orientation via template
    # --resource-path tells pandoc where to find referenced images
    cmd = [
        "pandoc",
        "--from", "gfm+attributes+tex_math_dollars",
        "--to", "docx",
        "--standalone",
        "--reference-doc", str(template_path),
        "--resource-path", str(md_path.parent),
        "--extract-media", str(docx_path.parent / (docx_path.stem + "_media")),
        "-o", str(docx_path),
        str(md_path),
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(
            f"Pandoc conversion failed ({proc.returncode}): {' '.join(cmd)}\n"
            f"STDERR:\n{err}"
        )

    print(f"✓ Converted markdown to DOCX (landscape): {docx_path}")

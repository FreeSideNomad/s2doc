"""
DOCX Comment Extractor
Extracts comments from Word documents with domain story context.
"""

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from lxml import etree
import yaml

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# WordprocessingML tags
P = W_NS + "p"
R = W_NS + "r"
T = W_NS + "t"
BOOKMARK_START = W_NS + "bookmarkStart"
BOOKMARK_END = W_NS + "bookmarkEnd"
PSTYLE = W_NS + "pStyle"
COMMENT_RANGE_START = W_NS + "commentRangeStart"
COMMENT_RANGE_END = W_NS + "commentRangeEnd"
COMMENT_REFERENCE = W_NS + "commentReference"
INS = W_NS + "ins"
DEL = W_NS + "del"


@dataclass
class StoryContext:
    """Context information for a domain story."""
    story_id: Optional[str] = None
    story_title: Optional[str] = None
    nearest_heading_text: Optional[str] = None
    story_id_source: Optional[str] = None  # bookmark|inline|unknown


@dataclass
class CommentSelection:
    """Represents a comment and its selected text."""
    comment_id: int
    selection_text: str = ""
    story_context: StoryContext = field(default_factory=StoryContext)
    start_index: int = -1
    end_index: int = -1
    para_text_before: Optional[str] = None
    para_text_after: Optional[str] = None


@dataclass
class CommentEntry:
    """Represents a comment from the Word document."""
    id: int
    author: Optional[str]
    date: Optional[str]
    text: str
    parent_id: Optional[int] = None


def _text_of(node) -> str:
    """Concatenate text from all w:t descendants within a node."""
    texts = []
    for t in node.iterfind(".//" + T):
        if t.text:
            texts.append(t.text)
    return "".join(texts)


def _iter_document_sequence(doc_root):
    """
    Iterate in a stable document order over child elements that affect reading flow.
    Yields (index, element).
    """
    i = 0
    for elem in doc_root.iter():
        if elem.tag in {P, R, T, BOOKMARK_START, BOOKMARK_END, COMMENT_RANGE_START,
                        COMMENT_RANGE_END, COMMENT_REFERENCE, INS, DEL}:
            yield i, elem
            i += 1


def _get_style_val(p_elem) -> Optional[str]:
    """Get paragraph style value."""
    pst = p_elem.find("./" + W_NS + "pPr/" + PSTYLE)
    if pst is not None:
        return pst.get(W_NS + "val") or pst.get("{" + PSTYLE.split('}')[0].strip('{') + "}" + "val")
    return None


def _nearest_story_info(doc_root, up_to_index: int) -> StoryContext:
    """
    Look backward from up_to_index for the most recent story_id + title.
    - Prefer a w:bookmarkStart whose name starts with "dst_...".
    - Fallback: inline 'Story ID: dst_xxx' detection.
    - Also capture nearest Heading 2 text.
    """
    story_id = None
    story_title = None
    story_id_source = None
    nearest_heading_text = None

    # Traverse backward
    for i, elem in reversed(list(_iter_document_sequence(doc_root))):
        if i > up_to_index:
            continue

        # Heading text (kept as nearest regardless of story)
        if elem.tag == P:
            style = _get_style_val(elem)
            if style and style.lower().startswith("heading"):
                if nearest_heading_text is None:
                    nearest_heading_text = _text_of(elem)

            # Inline "Story ID" fallback
            if story_id is None:
                txt = _text_of(elem)
                m = re.search(r"Story ID\s*[:：]\s*`?(dst_[A-Za-z0-9_\-]+)`?", txt)
                if m:
                    story_id = m.group(1)
                    story_id_source = "inline"

        # Bookmark preferred
        if elem.tag == BOOKMARK_START and story_id is None:
            name = elem.get(W_NS + "name") or elem.get("w:name")
            if name and name.startswith("dst_"):
                story_id = name
                story_id_source = "bookmark"

        if story_id is not None and nearest_heading_text is not None:
            break

    # If we found an H2 near this story, use that as story_title
    story_title = nearest_heading_text

    return StoryContext(
        story_id=story_id,
        story_title=story_title,
        nearest_heading_text=nearest_heading_text,
        story_id_source=story_id_source or "unknown",
    )


def _collect_comment_selections(doc_root) -> Dict[int, CommentSelection]:
    """
    Locate comment ranges and collect the selected text between start/end markers.
    Returns a mapping comment_id -> CommentSelection
    """
    active_ranges: Dict[int, CommentSelection] = {}
    selections: Dict[int, CommentSelection] = {}
    prev_para_text = None
    last_para_text = None

    for idx, elem in _iter_document_sequence(doc_root):
        if elem.tag == P:
            prev_para_text = last_para_text
            last_para_text = _text_of(elem)

        if elem.tag == COMMENT_RANGE_START:
            cid = int(elem.get(W_NS + "id") or elem.get("w:id"))
            ctx = _nearest_story_info(doc_root, up_to_index=idx)
            active_ranges[cid] = CommentSelection(
                comment_id=cid,
                selection_text="",
                story_context=ctx,
                start_index=idx,
                para_text_before=prev_para_text
            )

        if elem.tag == COMMENT_RANGE_END:
            cid = int(elem.get(W_NS + "id") or elem.get("w:id"))
            sel = active_ranges.get(cid)
            if sel:
                sel.end_index = idx
                sel.para_text_after = last_para_text
                selections[cid] = sel
                active_ranges.pop(cid, None)

        # While inside an active range, collect visible text
        if any(k in active_ranges for k in list(active_ranges.keys())):
            if elem.tag in {R, T}:
                t = _text_of(elem)
                for sel in active_ranges.values():
                    sel.selection_text += t

            # Include text inside tracked changes
            if elem.tag in {INS, DEL}:
                t = _text_of(elem)
                for sel in active_ranges.values():
                    if elem.tag == INS:
                        sel.selection_text += f"[+{t}+]"
                    else:
                        sel.selection_text += f"[-{t}-]"

    return selections


def _load_comments_xml(zf: zipfile.ZipFile) -> List[CommentEntry]:
    """Load comments from the Word document's comments.xml."""
    try:
        with zf.open("word/comments.xml") as f:
            tree = etree.parse(f)
    except KeyError:
        return []  # no comments part

    root = tree.getroot()
    comments: List[CommentEntry] = []

    for c in root.findall(W_NS + "comment"):
        cid = int(c.get(W_NS + "id") or c.get("w:id"))
        author = c.get(W_NS + "author") or c.get("w:author")
        date = c.get(W_NS + "date") or c.get("w:date")
        parent = c.get(W_NS + "parentId") or c.get("w:parentId")
        parent_id = int(parent) if parent is not None else None
        text = _text_of(c)
        comments.append(CommentEntry(
            id=cid,
            author=author,
            date=date,
            text=text,
            parent_id=parent_id
        ))

    return comments


def _group_comments_with_replies(comments: List[CommentEntry]) -> List[Dict]:
    """Group comments with their replies."""
    by_id = {c.id: c for c in comments}
    roots: List[Dict] = []
    children_map: Dict[int, List[CommentEntry]] = {}

    for c in comments:
        if c.parent_id is None:
            roots.append({"comment": c, "replies": []})
        else:
            children_map.setdefault(c.parent_id, []).append(c)

    for r in roots:
        r["replies"] = children_map.get(r["comment"].id, [])

    return roots


def extract_comments_to_yaml(
    docx_path: Path,
    yaml_path: Path,
    context_chars: int = 220,
    include_replies: bool = True
) -> None:
    """
    Extract comments + selection text and map to nearest domain story context.
    Writes a YAML file suitable for LLM processing.

    Args:
        docx_path: Path to input DOCX file with comments
        yaml_path: Path to output YAML file
        context_chars: Number of context characters to include
        include_replies: Whether to include comment replies

    Output YAML shape:
    - document: <docx filename>
    - comments:
        - story_id: dst_...
          story_title: "..."
          comment_id: 12
          author: "Alice"
          date: "2025-10-26T12:34:56Z"
          selection_text: "the exact text that was commented on"
          context_before: "preceding paragraph (trimmed)"
          context_after: "following paragraph (trimmed)"
          comment_text: "main comment text"
          replies:
            - author: "Bob"
              date: "..."
              text: "..."
    """
    docx_path = Path(docx_path)
    yaml_path = Path(yaml_path)

    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX not found: {docx_path}")

    with zipfile.ZipFile(docx_path, "r") as zf:
        # Parse the main document
        with zf.open("word/document.xml") as f:
            doc_tree = etree.parse(f)
        doc_root = doc_tree.getroot()

        # Collect comment selections
        selections = _collect_comment_selections(doc_root)

        # Load all comments
        comments = _load_comments_xml(zf)

    # Build output records
    if include_replies:
        grouped = _group_comments_with_replies(comments)
    else:
        grouped = [{"comment": c, "replies": []} for c in comments if c.parent_id is None]

    def _trim(s: Optional[str]) -> Optional[str]:
        if not s:
            return None
        s = re.sub(r"\s+", " ", s).strip()
        if len(s) > context_chars:
            return s[:context_chars] + "…"
        return s

    items: List[Dict] = []
    for g in grouped:
        c = g["comment"]
        sel = selections.get(c.id)

        entry = {
            "story_id": sel.story_context.story_id if sel else None,
            "story_title": sel.story_context.story_title if sel else None,
            "comment_id": c.id,
            "author": c.author,
            "date": c.date,
            "selection_text": _trim(sel.selection_text if sel else None),
            "context_before": _trim(sel.para_text_before if sel else None),
            "context_after": _trim(sel.para_text_after if sel else None),
            "comment_text": _trim(c.text),
        }

        if include_replies and g.get("replies"):
            entry["replies"] = [
                {
                    "author": r.author,
                    "date": r.date,
                    "text": _trim(r.text),
                }
                for r in g["replies"]
            ]

        items.append(entry)

    # Sort by story_id then comment_id for stable ordering
    items.sort(key=lambda x: (x.get("story_id") or "", x.get("comment_id") or -1))

    out = {
        "document": docx_path.name,
        "comments": items,
    }

    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(out, f, sort_keys=False, allow_unicode=True)

    print(f"✓ Extracted {len(items)} comments to: {yaml_path}")

# coding=utf-8
"""
LangChain driven text splitter utilities.

This module keeps the original ``SplitModel`` entrypoint used across the
project, but replaces all regex-based hierarchical parsing with LangChain
splitters. The new behavior provides:

* Markdown-aware hierarchical splitting (preserving titles).
* Overlapping chunk windows for recall.
* Optional whitespace normalization.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Sequence, Union

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

# ─────────────────────────────────────────────────────────────────────────────
# Markdown heading definitions
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_HEADERS_TO_SPLIT = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
    ("####", "h4"),
    ("#####", "h5"),
    ("######", "h6"),
]

MAX_TITLE_LEN = 256

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _normalize_text(text: str) -> str:
    """Collapse excessive whitespace and normalize newlines."""
    replace_map = {
        re.compile("\r"): "\n",
        re.compile("\t+"): " ",
        re.compile(" +"): " ",
        re.compile("\n{3,}"): "\n\n",
    }
    for pattern, repl in replace_map.items():
        text = re.sub(pattern, repl, text)
    return text.strip()

def _trim_title(title: str) -> str:
    """Normalize and clamp markdown titles to the API's length limit."""

    normalized = _normalize_text(title)
    return normalized[:MAX_TITLE_LEN]


def flat_map(arr):
    """Compatibility shim: flatten 2D lists."""
    result = []
    for e in arr:
        result.extend(e)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# SplitModel definition
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SplitModel:
    """
    Unified LangChain-based splitter.

    Args:
        content_level_pattern:
            If provided, enable Markdown header splitting (hierarchical).
        with_filter:
            Normalize output text chunks if True.
        limit:
            Maximum chunk length.
        overlap:
            Overlap for RecursiveCharacterTextSplitter.
    """

    content_level_pattern: Sequence | None
    with_filter: bool = True
    limit: int = 4096
    overlap: int | None = None

    # ------------------------------------------------------------------

    def __post_init__(self):
        """Ensure chunk size & overlap are valid."""
        if not self.limit or self.limit <= 0:
            self.limit = 4096
        self.limit = min(self.limit, 100000)

        # default ~20% overlap
        self.overlap = (
            self.overlap
            if self.overlap is not None
            else max(1, min(200, int(self.limit * 0.2)))
        )

    # ------------------------------------------------------------------

    def _build_splitter(self) -> RecursiveCharacterTextSplitter:
        """Create the chunk splitter."""
        return RecursiveCharacterTextSplitter(
            chunk_size=self.limit,
            chunk_overlap=self.overlap,
            separators=["\n\n", "\n", "。", ".", "?", "!", "；", ";", " "],
        )

    # ------------------------------------------------------------------

    def _split_markdown(self, text: str) -> List[dict]:
        """
        First split by markdown headers -> parent documents.
        Then split each parent document using recursive splitter
        to generate child chunks with inherited titles.
        """

        header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=DEFAULT_HEADERS_TO_SPLIT,
            strip_headers=False,
        )
        header_docs = header_splitter.split_text(text)

        splitter = self._build_splitter()
        child_docs = splitter.split_documents(header_docs)

        results = []
        for doc in child_docs:
            # Merge all markdown headings in metadata
            titles = [
                value for key, value in doc.metadata.items()
                if key.startswith("h")
            ]
            title = _trim_title(" ".join(titles)) if titles else ""
            #title = _trim_title(" ".join(title))

            content = doc.page_content
            if self.with_filter:
                content = _normalize_text(content)

            if content:
                results.append({
                    "title": title,
                    "content": content
                })

        return results

    # ------------------------------------------------------------------

    def _split_plain(self, text: str) -> List[dict]:
        """Non-markdown plain text splitting."""
        splitter = self._build_splitter()
        parts = splitter.split_text(text)

        results = []
        for part in parts:
            content = _normalize_text(part) if self.with_filter else part
            if content:
                results.append({"title": "", "content": content})

        return results

    # ------------------------------------------------------------------

    def parse(self, text: Union[str, bytes]) -> List[dict]:
        """Entrypoint for all consumers. Returns a list of chunks."""
        if isinstance(text, (bytes, bytearray)):
            text = text.decode(errors="ignore")

        text = text.replace("\0", "")

        if self.content_level_pattern:
            return self._split_markdown(text)

        return self._split_plain(text)


# ─────────────────────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────────────────────

def get_split_model(filename: str, with_filter: bool = False, limit: int = 100000):
    """Return an appropriate SplitModel based on filename."""
    is_md = filename.lower().endswith(".md")
    return SplitModel(
        content_level_pattern=DEFAULT_HEADERS_TO_SPLIT if is_md else None,
        with_filter=with_filter,
        limit=limit,
    )


# ─────────────────────────────────────────────────────────────────────────────

__all__ = ["SplitModel", "get_split_model", "flat_map"]

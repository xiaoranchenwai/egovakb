# coding=utf-8
"""
LangChain driven text splitter utilities.

This module keeps the original ``SplitModel`` entrypoint used across the
project, but replaces the hand-written regex parsing logic with LangChain
splitters.  It provides:

* Markdown-aware splitting to preserve parent/child heading structure.
* Overlapping character windows for downstream recall.
* Optional filtering to normalize whitespace in the final chunks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Sequence

from common.util.common import flat_map  # Backwards compatibility re-export

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

# Default markdown headers used when callers provide a ``pattern_list``
# (maintains compatibility with previous markdown oriented behaviour).
DEFAULT_HEADERS_TO_SPLIT = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
    ("####", "h4"),
    ("#####", "h5"),
    ("######", "h6"),
]


def _normalize_text(text: str) -> str:
    """Lightweight cleanup to collapse noisy whitespace characters."""

    replace_map = {
        re.compile("\r"): "\n",
        re.compile("\t+"): " ",
        re.compile(" +"): " ",
        re.compile("\n{3,}"): "\n\n",
    }
    for pattern, repl in replace_map.items():
        text = re.sub(pattern, repl, text)
    return text.strip()


@dataclass
class SplitModel:
    """LangChain based splitter wrapper.

    Args:
        content_level_pattern: Presence of a value triggers markdown header
            splitting so we maintain hierarchical context (parent/child blocks).
        with_filter: Whether to normalize whitespace in the returned chunks.
        limit: Maximum character length for each chunk.
        overlap: Character overlap between adjacent chunks to preserve context.
    """

    content_level_pattern: Sequence | None
    with_filter: bool = True
    limit: int = 4096
    overlap: int | None = None

    def __post_init__(self):
        if self.limit is None or self.limit <= 0:
            self.limit = 4096
        # Cap overly large limits to avoid huge chunks.
        self.limit = min(self.limit, 100_000)
        # Default overlap keeps ~20% of content for context.
        self.overlap = (
            self.overlap
            if self.overlap is not None
            else max(1, min(200, int(self.limit * 0.2)))
        )

    def _build_splitter(self) -> RecursiveCharacterTextSplitter:
        return RecursiveCharacterTextSplitter(
            chunk_size=self.limit,
            chunk_overlap=self.overlap,
            separators=["\n\n", "\n", "。", ".", "?", "!", "；", ";", " "],
        )

    def _split_markdown(self, text: str) -> List[dict]:
        """
        First split by markdown headers (parent nodes), then split children with
        overlapping windows so child retrieval can surface parent content.
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
            metadata_headers = [
                value for key, value in doc.metadata.items() if key.startswith("h")
            ]
            title = " ".join(metadata_headers)
            content = doc.page_content
            if self.with_filter:
                content = _normalize_text(content)
            results.append({"title": title, "content": content})
        return [item for item in results if item.get("content")]

    def _split_plain(self, text: str) -> List[dict]:
        splitter = self._build_splitter()
        parts = splitter.split_text(text)
        results = []
        for part in parts:
            content = _normalize_text(part) if self.with_filter else part
            if content:
                results.append({"title": "", "content": content})
        return results

    def parse(self, text: str | bytes) -> List[dict]:
        """Split input text into chunks.

        Returns a list of dictionaries with ``title`` and ``content`` keys to
        stay compatible with previous consumers.
        """

        if isinstance(text, (bytes, bytearray)):
            text = text.decode(errors="ignore")

        text = text.replace("\0", "")

        if self.content_level_pattern:
            return self._split_markdown(text)
        return self._split_plain(text)


def get_split_model(filename: str, with_filter: bool = False, limit: int = 100000):
    """Factory to create a ``SplitModel`` for a given filename."""

    use_markdown = filename.endswith(".md") or filename.endswith(".MD")
    return SplitModel(
        content_level_pattern=DEFAULT_HEADERS_TO_SPLIT if use_markdown else None,
        with_filter=with_filter,
        limit=limit,
    )


__all__ = ["SplitModel", "get_split_model", "flat_map"]


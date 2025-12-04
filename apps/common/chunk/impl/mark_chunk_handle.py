"""
LangChain based chunk handle that produces overlapping child chunks.
"""

from __future__ import annotations

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from common.chunk.i_chunk_handle import IChunkHandle

DEFAULT_CHUNK_LEN = 128


class MarkChunkHandle(IChunkHandle):
    def handle(self, chunk_list: List[str], chunk_patterns: str = None, chunk_length: int = None):
        """Split chunks using ``RecursiveCharacterTextSplitter`` with overlap."""

        chunk_length = chunk_length or DEFAULT_CHUNK_LEN
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_length,
            chunk_overlap=max(1, int(chunk_length * 0.2)),
            separators=["\n\n", "\n", "。", ".", "!", "?", "；", ";", " "],
        )

        result: List[str] = []
        for chunk in chunk_list:
            result.extend(splitter.split_text(chunk))
        return result


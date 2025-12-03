# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： __init__.py
    @date：2024/7/23 17:03
    @desc:
"""
from typing import List

from common.chunk.impl.mark_chunk_handle import MarkChunkHandle

handles = [MarkChunkHandle()]


def text_to_chunk(text: str, chunk_patterns: str = None, chunk_length: int = None):
    chunk_list = [text]
    for handle in handles:
        chunk_list = handle.handle(chunk_list, chunk_patterns, chunk_length)
    return chunk_list

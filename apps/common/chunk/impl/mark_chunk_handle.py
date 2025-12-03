# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： mark_chunk_handle.py
    @date：2024/7/23 16:52
    @desc:
"""
import re
from typing import List

from common.chunk.i_chunk_handle import IChunkHandle

max_chunk_len = 128
split_chunk_pattern = r'.{1,%d}[。| |\\.|！|;|；|!|\n]' % max_chunk_len
max_chunk_pattern = r'.{1,%d}' % max_chunk_len


class MarkChunkHandle(IChunkHandle):
    def handle(self, chunk_list: List[str], chunk_patterns: str = None, chunk_length: int = None):
        if chunk_length is None:
            chunk_length = max_chunk_len
            
        result = []
        for chunk in chunk_list:
            # 使用改进的分块逻辑
            remaining_text = chunk
            
            while remaining_text:
                # 如果剩余文本长度小于等于chunk_length，直接作为最后一个块
                if len(remaining_text) <= chunk_length:
                    chunk_part = remaining_text
                    if len(chunk_part) > 0:  # 不使用strip()，保留原始空白字符
                        result.append(chunk_part)
                    remaining_text = ""
                    continue
                    
                # 在chunk_length范围内查找标点符号
                search_text = remaining_text[:chunk_length]
                punctuation_positions = []
                
                # 查找所有标点符号的位置
                for i, char in enumerate(search_text):
                    if char in ['。', ' ', '\\.', '！', ';', '；', '!', '\n']:
                        punctuation_positions.append(i)
                
                if punctuation_positions:
                    # 找到标点符号，使用最后一个作为分割点
                    last_punctuation_pos = punctuation_positions[-1]
                    chunk_part = remaining_text[:last_punctuation_pos+1]
                    if len(chunk_part) > 0:  # 不使用strip()，保留原始空白字符
                        result.append(chunk_part)
                    remaining_text = remaining_text[len(chunk_part):]
                else:
                    # 在chunk_length范围内找不到标点符号，使用固定长度分割
                    chunk_part = remaining_text[:chunk_length]
                    if len(chunk_part) > 0:  # 不使用strip()，保留原始空白字符
                        result.append(chunk_part)
                    remaining_text = remaining_text[chunk_length:]

        return result

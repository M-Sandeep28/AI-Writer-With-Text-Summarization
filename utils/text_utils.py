"""
Text processing and analysis utilities for AI Writer with Text Summarization.
Provides word count, sentence count, text cleaning, compression calculation, and text chunking.
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean and normalize input text by stripping leading/trailing whitespace
    and removing excessive spacing or repeated carriage returns.
    """
    if not text:
        return ""
    # Replace multiple blank lines with double newlines
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    # Strip whitespace
    return text.strip()


def get_word_count(text: str) -> int:
    """
    Calculate total word count in text.
    Handles spaces, line breaks, and punctuation splitting.
    """
    if not text or not text.strip():
        return 0
    words = re.findall(r'\b\w+(?:[\'-]\w+)*\b', text)
    return len(words)


def get_char_count(text: str) -> int:
    """
    Calculate character count of text (excluding trailing newlines).
    """
    if not text:
        return 0
    return len(text.strip())


def get_sentence_count(text: str) -> int:
    """
    Calculate total sentence count using punctuation boundary detection.
    """
    if not text or not text.strip():
        return 0
    # Match sentence terminators (., !, ?) followed by whitespace or end of string
    sentences = re.split(r'[.!?]+(?:\s+|$)', text.strip())
    # Filter empty strings
    valid_sentences = [s for s in sentences if s.strip()]
    return max(len(valid_sentences), 1 if get_word_count(text) > 0 else 0)


def calculate_compression(original_words: int, summary_words: int) -> float:
    """
    Calculate percentage reduction (compression rate).
    Formula: (1 - summary_words / original_words) * 100
    Handles zero division edge cases safely.
    """
    if original_words <= 0:
        return 0.0

    if summary_words >= original_words:
        return 0.0

    compression = (1.0 - (summary_words / float(original_words))) * 100.0
    return max(0.0, min(100.0, compression))


def chunk_text(text: str, max_words_per_chunk: int = 400) -> List[str]:
    """
    Split long article into manageable text chunks based on sentence/paragraph boundaries
    to safely process long articles through Transformer models without truncation.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []

    words = cleaned.split()
    if len(words) <= max_words_per_chunk:
        return [cleaned]

    # Split by paragraphs first
    paragraphs = cleaned.split('\n\n')
    chunks = []
    current_chunk = []
    current_word_count = 0

    for para in paragraphs:
        para_words = para.split()
        if not para_words:
            continue

        if current_word_count + len(para_words) <= max_words_per_chunk:
            current_chunk.append(para)
            current_word_count += len(para_words)
        else:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))

            # If a single paragraph is larger than max_words_per_chunk, split by sentences or word slices
            if len(para_words) > max_words_per_chunk:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                # If sentence splitting didn't break down the text, slice by words
                if len(sentences) <= 1:
                    p_words = para.split()
                    for i in range(0, len(p_words), max_words_per_chunk):
                        chunks.append(" ".join(p_words[i:i + max_words_per_chunk]))
                    current_chunk = []
                    current_word_count = 0
                else:
                    sub_chunk = []
                    sub_word_count = 0
                    for sent in sentences:
                        sent_words = sent.split()
                        if sub_word_count + len(sent_words) <= max_words_per_chunk:
                            sub_chunk.append(sent)
                            sub_word_count += len(sent_words)
                        else:
                            if sub_chunk:
                                chunks.append(' '.join(sub_chunk))
                            sub_chunk = [sent]
                            sub_word_count = len(sent_words)
                    if sub_chunk:
                        current_chunk = [' '.join(sub_chunk)]
                        current_word_count = sub_word_count
                    else:
                        current_chunk = []
                        current_word_count = 0
            else:
                current_chunk = [para]
                current_word_count = len(para_words)

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks

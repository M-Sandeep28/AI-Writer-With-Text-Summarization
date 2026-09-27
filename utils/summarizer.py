"""
AI Summarization module for AI Writer with Text Summarization.
Uses Hugging Face AutoModelForSeq2SeqLM and AutoTokenizer (DistilBART / BART-large-CNN)
with Streamlit resource caching for fast, robust inference.
Handles short, medium, and detailed summaries as well as long article chunking.
"""

import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from utils.text_utils import clean_text, get_word_count, chunk_text


# Pretrained transformer models
PRIMARY_MODEL = "sshleifer/distilbart-cnn-12-6"
FALLBACK_MODEL = "facebook/bart-large-cnn"


# Length parameters mapping (max_length, min_length)
LENGTH_CONFIG = {
    "Short": {"max_length": 60, "min_length": 20},
    "Medium": {"max_length": 130, "min_length": 45},
    "Detailed": {"max_length": 250, "min_length": 90}
}


@st.cache_resource
def load_summarizer_model(model_name: str = PRIMARY_MODEL):
    """
    Load Hugging Face Tokenizer and Seq2SeqLM Model with Streamlit resource caching.
    Ensures model weights are loaded into memory once during session runtime.
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        return tokenizer, model, model_name
    except Exception as e:
        # Fallback to secondary model if primary fails
        tokenizer = AutoTokenizer.from_pretrained(FALLBACK_MODEL)
        model = AutoModelForSeq2SeqLM.from_pretrained(FALLBACK_MODEL)
        return tokenizer, model, FALLBACK_MODEL


def generate_single_summary(text: str, tokenizer, model, max_len: int, min_len: int) -> str:
    """Helper function to run model.generate on a single text string."""
    inputs = tokenizer(text, max_length=1024, truncation=True, return_tensors="pt")
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=max_len,
        min_length=min_len,
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True
    )
    summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary_text.strip()


def summarize_text(text: str, length_option: str = "Medium") -> str:
    """
    Generate summary using Hugging Face Transformer model.
    Handles long texts via intelligent chunking.

    Args:
        text (str): Input article text.
        length_option (str): 'Short', 'Medium', or 'Detailed'.

    Returns:
        str: Generated summary text.
    """
    cleaned_input = clean_text(text)
    input_word_count = get_word_count(cleaned_input)

    if input_word_count < 15:
        return "The provided text is too short for meaningful AI summarization. Please enter a longer article."

    # Fetch configuration for selected length
    config = LENGTH_CONFIG.get(length_option, LENGTH_CONFIG["Medium"])
    max_len = config["max_length"]
    min_len = config["min_length"]

    # Load cached tokenizer & model
    tokenizer, model, loaded_model_name = load_summarizer_model()

    # Split long text into manageable chunks (~350 words per chunk)
    chunks = chunk_text(cleaned_input, max_words_per_chunk=350)

    try:
        if len(chunks) == 1:
            # Adjust max_length dynamically if input is shorter than target max_length
            effective_max_len = min(max_len, max(min_len + 10, int(input_word_count * 0.8)))
            effective_min_len = min(min_len, max(10, int(effective_max_len * 0.4)))

            return generate_single_summary(
                cleaned_input, tokenizer, model,
                max_len=effective_max_len, min_len=effective_min_len
            )
        else:
            # Process multiple chunks
            intermediate_summaries = []
            chunk_max_len = max(50, int(max_len / min(len(chunks), 4)) + 30)
            chunk_min_len = max(15, int(min_len / min(len(chunks), 4)))

            for chunk in chunks:
                chunk_summary = generate_single_summary(
                    chunk, tokenizer, model,
                    max_len=chunk_max_len, min_len=chunk_min_len
                )
                intermediate_summaries.append(chunk_summary)

            combined_summary_text = " ".join(intermediate_summaries)

            # If combined summary exceeds max_len, run final summarization pass
            if get_word_count(combined_summary_text) > max_len:
                return generate_single_summary(
                    combined_summary_text, tokenizer, model,
                    max_len=max_len, min_len=min_len
                )
            else:
                return combined_summary_text.strip()

    except Exception as ex:
        raise RuntimeError(f"An error occurred during summarization: {str(ex)}")

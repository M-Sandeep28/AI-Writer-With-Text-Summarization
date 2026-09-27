"""
Comprehensive test script for AI Writer with Text Summarization application.
Tests database, auth, text utilities, summarizer pipeline, and user data isolation.
"""

import os
import sys

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    create_summary, get_user_summaries, get_summary_by_id,
    delete_summary, get_user_stats, update_user_name
)
from auth import (
    register_user, login_user, is_valid_email, hash_password, verify_password
)
from utils.text_utils import (
    clean_text, get_word_count, get_char_count, get_sentence_count,
    calculate_compression, chunk_text
)
from utils.summarizer import summarize_text


def test_database_and_auth():
    print("--- 1. Testing Database & Auth ---")
    if os.path.exists("app.db"):
        os.remove("app.db")

    init_db()
    print("[OK] DB Initialized")

    # Test Registration
    succ, msg = register_user("Alice Smith", "alice@example.com", "secret123", "secret123")
    assert succ is True, f"Registration failed: {msg}"
    print("[OK] User Alice registered")

    # Test Duplicate Registration
    succ, msg = register_user("Alice Two", "alice@example.com", "secret123", "secret123")
    assert succ is False, "Duplicate registration should fail!"
    print("[OK] Duplicate email prevented")

    # Test Password Mismatch
    succ, msg = register_user("Bob", "bob@example.com", "secret123", "different")
    assert succ is False, "Password mismatch should fail!"
    print("[OK] Password mismatch caught")

    # Test Login
    succ, msg = login_user("alice@example.com", "secret123")
    assert succ is True, f"Login failed: {msg}"
    print("[OK] User Alice logged in successfully")

    # Test Invalid Login
    succ, msg = login_user("alice@example.com", "wrongpassword")
    assert succ is False, "Invalid password login should fail!"
    print("[OK] Invalid password rejected")


def test_text_utilities():
    print("\n--- 2. Testing Text Utilities ---")
    raw_text = "   This is a sample article for testing!  It has multiple sentences. Is it working?   "
    cleaned = clean_text(raw_text)
    words = get_word_count(cleaned)
    chars = get_char_count(cleaned)
    sents = get_sentence_count(cleaned)

    assert words == 14, f"Expected 14 words, got {words}"
    assert chars > 0, "Expected non-zero char count"
    assert sents == 3, f"Expected 3 sentences, got {sents}"

    comp = calculate_compression(100, 30)
    assert abs(comp - 70.0) < 0.01, f"Expected 70% compression, got {comp}"

    # Test chunking
    long_article = ("Word " * 500)
    chunks = chunk_text(long_article, max_words_per_chunk=200)
    assert len(chunks) > 1, "Long article should be split into multiple chunks"
    print(f"[OK] Text utilities working cleanly! Long article (500 words) chunked into {len(chunks)} chunks.")


def test_user_data_isolation():
    print("\n--- 3. Testing User Data Isolation ---")
    # Register User B
    register_user("Bob Jones", "bob@example.com", "password123", "password123")
    user_alice = get_user_by_email("alice@example.com")
    user_bob = get_user_by_email("bob@example.com")

    # Save summary for Alice
    sum_id_alice = create_summary(
        user_id=user_alice["id"],
        title="Alice's Article",
        original_text="Alice's long original text",
        generated_summary="Alice's summary",
        original_word_count=100,
        summary_word_count=30,
        compression_percentage=70.0,
        summary_length="Medium"
    )

    # Save summary for Bob
    sum_id_bob = create_summary(
        user_id=user_bob["id"],
        title="Bob's Article",
        original_text="Bob's long original text",
        generated_summary="Bob's summary",
        original_word_count=200,
        summary_word_count=50,
        compression_percentage=75.0,
        summary_length="Short"
    )

    alice_summaries = get_user_summaries(user_alice["id"])
    bob_summaries = get_user_summaries(user_bob["id"])

    assert len(alice_summaries) == 1, "Alice should only see 1 summary"
    assert len(bob_summaries) == 1, "Bob should only see 1 summary"
    assert alice_summaries[0]["title"] == "Alice's Article"
    assert bob_summaries[0]["title"] == "Bob's Article"

    # Verify cross-user lookup returns None
    cross_lookup = get_summary_by_id(sum_id_bob, user_alice["id"])
    assert cross_lookup is None, "Alice must not be able to retrieve Bob's summary!"

    # Verify cross-user deletion returns False
    deleted = delete_summary(sum_id_bob, user_alice["id"])
    assert deleted is False, "Alice must not be able to delete Bob's summary!"

    print("[OK] Strict User Data Isolation Verified!")


def test_summarization_pipeline():
    print("\n--- 4. Testing Transformer Summarizer Pipeline ---")
    sample_article = (
        "Artificial Intelligence (AI) has rapidly transitioned from a theoretical concept in computer science "
        "to one of the most transformative technologies of the twenty-first century. At its core, AI refers "
        "to machine systems capable of performing tasks that traditionally require human intelligence, such as "
        "visual perception, speech recognition, decision-making, and natural language translation. "
        "The recent acceleration in AI development is largely driven by advances in machine learning and "
        "deep learning architectures. Machine learning algorithms allow systems to learn from data patterns without "
        "being explicitly programmed for every scenario. Deep learning, inspired by the neural structure of the "
        "human brain, uses multi-layered neural networks to process vast quantities of unstructured data. "
        "Key milestones such as Transformer neural network architectures have revolutionized Natural Language Processing, "
        "enabling models to understand context, generate coherent text, and summarize massive volumes of information."
    )

    print("Generating summary using Transformer model...")
    summary = summarize_text(sample_article, length_option="Medium")
    print(f"Generated Summary:\n{summary}")
    assert len(summary) > 10, "Summary should be non-empty string"
    print("[OK] Transformer Summarizer Test Passed!")


if __name__ == "__main__":
    print("Starting All Application Tests...")
    test_database_and_auth()
    test_text_utilities()
    test_user_data_isolation()
    test_summarization_pipeline()
    print("\n[SUCCESS] ALL TESTS PASSED SUCCESSFULLY!")

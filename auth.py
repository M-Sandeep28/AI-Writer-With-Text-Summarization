"""
Authentication module for AI Writer with Text Summarization.
Handles user registration, login, logout, password hashing, and session management.
"""

import re
import streamlit as st
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_user, get_user_by_email, get_user_by_id


EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


def is_valid_email(email: str) -> bool:
    """Validate email format using standard regex."""
    if not email:
        return False
    return bool(re.match(EMAIL_REGEX, email.strip()))


def hash_password(password: str) -> str:
    """Hash plain text password securely using pbkdf2:sha256."""
    return generate_password_hash(password, method="pbkdf2:sha256")


def verify_password(password_hash: str, password: str) -> bool:
    """Verify password against stored password hash."""
    return check_password_hash(password_hash, password)


def register_user(name: str, email: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """
    Validate user registration data and create account.
    Returns (success: bool, message: str).
    """
    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password or not confirm_password:
        return False, "All fields are required."

    if not is_valid_email(email):
        return False, "Please enter a valid email address."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    if password != confirm_password:
        return False, "Password and Confirm Password do not match."

    hashed_pw = hash_password(password)
    user_id = create_user(name=name, email=email, password_hash=hashed_pw)

    if user_id is None:
        return False, "An account with this email address already exists."

    return True, "Account registered successfully! You can now log in."


def login_user(email: str, password: str) -> tuple[bool, str]:
    """
    Authenticate user credentials and initialize session state.
    Returns (success: bool, message: str).
    """
    email = email.strip().lower()

    if not email or not password:
        return False, "Please fill in both email and password fields."

    user = get_user_by_email(email)

    # Generic error message to prevent account enumeration
    invalid_msg = "Invalid email or password. Please try again."

    if not user:
        return False, invalid_msg

    if not verify_password(user["password_hash"], password):
        return False, invalid_msg

    # Initialize Streamlit session state
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["user_name"] = user["name"]
    st.session_state["user_email"] = user["email"]

    return True, f"Welcome back, {user['name']}!"


def logout_user():
    """Clear user session state and reset app navigation."""
    st.session_state["authenticated"] = False
    st.session_state["user_id"] = None
    st.session_state["user_name"] = None
    st.session_state["user_email"] = None
    if "current_page" in st.session_state:
        st.session_state["current_page"] = "Login"


def is_authenticated() -> bool:
    """Check if a user is currently authenticated."""
    return st.session_state.get("authenticated", False) is True


def get_current_user() -> dict:
    """Return dictionary of current authenticated user details or empty dict."""
    if not is_authenticated():
        return {}
    return {
        "id": st.session_state.get("user_id"),
        "name": st.session_state.get("user_name"),
        "email": st.session_state.get("user_email")
    }

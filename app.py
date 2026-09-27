"""
Main Application Entry Point for AI Writer with Text Summarization.
Built with Streamlit, PyTorch, Hugging Face Transformers, and SQLite.
"""

import datetime
import streamlit as st

from database import (
    init_db,
    get_user_summaries,
    get_summary_by_id,
    create_summary,
    delete_summary,
    get_user_stats,
    get_user_by_id,
    update_user_name
)
from auth import (
    login_user,
    register_user,
    logout_user,
    is_authenticated,
    get_current_user
)
from utils.text_utils import (
    clean_text,
    get_word_count,
    get_char_count,
    get_sentence_count,
    calculate_compression
)
from utils.summarizer import summarize_text
from examples.sample_articles import SAMPLE_ARTICLES


# Page Configuration
st.set_page_config(
    page_title="AI Writer - Text Summarization",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Custom CSS Styling for a polished UI
st.markdown("""
    <style>
    /* Global Styles & Variables */
    :root {
        --primary: #4F46E5;
        --primary-hover: #4338CA;
        --bg-card: #1E293B;
        --text-main: #F8FAFC;
        --accent-glow: rgba(79, 70, 229, 0.15);
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Custom Header Banner */
    .app-header {
        background: linear-gradient(135deg, #312E81 0%, #4F46E5 50%, #7C3AED 100%);
        padding: 1.8rem 2rem;
        border-radius: 14px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.4);
    }
    .app-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF !important;
    }
    .app-header p {
        margin: 0.4rem 0 0 0;
        opacity: 0.9;
        font-size: 1.05rem;
    }

    /* Styled Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #6366F1 !important;
    }
    
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }

    /* Summary Card Output */
    .summary-box {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-left: 5px solid #6366F1;
        padding: 1.4rem;
        border-radius: 8px;
        font-size: 1.05rem;
        line-height: 1.7;
        color: #E2E8F0;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    
    .user-profile-badge {
        background: #1E293B;
        border: 1px solid #334155;
        padding: 0.9rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    /* Download File Formatting */
    .stDownloadButton button {
        background-color: #10B981 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    .stDownloadButton button:hover {
        background-color: #059669 !important;
    }

    </style>
""", unsafe_allow_html=True)


def init_app_state():
    """Initialize database and default session state variables."""
    init_db()

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = None
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Login"
    if "input_article" not in st.session_state:
        st.session_state["input_article"] = ""
    if "input_title" not in st.session_state:
        st.session_state["input_title"] = ""
    if "last_generated_result" not in st.session_state:
        st.session_state["last_generated_result"] = None
    if "auth_tab" not in st.session_state:
        st.session_state["auth_tab"] = "Login"


def render_sidebar():
    """Render sidebar navigation and user status."""
    st.sidebar.markdown("## 📝 **AI Writer**")
    st.sidebar.caption("Pretrained NLP Text Summarization")
    st.sidebar.markdown("---")

    if is_authenticated():
        user = get_current_user()
        st.sidebar.markdown(f"""
            <div class="user-profile-badge">
                <div style="font-weight: 600; font-size: 1rem; color: #F8FAFC;">👤 {user.get('name')}</div>
                <div style="font-size: 0.82rem; color: #94A3B8; word-break: break-all;">✉️ {user.get('email')}</div>
            </div>
        """, unsafe_allow_html=True)

        pages = {
            "🏠 Dashboard": "Dashboard",
            "📝 New Summary": "New Summary",
            "📜 History": "History",
            "👤 Profile": "Profile"
        }

        selected = st.sidebar.radio(
            "Navigation",
            options=list(pages.keys()),
            index=list(pages.values()).index(st.session_state.get("current_page", "Dashboard"))
            if st.session_state.get("current_page", "Dashboard") in pages.values() else 0
        )

        st.session_state["current_page"] = pages[selected]

        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()
            st.rerun()
    else:
        st.sidebar.info("🔒 Please Log In or Register to access the AI Summarizer.")


def render_auth_view():
    """Render Login and Registration view."""
    st.markdown("""
        <div class="app-header">
            <h1>AI Writer with Text Summarization</h1>
            <p>Transform long articles into concise, intelligent summaries using pretrained NLP Transformers.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

        with tab1:
            st.subheader("Login to Your Account")
            login_email = st.text_input("Email Address", key="login_email_input").strip()
            login_password = st.text_input("Password", type="password", key="login_pw_input")

            if st.button("Sign In", type="primary", use_container_width=True):
                success, msg = login_user(login_email, login_password)
                if success:
                    st.success(msg)
                    st.session_state["current_page"] = "Dashboard"
                    st.rerun()
                else:
                    st.error(msg)

        with tab2:
            st.subheader("Create a New Account")
            reg_name = st.text_input("Full Name", key="reg_name_input")
            reg_email = st.text_input("Email Address", key="reg_email_input")
            reg_password = st.text_input("Password", type="password", key="reg_pw_input")
            reg_confirm_pw = st.text_input("Confirm Password", type="password", key="reg_cpw_input")

            if st.button("Create Account", type="primary", use_container_width=True):
                success, msg = register_user(reg_name, reg_email, reg_password, reg_confirm_pw)
                if success:
                    st.success(msg)
                    st.info("You can now switch to the Login tab and sign in.")
                else:
                    st.error(msg)


def render_dashboard_page():
    """Render User Dashboard with metrics and quick navigation."""
    user = get_current_user()
    stats = get_user_stats(user["id"])

    st.markdown(f"""
        <div class="app-header">
            <h1>Welcome back, {user['name']}! 👋</h1>
            <p>Transform long articles, research papers, and documents into clear summaries instantly.</p>
        </div>
    """, unsafe_allow_html=True)

    # Dashboard Metrics Row
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            label="Total Summaries Generated",
            value=f"{stats['total_summaries']}"
        )
    with c2:
        st.metric(
            label="Total Words Processed",
            value=f"{stats['total_words_processed']:,}"
        )
    with c3:
        latest_date = stats['latest_summary_date']
        if latest_date:
            formatted_date = latest_date.split()[0]
        else:
            formatted_date = "No activity yet"
        st.metric(
            label="Latest Summary Date",
            value=formatted_date
        )

    st.markdown("---")

    # Main Action Quick Navigation
    st.subheader("🚀 Quick Actions")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("### 📝 New Summary")
        st.write("Paste an article or select a sample to generate an AI summary.")
        if st.button("Create Summary", type="primary", use_container_width=True):
            st.session_state["current_page"] = "New Summary"
            st.rerun()

    with col_b:
        st.markdown("### 📜 Summary History")
        st.write("View, manage, download, or delete past generated summaries.")
        if st.button("View History", use_container_width=True):
            st.session_state["current_page"] = "History"
            st.rerun()

    with col_c:
        st.markdown("### 👤 User Profile")
        st.write("Manage your account information and view usage statistics.")
        if st.button("View Profile", use_container_width=True):
            st.session_state["current_page"] = "Profile"
            st.rerun()

    st.markdown("---")

    # Architecture Overview Expander
    with st.expander("ℹ️ How the AI Summarizer Works"):
        st.markdown("""
        **Technology Stack & Transformer Architecture:**
        - **Model**: Hugging Face `sshleifer/distilbart-cnn-12-6` Pretrained NLP Model.
        - **Architecture**: Encoder-Decoder Transformer trained on CNN/DailyMail dataset.
        - **Long Text Chunking**: Articles exceeding model token capacity are automatically split into logical paragraph chunks, summarized independently, and aggregated.
        - **Storage**: Persistent SQLite storage keeping all user data strictly isolated and secure.
        """)


def render_new_summary_page():
    """Render Create New Summary page with inputs, sample loader, and AI model execution."""
    user = get_current_user()
    st.title("📝 Create New Summary")
    st.caption("Paste your long article or select a sample below to generate an AI summary.")

    # Sample Articles Selector
    st.markdown("##### 💡 Load Sample Article")
    sample_cols = st.columns([3, 1])

    with sample_cols[0]:
        selected_sample_key = st.selectbox(
            "Choose a sample article",
            options=list(SAMPLE_ARTICLES.keys()),
            label_visibility="collapsed"
        )
    with sample_cols[1]:
        if st.button("📥 Load Sample", use_container_width=True):
            sample_data = SAMPLE_ARTICLES[selected_sample_key]
            st.session_state["input_title"] = sample_data["title"]
            st.session_state["input_article"] = sample_data["text"]
            st.success(f"Loaded '{selected_sample_key}' sample!")
            st.rerun()

    st.markdown("---")

    # Main Input Form
    title_input = st.text_input(
        "Summary Title (Optional)",
        value=st.session_state.get("input_title", ""),
        placeholder="Enter a descriptive title for this summary...",
        key="title_input_widget"
    )

    article_input = st.text_area(
        "Enter your article or text",
        value=st.session_state.get("input_article", ""),
        height=280,
        placeholder="Paste your long text, article, or research paper here...",
        key="article_input_widget"
    )

    # Sync back to session state
    st.session_state["input_title"] = title_input
    st.session_state["input_article"] = article_input

    # Dynamic Input Statistics
    cleaned_input = clean_text(article_input)
    in_words = get_word_count(cleaned_input)
    in_chars = get_char_count(cleaned_input)
    in_sentences = get_sentence_count(cleaned_input)

    st.markdown("##### 📊 Input Text Statistics")
    stat_c1, stat_c2, stat_c3 = st.columns(3)
    stat_c1.info(f"**Words:** {in_words:,}")
    stat_c2.info(f"**Characters:** {in_chars:,}")
    stat_c3.info(f"**Sentences:** {in_sentences:,}")

    # Summary Options & Controls
    st.markdown("##### ⚙️ Summarization Options")
    opt_col1, opt_col2 = st.columns([2, 1])

    with opt_col1:
        length_option = st.radio(
            "Target Summary Length",
            options=["Short", "Medium", "Detailed"],
            index=1,
            horizontal=True,
            help="Short (~60 words), Medium (~130 words), Detailed (~250 words)."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1])

    with btn_col1:
        generate_clicked = st.button("✨ Generate Summary", type="primary", use_container_width=True)

    with btn_col2:
        if st.button("🧹 Clear Input", use_container_width=True):
            st.session_state["input_article"] = ""
            st.session_state["input_title"] = ""
            st.session_state["last_generated_result"] = None
            st.rerun()

    # Trigger Generation
    if generate_clicked:
        if not cleaned_input:
            st.error("Please enter or paste some text before generating a summary.")
        elif in_words < 15:
            st.warning("The input text is too short for meaningful AI summarization (at least 15 words recommended).")
        else:
            with st.spinner("🤖 AI Pretrained Transformer model is reading and summarizing your text..."):
                try:
                    summary_output = summarize_text(cleaned_input, length_option=length_option)

                    sum_words = get_word_count(summary_output)
                    sum_chars = get_char_count(summary_output)
                    comp_percentage = calculate_compression(in_words, sum_words)

                    # Determine title
                    final_title = title_input.strip()
                    if not final_title:
                        final_title = f"Summary - {datetime.date.today().strftime('%Y-%m-%d')}"

                    # Save summary to SQLite database
                    summary_id = create_summary(
                        user_id=user["id"],
                        title=final_title,
                        original_text=cleaned_input,
                        generated_summary=summary_output,
                        original_word_count=in_words,
                        summary_word_count=sum_words,
                        compression_percentage=comp_percentage,
                        summary_length=length_option
                    )

                    result_payload = {
                        "id": summary_id,
                        "title": final_title,
                        "generated_summary": summary_output,
                        "original_word_count": in_words,
                        "summary_word_count": sum_words,
                        "summary_char_count": sum_chars,
                        "compression_percentage": comp_percentage,
                        "summary_length": length_option,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    st.session_state["last_generated_result"] = result_payload
                    st.success("Summary generated and saved to your history successfully!")

                except Exception as ex:
                    st.error(f"Failed to generate summary: {str(ex)}")

    # Display Output Section if result exists
    result = st.session_state.get("last_generated_result")
    if result:
        st.markdown("---")
        st.subheader(f"📄 {result['title']}")

        # Summary Output Container
        st.markdown(f"""
            <div class="summary-box">
                {result['generated_summary']}
            </div>
        """, unsafe_allow_html=True)

        # Output Metrics
        res_c1, res_c2, res_c3 = st.columns(3)
        res_c1.metric("Summary Words", f"{result['summary_word_count']:,}")
        res_c2.metric("Summary Characters", f"{result['summary_char_count']:,}")
        res_c3.metric("Compression Rate", f"{result['compression_percentage']:.1f}%")

        # Download Summary Button
        download_text = (
            f"AI Writer with Text Summarization\n"
            f"====================================\n\n"
            f"Title: {result['title']}\n"
            f"Date: {result['date']}\n"
            f"Summary Length: {result['summary_length']}\n\n"
            f"GENERATED SUMMARY:\n"
            f"------------------\n"
            f"{result['generated_summary']}\n\n"
            f"STATISTICS:\n"
            f"-----------\n"
            f"Original Word Count: {result['original_word_count']}\n"
            f"Summary Word Count:  {result['summary_word_count']}\n"
            f"Compression Rate:    {result['compression_percentage']:.1f}%\n"
        )

        st.download_button(
            label="📥 Download Summary (.txt)",
            data=download_text,
            file_name=f"{result['title'].replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )


def render_history_page():
    """Render Summary History page displaying saved summaries with detail expander and deletion."""
    user = get_current_user()
    st.title("📜 Summary History")
    st.caption("View and manage your previously generated summaries.")

    summaries = get_user_summaries(user["id"])

    if not summaries:
        st.info("You haven't generated any summaries yet. Click below to create your first summary!")
        if st.button("Create New Summary", type="primary"):
            st.session_state["current_page"] = "New Summary"
            st.rerun()
        return

    st.write(f"Showing **{len(summaries)}** saved summary record(s).")
    st.markdown("---")

    for item in summaries:
        with st.expander(f"📌 {item['title']} — {item['created_at'].split()[0]} ({item['summary_length']})"):
            c_meta1, c_meta2, c_meta3 = st.columns(3)
            c_meta1.markdown(f"**Original Words:** {item['original_word_count']:,}")
            c_meta2.markdown(f"**Summary Words:** {item['summary_word_count']:,}")
            c_meta3.markdown(f"**Compression:** {item['compression_percentage']:.1f}%")

            st.markdown("#### **Generated Summary:**")
            st.info(item["generated_summary"])

            with st.expander("🔍 View Original Article Text"):
                st.text_area(
                    "Original Text",
                    value=item["original_text"],
                    height=200,
                    disabled=True,
                    key=f"orig_text_{item['id']}"
                )

            # Action Buttons Row: Download & Delete
            act_col1, act_col2 = st.columns([2, 1])

            with act_col1:
                hist_download_text = (
                    f"AI Writer with Text Summarization\n"
                    f"====================================\n\n"
                    f"Title: {item['title']}\n"
                    f"Date: {item['created_at']}\n"
                    f"Length Option: {item['summary_length']}\n\n"
                    f"GENERATED SUMMARY:\n"
                    f"------------------\n"
                    f"{item['generated_summary']}\n\n"
                    f"STATISTICS:\n"
                    f"-----------\n"
                    f"Original Word Count: {item['original_word_count']}\n"
                    f"Summary Word Count:  {item['summary_word_count']}\n"
                    f"Compression Rate:    {item['compression_percentage']:.1f}%\n"
                )
                st.download_button(
                    label="📥 Download (.txt)",
                    data=hist_download_text,
                    file_name=f"{item['title'].replace(' ', '_')}_{item['id']}.txt",
                    mime="text/plain",
                    key=f"dl_hist_{item['id']}"
                )

            with act_col2:
                # Confirm deletion toggle
                confirm_del = st.checkbox("Confirm Delete", key=f"confirm_{item['id']}")
                if confirm_del:
                    if st.button("🗑️ Delete Permanently", type="primary", key=f"del_btn_{item['id']}"):
                        deleted = delete_summary(item['id'], user['id'])
                        if deleted:
                            st.success("Summary deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete summary.")


def render_profile_page():
    """Render User Profile and account statistics."""
    user = get_current_user()
    db_user = get_user_by_id(user["id"])
    stats = get_user_stats(user["id"])

    st.title("👤 User Profile")
    st.caption("Manage your profile settings and view account details.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Account Details")
        st.markdown(f"**Full Name:** {db_user['name']}")
        st.markdown(f"**Email Address:** {db_user['email']}")
        st.markdown(f"**Member Since:** {db_user['created_at'].split()[0] if db_user and db_user.get('created_at') else 'N/A'}")
        st.markdown(f"**Total Summaries Created:** {stats['total_summaries']}")
        st.markdown(f"**Total Words Processed:** {stats['total_words_processed']:,}")

        st.markdown("---")
        st.subheader("✏️ Update Display Name")
        new_name_val = st.text_input("New Full Name", value=db_user["name"], key="update_name_input")
        if st.button("Save Name Changes", type="primary"):
            if new_name_val.strip():
                updated = update_user_name(user["id"], new_name_val)
                if updated:
                    st.session_state["user_name"] = new_name_val.strip()
                    st.success("Display name updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update display name.")
            else:
                st.error("Display name cannot be empty.")

    with col2:
        st.subheader("🔒 Security & Data Privacy")
        st.success("Password Hashing: Enabled (PBKDF2 SHA-256)")
        st.info("User Isolation: Enabled (All summary records are strictly tied to your account).")
        st.markdown("""
        **Data Policy:**
        - Passwords are securely salted and hashed before storing in SQLite.
        - Plaintext passwords are never stored or logged.
        - Your generated summaries are accessible only when you are signed in.
        """)


def main():
    """Application main entry point."""
    init_app_state()
    render_sidebar()

    if not is_authenticated():
        render_auth_view()
    else:
        page = st.session_state.get("current_page", "Dashboard")
        if page == "Dashboard":
            render_dashboard_page()
        elif page == "New Summary":
            render_new_summary_page()
        elif page == "History":
            render_history_page()
        elif page == "Profile":
            render_profile_page()
        else:
            render_dashboard_page()


if __name__ == "__main__":
    main()

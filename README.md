# AI WRITER WITH TEXT SUMMARIZATION

A complete, production-style, beginner-friendly AI/ML web application built with **Python**, **Streamlit**, **Hugging Face Transformers**, and **SQLite**.

---

## 📌 Introduction

**AI Writer with Text Summarization** is an intelligent web application designed for students, researchers, content creators, and professionals. It automatically converts lengthy articles, research papers, and documents into concise, readable summaries using state-of-the-art pretrained NLP Transformer models.

---

## ❓ Problem Statement

In today's information age, individuals are inundated with vast quantities of written text daily. Reading lengthy articles, technical papers, and long news reports consumes significant time and cognitive effort. Manually extracting key takeaways is inefficient. An automated, AI-driven summarization tool synthesizes critical information instantly, saving valuable time while preserving core context.

---

## 🎯 Objective

The primary objective of this project is to build an end-to-end, production-ready AI application for a 2-week AI/ML internship. It demonstrates a complete machine learning deployment pipeline—combining user authentication, data isolation, real-time Hugging Face Transformer inference, dynamic metrics calculation, persistent SQLite storage, and a polished Streamlit user interface.

---

## 🌟 Key Features

- **User Authentication**: Complete Registration, Login, and Logout system with secure password hashing.
- **User Isolation**: All summary history records and account details are strictly isolated per registered user.
- **Pretrained Transformer Model**: Utilizes Hugging Face's `sshleifer/distilbart-cnn-12-6` (distilled BART-large-CNN) model with `@st.cache_resource` for ultra-fast, single-load model inference.
- **Summary Length Customization**: Flexible options (**Short**, **Medium**, **Detailed**) mapped to model generation parameters.
- **Long Article Handling**: Smart text chunking splits articles exceeding token limits into logical paragraphs, summarizes each chunk, and aggregates them seamlessly without truncation or crashes.
- **Real-Time Input & Output Statistics**: Calculates dynamic Word Count, Character Count, Sentence Count, and Compression Percentage.
- **Built-in Sample Articles**: Includes pre-loaded demonstration articles covering Artificial Intelligence, Education, and Technology.
- **Downloadable Summaries**: Export generated summaries as formatted `.txt` files containing complete metadata and statistics.
- **Persistent Summary History**: Saved summaries can be reviewed, expanded, downloaded, or deleted from a dedicated History dashboard.
- **Interactive Dashboard & Profile**: Overview metrics displaying total summaries generated, total words processed, latest activity date, and editable user profiles.

---

## 🛠️ Technologies Used

| Category | Technology | Description |
| :--- | :--- | :--- |
| **Programming Language** | Python 3.10+ | Core development language. |
| **Application / UI Framework** | Streamlit | Rapid, modern web UI rendering. |
| **AI / NLP Framework** | Hugging Face Transformers | Pretrained NLP pipeline (`sshleifer/distilbart-cnn-12-6`). |
| **Deep Learning Engine** | PyTorch | Model inference execution. |
| **Database** | SQLite3 | Native persistent relational database storage (`app.db`). |
| **Security & Hashing** | Werkzeug (`pbkdf2:sha256`) | Cryptographic password hashing. |

---

## 🏗️ System Architecture

```
                               ┌───────────────────────────┐
                               │     User Registration     │
                               └─────────────┬─────────────┘
                                             │
                               ┌─────────────▼─────────────┐
                               │        User Login         │
                               └─────────────┬─────────────┘
                                             │
                               ┌─────────────▼─────────────┐
                               │      User Dashboard       │
                               └─────────────┬─────────────┘
                                             │
                               ┌─────────────▼─────────────┐
                               │  Article Input / Samples  │
                               └─────────────┬─────────────┘
                                             │
                               ┌─────────────▼─────────────┐
                               │   Text Preprocessing &    │
                               │    Sentence Chunking      │
                               └─────────────┬─────────────┘
                                             │
                               ┌─────────────▼─────────────┐
                               │   Hugging Face BART-CNN   │
                               │     Transformer Model     │
                               └─────────────┬─────────────┘
                                             │
                               ┌─────────────▼─────────────┐
                               │ Display Summary, Metrics  │
                               │   & Download (.txt) File  │
                               └─────────────┬─────────────┘
                                             │
                               ┌─────────────▼─────────────┐
                               │ Save Record to SQLite DB  │
                               └───────────────────────────┘
```

---

## 📊 Database Design

The application uses SQLite (`app.db`) with relational foreign keys (`users.id → summaries.user_id`):

### `users` Table
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `name`: TEXT NOT NULL
- `email`: TEXT UNIQUE NOT NULL
- `password_hash`: TEXT NOT NULL (Hashed using PBKDF2 SHA-256)
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### `summaries` Table
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `user_id`: INTEGER NOT NULL (Foreign Key referencing `users(id)`)
- `title`: TEXT NOT NULL
- `original_text`: TEXT NOT NULL
- `generated_summary`: TEXT NOT NULL
- `original_word_count`: INTEGER NOT NULL
- `summary_word_count`: INTEGER NOT NULL
- `compression_percentage`: REAL NOT NULL
- `summary_length`: TEXT NOT NULL
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

---

## 🚀 Installation & Setup Instructions

Follow these steps to set up and run the application locally on your machine.

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/AI-Writer-Text-Summarization.git
cd AI-Writer-Text-Summarization
```

### Step 2: Create a Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Launch the Streamlit web application:

```bash
streamlit run app.py
```

After executing the command, Streamlit will open the application automatically in your default web browser at `http://localhost:8501`.

---

## 🌐 Deployment Instructions

### GitHub Deployment
1. Initialize git and commit files:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - AI Writer with Text Summarization"
   ```
2. Push your codebase to your GitHub repository.

### Streamlit Community Cloud
1. Sign in to [Streamlit Community Cloud](https://streamlit.io/cloud).
2. Click **New app**.
3. Select your GitHub repository, branch (`main`), and set Main file path to `app.py`.
4. Click **Deploy!**

> **Note on SQLite Persistence in Cloud Environments**: Streamlit Community Cloud containers are ephemeral. Database entries created in local `app.db` persist across server restarts on local installations. For cloud deployments requiring permanent cross-container persistence, connect to a cloud database (e.g., Supabase or PostgreSQL).

---

## 🔮 Future Enhancements

- 📄 **PDF & DOCX File Upload**: Support direct document parsing for summary generation.
- 🌐 **Multi-Language Support**: Integrate translation capabilities for non-English articles.
- 🎙️ **Voice Input & Text-to-Speech**: Speech recognition input and audio playback for generated summaries.
- 🤖 **Multiple NLP Models**: Allow user selection between DistilBART, T5, and Pegasus models.
- ☁️ **Cloud Database Integration**: PostgreSQL/Supabase integration for cloud persistence.



# AI Resume Matcher

This **Streamlit** web app recommends the most relevant candidates for a given job description.
It uses **SentenceTransformer embeddings** (`all-MiniLM-L6-v2`) to compute cosine similarity between the job description and each candidate resume.
The app then uses **OpenAI’s GPT model** to generate a concise AI-written summary explaining why each candidate could be a good fit.

---

## How It Works

### 1. Input

* **Job description** is entered as plain text.
* **Candidate resumes** can be uploaded (`.pdf`, `.docx`, `.txt`) or pasted directly into a text box (separated by **double newlines**).

### 2. Processing

* Resumes are extracted using **PyMuPDF** (PDF) or **docx2txt** (Word).
* Text embeddings are generated using **SentenceTransformers** with the `all-MiniLM-L6-v2` model.
* Cosine similarity is computed via **scikit-learn** to rank candidates by relevance.

### 3. Output

* Displays the **top 5–10 most relevant candidates**, showing:

  * Candidate name (or `"Candidate #"` if not found)
  * Similarity score *(0–1, higher = more relevant)*
  * AI-generated fit summary *(3–4 sentences)*

### 4. AI Summary Generation

* Uses OpenAI’s GPT model (`gpt-3.5-turbo`) to produce a short explanation of why the candidate is a good fit based on their resume, the job description, and the similarity score.

---

## API Key Setup

The OpenAI API key is stored securely in **Streamlit Secrets**.

1. Create a `.streamlit` folder in your project directory.
2. Inside `.streamlit`, create a file named `secrets.toml` with:

   ```toml
   [openai]
   api_key = "your_api_key_here"
   ```

---


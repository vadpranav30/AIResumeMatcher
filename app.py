import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import fitz  # PyMuPDF for PDFs
import docx2txt
import openai
import time


openai.api_key = st.secrets["openai"]["api_key"]



# Extract text from uploaded file
def extract_text_from_file(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc)
    elif uploaded_file.name.endswith(".docx"):
        return docx2txt.process(uploaded_file)
    elif uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")
    return ""

# Parse and preprocess all resumes
def preprocess_resumes(resume_upload, resumes_text):
    resume_texts = []

    for file in resume_upload:
        try:
            resume_texts.append(extract_text_from_file(file))
        except Exception as e:
            st.warning(f"Could not read {file.name}: {e}")

    if resumes_text.strip():
        chunks = resumes_text.strip().split("\n\n")
        for chunk in chunks:
            if chunk.strip():
                resume_texts.append(chunk.strip())

    return resume_texts

# Embed using SentenceTransformers
def embed_texts(texts, model):
    return model.encode(texts)

def generate_candidate_summary(resume_text, job_description, similarity_score):
    prompt = (
        f"Job Description:\n{job_description}\n\n"
        f"Candidate Resume:\n{resume_text}\n\n"
        f"Similarity Score: {similarity_score}\n\n"
        "Given the above, write a concise 3-4 sentence summary explaining why this candidate could be a great fit for the role. "
        "Use the similarity score to help clarify and distinguish the candidate's fit."
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary generation failed: {e}"

#StreamLit UI
st.set_page_config(page_title="AI Resume Matcher", layout="centered")
st.title("🔍 AI-Powered Resume Matcher")

st.header("1. Job Description")
job_description = st.text_area(
    "Paste the job description:",
    height=200,
    key="job_description",
    placeholder='Paste job description here...'
)

st.header("2. Candidate Resumes")
resume_upload = st.file_uploader(
    "Upload candidate resumes:",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    key="resume_upload"
)

resumes_text = st.text_area(
    "OR paste resumes separated double newlines):",
    height=200,
    key="resumes_text",
    placeholder='Paste resumes here...'
)

st.header("3. Find Relevant Candidates")

#Main Logic
if st.button("Find Top Matches"):
    if not job_description.strip():
        st.warning("Please enter a job description.")
    else:
        with st.spinner("Processing resumes and calculating matches..."):
            all_resumes = preprocess_resumes(resume_upload, resumes_text)

            if not all_resumes:
                st.warning("No resumes found. Please upload or paste at least one.")
            else:
                # Load embedding model
                model = SentenceTransformer("all-MiniLM-L6-v2")  

                # Generate embeddings
                job_embed = embed_texts([job_description], model)
                resume_embeds = embed_texts(all_resumes, model)

                # Compute similarity scores
                similarities = cosine_similarity(job_embed, resume_embeds)[0]
                sorted_indices = np.argsort(similarities)[::-1]

                # Display top matches
                top_k = min(10, len(all_resumes))
                top_rows = []
                for i in range(top_k):
                    idx = sorted_indices[i]
                    resume_text = all_resumes[idx]
                    candidate_name = resume_text.splitlines()[0].strip() if resume_text.splitlines() else f"Candidate {idx + 1}"
                    score = round(similarities[idx], 3)
                    summary = generate_candidate_summary(resume_text, job_description, score)
                    top_rows.append({
                        "Candidate Name": candidate_name,
                        "Similarity Score": score,
                        "Summary": summary
                    })
                    time.sleep(1)  # To avoid hitting rate limits

                df = pd.DataFrame(top_rows)
                st.subheader("Most Relevant Candidates")
                for row in top_rows:
                    with st.expander(f"{row['Candidate Name']} (Score: {row['Similarity Score']})"):
                        st.write(row["Summary"])

else:
    st.write("Paste a job description and resumes above, then click the button 'Find Top Matches'.")


import streamlit as st
import os
from groq import Groq
from pypdf import PdfReader

# ✅ Secure API key from Streamlit Secrets
client = Groq(api_key=os.environ["GROQ_API_KEY"])

# Page config
st.set_page_config(page_title="AI Second Brain", layout="wide")

st.title("🧠 AI Second Brain")

# Session state
if "chat" not in st.session_state:
    st.session_state.chat = []

if "chunks" not in st.session_state:
    st.session_state.chunks = []

# Upload PDF
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

# Function to split text into chunks
def split_text(text, chunk_size=1000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Process PDF
if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = ""

    for page in reader.pages:
        full_text += page.extract_text() or ""

    st.session_state.chunks = split_text(full_text)

    st.success("✅ PDF processed successfully!")

# Input question
question = st.text_input("Ask something from your PDF:")

# Function to get AI answer
def get_answer(question, context):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant. Answer only from the given PDF context."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ]
    )
    return response.choices[0].message.content

# Ask button
if st.button("Ask"):

    if uploaded_file and question:

        # Simple retrieval (first few chunks)
        context = " ".join(st.session_state.chunks[:3])

        answer = get_answer(question, context)

        st.session_state.chat.append(("You", question))
        st.session_state.chat.append(("AI", answer))

    else:
        st.warning("⚠️ Upload PDF and ask a question!")

# Display chat history
st.divider()

for role, msg in st.session_state.chat:
    if role == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 AI:** {msg}")

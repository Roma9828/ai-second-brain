import streamlit as st
from groq import Groq
from pypdf import PdfReader

client = Groq(api_key="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")

st.set_page_config(page_title="AI Second Brain", layout="wide")

st.title("🧠 AI Second Brain (Final Year Project)")


if "chat" not in st.session_state:
    st.session_state.chat = []

if "chunks" not in st.session_state:
    st.session_state.chunks = []


uploaded_file = st.file_uploader("Upload PDF", type="pdf")

def split_text(text, chunk_size=1000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = ""

    for page in reader.pages:
        full_text += page.extract_text() or ""

    st.session_state.chunks = split_text(full_text)

    st.success("PDF processed successfully!")


question = st.text_input("Ask something from your PDF:")


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


if st.button("Ask"):

    if uploaded_file and question:

        # combine chunks (simple retrieval)
        context = " ".join(st.session_state.chunks[:3])

        answer = get_answer(question, context)

        st.session_state.chat.append(("user", question))
        st.session_state.chat.append(("ai", answer))

    else:
        st.warning("Upload PDF and ask a question!")


for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 AI:** {msg}")
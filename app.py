import streamlit as st
from groq import Groq
from pypdf import PdfReader

# 🔐 API KEY (Replace with your new key)
client = Groq(api_key="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")

st.set_page_config(page_title="AI Second Brain", layout="wide")

# ---------------- LOGIN SYSTEM ---------------- #
USERS = {"khushwant": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def login_page():
    st.title("🔐 Login to AI Second Brain")
    st.caption("Enter your credentials")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Username or Password ❌")

# ---------------- MAIN APP ---------------- #
def main_app():

    # Sidebar
    st.sidebar.title("🧠 AI Second Brain")
    st.sidebar.write(f"Welcome, {st.session_state.username} 👋")

    menu = st.sidebar.selectbox("Menu", ["Home", "History", "Logout"])

    # Session states
    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "chunks" not in st.session_state:
        st.session_state.chunks = []

    # ---------------- HOME ---------------- #
    if menu == "Home":

        st.title("🤖 My AII Assistent")

        uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf")

        def split_text(text, chunk_size=1000):
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

        if uploaded_file:
            reader = PdfReader(uploaded_file)
            full_text = ""

            for page in reader.pages:
                full_text += page.extract_text() or ""

            st.session_state.chunks = split_text(full_text)
            st.success("✅ PDF processed successfully!")

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

                with st.spinner("Thinking... 🤖"):
                    context = " ".join(st.session_state.chunks[:3])
                    answer = get_answer(question, context)

                st.session_state.chat.append(("You", question))
                st.session_state.chat.append(("AI", answer))

                st.success("Answer generated!")
                st.write("🤖 AI:", answer)

            else:
                st.warning("⚠️ Upload PDF and ask a question!")


    # ---------------- HISTORY ---------------- #
    elif menu == "History":

        st.title("📜 Chat History")

        if st.session_state.chat:
            for role, msg in st.session_state.chat[::-1]:
                if role == "You":
                    st.markdown(f"**🧑 You:** {msg}")
                else:
                    st.markdown(f"**🤖 AI:** {msg}")
                st.divider()
        else:
            st.info("No history yet!")

    # ---------------- LOGOUT ---------------- #
    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# ---------------- ROUTING ---------------- #
if st.session_state.logged_in:
    main_app()
else:
    login_page()
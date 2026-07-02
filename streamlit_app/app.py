"""FinSolve Technologies - Role-Based Internal Chatbot UI."""

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="FinSolve Internal Chatbot",
    page_icon="💬",
    layout="wide",
)

st.title("FinSolve Internal Chatbot")
st.caption("Secure, role-based access to company knowledge")


def login(username: str, password: str) -> dict | None:
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        st.error(f"Cannot connect to API at {API_URL}. Is the backend running?")
        return None


def ask_question(token: str, query: str) -> dict | None:
    try:
        response = requests.post(
            f"{API_URL}/chat/query",
            json={"query": query},
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        if response.status_code == 200:
            return response.json()
        if response.status_code == 401:
            st.warning("Session expired. Please log in again.")
            return None
        st.error(f"API error: {response.status_code} - {response.text}")
        return None
    except requests.RequestException as exc:
        st.error(f"Request failed: {exc}")
        return None


def logout() -> None:
    for key in ["token", "user", "messages"]:
        st.session_state.pop(key, None)


# Session state initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# Login screen
if not st.session_state.token:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Sign In")
        st.info(
            "Demo accounts (password: **finsolve123**): "
            "`finance_user`, `marketing_user`, `hr_user`, "
            "`engineering_user`, `executive_user`, `employee_user`"
        )
        username = st.text_input("Username", placeholder="e.g. finance_user")
        password = st.text_input("Password", type="password")
        if st.button("Login", type="primary", use_container_width=True):
            result = login(username, password)
            if result:
                st.session_state.token = result["access_token"]
                st.session_state.user = result
                st.session_state.messages = []
                st.rerun()
            else:
                st.error("Invalid username or password.")
else:
    user = st.session_state.user

    with st.sidebar:
        st.markdown(f"**User:** {user['display_name']}")
        st.markdown(f"**Role:** `{user['role']}`")
        st.markdown("**Accessible departments:**")
        for dept in user["allowed_departments"]:
            st.markdown(f"- {dept}")
        st.divider()
        st.markdown("**Sample questions**")
        samples = {
            "finance": "What was FinSolve's revenue growth in 2024?",
            "marketing": "Summarize Q3 2024 campaign performance.",
            "hr": "What is the average performance rating in HR data?",
            "engineering": "Describe FinSolve's microservices architecture.",
            "executive": "Give a company-wide summary across departments.",
            "employee": "What is the leave policy for annual leave?",
        }
        sample = samples.get(user["role"], "What company policies should I know?")
        st.caption(sample)
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Sources"):
                    for src in msg["sources"]:
                        st.markdown(
                            f"**{src['document']}** ({src['department']}) — "
                            f"score: {src.get('relevance_score', 'N/A')}"
                        )
                        st.caption(src["excerpt"])

    if prompt := st.chat_input("Ask a question about company data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving context and generating answer..."):
                result = ask_question(st.session_state.token, prompt)
            if result:
                st.markdown(result["answer"])
                if result["sources"]:
                    with st.expander("Sources"):
                        for src in result["sources"]:
                            st.markdown(
                                f"**{src['document']}** ({src['department']}) — "
                                f"score: {src.get('relevance_score', 'N/A')}"
                            )
                            st.caption(src["excerpt"])
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                    }
                )
            elif st.session_state.token is None:
                st.rerun()

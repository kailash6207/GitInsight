import streamlit as st
from google import genai
from google.genai import types
from github_helper import get_repo_contents

st.set_page_config(page_title="GitHub Repo Chat", page_icon="🐙", layout="wide")

st.title("🐙 GitHub Repository Explorer")
st.markdown("Enter a GitHub username and repository to ask questions about the codebase.")

# Inject custom CSS to hide the Streamlit menu and footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Global memory bank that survives browser refreshes
@st.cache_resource
def get_memory_bank():
    return {
        "repo_histories": {},
        "gemini_key": "",
        "github_token": ""
    }

memory = get_memory_bank()

# --- NEW: Session State that wipes clean on refresh ---
# If you refresh, this resets to None, making the main page go blank.
if "current_repo" not in st.session_state:
    st.session_state.current_repo = None

# Sidebar for configuration and history
with st.sidebar:
    st.header("Settings")
    
    gemini_key = st.text_input("Gemini API Key", type="password", value=memory["gemini_key"])
    github_token = st.text_input("GitHub Token", type="password", value=memory["github_token"])
    
    memory["gemini_key"] = gemini_key
    memory["github_token"] = github_token
    
    st.divider()
    
    st.header("Target Repository")
    username = st.text_input("GitHub Username", placeholder="e.g., hwchase17")
    repo = st.text_input("Repository Name", placeholder="e.g., langchain")
    
    load_button = st.button("Load Repository")
    
    st.divider()
    
    st.header("📜 Chat History")
    if memory["repo_histories"]:
        for loaded_repo in memory["repo_histories"].keys():
            # Highlight the currently active one with a green circle
            is_active = (loaded_repo == st.session_state.current_repo)
            button_label = f"🟢 {loaded_repo}" if is_active else f"📂 {loaded_repo}"
            
            if st.button(button_label, use_container_width=True):
                # Clicking a history button sets the active view back to this repo
                st.session_state.current_repo = loaded_repo
                st.rerun() 
    else:
        st.caption("No repositories loaded yet.")

# Handle NEW repository loading
if load_button:
    if not gemini_key:
        st.sidebar.error("Please provide a Gemini API Key.")
    elif not username or not repo:
        st.sidebar.error("Please provide both Username and Repository name.")
    else:
        repo_key = f"{username.strip().lower()}/{repo.strip().lower()}"
        # Set the active view to the newly loaded repo
        st.session_state.current_repo = repo_key
        
        if repo_key not in memory["repo_histories"]:
            with st.spinner(f"Fetching files for {repo_key}..."):
                code_context, message = get_repo_contents(username.strip(), repo.strip(), github_token)
                
                if code_context:
                    client = genai.Client(api_key=gemini_key)
                    
                    new_session = client.chats.create(
                        model="gemini-2.5-flash",
                        config=types.GenerateContentConfig(
                            system_instruction="You are an expert software engineer. Answer questions based on the provided codebase."
                        )
                    )
                    
                    new_session.send_message(
                        f"Here is the codebase for {username}/{repo}. Read it and prepare to answer questions:\n\n{code_context[:750000]}"
                    )
                    
                    # Save the new chat to the permanent memory bank
                    memory["repo_histories"][repo_key] = {
                        "messages": [],
                        "chat_session": new_session,
                        "client": client
                    }
                    st.sidebar.success(f"Successfully loaded {repo_key}!")
                
                elif message == "TOKEN_EXPIRED":
                    st.sidebar.warning("⚠️ **Token Expired!** Your GitHub Token is invalid or expired. Please generate a new one in your GitHub settings.")
                    st.session_state.current_repo = None
                else:
                    st.sidebar.error(message)
                    st.session_state.current_repo = None
        else:
            st.sidebar.success(f"Switched back to cached history for {repo_key}!")

# Chat Interface
# We check st.session_state instead of memory to see if we should display a chat
if st.session_state.current_repo and st.session_state.current_repo in memory["repo_histories"]:
    current_key = st.session_state.current_repo
    repo_data = memory["repo_histories"][current_key]
    
    st.caption(f"Currently viewing history for: **{current_key}**")
    
    for msg in repo_data["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"].replace("$", r"\$"))

    if prompt := st.chat_input(f"Ask a question about {current_key}..."):
        st.chat_message("user").markdown(prompt)
        repo_data["messages"].append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing codebase..."):
                try:
                    response = repo_data["chat_session"].send_message(prompt)
                    st.markdown(response.text.replace("$", r"\$"))
                    repo_data["messages"].append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"An error occurred: {e}")
else:
    display_name = username if username else "Kaiser"
    st.info(f"👋 Hello {display_name}, ready to learn?")
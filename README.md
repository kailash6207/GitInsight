# 🐙 GitInsight

An interactive, AI-powered web application built with **Streamlit** and the **Google GenAI SDK** that helps you learn, explore, and chat with GitHub repositories. Simply input a public repository, and instantly ask questions about its architecture, logic, or setup steps.

### ✨ Key Features
* 💬 **Context-Aware Code Chat:** Primed with repository code logic using `gemini-2.5-flash`.
* 📜 **Persistent Multi-Repo History:** Switch seamlessly between different scanned codebases without losing your chat logs.
* 🛡️ **Session Memory:** Your API keys and chat histories survive accidental browser refreshes.
* 🎨 **Clean Custom UI:** A tailored interface built specifically for reading code and developer explanations safely without layout-breaking LaTeX bugs.
* ⚡ **Optimized File Fetching:** Intelligently filters out massive lock files to stay safely within LLM token limits.

### 🛠️ Prerequisites
To run this app locally, you will need:
1. Python 3.8+
2. A [Gemini API Key](https://aistudio.google.com/app/apikey)
3. A [GitHub Personal Access Token](https://github.com/settings/tokens) (Classic or Fine-grained)

### 🚀 Installation & Setup

---

**1. Clone the repository:**
```bash
git clone [https://github.com/kailash6207/GitInsight.git](https://github.com/kailash6207/GitInsight.git)
cd GitInsight

---

2. Install dependencies:

Bash
pip install -r requirements.txt

---

3. Run the application:

Bash
streamlit run app.py

---

💡 How to Use
Open the local link provided by Streamlit in your browser.

Enter your Gemini API Key and GitHub Token in the left sidebar.

Enter the target GitHub username and repository name (e.g., hwchase17 and langchain).

Click Load Repository and start asking questions!

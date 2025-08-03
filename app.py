import os
from dotenv import load_dotenv
from pathlib import Path
import time

# --- Flask for the Web Server ---
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# --- LangChain and LLM Imports ---
# UPDATED: Switched back to Groq
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, tool, create_json_chat_agent
from langchain.prompts import PromptTemplate

# --- Pydantic for robust tool inputs ---
from pydantic import BaseModel, Field

# --- Playwright for Browser Control ---
from playwright.sync_api import sync_playwright, Page

# --- Initial Setup ---
print("🔑 Loading API keys...")
dotenv_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=dotenv_path)
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# UPDATED: Check for the Groq API Key
if not os.getenv("GROQ_API_KEY"):
    print("\n❌ ERROR: GROQ_API_KEY not found in .env file.")
    print("Please ensure your .env file contains your Groq API key.")
    exit()

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- Global variable for the Playwright page object ---
page: Page = None

# --- Global Agent Setup ---
# UPDATED: The agent's brain is now Groq again
print("🧠 Setting up the AI's brain with Groq...")
llm = ChatGroq(model="llama3-70b-8192", temperature=0)

# --- Tool Definitions (Rewritten for a more autonomous agent) ---

@tool
def google_search(query: str) -> str:
    """
    Use this as the first step for any task that requires accessing the web.
    This tool is for general web searches to find information or websites.
    """
    global page
    if not page: return "Browser is not running."
    print(f"  > Tool Action: Searching Google for '{query}' with Playwright")
    try:
        page.goto("https://www.google.com", wait_until="domcontentloaded")
        page.locator('textarea[name="q"]').fill(query)
        page.keyboard.press("Enter")
        return f"Successfully searched for '{query}'. The results are now on the screen."
    except Exception as e:
        return f"Error during Google search: {e}"

@tool
def navigate_to_url(url: str) -> str:
    """
    Use this tool to navigate to a specific URL that you have discovered.
    """
    global page
    if not page: return "Browser is not running."
    print(f"  > Tool Action: Navigating to {url}")
    try:
        page.goto(url, wait_until="domcontentloaded")
        return f"Successfully navigated to {url}."
    except Exception as e:
        return f"Error navigating to url: {e}"

class TypeTextInput(BaseModel):
    css_selector: str = Field(description="The CSS selector of the input field to type into.")
    text: str = Field(description="The text to type into the input field.")

@tool(args_schema=TypeTextInput)
def type_text(css_selector: str, text: str) -> str:
    """
    Use this tool to type text into an input field on a webpage, like a search bar or a form field.
    """
    global page
    if not page: return "Browser is not running."
    print(f"  > Tool Action: Typing '{text}' into element '{css_selector}'")
    try:
        page.locator(css_selector).fill(text)
        return f"Successfully typed '{text}' into the element."
    except Exception as e:
        return f"Error typing text: {e}"

@tool
def click_element(css_selector: str) -> str:
    """
    Use this tool to click on an element on a webpage, such as a button or a link.
    """
    global page
    if not page: return "Browser is not running."
    print(f"  > Tool Action: Clicking element '{css_selector}'")
    try:
        page.locator(css_selector).click()
        return f"Successfully clicked the element."
    except Exception as e:
        return f"Error clicking element: {e}"

@tool
def read_current_page_content() -> str:
    """
    Use this tool to read the visible text content of the current webpage to find information or decide the next step.
    """
    global page
    if not page: return "Browser is not running."
    print("  > Tool Action: Reading page content with Playwright")
    try:
        page.wait_for_load_state("networkidle")
        content = page.locator('body').inner_text()
        return content[:4000]
    except Exception as e:
        return f"Could not get page content. Error: {e}"


# --- The agent's toolbox now contains general-purpose browser tools ---
tools = [google_search, navigate_to_url, type_text, click_element, read_current_page_content]

# --- Custom prompt with all required variables ---
prompt_template = """
You are a powerful AI browser agent. Your goal is to complete the user's task by using the available tools.

**TOOLS:**
You have access to the following tools:
{tools}

To use a tool, please respond with a JSON object with a single `action` key and a single `action_input` key.
The `action` key should be the name of the tool to use, which must be one of {tool_names}.
The `action_input` key should be the input to the tool.

When you have the final answer, respond with a JSON object containing a single `action` key with the value `Final Answer` and a single `action_input` key with your final answer.

**IMPORTANT RULES:**
- Do not stop until the final answer to the user's original request has been found.
- After searching or navigating, you MUST use the `read_current_page_content` tool to understand what is on the screen.
- Break down complex tasks into smaller, logical steps.

**BEGIN!**

**USER'S TASK:**
{input}

**PREVIOUS STEPS (CHAT HISTORY):**
{chat_history}

**AGENT'S SCRATCHPAD (YOUR THOUGHTS AND PREVIOUS ACTIONS):**
{agent_scratchpad}
"""
prompt = PromptTemplate.from_template(prompt_template)

agent = create_json_chat_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
)

# --- Route to serve the frontend ---
@app.route('/')
def index():
    return render_template('index.html')

# --- API Endpoint for the agent ---
@app.route('/execute-task', methods=['POST'])
def execute_task():
    global page
    print("\n🚀 Received a new task from the frontend!")
    data = request.json
    task = data.get('task')

    if not task:
        return jsonify({"error": "No task provided"}), 400
    
    with sync_playwright() as p:
        try:
            print("🖥️  Setting up Playwright browser for this task...")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            print(f"▶️  Starting agent with task: '{task}'")
            # We pass an empty chat history to start
            result = agent_executor.invoke({"input": task, "chat_history": []})
            
            print("✅ --- Agent Finished ---")
            time.sleep(5) 
            return jsonify({"result": result['output']})

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            if 'browser' in locals() and browser.is_connected():
                print("🖥️  Task complete. Closing browser.")
                browser.close()


# --- Run the Server ---
if __name__ == '__main__':
    print("🚀 Starting Flask server at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
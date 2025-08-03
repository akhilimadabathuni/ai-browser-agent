AI Browser Agent 🤖
Welcome to the AI Browser Agent, a powerful and interactive application that uses a large language model to understand your commands and control a web browser to perform tasks autonomously.

This project combines a sophisticated AI "brain" with robust browser automation "hands" to create a personal assistant that can browse the web, find information, and complete tasks on your behalf, all through a sleek, futuristic web interface.


✨ Core Features
Natural Language Control: Give the agent tasks in plain English. It understands your intent and formulates a plan to achieve your goal.

Autonomous Browser Automation: The agent launches and controls a real browser window on your computer to navigate websites, fill out forms, click buttons, and read content.

Multi-Tool Capability: Intelligently selects the right tool for the job. It can perform a general Google search or execute a specific, multi-step task like searching for bus tickets on a booking website.

Interactive Web Interface: A user-friendly, responsive frontend with a dark, high-VFX theme allows you to easily command the agent and view its final reports.

Extensible by Design: The project is structured to be easily expandable. You can add new tools and skills to the agent by simply creating new Python functions.

🛠️ Technology Stack
Backend Framework: Python with Flask

AI Agent Framework: LangChain

LLM (The "Brain"): Groq API (Llama 3 70B)

Browser Automation (The "Hands"): Playwright

Frontend: HTML, Tailwind CSS, JavaScript

🚀 Getting Started
Follow these steps to set up and run the project on your local machine.

1. Prerequisites
Python 3.8+ installed on your system.

A web browser like Google Chrome.

A free API key from Groq.

2. Clone the Repository
git clone https://github.com/akhilimadabathuni/ai-browser-agent.git
cd ai-browser-agent

3. Install Dependencies
Install all the required Python packages:

# It's recommended to use a virtual environment
py -m venv venv
venv\Scripts\activate

# Install packages
py -m pip install flask flask-cors langchain langchain-groq playwright python-dotenv pydantic

# Install Playwright's browser binaries
py -m playwright install

4. Set Up API Keys
In the root of the project folder, create a file named .env.

Add your Groq API key to this file:

GROQ_API_KEY="gsk_...your_secret_groq_key..."

💡 How to Use
1. Run the Backend Server

Open a terminal in the project folder and start the Flask application:

py app.py

You will see output indicating that the server is running on http://127.0.0.1:5000.

2. Open the Frontend

Open your web browser (e.g., Chrome, Firefox).

Navigate to the following address:
http://127.0.0.1:5000

The web interface will load. Now you can give your agent a task!

Example Commands:

"Search for the lowest price buses from Hyderabad to Vijayawada."

"What is the latest news about the Indian stock market?"

"Who won the last FIFA world cup?"

When you click "LAUNCH AGENT", a new browser window will open on your computer, and you will see the agent performing the steps to complete your request.
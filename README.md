 AI-Powered Code Reviewer & Quality Assistant

 
 📌 Overview
AI-Powered Code Reviewer Pro combines static AST analysis with LLM intelligence to automate one of the most tedious parts of software development — writing documentation.
Upload any .py file or point it at a folder, and the tool instantly:

Maps every function and class across your codebase
Measures docstring coverage with per-file breakdowns
Generates structured docstrings in Google, NumPy, or reST format
Validates PEP 257 compliance and highlights violations
Writes approved docstrings directly back to your source files


✨ Features
🧠 AI Docstring Generator

3 style formats — Google, NumPy, reST
LLM backends — Groq (cloud), Ollama (local), OpenAI
Smart rule engine — works without any API key
Edit generated docstrings inline before applying
One-click write-back to disk — VS Code auto-reloads

✅ Code Validation

PEP 257 compliance for modules, functions, and classes
Live inline fix buttons per function
Pie charts showing violation distribution by rule and file
Syntax error detection with editor fallback

📊 Coverage Dashboard

Cyclomatic complexity scored per function
Docstring coverage % with progress bars
Per-file stats table with sorting
Complexity heatmap — red flags high-risk functions

🔍 Filters, Search & Export

Filter results by documentation status (OK / Fix)
Instant search across all parsed functions
Export full report as JSON or CSV
CI/CD-ready output format


🏗️ Architecture
┌─────────────────────────────────┐
│     Streamlit UI  (main_app.py) │
└────────────────┬────────────────┘
                 │
         Unified File Input
         (upload or folder path)
                 │
    ┌────────────▼────────────┐
    │   AST Parser            │  ← core/parser/python_parser.py
    │   Extract functions,    │
    │   args, types, bodies   │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │   AI Docstring Engine   │  ← core/docstring_engine/
    │   Rule-based + LLM      │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │   Validation Engine     │  ← core/validator/validator.py
    │   PEP 257 compliance    │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │   Coverage Reporter     │  ← core/reporter/coverage_reporter.py
    │   Stats, JSON, CSV      │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │   Dashboard & Export    │  ← dashboard_ui/
    └─────────────────────────┘

⚙️ Tech Stack
LayerTechnologyFrontendStreamlitBackendPython 3.9+AST ParsingPython built-in ast moduleAI — CloudGroq API (llama3-8b-8192)AI — LocalOllama (mistral)VisualizationPlotly, MatplotlibData ProcessingPandasTestingpytest

📂 Project Structure
AI_POWERED_CHATBOT/
│
├── main_app.py                   # ← Entry point — run this
│
├── core/
│   ├── parser/
│   │   └── python_parser.py      # AST parsing, scan, inject docstrings
│   ├── docstring_engine/
│   │   ├── generator.py          # Rule-based docstring generation
│   │   └── llm_integration.py    # Groq / Ollama / OpenAI backends
│   ├── reporter/
│   │   └── coverage_reporter.py  # JSON/CSV export, per-file stats
│   ├── review_engine/
│   │   └── ai_review.py          # Orchestrates review + file write-back
│   └── validator/
│       └── validator.py          # PEP 257 compliance checks
│
├── dashboard_ui/
│   └── dashboard.py              # Streamlit UI components & nav cards
│
├── examples/
│   ├── sample_a.py               # Demo file A — undocumented functions
│   └── sample_b.py               # Demo file B — mixed coverage
│
├── experiments/
│   ├── llm_groq.py               # Groq API generation test script
│   └── llm_local.py              # Local Ollama generation test script
│
├── storage/
│   └── reports/                  # Auto-generated JSON/CSV reports
│
├── tests/
│   ├── test_parser.py
│   ├── test_generator.py
│   ├── test_coverage_reporter.py
│   ├── test_validation.py
│   ├── test_llm_integration.py
│   └── test_dashboard.py
│
├── .env                          # API keys — never commit this file
├── requirements.txt
└── README.md

🚀 Quick Start
Option A — No API key needed (rule-based)
bashgit clone https://github.com/your-username/AI_POWERED_CHATBOT.git
cd AI_POWERED_CHATBOT
pip install -r requirements.txt
streamlit run main_app.py
Then click 🧪 Load Demo Files in the sidebar — no setup required.
Option B — With Groq AI (recommended)
bashpip install -r requirements.txt
Create .env in the project root:
envGROQ_API_KEY=your_groq_api_key_here
Get a free key at console.groq.com → then run:
bashstreamlit run main_app.py
Option C — Fully local with Ollama (no internet needed)
bashollama pull mistral
ollama serve
Set in .env:
envOLLAMA_HOST=http://localhost:11434

🖥️ How to Use
StepAction1Open the app at http://localhost:85012Upload .py files or paste a folder path in the sidebar3Click ▶ Load & Analyse4Navigate pages using the View dropdown5Generate, edit, and save docstrings from 🔮 Docstring Reviewer6Export your coverage report from 📊 Dashboard → Export

🌐 Deploy to Streamlit Cloud

Push your repo to GitHub
Go to streamlit.io/cloud → New app
Select your repo, set main file to main_app.py
Under Settings → Secrets, add:

tomlGROQ_API_KEY = "your_groq_api_key_here"

Hit Deploy 🚀 — live in under 2 minutes


Tip: Delete the pages/ folder before deploying to avoid unwanted Streamlit multi-page navigation.


🧪 Running Tests
bash# Run the full test suite
pytest tests/ -v

# Run a specific module
pytest tests/test_parser.py -v
pytest tests/test_coverage_reporter.py -v
pytest tests/test_validation.py -v

📊 Key Results
MetricValueDocumentation coverage improvement70%+Docstring styles supported3 (Google, NumPy, reST)LLM backends supported3 (Groq, Ollama, OpenAI)Export formatsJSON, CSVTest files6

✅ Advantages

Zero config to start — works out of the box with demo files
Offline capable — use Ollama for fully local AI generation
Non-destructive — preview and edit before writing to disk
CI/CD friendly — JSON/CSV exports plug into any pipeline
Dark & light theme — easy on the eyes either way


⚠️ Limitations

Supports Python only (.py files)
LLM generation requires either an API key or local Ollama
Folder path write-back needs local filesystem access — not available on Streamlit Cloud


🔮 Future Scope

🌍 Multi-language support (JavaScript, TypeScript, Java)
🤖 GitHub PR bot — auto-comment missing docstrings on pull requests
🔧 AI-powered refactoring suggestions beyond docstrings
📈 Historical coverage trends dashboard for teams
🧩 VS Code extension


🤝 Contributing
Contributions are welcome!
bash# 1. Fork the repo and clone it
git clone https://github.com/your-username/AI_POWERED_CHATBOT.git

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes and run tests
pytest tests/ -v

# 4. Commit and push
git commit -m "feat: add your feature"
git push origin feature/your-feature-name

# 5. Open a Pull Request

📜 License
This project is licensed under the MIT License — see the LICENSE file for details.
Free to use, modify, and distribute for personal and commercial projects.

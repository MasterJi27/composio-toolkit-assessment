# Toolkit Parity Agent
An AI agent platform that audits 100 developer APIs for buildability, auth methods, self-serve access, and MCP coverage.

**Live Case Study URL**: [https://composio-research-report.vercel.app](https://composio-research-report.vercel.app)

**Source Repo URL**: [https://github.com/MasterJi27/composio-toolkit-assessment](https://github.com/MasterJi27/composio-toolkit-assessment)

---

## How to Run the Agent

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/MasterJi27/composio-toolkit-assessment.git
cd composio-toolkit-assessment

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure Environment Variables
Open the `.env` file and set the following keys:
```env
COMPOSIO_API_KEY=your_composio_api_key  # Optional: For Composio SDK integration
GEMINI_API_KEY=your_gemini_api_key      # Required for Agentic execution
```

### 3. Run the Research Pipeline
```bash
# Run deterministic pipeline (Fast, loads pre-verified documentation data)
python -m cli.main run-pipeline

# Run agentic pipeline (Queries Gemini Flash 1.5 and Composio MCP to research live APIs)
python -m cli.main run-pipeline --agentic --limit 10
```

### 4. Run Verification Loop
```bash
# Verify the agent findings against a stratified sample of 20 apps
python -m cli.main verify
```

---

## Project Structure
```
composio-toolkit-assessment/
├── agents/             # Research, Evidence, Verification, and Pattern Discovery agents
├── research/           # SaaS app categories and profiled database
├── backend/            # SQLite client & Composio SDK wrappers
├── reports/            # Jinja2 template report builders
├── index.html          # Deployed static HTML report page (copied to root)
├── vercel.json         # Vercel static deployment config
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

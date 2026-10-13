# Comparative AI Refactoring Pipeline

An automated, empirical benchmarking pipeline designed to evaluate Large Language Models (OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet, and offline Mock providers) on legacy code refactoring. The system quantitatively measures changes in code maintainability, cognitive effort, and cyclomatic complexity while enforcing strict behavioral invariance inside a zero-trust Docker execution sandbox.

---

## Architecture & Features

- **Multi-Provider LLM Abstraction:** Seamlessly switch between OpenAI (`gpt-4o`, `gpt-4o-mini`), Anthropic (`claude-3-5-sonnet`), and offline deterministic `mock` providers via an extensible factory.
- **Dual-Tier Metric Evaluation:**
  - **Static Analysis:** Computes McCabe Cyclomatic Complexity ($CC$), Halstead Volume ($HV$), and Maintainability Index ($MI$) via AST parsing with [Radon](https://radon.readthedocs.io/).
  - **Dynamic Sandboxed Testing:** Executes untrusted, AI-generated code against full pytest regression suites inside an isolated Docker container with complete network disablement (`--network none`), dropped capabilities (`--cap-drop=ALL`), and strict resource limits.
- **Behavioral Invariance Guarantee:** Verifies that candidate refactored code passes 100% of existing tests with no behavioral regressions.
- **Persistent Telemetry:** Automatically logs experimental runs, researcher metadata, and metric deltas to SQLite or MySQL using SQLAlchemy.
- **Automated Visualization:** Produces publication-ready grouped delta bar charts comparing complexity and maintainability shifts across prompting strategies.

---

## Project Structure

```text
actual_app/
├── app/
│   ├── models/                  # Domain dataclasses (Researcher, Metrics, Prompts)
│   ├── services/                # Core business logic
│   │   ├── ai_refactoring_service.py     # AI request orchestrator
│   │   ├── code_cleaner.py               # Markdown fence & code sanitization
│   │   ├── dataset_service.py            # Dataset loader and file finder
│   │   ├── docker_sandbox_service.py     # Ephemeral container execution runner
│   │   ├── experiment_runner.py          # Factorial matrix benchmark runner
│   │   ├── provider_factory.py           # LLM provider factory
│   │   ├── reporting_service.py          # Delta calculation & CSV exporter
│   │   ├── static_analysis_service.py    # Radon static metric extractor
│   │   └── visual_reporting_service.py   # Matplotlib delta chart generator
│   ├── storage/                 # Database connection & SQLAlchemy repository
│   └── main.py                  # CLI pipeline entry point
├── datasets/
│   ├── legacy/                  # Target legacy Python source files
│   └── tests/                   # Associated pytest verification suites
├── docker/
│   └── Dockerfile               # Minimal Python Alpine image for test sandboxing
├── results/                     # Output directory for benchmarks, charts, and DB
│   ├── benchmark_report.csv
│   ├── complexity_maintainability_delta.png
│   └── research_benchmark.db
├── scripts/                     # Utility scripts (e.g., HumanEval dataset loader)
├── tests/                       # Unit and integration tests for the pipeline
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment variable template
```

---

## Prerequisites

- **Python:** Version 3.10 to 3.13
- **Docker Engine / Docker Desktop:** Running locally (required for sandboxed test execution)
- **Git:** Version 2.20+

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/spkara25/Comparative-AI-Refactoring-Pipeline.git
cd Comparative-AI-Refactoring-Pipeline/actual_app
```

### 2. Create and Activate a Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (WSL or PowerShell)
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template file to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to configure your preferred provider and API keys:
```ini
# Provider Options: mock | openai | anthropic
LLM_PROVIDER=mock

# Model Selection:
# For OpenAI: gpt-4o-mini, gpt-4o
# For Anthropic: claude-3-5-sonnet-20241022
# For Mock: mock-default
LLM_MODEL=mock-default

# API Keys (Required only if using live cloud providers)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Researcher Metadata (Optional)
RESEARCHER_NAME="Shreeja Karajagi"
RESEARCHER_EMAIL="researcher@benchmark.local"
```

> **Note:** The `mock` provider runs completely offline and requires no API keys or network connection.

### 5. Build the Docker Sandbox Image
Ensure Docker Desktop or the Docker daemon is running, then build the sandbox image:
```bash
docker build -t ai-refactor-sandbox docker/
```

Verify that the image built successfully:
```bash
docker image inspect ai-refactor-sandbox > /dev/null && echo "Sandbox ready!"
```

---

## Running the Pipeline

Execute the main CLI entry point:
```bash
python -m app.main
```

### What Happens During Execution:
1. **Database Initialization:** Sets up the SQLite database schema in `results/research_benchmark.db` and registers the active researcher.
2. **Dataset Ingestion:** Discovers legacy code modules in `datasets/legacy` (`humaneval_0.py`–`4.py`, `monolithic_processor.py`, `nested_calculator.py`) and maps them to their respective test suites in `datasets/tests/`.
3. **Experiment Matrix Setup:** Prepares prompting strategies:
   - *Strategy 1:* Refactor to adhere strictly to PEP 8 standards with type hints and docstrings.
   - *Strategy 2:* Refactor to reduce cyclomatic complexity and flatten conditional branches.
4. **Execution & Metric Extraction:**
   - Evaluates baseline static metrics on the host OS using Radon.
   - Invokes the selected LLM provider and cleans markdown formatting via regex sanitization.
   - Evaluates refactored static metrics.
   - Mounts original and refactored code into the isolated Docker container to execute dynamic tests and extract coverage percentages.
   - Evaluates behavioral invariance ($\text{PassRate}_{\text{refact}} \ge \text{PassRate}_{\text{orig}}$).
5. **Persistence & Export:**
   - Persists all metrics and experiment records to the relational database.
   - Writes a full CSV report to `results/benchmark_report.csv`.
   - Generates a grouped delta bar chart at `results/complexity_maintainability_delta.png`.

---

## Generated Artifacts

Upon completion, all outputs are located in the `results/` folder:

- **`results/benchmark_report.csv`:** Detailed metrics per run (original vs. refactored CC, Halstead Volume, Maintainability Index, pass rate, coverage, delta calculations, and boolean `behavior_preserved`).
- **`results/complexity_maintainability_delta.png`:** Comparative visualization of $\Delta CC$ vs. $\Delta MI$ across all experimental runs.
- **`results/research_benchmark.db`:** SQLite database storing normalized tables (`researchers`, `evaluation_metrics`, `experiment_results`).

---

## Running the Test Suite

The repository contains unit tests, integration tests, and sandbox validation tests:

```bash
# Run all tests
pytest tests/

# Run with verbose output and coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

To run end-to-end pipeline verification:
```bash
pytest tests/test_e2e_pipeline.py -v
```

---

## Security Sandbox Specifications

To protect the host operating system against untrusted or hallucinated generative code, the Docker sandbox enforces:
- `--network none`: Complete network isolation.
- `--read-only`: Read-only root filesystem.
- `--cap-drop=ALL`: Removal of all Linux kernel capabilities.
- `--security-opt=no-new-privileges`: Prevention of privilege escalation.
- `--memory=256m` and `--cpus=1`: Strict resource limits preventing denial-of-service / fork-bombs.
- Temporary volume mounts (`/sandbox:ro` and `/results:rw`) to strictly isolate source code from result telemetry.

---

## License & Citation

Developed for empirical software engineering research in automated code refactoring. For citation details, refer to the [IEEE Project Report](IEEE_Project_Report.md).

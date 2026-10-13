# Comparative AI Refactoring Pipeline

A research-oriented Python application for evaluating Large Language Models (LLMs) on legacy Python code refactoring. The pipeline runs refactoring experiments, measures code quality before and after refactoring, executes regression tests, and records the results for quantitative analysis.

The project is designed to investigate how different models and prompting strategies affect code complexity, maintainability, and test outcomes.

> **Project status:** Experimental research prototype. The current results include preliminary experiments using Gemini and separate mock-provider benchmark runs. Further experiments are required before drawing general conclusions about model performance.

---

## Table of Contents

- [Objectives](#objectives)
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Tests](#running-the-tests)
- [Running Experiments](#running-experiments)
- [Understanding the Results](#understanding-the-results)
- [Preliminary Gemini Experiments](#preliminary-gemini-experiments)
- [Research Limitations](#research-limitations)
- [Security Notes](#security-notes)
- [Future Work](#future-work)

## Objectives

The project aims to:

1. Automate the evaluation of AI-generated refactoring of legacy Python code.
2. Measure changes in static code quality metrics before and after refactoring.
3. Execute available regression tests against original and refactored code.
4. Record experimental outcomes in structured reports.
5. Provide a foundation for comparing LLM providers and prompting strategies under a consistent evaluation procedure.

## Features

- **LLM provider abstraction:** A configurable provider factory supports the providers implemented in the project, including Gemini and a mock provider. OpenAI and Anthropic provider integrations are available where implemented and configured.
- **Code cleaning and syntax validation:** Extracts Python code from model responses and checks whether the resulting source can be parsed.
- **Static analysis:** Uses Radon to calculate cyclomatic complexity, Halstead volume, and maintainability index.
- **Automated test evaluation:** Runs available tests against original and refactored programs using the project's test-execution and sandbox workflow.
- **Experiment reporting:** Records original metrics, refactored metrics, metric deltas, test outcomes, and experiment metadata in CSV reports.
- **Visualization:** Provides a utility to regenerate the complexity and maintainability chart from existing benchmark data.
- **Reliability and diagnostics:** Includes retry handling for supported transient LLM errors and application logging.

## Architecture

The application follows a modular design.

| Component | Responsibility |
|---|---|
| `app/main.py` | Application entry point and experiment configuration |
| `app/services/provider_factory.py` | Selects the configured LLM provider |
| `app/services/llm_provider.py` | Shared LLM provider abstractions and retry behavior |
| `app/services/gemini_provider.py` | Gemini integration |
| `app/services/ai_refactoring_service.py` | Coordinates refactoring requests |
| `app/services/code_cleaner.py` | Extracts and validates generated Python code |
| `app/services/static_analysis_service.py` | Computes static code metrics |
| `app/services/test_execution_service.py` | Coordinates test evaluation |
| `app/services/docker_sandbox_service.py` | Supports sandbox-based code execution |
| `app/services/experiment_runner.py` | Runs individual experiments and experiment matrices |
| `app/services/reporting_service.py` | Calculates and exports experiment metrics |
| `app/services/visual_reporting_service.py` | Generates result visualizations |
| `app/storage/` | Database and persistence components |
| `datasets/legacy/` | Legacy Python programs used as experiment inputs |
| `datasets/tests/` | Associated test files |
| `tests/` | Automated tests for the pipeline |
| `results/` | Experiment reports and generated artifacts |

## Requirements

- Python version compatible with the project's dependencies; Python 3.13 has been used in development.
- Git.
- Docker Desktop or Docker Engine for experiments that use the Docker sandbox.
- A valid API key for the selected real LLM provider.
- Python dependencies listed in `requirements.txt`.

Docker availability and configuration may be required for the experiment runner to evaluate code. Consult the sandbox implementation and local Docker setup if an experiment fails during test execution.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/spkara25/Comparative-AI-Refactoring-Pipeline.git
cd Comparative-AI-Refactoring-Pipeline/actual_app
```

### 2. Create a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local environment file from the provided template:

**macOS / Linux**

```bash
cp .env.example .env
```

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

Edit `.env` locally to configure the desired provider, model, and corresponding API credentials.

Do not commit `.env` or publish API keys.

## Configuration

The `.env.example` file provides the configuration template.

For a Gemini experiment, the relevant settings are:

```dotenv
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash-lite
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your own API key in the local `.env` file.

For a mock-provider run, configure:

```dotenv
LLM_PROVIDER=mock
```

The mock provider is useful for checking the pipeline workflow without making a real LLM API request. Mock-generated outputs must not be interpreted as actual Gemini, OpenAI, or Anthropic results.

Provider names, model identifiers, required credentials, and optional settings must match the implementations available in the repository.

## Running the Tests

Run the automated test suite from the project root:

```bash
python -m pytest -q
```

This executes the project's available automated tests. A successful test run helps verify the pipeline implementation, but does not independently establish the correctness of every experiment or every generated refactoring.

## Running Experiments

### Run the configured experiment workflow

Review `app/main.py` and the relevant provider and experiment configuration before running:

```bash
python -m app.main
```

The configured provider and experiment settings determine which experiments are executed.

**Important:** The full experiment workflow may make API calls, incur provider charges, and overwrite existing report files. Back up any results you need to preserve before running it.

For initial setup checks, use the mock provider. Use a real provider when you are ready to perform and record genuine LLM experiments.

### Run an individual experiment

The project also supports running individual experiments through its experiment runner. The source file, prompt configuration, and provider can be selected in the calling code.

For example, the development workflow has used `ExperimentRunner.run_single()` to evaluate individual legacy programs with the Gemini provider.

Refer to `app/services/experiment_runner.py` and the current application configuration for the exact parameters and supported invocation.

### Regenerate the visualization

To regenerate the chart from an existing benchmark report without running the full benchmark:

```bash
python regenerate_chart.py
```

Ensure that the input report contains the intended dataset before regenerating the chart. A visualization based on mock-provider results should be identified accordingly.

## Understanding the Results

The evaluation records measurements before and after refactoring.

| Metric | Interpretation |
|---|---|
| Cyclomatic complexity | Measures the number of independent control-flow paths; a reduction may indicate simpler control flow |
| Halstead volume | Estimates program volume from operators and operands |
| Maintainability index | A composite static metric; a higher value generally indicates better maintainability under the metric's assumptions |
| Test pass rate | Percentage of executed tests that pass |
| Coverage percentage | Percentage of measured code covered during test execution |

### Metric deltas

For the metrics reported by this project, the delta is calculated as:

**Delta = Refactored value − Original value**

Consequently:

- A negative complexity delta indicates reduced cyclomatic complexity.
- A negative Halstead-volume delta indicates reduced Halstead volume.
- A positive maintainability-index
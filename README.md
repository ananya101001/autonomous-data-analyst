# Autonomous AI Data Analyst Agent

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangChain-LangGraph-f29f05?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-Llama_3-FF6E00?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)

---

## 🚀 Live Demo

**Try the live application here:** [**https://autonomous-data-analyst-bkx3vrguf5htkpqqsfx72p.streamlit.app/**](https://autonomous-data-analyst-bkx3vrguf5htkpqqsfx72p.streamlit.app/)

---

## Project Overview

This project is a powerful demonstration of an autonomous AI agent capable of solving data analysis tasks from natural language prompts. The agent plans a solution, writes Python code, and executes it to produce the desired output, such as CSV files or data visualizations.

The entire application is wrapped in an interactive web UI built with Streamlit, making it accessible to non-technical users.

### Generating a CSV File from a Prompt
![Generating a CSV from a prompt](demo-csv.png)

### Generating a Visualization from a Prompt
![Generating a visualization from a prompt](demo-chart.png)

## Key Features & Concepts Demonstrated

This project goes beyond a simple script and showcases a range of advanced AI engineering skills:

*   **Autonomous Code Generation:** The agent uses an LLM (Llama 3.1 8B via Groq) to dynamically write Python scripts tailored to the user's specific request.
*   **Sandboxed Code Execution:** For safe and reproducible execution, the generated code is run in an isolated environment. The original implementation used Docker for maximum security, while the deployed version uses a `subprocess` for compatibility with free hosting platforms.
*   **Advanced Prompt Engineering:** The agent's reliability is achieved through a highly-engineered system prompt that uses "Golden Path" examples and self-correction instructions to guide the LLM, minimizing errors and incomplete code.
*   **Full-Stack Application:** The project integrates a powerful AI backend with a clean, user-friendly frontend built with Streamlit, demonstrating the ability to build and deploy complete applications.

## Architecture and Workflow

The final architecture was simplified to a robust, single-shot model to maximize reliability with the chosen LLM. The workflow is as follows:

1.  The **Streamlit UI** captures the user's natural language task.
2.  The task is passed to the **Code Generation Agent**, which is guided by a highly-structured prompt.
3.  The LLM generates a complete Python script.
4.  The **Code Executor** runs this script in a sandboxed environment where necessary libraries are pre-installed.
5.  Any created files (CSVs, PNGs) or terminal output are captured and displayed back in the Streamlit UI.

```mermaid
graph TD
  A["User enters task in Streamlit UI"] --> B{"Code Generation Agent"}
  B --> C["LLM Llama 3.1 8B"]
  C --> D["Code Executor subprocess"]
  D --> E["Created files such as CSV or PNG"]
  D --> F["Terminal output and errors"]
  E --> G["Display result in Streamlit UI"]
  F --> G

```

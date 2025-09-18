# code_agent.py

import os
import subprocess
import sys
from dotenv import load_dotenv
from typing import TypedDict
import re
import time

# LangChain Imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# --- 1. SETUP: LLM and Prompts ---
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# The FINAL, CORRECTLY ESCAPED prompt.
code_generation_prompt = ChatPromptTemplate.from_template(
    "You are an expert Python data scientist. Your sole task is to write a single, complete, and correct Python script to solve the user's request. "
    "The execution environment has pandas, yfinance, matplotlib, and seaborn pre-installed. "
    "\n\n**CRITICAL INSTRUCTIONS:**"
    "\n1. Your response MUST be ONLY the raw Python code for the task, enclosed in ```python ... ``` tags."
    "\n2. DO NOT include any explanations or comments."
    "\n3. The file path for saving MUST ALWAYS start with `outputs/`."
    "\n4. If the user asks for current stock prices, you MUST follow this exact, simple, and reliable code pattern:"
    "\n   ```python"
    "\n   import yfinance as yf"
    "\n   import pandas as pd"
    "\n   tickers = ['TICKER1', 'TICKER2']"
    "\n   data = []"
    "\n   for ticker in tickers:"
    "\n       price = yf.Ticker(ticker).info['currentPrice']"
    # V V V THIS IS THE LINE WE FIXED V V V
    "\n       data.append({{'Ticker': ticker, 'Price': price}})"
    # ^ ^ ^ THIS IS THE LINE WE FIXED ^ ^ ^
    "\n   df = pd.DataFrame(data)"
    "\n   df.to_csv('outputs/filename.csv', index=False)"
    "\n   ```"
    "\n5. For charts, you must use `plt.savefig('outputs/filename.png')`."
    "\n\nUser request: {task}"
)

# --- 2. THE DOCKER TOOL: SECURE CODE EXECUTION ---
# def execute_code_in_docker(code: str) -> str:
#     """
#     Executes a complete Python script in a sandboxed Docker container
#     after automatically installing necessary libraries and mounting the current directory.
#     """
#     code = code.replace("`", "")
#     full_command = f"""
#     pip install -q pandas yfinance matplotlib seaborn && \
#     python -c "{code.replace('"', '\\"')}"
#     """
    
#     try:
#         print("--- EXECUTOR: Starting Docker container ---")
#         client = docker.from_env()
#         # Ensure the 'outputs' directory exists for saving files
#         os.makedirs("outputs", exist_ok=True)
        
#         container = client.containers.run(
#             'python:3.11-slim',
#             command=['/bin/sh', '-c', full_command],
#             remove=True,
#             stderr=True,
#             stdout=True,
#             network_disabled=False,
#             volumes={os.path.join(os.getcwd(), "outputs"): {'bind': '/app/outputs', 'mode': 'rw'}},
#             working_dir='/app'
#         )
#         output = container.decode('utf-8')
#         print(f"--- EXECUTOR: Finished with output ---\n{output}")
#         return output.strip()
#     except Exception as e:
#         print(f"--- EXECUTOR: Docker failed --- \n{e}")
#         return f"Error executing code: {e}"

# --- 2. NEW LOCAL CODE EXECUTOR (REPLACES DOCKER) ---
def execute_code_locally(code: str) -> str:
    """
    Executes a Python script locally using a subprocess.
    Assumes all necessary packages are already installed in the environment.
    """
    code = code.replace("`", "")
    
    # The command is now just the python code execution part.
    full_command = f'"{sys.executable}" -c "{code.replace("`", "").replace("'", "\\'")}"'
    
    try:
        print("--- EXECUTOR: Running code locally via subprocess ---")
        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=45,
            check=False
        )
        
        output = result.stdout
        if result.returncode != 0:
            output += f"\n--- ERROR ---\n{result.stderr}"

        print(f"--- EXECUTOR: Finished with output ---\n{output}")
        return output.strip()
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out after 45 seconds."
    except Exception as e:
        print(f"--- EXECUTOR: Subprocess failed --- \n{e}")
        return f"Error executing code: {e}"

# --- 3. AGENT LOGIC ---
# Define the structure for our return value
class AgentResult(TypedDict):
    code: str
    output: str
    file_path: str | None
    error: str | None

# The NEW, MORE ROBUST version
def find_created_file(task_description: str) -> str | None:
    """
    Tries to find the filename of a file created by the agent,
    with a short retry loop to handle filesystem delays with Docker.
    """
    match = re.search(r"['\"]([^'\"]+\.(?:csv|png|jpg|jpeg|json|txt))['\"]", task_description)
    if not match:
        return None

    filename = match.group(1)
    # All files are saved in the 'outputs' directory
    full_path = os.path.join(os.getcwd(), filename)

    # Retry loop to wait for the file to appear
    max_retries = 5
    wait_time = 0.2 # 200 milliseconds
    for i in range(max_retries):
        if os.path.exists(full_path):
            print(f"File found at: {full_path}")
            return full_path
        else:
            print(f"File not found yet, retrying in {wait_time}s... ({i+1}/{max_retries})")
            time.sleep(wait_time)
            
    print("File not found after multiple retries.")
    return None

def solve_task(task: str) -> AgentResult:
    """
    Main function to generate and execute code to solve a task.
    This is the core logic that will be called by the UI.
    """
    print("--- GENERATING SCRIPT ---")
    script_generation_chain = code_generation_prompt | llm
    response = script_generation_chain.invoke({"task": task})
    code_script = response.content.strip().replace("```python", "").replace("```", "")
    print(f"--- GENERATED SCRIPT ---\n{code_script}")
    
    # execution_output = execute_code_in_docker(code_script)
    execution_output = execute_code_locally(code_script)
    
    # Check for errors and created files
    error_message = execution_output if "error" in execution_output.lower() else None
    created_file = find_created_file(task) if not error_message else None

    return {
        "code": code_script,
        "output": execution_output,
        "file_path": created_file,
        "error": error_message
    }

# --- 4. RUN SCRIPT DIRECTLY (for testing) ---
if __name__ == "__main__":
    # This block allows you to still test the agent from the command line
    task = (
        "Fetch the current stock prices for NVIDIA (NVDA) and Apple (AAPL) "
        "and save them to a CSV file named 'outputs/stock_prices.csv'."
    )
    result = solve_task(task)
    print("\n--- FINAL RESULT ---")
    if result["file_path"]:
        print(f"Success! File created at: {result['file_path']}")
    else:
        print("Process finished, but the target file was not created.")
        print("Final output from execution:", result["output"])
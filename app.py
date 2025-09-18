# app.py

import streamlit as st
import pandas as pd
from code_agent import solve_task # Import our core agent logic

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Autonomous Code Agent", layout="wide")
st.title("🤖 Autonomous Code Agent")
st.markdown("Enter a data analysis task, and the AI agent will write, execute, and debug Python code to solve it.")

# --- UI Components ---
st.sidebar.header("Example Tasks")
example_1 = "Fetch the current stock prices for NVIDIA (NVDA), Apple (AAPL), and Alphabet (GOOGL) and save them to a CSV file named 'outputs/stock_prices.csv'."
example_2 = "Create a bar chart showing the stock prices of TSLA, MSFT, and AMZN, and save it as a PNG file named 'outputs/price_chart.png'. Use a title for the chart."

if st.sidebar.button("Use Example 1: Stocks CSV"):
    st.session_state.task = example_1
if st.sidebar.button("Use Example 2: Price Chart"):
    st.session_state.task = example_2

user_task = st.text_area(
    "Enter your data analysis task:",
    key="task",
    height=150,
    placeholder="e.g., Fetch the current stock prices for NVIDIA (NVDA)..."
)

if st.button("🚀 Generate and Run Code"):
    if not user_task:
        st.warning("Please enter a task.")
    else:
        with st.spinner("Agent is thinking, coding, and running... Please wait."):
            # Call the agent logic from code_agent.py
            result = solve_task(user_task)

            # --- Display Results ---
            st.subheader("Generated Code")
            with st.expander("Click to view the code written by the agent"):
                st.code(result["code"], language="python")
            
            st.subheader("Execution Log")
            st.code(result["output"], language="bash")
            
            st.subheader("Final Result")
            if result["error"]:
                st.error(f"The agent encountered an error: {result['error']}")
            elif result["file_path"]:
                st.success(f"Success! The agent created the file: `{result['file_path']}`")
                
                # Display the content of the created file
                if result["file_path"].endswith(".csv"):
                    df = pd.read_csv(result["file_path"])
                    st.dataframe(df)
                elif result["file_path"].endswith((".png", ".jpg", ".jpeg")):
                    st.image(result["file_path"])
            else:
                st.info("The agent finished, but no output file was detected.")
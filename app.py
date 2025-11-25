import streamlit as st
import os
from src.mcts.engine import MCTSEngine
from src.llm.gemini_client import GeminiClient

# Page Configuration
st.set_page_config(
    page_title="CogniCode MCTS",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for that "Hacker" feel
st.markdown("""
<style>
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
    }
    .stCode {
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧠 CogniCode: System-2 Reasoning Engine")
st.markdown("Use **Monte Carlo Tree Search (MCTS)** to force Gemini to think, test, and self-correct before giving you an answer.")

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("Configuration")
    
    # 1. API Key
    api_key_input = st.text_input("Gemini API Key", type="password", help="Leave empty if using .env file")
    if not api_key_input:
        api_key_input = os.getenv("GEMINI_API_KEY")
    
    # 2. Iterations
    iterations = st.slider("Search Iterations", min_value=5, max_value=50, value=20, help="More iterations = Deeper search but slower.")

    st.divider()
    st.info("💡 **How it works:**\n1. Generates code candidates.\n2. Runs them in a sandbox.\n3. Checks syntax & unit tests.\n4. Backtracks if tests fail.")

# --- MAIN INTERFACE ---

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Define the Challenge")
    
    # Input: Problem Description
    problem_desc = st.text_area(
        "Problem Description", 
        value="Write a Python function named 'fibonacci' that returns the nth number in the sequence.",
        height=100
    )
    
    # Input: Starting Code (Seed)
    starting_code = st.text_input(
        "Function Signature (Seed)", 
        value="def fibonacci(n):",
        help="This anchors the AI to start writing from a specific point."
    )
    
    # Input: Test Harness (Hidden Ground Truth)
    default_test = """
if __name__ == "__main__":
    try:
        assert fibonacci(0) == 0
        assert fibonacci(1) == 1
        assert fibonacci(10) == 55
        print("ALL TESTS PASSED")
    except NameError:
        exit(1)
    except AssertionError:
        exit(1)
"""
    test_harness = st.text_area(
        "Validation Logic (Hidden Unit Tests)", 
        value=default_test.strip(),
        height=200,
        help="The AI will NOT see this. The sandbox uses this to grade the AI's code."
    )

    start_btn = st.button("🚀 Start Reasoning", type="primary", use_container_width=True)

with col2:
    st.subheader("2. Reasoning Process")
    
    # Container for Logs
    log_container = st.container(height=300, border=True)
    
    # Container for Final Result
    result_container = st.empty()

# --- EXECUTION LOGIC ---
if start_btn:
    if not api_key_input:
        st.error("Please provide a Gemini API Key in the sidebar.")
    else:
        # Initialize Client
        client = GeminiClient(api_key=api_key_input)
        
        # Initialize Engine
        engine = MCTSEngine(
            llm_client=client,
            problem_desc=problem_desc,
            test_harness=test_harness,
            starting_code=starting_code
        )
        
        # Helper to update logs in real-time
        logs = []
        def ui_callback(msg):
            logs.append(msg)
            # Join logs with line breaks and push to container
            log_container.code("\n".join(logs), language="text")

        # Run with Status Spinner
        with st.status("Thinking...", expanded=True) as status:
            st.write("Initializing Search Tree...")
            final_code = engine.run(iterations=iterations, on_step=ui_callback)
            status.update(label="Reasoning Complete!", state="complete", expanded=False)

        # Show Result
        result_container.success("Solution Found!")
        result_container.markdown("### 🏆 Final Generated Code")
        result_container.code(final_code, language="python")
CNC Process Planner - README

This project is designed to run on VS Code using the built-in Jupyter Notebook support.

API Key Setup:
- Create a `.env` file in the project root directory.
- Add the following line (replace with your actual key):

  OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

How to Run:

1. Open VS Code and launch the file `cnc_llm.ipynb`.
2. Run the entire notebook from top to bottom.


Interface Usage:
- Scroll to the bottom of the notebook.

- You'll see two input elements:
  - A text box for describing the part.
  - A dropdown menu to choose the material.

- Click **"Generate CNC Plan"**.
  - When you see `[Attempt 1] Calling LLM...`, it means the model is generating output.
  - Wait a few seconds for the result.

- Click **"Export CSV"** to download the final result table.

Requirements:
- Python 3.8+
- OpenAI API key
- VS Code with Jupyter extension

Enjoy using the CNC Process Planner!

import os
from http.client import HTTPException


def get_design_critique_prompt() -> str:
    # Print the directory of the current file (text_review.py)
    current_file_dir = os.path.dirname(__file__)
    print(f"DEBUG: Current file directory: {current_file_dir}")

    # Construct the path to the prompt file
    prompt_file_path = os.path.join(current_file_dir, '..', 'prompts', 'design_critique_prompt.txt')
    print(f"DEBUG: Attempting to open prompt file at: {prompt_file_path}")

    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except FileNotFoundError:
        print(f"DEBUG: ERROR: Prompt file NOT FOUND at: {prompt_file_path}")
        raise HTTPException(status_code=500, detail="Server configuration error: Design critique prompt not loaded.")
    except Exception as e:
        print(f"DEBUG: ERROR: An unexpected error occurred while reading the prompt file: {e}")
        raise HTTPException(status_code=500, detail="Server configuration error: Failed to read prompt file.")
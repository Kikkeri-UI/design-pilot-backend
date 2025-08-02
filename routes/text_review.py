# routes/text_review.py

import os
import json  # New import for JSON parsing
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field  # Import Field for better validation/documentation
from openai import AsyncOpenAI, OpenAIError
from .models import DesignCritiqueOutput

router = APIRouter()


# Input model for the user's design description
class TextReviewInput(BaseModel):
    description: str


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


@router.post('/text-review', response_model=DesignCritiqueOutput)  # Tell FastAPI to validate/document this output
async def text_review(review_request: TextReviewInput):  # Changed parameter name to avoid confusion with the file

    openai_api_key = os.environ.get("OPEN_AI_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not found in environment variables.")

    openai_client = AsyncOpenAI(api_key=openai_api_key)

    system_message_template = get_design_critique_prompt()

    messages_for_openai = [
        {"role": "system", "content": system_message_template},
        # The user message can be a simple instruction to apply the critique.
        {"role": "user", "content": "Please provide the critique in the specified JSON format."}
    ]

    try:
        chat_completion = await openai_client.chat.completions.create(
            model="gpt-4o",  # IMPORTANT: Confirm this model name is valid and available to you
            messages=messages_for_openai,
            temperature=0.7,
            max_tokens=2000,  # Increased max_tokens as JSON output can be verbose
            response_format={"type": "json_object"}  # <--- CRUCIAL: Instructs the model to output JSON
        )

        critique_content = chat_completion.choices[0].message.content

        if not critique_content:
            raise HTTPException(status_code=500, detail="OpenAI returned an empty critique.")

        # Parse the JSON response from the AI
        try:
            parsed_critique = json.loads(critique_content)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error from OpenAI response: {e}\nResponse: {critique_content}")
            raise HTTPException(status_code=500, detail="Failed to parse AI critique as valid JSON. Please try again.")

        # Validate the parsed JSON against your Pydantic model
        # This will raise a ValidationError if the structure doesn't match
        validated_critique = DesignCritiqueOutput(**parsed_critique)

        return validated_critique

    except OpenAIError as e:
        print(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e.body.get('message', str(e))}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")
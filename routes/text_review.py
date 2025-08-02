# routes/text_review.py

import os
import json  # New import for JSON parsing
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field  # Import Field for better validation/documentation
from openai import AsyncOpenAI, OpenAIError
from .models import DesignCritiqueOutput
from .shared_functions import get_design_critique_prompt

router = APIRouter()


# Input model for the user's design description
class TextReviewInput(BaseModel):
    description: str


@router.post('/text-review', response_model=DesignCritiqueOutput)
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
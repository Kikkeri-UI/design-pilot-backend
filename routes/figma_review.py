import json
import os
import re
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .models import DesignCritiqueOutput
from openai import AsyncOpenAI, OpenAIError
from .shared_functions import get_design_critique_prompt

router = APIRouter()

class FigmaRequest(BaseModel):
    figma_url: str
    figma_pat: str
    figma_node: str | None = None

# method to extract the file_key from the url
def extract_file_key(figma_url: str) -> str | None | Any:
    match = re.search(r"figma\.com/(file|design)/([a-zA-Z0-9]+)", figma_url)
    if match:
        return match.group(2)
    return None


@router.post('/figma-review', response_model=DesignCritiqueOutput)
async def figma_review(review_request: FigmaRequest):
    figma_url = review_request.figma_url
    figma_pat = review_request.figma_pat
    figma_node = review_request.figma_node

    openai_api_key = os.environ.get("OPEN_AI_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=404, detail="OpenAI API key not set")
    openai_client = AsyncOpenAI(api_key=openai_api_key)

    # step 1: fetch the file id from the url provided
    try:
        file_key = extract_file_key(figma_url)
        if file_key is None:
            raise HTTPException(status_code=404, detail="Figma File not found.")
        figma_file_id = file_key

        # If node id is not provided in the request, extract it from the url
        if not figma_node:
            node_id_match = re.search(r"node-id=([^&]+)", figma_url)
            if node_id_match:
                figma_node = node_id_match.group(1).replace('%3A', ':')

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch the file key from the provided url{str(e)}")

    # step 2: calling the figma api to fetch the image url of the node
    figma_image_api_url = f"https://api.figma.com/v1/images/{figma_file_id}"

    params = {
        "format": "png",
        "scale": "2"
    }

    if figma_node:
        params["ids"] = figma_node

    headers = {
        "X-Figma-Token": figma_pat
    }

    async with httpx.AsyncClient() as client:
        try:
            figma_response = await client.get(figma_image_api_url, params=params, headers=headers, timeout=30) # it takes at least 15-20 seconds for the api to fetch
            figma_response.raise_for_status()
            figma_data = figma_response.json()

            if not figma_data.get("images"):
                raise HTTPException(status_code=404, detail="Figma Image not found. Please check for permissions in figma")
            image_url = list(figma_data["images"].values())[0]

        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Could not fetch the image from the provided url {str(e)}")

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code = e.response.status_code, detail=f"Oops, figma API returned an error {str(e)}")

        except ValueError as e:
            raise ValueError("Failed to parse the figma API response", {e})

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error occured {str(e)}")


    # step 3: call the open ai api with all the necessary parameters

    system_message = get_design_critique_prompt()

    user_content_message = [
        {"type": "text", "text": "critique this design based on the instructions"},
        {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
    ]

    messages_for_openai = [
        {"role": "system", "content": system_message},
        # The user message can be a simple instruction to apply the critique.
        {"role": "user", "content": user_content_message}
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

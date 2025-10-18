import json
import os
import re
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from routes.models import DesignCritiqueOutput, FigmaRequest
from openai import AsyncOpenAI, OpenAIError
from .shared_functions import get_design_critique_prompt, extract_file_key
from services.design_critique import get_design_critique

router = APIRouter()

@router.post('/figma-review', response_model=DesignCritiqueOutput)
async def figma_review(review_request: FigmaRequest):
    return await get_design_critique(
        figma_url=review_request.figma_url,
        figma_pat=review_request.figma_pat,
        figma_node=review_request.figma_node
    )


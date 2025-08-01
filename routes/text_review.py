import os
from fastapi import APIRouter
from pydantic import BaseModel

router=APIRouter()

class TextReview(BaseModel):
    description: str

@router.post('/text-review')
async def text_review(text: TextReview):
    return text.description
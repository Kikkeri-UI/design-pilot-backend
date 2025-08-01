import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class FigmaRequest(BaseModel):
    description: str

@router.post('/figma-review')
async def figma_review(test: FigmaRequest):
    return  test.description
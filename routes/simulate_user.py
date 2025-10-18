import json
from fastapi import APIRouter, HTTPException

# Use absolute imports now that the structure is finalized
from routes.models import SimulateUser, DesignCritiqueOutput
from services.design_critique import get_design_critique  # The reusable service function

router = APIRouter()


@router.post('/simulate-user', response_model=DesignCritiqueOutput, tags=["Critique"])
async def simulate_user(review_request: SimulateUser):
    """
    Generates a UX critique by simulating a specific user persona 
    against the provided Figma design.
    """

    # 1. Construct the Dynamic System Message
    dynamic_system_message = f"""
    **CRUCIAL INSTRUCTION:** You must behave like the the user with all the persona provided above and critique
    this in such a way , it should feel like the user is doing it really.

    **USER SIMULATION CONTEXT:**
    {review_request.user_context}

    ---

    Your output MUST strictly follow the JSON schema provided.
    """

    # 2. Call the Reusable Service (Requires a slight modification to the service function)

    # NOTE: Since your current service function doesn't accept 'system_message', 
    # we must update the service function to be flexible (see Step 3). 
    # For now, let's assume the service is updated to accept it.

    try:
        critique_result = await get_design_critique(
            figma_url=review_request.figma_url,
            figma_pat=review_request.figma_pat,
            figma_node=review_request.figma_node,
            user_context=dynamic_system_message
        )

        return critique_result

    except HTTPException:
        raise
    except Exception as e:
        print(f"User Simulation Critique Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate simulated critique.")
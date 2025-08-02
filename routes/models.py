# Pydantic Models for the AI's Critique Output (mirroring your prompt's JSON format)
from pydantic import Field, BaseModel


class MetricCritiqueDetail(BaseModel):
    score: int = Field(..., ge=0, le=5)  # Score between 0 and 5
    analysis: str
    recommendations: list[str] = Field(default_factory=list)  # Ensure it's a list of strings


class MetricsCritique(BaseModel):
    usability_learnability: MetricCritiqueDetail
    usability_efficiency: MetricCritiqueDetail
    usability_memorability: MetricCritiqueDetail
    usability_errors: MetricCritiqueDetail
    usability_satisfaction: MetricCritiqueDetail
    accessibility: MetricCritiqueDetail
    information_architecture: MetricCritiqueDetail
    visual_design: MetricCritiqueDetail


class DesignCritiqueOutput(BaseModel):  # The main output model
    overall_summary: str
    metrics_critique: MetricsCritique
    general_recommendations: list[str] = Field(default_factory=list)
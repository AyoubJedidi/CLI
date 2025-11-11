
from pydantic import BaseModel, Field, validator
from typing import Optional, List


class ProjectInfo(BaseModel):
    language: str
    framework: Optional[str] = None
    build_tool: Optional[str] = None

    @validator("language", pre=True, always=True)
    def _normalize_language(cls, v):
        if v is None or str(v).strip() == "":
            raise ValueError("language is required")
        return str(v).strip().lower()
class Config(BaseModel):
    name: str
    project_type: str = Field(..., alias="type")
    stages: List[str] = Field(default_factory=lambda: ["build", "test", "deploy"])

    class Config:
        allow_population_by_field_name = True

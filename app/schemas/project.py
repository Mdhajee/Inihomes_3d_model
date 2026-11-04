
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.building import BuildingSchema


class ProjectSchema(BaseModel):
    project_id: Optional[str] = None
    project_name: str = Field(min_length=1)
    building: BuildingSchema
    status: str = "draft"

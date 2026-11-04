
from pydantic import BaseModel, Field
from typing import List, Dict, Any


# =========================================================
# 1. PLOT DETAILS
# =========================================================

class PlotSchema(BaseModel):
    width: float = Field(gt=0)
    length: float = Field(gt=0)


# =========================================================
# 2. ROOM DETAILS
# =========================================================

class RoomSchema(BaseModel):
    name: str
    width: float = Field(gt=0)
    length: float = Field(gt=0)
    x: float = 0.0
    z: float = 0.0


# =========================================================
# 3. DOOR DETAILS
# =========================================================

class DoorSchema(BaseModel):
    door_id: str
    name: str = "Standard Door"

    width: float = Field(default=0.9, gt=0)
    height: float = Field(default=2.1, gt=0)
    thickness: float = Field(default=0.05, gt=0)

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    floor_number: int = Field(ge=1)
    wall_type: str = "internal"
    material: str = "wood"


# =========================================================
# 4. ROOF DETAILS
# =========================================================

class RoofSchema(BaseModel):
    roof_type: str = "flat"
    thickness: float = Field(default=0.15, gt=0)
    material: str = "concrete"


# =========================================================
# 5. FLOOR DETAILS
# =========================================================

class FloorSchema(BaseModel):
    floor_number: int = Field(ge=1)
    height: float = Field(gt=0, default=3.0)

    # Individual room information
    rooms: List[RoomSchema] = Field(default_factory=list)

    # Prompt-extracted room counts
    room_counts: Dict[str, int] = Field(default_factory=dict)

    # Geometry elements
    walls: List[Dict[str, Any]] = Field(default_factory=list)
    doors: List[DoorSchema] = Field(default_factory=list)
    windows: List[Dict[str, Any]] = Field(default_factory=list)
    furniture: List[Dict[str, Any]] = Field(default_factory=list)


# =========================================================
# 6. COMPLETE BUILDING DETAILS
# =========================================================

class BuildingSchema(BaseModel):
    name: str
    architectural_style: str = "unspecified"
    unit: str = "meter"

    plot: PlotSchema

    floors: List[FloorSchema]

    # Roof information
    roof: RoofSchema = Field(default_factory=RoofSchema)

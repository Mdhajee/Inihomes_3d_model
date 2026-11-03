# INIHOME – Member 3 Geometry Engine

## Scope
Converts 2D floor-plan coordinates into structured house-design JSON for the Three.js frontend.

## Coordinate convention
- Input floor-plan coordinates are in metres.
- Input 2D `x` increases right; input 2D `y` increases down.
- Output Three.js coordinates use `x` for width, `y` for height and `z` for depth.
- Mapping used here: `world_x = canvas_x`, `world_z = -canvas_y`.
- Wall geometry is a box with local width = wall length, height = wall height, depth = wall thickness.
- `rotation_y` is in radians.
- Door/window `position` is normalized along the wall: 0 = start, 1 = end.

IMPORTANT: The frontend must convert pixels to metres before sending this backend payload. Agree the exact coordinate and opening conventions with all team members before integration.

## Setup (Windows PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Run tests
```powershell
python -m pytest -q
```

## Quick usage
Call `create_building(floorplan)` from `app.services.building_service`.

This module does not connect to MongoDB and does not define API routes; those belong to the other team members.

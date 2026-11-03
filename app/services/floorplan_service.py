from app.geometry.generator import generate_house


def process_floorplan(floorplan: dict) -> dict:
    """Entry point for 2D floor-plan processing."""
    if not isinstance(floorplan, dict):
        raise ValueError("Floor plan must be a JSON object")
    return generate_house(floorplan)

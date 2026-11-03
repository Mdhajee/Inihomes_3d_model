from app.services.floorplan_service import process_floorplan


def create_building(floorplan: dict) -> dict:
    """Coordinate building generation; persistence is handled by Member 2."""
    house_design = process_floorplan(floorplan)
    return house_design

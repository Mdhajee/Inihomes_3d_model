from app.geometry.wall import generate_wall
from app.geometry.room import generate_room
from app.geometry.door import generate_door
from app.geometry.window import generate_window


def generate_house(floorplan: dict) -> dict:
    """Generate the shared house-design JSON from a 2D floor-plan payload."""
    if floorplan.get("unit", "meter") != "meter":
        raise ValueError("Backend geometry input must use meters")

    plot = floorplan.get("plot", {})
    plot_width = float(plot.get("width", 0))
    plot_length = float(plot.get("length", 0))
    if plot_width <= 0 or plot_length <= 0:
        raise ValueError("Plot width and length must be greater than zero")

    floors_input = floorplan.get("floors", [])
    if not floors_input:
        raise ValueError("At least one floor is required")

    generated_floors = []
    floor_numbers = set()

    for floor in floors_input:
        floor_number = int(floor["floor_number"])
        if floor_number in floor_numbers:
            raise ValueError(f"Duplicate floor_number: {floor_number}")
        floor_numbers.add(floor_number)

        floor_height = float(floor.get("height", 3.0))
        if floor_height <= 0:
            raise ValueError("Floor height must be greater than zero")

        walls = [
            generate_wall(w, default_height=floor_height)
            for w in floor.get("walls", [])
        ]
        wall_ids = [w["id"] for w in walls]
        if len(wall_ids) != len(set(wall_ids)):
            raise ValueError(f"Duplicate wall IDs on floor {floor_number}")
        walls_by_id = {w["id"]: w for w in walls}

        rooms = [generate_room(r) for r in floor.get("rooms", [])]
        doors = [generate_door(d, walls_by_id) for d in floor.get("doors", [])]
        windows = [generate_window(w, walls_by_id) for w in floor.get("windows", [])]

        floor_y = (floor_number - 1) * floor_height
        # Offset all generated objects vertically for stacked storeys.
        for wall in walls:
            wall["position"]["y"] += floor_y
        for door in doors:
            door["world_position"]["y"] += floor_y
        for window in windows:
            window["world_position"]["y"] += floor_y
        for room in rooms:
            for vertex in room["floor"]["vertices"]:
                vertex["y"] += floor_y

        generated_floors.append({
            "floor_number": floor_number,
            "height": floor_height,
            "elevation": floor_y,
            "walls": walls,
            "rooms": rooms,
            "doors": doors,
            "windows": windows,
            "furniture": floor.get("furniture", [])
        })

    generated_floors.sort(key=lambda f: f["floor_number"])

    return {
        "project_id": floorplan.get("project_id", "new_project"),
        "name": floorplan.get("name", "Untitled House"),
        "unit": "meter",
        "plot": {"width": plot_width, "length": plot_length},
        "floors": generated_floors
    }

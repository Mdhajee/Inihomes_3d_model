def generate_door(door: dict, walls_by_id: dict) -> dict:
    """Calculate a door centre along its referenced wall.

    position is normalized from 0.0 (wall start) to 1.0 (wall end).
    """
    wall_id = door["wall_id"]
    if wall_id not in walls_by_id:
        raise ValueError(f"Door {door.get('id')} references unknown wall {wall_id}")

    wall = walls_by_id[wall_id]
    t = float(door.get("position", 0.5))
    width = float(door.get("width", 0.9))
    height = float(door.get("height", 2.1))

    if not 0.0 <= t <= 1.0:
        raise ValueError("Door position must be between 0 and 1")
    if width <= 0 or height <= 0:
        raise ValueError("Door width and height must be greater than zero")
    if width > wall["length"]:
        raise ValueError(f"Door {door.get('id')} is wider than its wall")
    if height > wall["height"]:
        raise ValueError(f"Door {door.get('id')} is taller than its wall")

    start = wall["start"]
    end = wall["end"]
    canvas_x = start["x"] + (end["x"] - start["x"]) * t
    canvas_y = start["y"] + (end["y"] - start["y"]) * t

    return {
        "id": door["id"],
        "wall_id": wall_id,
        "width": width,
        "height": height,
        "position": t,
        "world_position": {
            "x": canvas_x,
            "y": height / 2,
            "z": -canvas_y
        },
        "rotation_y": wall["rotation_y"],
        "opening_type": "door"
    }

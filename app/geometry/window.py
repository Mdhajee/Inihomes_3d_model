def generate_window(window: dict, walls_by_id: dict) -> dict:
    """Calculate a window centre along its referenced wall."""
    wall_id = window["wall_id"]
    if wall_id not in walls_by_id:
        raise ValueError(f"Window {window.get('id')} references unknown wall {wall_id}")

    wall = walls_by_id[wall_id]
    t = float(window.get("position", 0.5))
    width = float(window.get("width", 1.2))
    height = float(window.get("height", 1.0))
    sill_height = float(window.get("sill_height", 0.9))

    if not 0.0 <= t <= 1.0:
        raise ValueError("Window position must be between 0 and 1")
    if width <= 0 or height <= 0 or sill_height < 0:
        raise ValueError("Window dimensions must be positive and sill height cannot be negative")
    if width > wall["length"]:
        raise ValueError(f"Window {window.get('id')} is wider than its wall")
    if sill_height + height > wall["height"]:
        raise ValueError(f"Window {window.get('id')} extends above its wall")

    start = wall["start"]
    end = wall["end"]
    canvas_x = start["x"] + (end["x"] - start["x"]) * t
    canvas_y = start["y"] + (end["y"] - start["y"]) * t

    return {
        "id": window["id"],
        "wall_id": wall_id,
        "width": width,
        "height": height,
        "sill_height": sill_height,
        "position": t,
        "world_position": {
            "x": canvas_x,
            "y": sill_height + height / 2,
            "z": -canvas_y
        },
        "rotation_y": wall["rotation_y"],
        "opening_type": "window"
    }

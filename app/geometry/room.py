def generate_room(room: dict) -> dict:
    """Validate a closed room polygon and calculate its dimensions and area."""
    boundary = room.get("boundary", [])
    if len(boundary) < 3:
        raise ValueError(f"Room {room.get('id', '<unknown>')} needs at least 3 boundary points")

    points = [{"x": float(p["x"]), "y": float(p["y"])} for p in boundary]

    # Shoelace formula. The polygon is implicitly closed.
    twice_area = 0.0
    for i, point in enumerate(points):
        nxt = points[(i + 1) % len(points)]
        twice_area += point["x"] * nxt["y"] - nxt["x"] * point["y"]

    area = abs(twice_area) / 2
    if area <= 0:
        raise ValueError(f"Room {room.get('id', '<unknown>')} has zero area")

    xs = [p["x"] for p in points]
    ys = [p["y"] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Preserve source boundary and provide mapped Three.js floor vertices.
    floor_vertices = [{"x": p["x"], "y": 0.0, "z": -p["y"]} for p in points]

    return {
        "id": room["id"],
        "name": room.get("name", "Room"),
        "boundary": points,
        "width": max_x - min_x,
        "length": max_y - min_y,
        "area": area,
        "floor": {
            "shape": "polygon",
            "vertices": floor_vertices
        }
    }

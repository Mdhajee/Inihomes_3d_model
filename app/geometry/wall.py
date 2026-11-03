import math


def generate_wall(wall: dict, default_height: float = 3.0,
                  default_thickness: float = 0.2) -> dict:
    """Convert a 2D canvas wall into a Three.js-friendly wall descriptor.

    Canvas: x grows right, y grows down.
    Three.js: x grows right, y is vertical, z is depth.
    This implementation maps canvas y to negative Three.js z.
    """
    start = wall["start"]
    end = wall["end"]

    x1, y1 = float(start["x"]), float(start["y"])
    x2, y2 = float(end["x"]), float(end["y"])

    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)

    if length <= 0:
        raise ValueError(f"Wall {wall.get('id', '<unknown>')} has zero length")

    height = float(wall.get("height", default_height))
    thickness = float(wall.get("thickness", default_thickness))
    if height <= 0:
        raise ValueError("Wall height must be greater than zero")
    if thickness <= 0:
        raise ValueError("Wall thickness must be greater than zero")

    # Canvas y-down -> Three.js z = -y.
    center_x = (x1 + x2) / 2
    center_z = -(y1 + y2) / 2
    rotation_y = math.atan2(-dy, dx)

    return {
        "id": wall["id"],
        "start": {"x": x1, "y": y1},
        "end": {"x": x2, "y": y2},
        "length": length,
        "height": height,
        "thickness": thickness,
        "position": {
            "x": center_x,
            "y": height / 2,
            "z": center_z
        },
        "rotation_y": rotation_y,
        "geometry": {
            "type": "box",
            "width": length,
            "height": height,
            "depth": thickness
        }
    }

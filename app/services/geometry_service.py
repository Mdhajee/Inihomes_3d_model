
import math


# =========================================================
# CONFIGURATION
# =========================================================

FLOOR_HEIGHT = 3.0
WALL_THICKNESS = 0.20
SLAB_THICKNESS = 0.15
WALL_HEIGHT = FLOOR_HEIGHT - (SLAB_THICKNESS / 2)  

DOOR_WIDTH = 0.9
DOOR_HEIGHT = 2.1
DOOR_THICKNESS = 0.05

STAIR_WIDTH = 1.0
STAIR_TREAD = 0.28
STAIR_RISERS = 16
STAIR_WELL_LENGTH = STAIR_TREAD * STAIR_RISERS
STAIR_X = 0.0
STAIR_START_Z = -2.0


# =========================================================
# 1. GENERATE FLOOR SLABS
# =========================================================

def generate_floor_slabs(building_data: dict) -> list:
    """
    Generate floor slabs.
    The upper floor has an opening for the staircase.
    """

    plot = building_data["plot"]
    width = plot["width"]
    length = plot["length"]

    floors = building_data["floors"]
    slabs = []

    for index, floor in enumerate(floors):

        floor_number = floor["floor_number"]
        y = index * FLOOR_HEIGHT

        # Ground floor: complete slab
        if index == 0:
            slabs.append({
                "type": "floor_slab",
                "floor_number": floor_number,
                "width": width,
                "length": length,
                "thickness": SLAB_THICKNESS,
                "position": {
                    "x": 0,
                    "y": y,
                    "z": 0
                },
                "material": "concrete"
            })

        # Upper floor: split slab around staircase opening
        elif index == 1:

            opening_left = STAIR_X - STAIR_WIDTH / 2
            opening_right = STAIR_X + STAIR_WIDTH / 2

            plot_left = -width / 2
            plot_right = width / 2

            opening_front = STAIR_START_Z
            # Include the staircase landing in the slab opening
            opening_back = STAIR_START_Z + STAIR_WELL_LENGTH + 1.0

            plot_front = -length / 2
            plot_back = length / 2

            # Left slab section
            left_width = opening_left - plot_left

            if left_width > 0:
                slabs.append({
                    "type": "floor_slab",
                    "floor_number": floor_number,
                    "width": left_width,
                    "length": length,
                    "thickness": SLAB_THICKNESS,
                    "position": {
                        "x": (plot_left + opening_left) / 2,
                        "y": y,
                        "z": 0
                    },
                    "material": "concrete"
                })

            # Right slab section
            right_width = plot_right - opening_right

            if right_width > 0:
                slabs.append({
                    "type": "floor_slab",
                    "floor_number": floor_number,
                    "width": right_width,
                    "length": length,
                    "thickness": SLAB_THICKNESS,
                    "position": {
                        "x": (opening_right + plot_right) / 2,
                        "y": y,
                        "z": 0
                    },
                    "material": "concrete"
                })

            # Rear slab section
            rear_length = plot_back - opening_back

            if rear_length > 0:
                slabs.append({
                    "type": "floor_slab",
                    "floor_number": floor_number,
                    "width": STAIR_WIDTH,
                    "length": rear_length,
                    "thickness": SLAB_THICKNESS,
                    "position": {
                        "x": STAIR_X,
                        "y": y,
                        "z": (opening_back + plot_back) / 2
                    },
                    "material": "concrete"
                })

        else:
            # Additional floors: complete slab
            slabs.append({
                "type": "floor_slab",
                "floor_number": floor_number,
                "width": width,
                "length": length,
                "thickness": SLAB_THICKNESS,
                "position": {
                    "x": 0,
                    "y": y,
                    "z": 0
                },
                "material": "concrete"
            })

    return slabs


# =========================================================
# 2. GENERATE EXTERNAL WALLS
# =========================================================

def generate_external_walls(building_data: dict) -> list:
    """
    Generate external walls.
    Only the ground floor has the main entrance opening.
    """

    plot = building_data["plot"]

    width = plot["width"]
    length = plot["length"]

    walls = []

    side_width = (width - DOOR_WIDTH) / 2
    lintel_height = WALL_HEIGHT - DOOR_HEIGHT

    if side_width <= 0 or lintel_height <= 0:
        raise ValueError("Plot dimensions are too small for the entrance")

    for index, floor in enumerate(building_data["floors"]):

        floor_number = floor["floor_number"]
        base_y = index * FLOOR_HEIGHT

        front_z = -length / 2 + WALL_THICKNESS / 2

        # Ground floor front wall with doorway
        if index == 0:

            front_sections = [
                {
                    "width": side_width,
                    "height": WALL_HEIGHT,
                    "x": -(DOOR_WIDTH / 2 + side_width / 2),
                    "y": base_y + WALL_HEIGHT / 2
                },
                {
                    "width": side_width,
                    "height": WALL_HEIGHT,
                    "x": DOOR_WIDTH / 2 + side_width / 2,
                    "y": base_y + WALL_HEIGHT / 2
                },
                {
                    "width": DOOR_WIDTH,
                    "height": lintel_height,
                    "x": 0,
                    "y": base_y + DOOR_HEIGHT + lintel_height / 2
                }
            ]

            for section in front_sections:
                walls.append({
                    "type": "external_wall",
                    "floor_number": floor_number,
                    "size": {
                        "width": section["width"],
                        "height": section["height"],
                        "depth": WALL_THICKNESS
                    },
                    "position": {
                        "x": section["x"],
                        "y": section["y"],
                        "z": front_z
                    },
                    "material": "concrete"
                })

        else:
            # Upper floor has a complete front wall
            walls.append({
                "type": "external_wall",
                "floor_number": floor_number,
                "size": {
                    "width": width,
                    "height": WALL_HEIGHT,
                    "depth": WALL_THICKNESS
                },
                "position": {
                    "x": 0,
                    "y": base_y + WALL_HEIGHT / 2,
                    "z": front_z
                },
                "material": "concrete"
            })

        # Back wall
        walls.append({
            "type": "external_wall",
            "floor_number": floor_number,
            "size": {
                "width": width,
                "height": WALL_HEIGHT,
                "depth": WALL_THICKNESS
            },
            "position": {
                "x": 0,
                "y": base_y + WALL_HEIGHT / 2,
                "z": length / 2 - WALL_THICKNESS / 2
            },
            "material": "concrete"
        })

        # Left side wall
        walls.append({
            "type": "external_wall",
            "floor_number": floor_number,
            "size": {
                "width": WALL_THICKNESS,
                "height": WALL_HEIGHT,
                "depth": length - 2 * WALL_THICKNESS
            },
            "position": {
                "x": -width / 2 + WALL_THICKNESS / 2,
                "y": base_y + WALL_HEIGHT / 2,
                "z": 0
            },
            "material": "concrete"
        })

        # Right side wall
        walls.append({
            "type": "external_wall",
            "floor_number": floor_number,
            "size": {
                "width": WALL_THICKNESS,
                "height": WALL_HEIGHT,
                "depth": length - 2 * WALL_THICKNESS
            },
            "position": {
                "x": width / 2 - WALL_THICKNESS / 2,
                "y": base_y + WALL_HEIGHT / 2,
                "z": 0
            },
            "material": "concrete"
        })

    return walls


# =========================================================
# 3. GENERATE ROOM LAYOUT
# =========================================================


def generate_room_layout(building_data: dict) -> list:
    """
    Use AI-generated room dimensions and positions.

    AI coordinates represent the bottom-left corner
    of each room relative to the plot.

    Geometry coordinates represent room centres
    relative to the plot centre.
    """

    plot = building_data["plot"]

    plot_width = plot["width"]
    plot_length = plot["length"]

    all_floor_layouts = []

    for floor in building_data["floors"]:

        rooms_data = floor.get("rooms", [])
        room_layout = []

        for room in rooms_data:

            width = room["width"]
            length = room["length"]

            # AI bottom-left coordinates
            ai_x = room.get("x", 0.0)
            ai_z = room.get("z", 0.0)

            # Convert to geometry centre coordinates
            center_x = (
                -plot_width / 2
                + ai_x
                + width / 2
            )

            center_z = (
                -plot_length / 2
                + ai_z
                + length / 2
            )

            room_layout.append({
                "name": room["name"],
                "width": width,
                "length": length,
                "x": round(center_x, 3),
                "z": round(center_z, 3)
            })

        all_floor_layouts.append({
            "floor_number": floor["floor_number"],
            "room_layout": room_layout
        })

    return all_floor_layouts



# =========================================================
# 4. GENERATE INTERNAL WALLS
# =========================================================


def generate_internal_walls(building_data: dict) -> list:
    """
    Generate internal partition walls between adjacent rooms.

    Uses AI-generated room positions and dimensions.
    Coordinates represent room centres.

    Internal walls are clipped to the inner boundaries
    of the external walls to prevent visible protrusions.
    """

    wall_thickness = 0.10
    wall_height = WALL_HEIGHT
    room_gap = 0.15
    tolerance = 0.02

    all_floor_layouts = generate_room_layout(building_data)

    internal_walls = []

    # Get plot dimensions
    plot_width = building_data["plot"]["width"]
    plot_length = building_data["plot"]["length"]

    # Calculate internal building boundaries
    x_min = -plot_width / 2 + WALL_THICKNESS
    x_max = plot_width / 2 - WALL_THICKNESS

    z_min = -plot_length / 2 + WALL_THICKNESS
    z_max = plot_length / 2 - WALL_THICKNESS

    for floor_index, floor_layout in enumerate(all_floor_layouts):

        rooms = floor_layout["room_layout"]
        floor_number = floor_layout["floor_number"]
        base_y = floor_index * FLOOR_HEIGHT

        for i in range(len(rooms)):

            room_a = rooms[i]

            ax_left = room_a["x"] - room_a["width"] / 2
            ax_right = room_a["x"] + room_a["width"] / 2
            az_front = room_a["z"] - room_a["length"] / 2
            az_back = room_a["z"] + room_a["length"] / 2

            for j in range(i + 1, len(rooms)):

                room_b = rooms[j]

                bx_left = room_b["x"] - room_b["width"] / 2
                bx_right = room_b["x"] + room_b["width"] / 2
                bz_front = room_b["z"] - room_b["length"] / 2
                bz_back = room_b["z"] + room_b["length"] / 2

                # -------------------------------------
                # CHECK VERTICAL PARTITION (GAP ALONG X)
                # -------------------------------------

                overlap_z = min(az_back, bz_back) - max(
                    az_front, bz_front
                )

                gap_x = min(
                    abs(ax_right - bx_left),
                    abs(bx_right - ax_left)
                )

                if overlap_z > tolerance and abs(gap_x - room_gap) <= tolerance:

                    wall_x = (
                        (ax_right + bx_left) / 2
                        if ax_right <= bx_left
                        else (bx_right + ax_left) / 2
                    )

                    # Calculate original wall Z boundaries
                    wall_z_min = max(az_front, bz_front)
                    wall_z_max = min(az_back, bz_back)

                    # Clip wall to internal front/back boundaries
                    wall_z_min = max(wall_z_min, z_min)
                    wall_z_max = min(wall_z_max, z_max)

                    wall_depth = wall_z_max - wall_z_min

                    if wall_depth > 0:

                        wall_z = (wall_z_min + wall_z_max) / 2

                        internal_walls.append({
                            "type": "internal_wall",
                            "floor_number": floor_number,
                            "size": {
                                "width": wall_thickness,
                                "height": wall_height,
                                "depth": round(wall_depth, 3)
                            },
                            "position": {
                                "x": round(wall_x, 3),
                                "y": base_y + wall_height / 2,
                                "z": round(wall_z, 3)
                            },
                            "material": "brick"
                        })

                # -------------------------------------
                # CHECK HORIZONTAL PARTITION (GAP ALONG Z)
                # -------------------------------------

                overlap_x = min(ax_right, bx_right) - max(
                    ax_left, bx_left
                )

                gap_z = min(
                    abs(az_back - bz_front),
                    abs(bz_back - az_front)
                )

                if overlap_x > tolerance and abs(gap_z - room_gap) <= tolerance:

                    wall_z = (
                        (az_back + bz_front) / 2
                        if az_back <= bz_front
                        else (bz_back + az_front) / 2
                    )

                    # Calculate original wall X boundaries
                    wall_x_min = max(ax_left, bx_left)
                    wall_x_max = min(ax_right, bx_right)

                    # Clip wall to internal left/right boundaries
                    wall_x_min = max(wall_x_min, x_min)
                    wall_x_max = min(wall_x_max, x_max)

                    wall_width = wall_x_max - wall_x_min

                    if wall_width > 0:

                        wall_x = (wall_x_min + wall_x_max) / 2

                        internal_walls.append({
                            "type": "internal_wall",
                            "floor_number": floor_number,
                            "size": {
                                "width": round(wall_width, 3),
                                "height": wall_height,
                                "depth": wall_thickness
                            },
                            "position": {
                                "x": round(wall_x, 3),
                                "y": base_y + wall_height / 2,
                                "z": round(wall_z, 3)
                            },
                            "material": "brick"
                        })

    return internal_walls



# =========================================================
# 5. VALIDATE GEOMETRY DATA
# =========================================================

def validate_geometry_data(building_data: dict) -> dict:
    """
    Validate basic geometry dimensions and room positions.
    """

    errors = []

    plot_width = building_data["plot"]["width"]
    plot_length = building_data["plot"]["length"]

    slabs = generate_floor_slabs(building_data)
    external_walls = generate_external_walls(building_data)
    room_layouts = generate_room_layout(building_data)
    internal_walls = generate_internal_walls(building_data)

    if plot_width <= 0 or plot_length <= 0:
        errors.append("Invalid plot dimensions")

    for slab in slabs:
        if (
            slab["width"] <= 0
            or slab["length"] <= 0
            or slab["thickness"] <= 0
        ):
            errors.append(
                f"Invalid floor slab on floor {slab['floor_number']}"
            )

    for wall in external_walls + internal_walls:
        size = wall["size"]

        if (
            size["width"] <= 0
            or size["height"] <= 0
            or size["depth"] <= 0
        ):
            errors.append(
                f"Invalid wall dimensions on floor {wall['floor_number']}"
            )

    for floor in room_layouts:
        for room in floor["room_layout"]:

            if room["width"] <= 0 or room["length"] <= 0:
                errors.append(
                    f"Invalid dimensions for {room['name']}"
                )

            if (
                abs(room["x"]) + room["width"] / 2 > plot_width / 2 + 0.01
                or abs(room["z"]) + room["length"] / 2 > plot_length / 2 + 0.01
            ):
                errors.append(
                    f"{room['name']} is outside the plot boundary"
                )

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "geometry_counts": {
            "floor_slabs": len(slabs),
            "external_walls": len(external_walls),
            "internal_walls": len(internal_walls),
            "floors": len(building_data["floors"]),
            "rooms": sum(
                len(floor["room_layout"])
                for floor in room_layouts
            )
        }
    }


# =========================================================
# 6. GENERATE GROUND FLOOR ENTRANCE DOOR
# =========================================================

def generate_doors(building_data: dict) -> list:
    """
    Generate one main entrance door on the ground floor only.
    """

    if not building_data["floors"]:
        return []

    plot = building_data["plot"]

    return [{
        "door_id": "D001",
        "name": "Main Entrance Door",
        "width": DOOR_WIDTH,
        "height": DOOR_HEIGHT,
        "thickness": DOOR_THICKNESS,
        "x": 0.0,
        "y": DOOR_HEIGHT / 2,
        "z": -plot["length"] / 2 + WALL_THICKNESS / 2,
        "floor_number": building_data["floors"][0]["floor_number"],
        "wall_type": "external",
        "material": "wood"
    }]


# =========================================================
# 7. GENERATE DOOR PANELS
# =========================================================

def generate_door_panels(building_data: dict) -> list:
    """
    Generate visible wooden entrance door panels.
    """

    door_panels = []

    for door in generate_doors(building_data):

        door_panels.append({
            "type": "door_panel",
            "door_id": door["door_id"],
            "floor_number": door["floor_number"],
            "size": {
                "width": door["width"],
                "height": door["height"],
                "depth": door["thickness"]
            },
            "position": {
                "x": door["x"],
                "y": door["y"],
                "z": door["z"]
            },
            "material": "wood"
        })

    return door_panels


# =========================================================
# 8. GENERATE STAIRCASE
# =========================================================


def generate_staircase(building_data: dict) -> list:
    """
    Generate individual equal-height staircase steps
    between the ground floor and first floor.
    """

    if len(building_data["floors"]) < 2:
        return []

    plot = building_data["plot"]

    width = plot["width"]
    length = plot["length"]

    stair_width = STAIR_WIDTH
    tread = STAIR_TREAD
    risers = STAIR_RISERS

    # Check plot boundaries
    if STAIR_X - stair_width / 2 < -width / 2:
        raise ValueError("Staircase exceeds left plot boundary")

    if STAIR_X + stair_width / 2 > width / 2:
        raise ValueError("Staircase exceeds right plot boundary")

    if STAIR_START_Z < -length / 2:
        raise ValueError("Staircase starts outside plot boundary")

    if STAIR_START_Z + risers * tread > length / 2:
        raise ValueError("Staircase exceeds plot depth")

    # Calculate equal riser height
    total_rise = FLOOR_HEIGHT
    riser_height = total_rise / risers

    staircase = []

    # Generate 16 equal-height steps
    for index in range(risers):

        staircase.append({
            "type": "stair_step",
            "step_number": index + 1,
            "size": {
                "width": stair_width,
                "height": riser_height,
                "depth": tread
            },
            "position": {
                "x": STAIR_X,
                "y": SLAB_THICKNESS / 2 + (index + 0.5) * riser_height,
                "z": STAIR_START_Z + index * tread + tread / 2
            },
            "material": "concrete"
        })

    # Upper floor landing
    staircase.append({
        "type": "stair_landing",
        "size": {
            "width": stair_width,
            "height": SLAB_THICKNESS,
            "depth": 1.0
        },
        "position": {
            "x": STAIR_X,
            "y": FLOOR_HEIGHT,
            "z": STAIR_START_Z + STAIR_WELL_LENGTH + 0.5
        },
        "material": "concrete"
    })

    return staircase



# =========================================================
# 9. GENERATE ROOF
# =========================================================

def generate_roof(building_data: dict) -> list:
    """
    Generate a flat RCC roof slab above the top floor.
    """

    plot = building_data["plot"]

    floors = building_data["floors"]

    if not floors:
        raise ValueError("Cannot generate a roof without floors")

    roof_data = building_data.get("roof", {})

    roof_thickness = roof_data.get("thickness", 0.15)
    roof_material = roof_data.get("material", "concrete")

    if roof_thickness <= 0:
        raise ValueError("Roof thickness must be positive")

    top_floor_index = len(floors) - 1
    top_floor_base = top_floor_index * FLOOR_HEIGHT

    roof_y = (
        top_floor_base
        + WALL_HEIGHT
        + roof_thickness / 2
    )

    return [{
        "type": "roof",
        "roof_type": roof_data.get("roof_type", "flat"),
        "size": {
            "width": plot["width"],
            "height": roof_thickness,
            "depth": plot["length"]
        },
        "position": {
            "x": 0,
            "y": roof_y,
            "z": 0
        },
        "material": roof_material
    }]

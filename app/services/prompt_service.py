import re
import math
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from app.schemas.building import BuildingSchema
from app.services.llm_service import generate_house_requirements


# ============================================================
# 1. UNIT CONVERSION
# ============================================================

def feet_to_meters(value: float) -> float:
    """Convert feet into meters."""
    return round(value * 0.3048, 3)


# ============================================================
# 2. EXTRACT PLOT DIMENSIONS (RULE-BASED HELPER)
# ============================================================

def extract_plot_dimensions(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Extract plot dimensions from a prompt.

    Examples:
        30 x 40 feet
        30 by 40 ft
        9 x 12 meters
        30*40 feet
    """

    pattern = (
        r"(\d+(?:\.\d+)?)\s*"
        r"(?:x|X|\*|by)\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(feet|foot|ft|meters|metres|meter|metre|m)?"
    )

    match = re.search(pattern, prompt, re.IGNORECASE)

    if not match:
        return None

    width = float(match.group(1))
    length = float(match.group(2))
    unit = (match.group(3) or "feet").lower()

    if width <= 0 or length <= 0:
        return None

    if unit in ["feet", "foot", "ft"]:
        width = feet_to_meters(width)
        length = feet_to_meters(length)

    return {
        "width": round(width, 3),
        "length": round(length, 3),
        "unit": "meter"
    }


# ============================================================
# 3. EXTRACT NUMBER OF FLOORS (RULE-BASED HELPER)
# ============================================================

def extract_floor_count(prompt: str) -> int:
    """Extract the number of floors from a prompt."""

    text = prompt.lower()

    word_numbers = {
        "one": 1,
        "single": 1,
        "two": 2,
        "double": 2,
        "three": 3,
        "four": 4,
        "five": 5
    }

    for word, number in word_numbers.items():

        pattern = (
            rf"\b{word}\s*"
            rf"(?:-?\s*)?"
            rf"(?:floor|floors|storey|storeys|story|stories)\b"
        )

        if re.search(pattern, text):
            return number

    digit_match = re.search(
        r"\b(\d+)\s*(?:-?\s*)?"
        r"(?:floor|floors|storey|storeys|story|stories)\b",
        text
    )

    if digit_match:
        count = int(digit_match.group(1))

        if 1 <= count <= 10:
            return count

    if "ground floor" in text or "single floor" in text:
        return 1

    return 1


# ============================================================
# 4. EXTRACT ROOM REQUIREMENTS (RULE-BASED HELPER)
# ============================================================

def extract_room_requirements(prompt: str) -> Dict[str, int]:
    """
    Extract room counts using regular expressions.

    This is a helper function. The main generation workflow
    currently uses Ollama for requirement extraction.
    """

    text = prompt.lower()

    room_patterns = {
        "bedrooms": r"(\d+|one|two|three|four|five)\s*(?:bedroom|bedrooms|bed room|bed rooms)\b",
        "kitchens": r"(\d+|one|two|three|four|five)\s*(?:kitchen|kitchens)\b",
        "living_rooms": r"(\d+|one|two|three|four|five)\s*(?:living room|living rooms|hall|halls)\b",
        "bathrooms": r"(\d+|one|two|three|four|five)\s*(?:bathroom|bathrooms|bath room|bath rooms)\b",
        "dining_rooms": r"(\d+|one|two|three|four|five)\s*(?:dining room|dining rooms)\b",
        "balconies": r"(\d+|one|two|three|four|five)\s*(?:balcony|balconies)\b",
        "parking_spaces": r"(\d+|one|two|three|four|five)\s*(?:car parking|parking space|parking spaces)\b"
    }

    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5
    }

    room_counts = {}

    for room_type, pattern in room_patterns.items():

        match = re.search(pattern, text)

        if match:
            value = match.group(1)

            if value.isdigit():
                count = int(value)
            else:
                count = number_words.get(value, 0)
        else:
            count = 0

        room_counts[room_type] = count

    return room_counts


# ============================================================
# 5. EXTRACT ARCHITECTURAL STYLE (RULE-BASED HELPER)
# ============================================================

def extract_architectural_style(prompt: str) -> str:
    """Identify architectural style from a prompt."""

    text = prompt.lower()

    styles = [
        "modern",
        "traditional",
        "contemporary",
        "minimalist",
        "industrial",
        "mediterranean",
        "farmhouse",
        "colonial",
        "victorian",
        "scandinavian"
    ]

    for style in styles:
        if style in text:
            return style

    return "unspecified"


# ============================================================
# 6. CREATE INDIVIDUAL ROOM OBJECTS
# ============================================================

def create_room_objects(
    room_counts: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Convert room counts into individual room objects.

    Dimensions and coordinates are temporary placeholders.
    """

    room_names = {
        "bedrooms": "Bedroom",
        "kitchens": "Kitchen",
        "living_rooms": "Living Room",
        "bathrooms": "Bathroom",
        "dining_rooms": "Dining Room",
        "balconies": "Balcony",
        "parking_spaces": "Parking Space"
    }

    rooms = []

    for room_type, count in room_counts.items():

        room_name = room_names.get(room_type, room_type)

        for index in range(1, count + 1):

            name = (
                room_name
                if count == 1
                else f"{room_name} {index}"
            )

            rooms.append({
                "name": name,
                "width": 1.0,
                "length": 1.0,
                "x": 0.0,
                "z": 0.0
            })

    return rooms


# ============================================================
# 7. ALLOCATE ROOMS ACROSS FLOORS
# ============================================================


def allocate_rooms_to_floors(
    room_counts: Dict[str, int],
    floor_count: int,
    plot_width: float,
    plot_length: float
) -> List[Dict[str, Any]]:
    """
    Allocate rooms across floors and calculate room dimensions
    and non-overlapping grid positions.

    Coordinates:
        x = horizontal position
        z = depth position

    All dimensions are in metres.
    """

    room_names = {
        "bedrooms": "Bedroom",
        "bathrooms": "Bathroom",
        "kitchens": "Kitchen",
        "living_rooms": "Living Room",
        "dining_rooms": "Dining Room",
        "balconies": "Balcony",
        "parking_spaces": "Parking Space"
    }

    # Default dimensions: width x length (metres)
    room_dimensions = {
        "bedrooms": (3.0, 3.5),
        "bathrooms": (1.5, 2.0),
        "kitchens": (2.5, 3.0),
        "living_rooms": (3.5, 4.0),
        "dining_rooms": (2.5, 3.0),
        "balconies": (1.5, 3.0),
        "parking_spaces": (2.7, 5.0)
    }

    floor_rooms = {
        floor_number: []
        for floor_number in range(1, floor_count + 1)
    }

    ground_floor_rooms = [
        "living_rooms",
        "kitchens",
        "dining_rooms",
        "parking_spaces"
    ]

    upper_floor_rooms = [
        "bedrooms",
        "bathrooms",
        "balconies"
    ]

    if floor_count == 1:
        upper_floor_numbers = [1]
    else:
        upper_floor_numbers = list(range(2, floor_count + 1))

    # Step A: Allocate rooms to floors
    for room_type, count in room_counts.items():

        room_name = room_names[room_type]

        if room_type in ground_floor_rooms:
            target_floors = [1]
        elif room_type in upper_floor_rooms:
            target_floors = upper_floor_numbers
        else:
            target_floors = [1]

        for index in range(1, count + 1):

            name = (
                room_name
                if count == 1
                else f"{room_name} {index}"
            )

            assigned_floor = target_floors[
                (index - 1) % len(target_floors)
            ]

            width, length = room_dimensions[room_type]

            room = {
                "name": name,
                "width": width,
                "length": length,
                "x": 0.0,
                "z": 0.0
            }

            floor_rooms[assigned_floor].append(room)

    # Step B: Position rooms without overlapping
    gap = 0.15
    result = []

    for floor_number, rooms in floor_rooms.items():

        current_x = 0.0
        current_z = 0.0
        row_depth = 0.0

        for room in rooms:

            width = room["width"]
            length = room["length"]

            if width > plot_width or length > plot_length:
                raise ValueError(
                    f"{room['name']} dimensions exceed plot boundaries."
                )

            # Start a new row if the room does not fit horizontally
            if current_x + width > plot_width:
                current_x = 0.0
                current_z += row_depth + gap
                row_depth = 0.0

            # Check whether the room fits vertically in the plot
            if current_z + length > plot_length:
                raise ValueError(
                    f"Rooms on floor {floor_number} exceed "
                    "the available plot area. Reduce room counts "
                    "or adjust room dimensions."
                )

            room["x"] = round(current_x, 3)
            room["z"] = round(current_z, 3)

            current_x += width + gap
            row_depth = max(row_depth, length)

        # Calculate room counts for this floor
        counts = {
            room_type: 0
            for room_type in room_counts
        }

        for room in rooms:
            for room_type, display_name in room_names.items():

                if (
                    room["name"] == display_name
                    or room["name"].startswith(display_name + " ")
                ):
                    counts[room_type] += 1
                    break

        result.append({
            "floor_number": floor_number,
            "rooms": rooms,
            "room_counts": counts
        })

    return result



# ============================================================
# 8. GENERATE BUILDING JSON USING OLLAMA
# ============================================================

def generate_building_data(prompt: str) -> Dict[str, Any]:
    """
    Generate structured building JSON.

    Workflow:
        User Prompt
            -> Ollama
            -> Extract Requirements
            -> Allocate Rooms
            -> Generate Building JSON
    """

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    # 1. Extract requirements using Ollama
    requirements = generate_house_requirements(prompt)

    if not isinstance(requirements, dict):
        raise ValueError("Ollama must return a JSON object.")

    # 2. Extract and validate plot dimensions
    try:
        plot_width = float(requirements["plot_width"])
        plot_length = float(requirements["plot_length"])

    except (KeyError, TypeError, ValueError):
        raise ValueError(
            "Ollama could not identify valid plot dimensions."
        )

    if plot_width <= 0 or plot_length <= 0:
        raise ValueError(
            "Plot dimensions must be greater than zero."
        )

    # 3. Extract number of floors
    try:
        floor_value = requirements["number_of_floors"]

        if isinstance(floor_value, bool):
            raise ValueError

        floor_count = int(floor_value)

        if float(floor_value) != floor_count:
            raise ValueError

    except (KeyError, TypeError, ValueError):
        raise ValueError(
            "Invalid number of floors returned by Ollama."
        )

    if floor_count < 1 or floor_count > 10:
        raise ValueError(
            "Number of floors must be between 1 and 10."
        )

    # 4. Extract and validate room counts
    room_types = [
        "bedrooms",
        "bathrooms",
        "kitchens",
        "living_rooms",
        "dining_rooms",
        "balconies",
        "parking_spaces"
    ]

    room_counts = {}

    for room_type in room_types:

        value = requirements.get(room_type, 0)

        try:
            if isinstance(value, bool):
                raise ValueError

            count = int(value)

            if float(value) != count:
                raise ValueError

        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid room count returned for {room_type}."
            )

        if count < 0:
            raise ValueError(
                f"{room_type} cannot have a negative count."
            )

        room_counts[room_type] = count

    # 5. Extract architectural style
    architectural_style = requirements.get(
        "architectural_style",
        "unspecified"
    )

    if not isinstance(architectural_style, str):
        architectural_style = "unspecified"

    architectural_style = architectural_style.strip().lower()

    if not architectural_style:
        architectural_style = "unspecified"

    # 6. Allocate rooms across floors
    floor_allocations = allocate_rooms_to_floors(
    room_counts,
    floor_count,
    plot_width,
    plot_length
)

    # 7. Create floor structure
    floors = []

    for allocation in floor_allocations:

        floors.append({
            "floor_number": allocation["floor_number"],
            "height": 3.0,
            "rooms": allocation["rooms"],
            "room_counts": allocation["room_counts"],
            "walls": [],
            "doors": [],
            "windows": [],
            "furniture": []
        })

    # 8. Generate final building JSON
    building_data = {
        "name": "AI Generated House",
        "architectural_style": architectural_style,
        "unit": "meter",
        "plot": {
            "width": round(plot_width, 3),
            "length": round(plot_length, 3)
        },
        "floors": floors,
        "roof": {
            "roof_type": "flat",
            "thickness": 0.15,
            "material": "concrete"
        }
    }

    return building_data


# ============================================================
# 9. VALIDATE GENERATED BUILDING JSON
# ============================================================

def validate_building_data(
    building_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate building JSON using the Pydantic BuildingSchema.
    """

    if not isinstance(building_data, dict):
        return {
            "is_valid": False,
            "errors": ["Building data must be a dictionary."]
        }

    try:
        validated_building = BuildingSchema(**building_data)

        return {
            "is_valid": True,
            "errors": [],
            "validated_data": validated_building.model_dump()
        }

    except ValidationError as error:

        return {
            "is_valid": False,
            "errors": error.errors()
        }

    except Exception as error:

        return {
            "is_valid": False,
            "errors": [str(error)]
        }

    
# ============================================================
# 10. VALIDATE ROOM LAYOUT AND GEOMETRY
# ============================================================

def validate_building_layout(
    building_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate room dimensions, plot boundaries,
    room overlaps, floor assignments and room counts.
    """

    errors = []

    if not isinstance(building_data, dict):
        return {
            "is_valid": False,
            "errors": ["Building data must be a dictionary."]
        }

    plot = building_data.get("plot")
    floors = building_data.get("floors")

    if not isinstance(plot, dict):
        return {
            "is_valid": False,
            "errors": ["Invalid plot information."]
        }

    try:
        plot_width = float(plot["width"])
        plot_length = float(plot["length"])
    except (KeyError, TypeError, ValueError):
        return {
            "is_valid": False,
            "errors": ["Invalid plot dimensions."]
        }

    if plot_width <= 0 or plot_length <= 0:
        return {
            "is_valid": False,
            "errors": ["Plot dimensions must be positive."]
        }

    if not isinstance(floors, list) or not floors:
        return {
            "is_valid": False,
            "errors": ["Building must contain at least one floor."]
        }

    room_names = {
        "bedrooms": "Bedroom",
        "bathrooms": "Bathroom",
        "kitchens": "Kitchen",
        "living_rooms": "Living Room",
        "dining_rooms": "Dining Room",
        "balconies": "Balcony",
        "parking_spaces": "Parking Space"
    }

    seen_floors = set()

    for floor in floors:

        if not isinstance(floor, dict):
            errors.append("Invalid floor information.")
            continue

        floor_number = floor.get("floor_number")
        rooms = floor.get("rooms", [])
        room_counts = floor.get("room_counts", {})

        if (
            isinstance(floor_number, bool)
            or not isinstance(floor_number, int)
            or floor_number < 1
        ):
            errors.append(
                f"Invalid floor number: {floor_number}"
            )
            continue

        if floor_number in seen_floors:
            errors.append(
                f"Duplicate floor number: {floor_number}"
            )

        seen_floors.add(floor_number)

        if not isinstance(rooms, list):
            errors.append(
                f"Rooms on floor {floor_number} must be a list."
            )
            continue

        if not isinstance(room_counts, dict):
            errors.append(
                f"Invalid room counts on floor {floor_number}."
            )
            room_counts = {}

        valid_rooms = []

        # ----------------------------------------------------
        # A. Validate individual rooms
        # ----------------------------------------------------

        for index, room in enumerate(rooms, start=1):

            if not isinstance(room, dict):
                errors.append(
                    f"Invalid room object on floor {floor_number}."
                )
                continue

            room_name = room.get("name", f"Room {index}")

            try:
                width = float(room["width"])
                length = float(room["length"])
                x = float(room["x"])
                z = float(room["z"])

            except (KeyError, TypeError, ValueError):
                errors.append(
                    f"{room_name}: Invalid dimensions or coordinates."
                )
                continue

            if not all(
                math.isfinite(value)
                for value in (width, length, x, z)
            ):
                errors.append(
                    f"{room_name}: Dimensions and coordinates "
                    "must be finite numbers."
                )
                continue

            if width <= 0 or length <= 0:
                errors.append(
                    f"{room_name}: Width and length must be positive."
                )
                continue

            if x < 0 or z < 0:
                errors.append(
                    f"{room_name}: Coordinates cannot be negative."
                )
                continue

            # Check plot width
            if x + width > plot_width + 1e-6:
                errors.append(
                    f"{room_name} on floor {floor_number} "
                    "exceeds plot width."
                )
                continue

            # Check plot length
            if z + length > plot_length + 1e-6:
                errors.append(
                    f"{room_name} on floor {floor_number} "
                    "exceeds plot length."
                )
                continue

            valid_rooms.append({
                "name": room_name,
                "x": x,
                "z": z,
                "width": width,
                "length": length
            })

        # ----------------------------------------------------
        # B. Check room overlaps
        # ----------------------------------------------------

        for i in range(len(valid_rooms)):

            for j in range(i + 1, len(valid_rooms)):

                room_a = valid_rooms[i]
                room_b = valid_rooms[j]

                overlap_x = (
                    room_a["x"] <
                    room_b["x"] + room_b["width"]
                    and
                    room_a["x"] + room_a["width"] >
                    room_b["x"]
                )

                overlap_z = (
                    room_a["z"] <
                    room_b["z"] + room_b["length"]
                    and
                    room_a["z"] + room_a["length"] >
                    room_b["z"]
                )

                if overlap_x and overlap_z:
                    errors.append(
                        f"{room_a['name']} and {room_b['name']} "
                        f"overlap on floor {floor_number}."
                    )

        # ----------------------------------------------------
        # C. Check floor-wise room counts
        # ----------------------------------------------------

        actual_counts = {
            room_type: 0
            for room_type in room_names
        }

        for room in rooms:

            if not isinstance(room, dict):
                continue

            name = room.get("name", "")

            if not isinstance(name, str):
                continue

            for room_type, display_name in room_names.items():

                if (
                    name == display_name
                    or name.startswith(display_name + " ")
                ):
                    actual_counts[room_type] += 1
                    break

        for room_type, actual_count in actual_counts.items():

            expected_count = room_counts.get(room_type, 0)

            if (
                isinstance(expected_count, bool)
                or not isinstance(expected_count, int)
                or expected_count < 0
            ):
                errors.append(
                    f"Floor {floor_number}: Invalid count for "
                    f"{room_type}."
                )
                continue

            if expected_count != actual_count:
                errors.append(
                    f"Floor {floor_number}: {room_type} count mismatch. "
                    f"Expected {expected_count}, found {actual_count}."
                )

    # --------------------------------------------------------
    # D. Final validation result
    # --------------------------------------------------------

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


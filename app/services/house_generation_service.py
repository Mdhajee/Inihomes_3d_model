from pathlib import Path

from app.services.prompt_service import (
    generate_building_data,
    validate_building_data,
    validate_building_layout
)

from app.services.geometry_service import (
    generate_floor_slabs,
    generate_external_walls,
    generate_internal_walls,
    generate_doors,
    generate_door_panels,
    generate_staircase,
    generate_roof
)

from app.exporters.glb_exporter import export_house_to_glb



def generate_complete_house(
    user_prompt: str,
    output_path: str = "exports/house_exterior.glb"
) -> dict:
    """
    Generate a complete house and export exterior
    and interior cutaway GLB models.
    """

    # 1. Generate house requirements
    building_data = generate_building_data(user_prompt)

    # 2. Validate building data
    validate_building_data(building_data)

    # 3. Validate room layout
    validate_building_layout(building_data)

    # 4. Generate geometry components once
    floor_slabs = generate_floor_slabs(building_data)
    external_walls = generate_external_walls(building_data)
    internal_walls = generate_internal_walls(building_data)
    doors = generate_doors(building_data)
    door_panels = generate_door_panels(building_data)
    staircase = generate_staircase(building_data)
    roofs = generate_roof(building_data)

    # 5. Common exporter arguments
    export_args = {
        "floor_slabs": floor_slabs,
        "external_walls": external_walls,
        "internal_walls": internal_walls,
        "door_panels": door_panels,
        "roofs": roofs,
        "staircase": staircase
    }

    # 6. Export complete exterior
    exterior_path = output_path

    export_house_to_glb(
        **export_args,
        output_path=exterior_path,
        view_mode="exterior"
    )

    # 7. Export interior cutaway
    interior_path = str(
        Path(output_path).with_name("house_interior.glb")
    )

    export_house_to_glb(
        **export_args,
        output_path=interior_path,
        view_mode="interior"
    )

    # 8. Return generation details
    return {
        "status": "success",
        "building_data": building_data,
        "geometry_summary": {
            "floor_slabs": len(floor_slabs),
            "external_walls": len(external_walls),
            "internal_walls": len(internal_walls),
            "doors": len(doors),
            "door_panels": len(door_panels),
            "staircase_elements": len(staircase),
            "roof_elements": len(roofs)
        },
        "glb_paths": {
            "exterior": exterior_path,
            "interior": interior_path
        }
    }


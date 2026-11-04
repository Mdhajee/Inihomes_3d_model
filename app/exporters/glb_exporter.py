
import trimesh
from pathlib import Path


def export_house_to_glb(
    floor_slabs: list,
    external_walls: list,
    internal_walls: list,
    output_path: str = "exports/house.glb",
    door_panels: list = None,
    roofs: list = None,
    staircase: list = None,
    view_mode: str = "exterior"
) -> str:
    """
    Export house geometry as an exterior or interior cutaway GLB.

    exterior:
        Complete house with all exterior walls.

    interior:
        Front exterior wall sections omitted to expose the interior.
    """

    if view_mode not in ("exterior", "interior"):
        raise ValueError(
            "view_mode must be 'exterior' or 'interior'"
        )

    scene = trimesh.Scene()

    # Keep all original geometry unchanged.
    selected_external_walls = []

    for wall in external_walls:

        # Identify front-facing walls using their position.
        # Front walls have their centre near the minimum Z boundary.
        if view_mode == "interior":
            if wall["position"]["z"] < 0:
                continue

        selected_external_walls.append(wall)

    all_elements = (
        floor_slabs
        + selected_external_walls
        + internal_walls
        + (door_panels or [])
        + (roofs or [])
        + (staircase or [])
    )

    for index, element in enumerate(all_elements):

        if element["type"] == "floor_slab":
            width = element["width"]
            height = element["thickness"]
            depth = element["length"]

        else:
            width = element["size"]["width"]
            height = element["size"]["height"]
            depth = element["size"]["depth"]

        mesh = trimesh.creation.box(
            extents=[width, height, depth]
        )

        # Assign colours based on geometry type.
        if element["type"] == "floor_slab":
            mesh.visual.face_colors = [160, 160, 160, 255]

        elif element["type"] == "external_wall":
            mesh.visual.face_colors = [180, 210, 240, 255]

        elif element["type"] == "internal_wall":
            mesh.visual.face_colors = [230, 180, 120, 255]

        elif element["type"] == "door_panel":
            mesh.visual.face_colors = [120, 70, 35, 255]

        elif element["type"] == "roof":
            mesh.visual.face_colors = [110, 110, 110, 255]

        elif element["type"] == "stair_step":
            mesh.visual.face_colors = [190, 190, 190, 255]

        elif element["type"] == "stair_landing":
            mesh.visual.face_colors = [160, 160, 160, 255]

        position = element["position"]

        mesh.apply_translation([
            position["x"],
            position["y"],
            position["z"]
        ])

        scene.add_geometry(
            mesh,
            node_name=f"{element['type']}_{index}"
        )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    scene.export(output_file, file_type="glb")

    return str(output_file)

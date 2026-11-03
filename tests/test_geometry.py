import pytest
from app.geometry.wall import generate_wall
from app.geometry.room import generate_room
from app.services.building_service import create_building


def sample_plan():
    return {
        "project_id": "house_001",
        "name": "Test House",
        "unit": "meter",
        "plot": {"width": 10, "length": 10},
        "floors": [{
            "floor_number": 1,
            "height": 3,
            "walls": [
                {"id": "w1", "start": {"x": 0, "y": 0}, "end": {"x": 5, "y": 0}},
                {"id": "w2", "start": {"x": 5, "y": 0}, "end": {"x": 5, "y": 4}},
                {"id": "w3", "start": {"x": 5, "y": 4}, "end": {"x": 0, "y": 4}},
                {"id": "w4", "start": {"x": 0, "y": 4}, "end": {"x": 0, "y": 0}}
            ],
            "rooms": [{
                "id": "r1",
                "name": "Bedroom",
                "boundary": [
                    {"x": 0, "y": 0}, {"x": 5, "y": 0},
                    {"x": 5, "y": 4}, {"x": 0, "y": 4}
                ]
            }],
            "doors": [{
                "id": "d1", "wall_id": "w1",
                "width": 0.9, "height": 2.1, "position": 0.5
            }],
            "windows": [{
                "id": "win1", "wall_id": "w3",
                "width": 1.2, "height": 1.0,
                "sill_height": 0.9, "position": 0.5
            }]
        }]
    }


def test_wall_length_and_center():
    wall = generate_wall({
        "id": "w1",
        "start": {"x": 0, "y": 0},
        "end": {"x": 5, "y": 0}
    })
    assert wall["length"] == pytest.approx(5)
    assert wall["position"]["x"] == pytest.approx(2.5)
    assert wall["position"]["y"] == pytest.approx(1.5)


def test_room_area():
    room = generate_room({
        "id": "r1",
        "boundary": [
            {"x": 0, "y": 0}, {"x": 5, "y": 0},
            {"x": 5, "y": 4}, {"x": 0, "y": 4}
        ]
    })
    assert room["area"] == pytest.approx(20)


def test_full_house_generation():
    result = create_building(sample_plan())
    floor = result["floors"][0]
    assert len(floor["walls"]) == 4
    assert len(floor["rooms"]) == 1
    assert len(floor["doors"]) == 1
    assert len(floor["windows"]) == 1
    assert result["unit"] == "meter"


def test_zero_length_wall_rejected():
    with pytest.raises(ValueError):
        generate_wall({
            "id": "bad",
            "start": {"x": 1, "y": 1},
            "end": {"x": 1, "y": 1}
        })


def test_invalid_door_reference_rejected():
    plan = sample_plan()
    plan["floors"][0]["doors"][0]["wall_id"] = "missing"
    with pytest.raises(ValueError):
        create_building(plan)

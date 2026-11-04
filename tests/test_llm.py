import copy

from app.services.prompt_service import (
    generate_building_data,
    validate_building_data,
    validate_building_layout
)

prompt = """
Create a modern two-floor house on a 30 x 40 feet plot.
It should have 2 bedrooms, 2 bathrooms,
1 kitchen, 1 living room and 1 dining room.
"""

# Step 1: Generate building data
building_data = generate_building_data(prompt)

# Step 2: Display floor-wise room allocation
print("\nFLOOR-WISE ROOM ALLOCATION")
print("==========================")

for floor in building_data["floors"]:

    print(f"\nFloor {floor['floor_number']}")

    for room in floor["rooms"]:
        print(
            f" - {room['name']} | "
            f"Width: {room['width']} m | "
            f"Length: {room['length']} m | "
            f"X: {room['x']} | "
            f"Z: {room['z']}"
        )

    print("Room counts:", floor["room_counts"])


# Step 3: Pydantic validation
print("\nPYDANTIC VALIDATION RESULT")
print("==========================")

validation_result = validate_building_data(building_data)

print(validation_result)


# Step 4: Layout validation
print("\nLAYOUT VALIDATION RESULT")
print("========================")

layout_result = validate_building_layout(building_data)

print(layout_result)

# Step 5: Test room overlap detection

print("\nOVERLAP DETECTION TEST")
print("======================")

# Create a separate copy so original building data is unchanged
test_building = copy.deepcopy(building_data)

# Select two rooms on the ground floor
rooms = test_building["floors"][0]["rooms"]

# Place the second room at exactly the same position as the first
rooms[1]["x"] = rooms[0]["x"]
rooms[1]["z"] = rooms[0]["z"]

# Validate the modified layout
overlap_result = validate_building_layout(test_building)

print(overlap_result)

# Step 6: Test plot-boundary detection

print("\nPLOT BOUNDARY TEST")
print("==================")

boundary_test = copy.deepcopy(building_data)

# Move the kitchen beyond the plot width
kitchen = boundary_test["floors"][0]["rooms"][0]
kitchen["x"] = 20.0

boundary_result = validate_building_layout(boundary_test)

print(boundary_result)
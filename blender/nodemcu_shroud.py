import bpy

# --- Configuration Parameters ---
# 0. Select Board
ACTIVE_BOARD_NAME = "NodeMCU_Amica" # Change this to select a different board

# 1. Board Definition
all_board_configs = {
    "NodeMCU_Amica": {
        "name": "NodeMCU_Amica", # This can be redundant if key is used, but good for self-documentation
        "pins_per_row": 15,
        "pin_pitch": 2.54,  # mm
        "row_spacing": 22.86,  # mm (centerline to centerline of the two rows)
        "pin_length": 6.0,  # mm (length of the metal part of the pin exposed from the PCB)
        # Pin naming: (Row_Index (0 or 1), Pin_Index_in_Row (0 to 14 from one end))
        # !!! CRITICAL USER VERIFICATION NEEDED FOR PIN_MAP !!!
        # This pin_map is an EXAMPLE. You MUST verify it against your specific NodeMCU Amica
        # board and your chosen orientation/numbering convention.
        # For instance, if USB is to the left:
        # Row 0 could be the "top" row (pins 0-14 counted from right-to-left, A0 to VIN).
        # Row 1 could be the "bottom" row (pins 0-14 counted from right-to-left, D0 to SK2).
        "pin_map": {
            # Row 0 (Example: "top" or "left" row, pins 0-14)
            "A0":    (0, 0), "RSV1":  (0, 1), "RSV2":  (0, 2), "SD3":   (0, 3),
            "SD2":   (0, 4), "SD1":   (0, 5), "CMD":   (0, 6), "SD0":   (0, 7),
            "CLK":   (0, 8), "GND1":  (0, 9), "3V3_1": (0, 10),"EN":    (0, 11),
            "RST":   (0, 12),"GND2":  (0, 13),"VIN":   (0, 14),
            # Row 1 (Example: "bottom" or "right" row, pins 0-14)
            "D0":    (1, 0), "D1":    (1, 1), "D2":    (1, 2), "D3":    (1, 3),
            "D4":    (1, 4), "D5":    (1, 5), "D6":    (1, 6), "D7":    (1, 7),
            "D8":    (1, 8), "RX":    (1, 9), "TX":    (1, 10),"GND3":  (1, 11),
            "3V3_2": (1, 12),"SK1":   (1, 13),"SK2":   (1, 14) # SK usually 'डू नॉट कनेक्ट' or special
        }
    },
    # Example for another board (you'd fill this in with actual data)
    # "ESP32_DevKitC": {
    #     "name": "ESP32_DevKitC",
    #     "pins_per_row": 19, # Example value
    #     "pin_pitch": 2.54,
    #     "row_spacing": 25.4, # Example value
    #     "pin_length": 5.0,   # Example value
    #     "pin_map": { /* ... ESP32 specific pin map ... */ }
    # }
}

# Select the active board configuration
if ACTIVE_BOARD_NAME not in all_board_configs:
    raise ValueError(f"Board '{ACTIVE_BOARD_NAME}' not found in all_board_configs. Available boards: {list(all_board_configs.keys())}")
board_config = all_board_configs[ACTIVE_BOARD_NAME]

# 2. Shroud Design Parameters
pin_depth_clearance = 0.5      # mm (extra depth for pin holes beyond actual pin length)
top_surface_thickness = 1.5    # mm (thickness of the shroud's solid top, above where standard pins end)

standard_pin_hole_square_width = 1.0  # mm (Width of the square holes for standard pins. Try 0.9mm for tighter, 1.0mm for slightly looser for ~0.64mm pins)

jumper_cutout_square_width = 3.0  # mm (Width for the larger square cutouts for jumper access)
# List of pin names (from pin_map) that should get jumper access cutouts
pins_for_jumper_access = ["VIN", "GND1", "D1", "D2", "D7", "3V3_1"]

# Chamfering for pin hole openings (helps with printability)
enable_pin_hole_opening_chamfer = True # If True, adds a slight enlargement at the hole opening
pin_hole_chamfer_additional_width_per_side = 0.3  # mm, how much wider the chamfer makes the hole on each side (e.g., 0.3mm means opening is 0.6mm wider in total)
pin_hole_chamfer_depth = 0.5 # mm, how deep this enlarged section goes from the opening

remove_middle_material = True  # If True, removes material between the two pin rows
middle_channel_jumper_separation = 0.5 # mm, thickness of the wall to leave between the middle channel and the edge of a jumper hole.
middle_material_cutout_length_offset = 0.0 # mm, additional length adjustment for the middle cutout.
                                           # The base length is calculated to leave 'middle_channel_jumper_separation'
                                           # around potential end jumper pins (i.e., shorter than pin_block_row_length).
                                           # A value of 0.0 uses this base length.
                                           # Positive values make it longer; negative values make it shorter.

wall_thickness = 2.0  # mm (general wall thickness around the pin area)


# --- Calculated Dimensions (Derived from Parameters using the selected board_config) ---
internal_pin_depth = board_config["pin_length"] + pin_depth_clearance
total_part_height = internal_pin_depth + top_surface_thickness

# Overall length of the block of pins in a single row (center of first pin to center of last pin)
pin_block_row_length = (board_config["pins_per_row"] - 1) * board_config["pin_pitch"]

# Use the width of the standard pin opening for calculating overall shroud size
# This dimension is added to the span of pin centerlines to get an outer boundary for the pin area
pin_opening_dimension_for_spacing = standard_pin_hole_square_width

# Calculate outer dimensions of the shroud
outer_shroud_width = board_config["row_spacing"] + pin_opening_dimension_for_spacing + (2 * wall_thickness)
outer_shroud_length = pin_block_row_length + pin_opening_dimension_for_spacing + (2 * wall_thickness)

# --- Helper Functions (General Purpose) ---
def clear_scene():
    """Deletes all MESH objects from the current scene."""
    if bpy.ops.object.mode_set.poll(): # Ensure not in Edit Mode
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

def apply_boolean(main_object, cutter_object, operation='DIFFERENCE'):
    """Applies a boolean modifier to main_object with cutter_object, then removes cutter."""
    bool_mod = main_object.modifiers.new(name="Boolean_" + cutter_object.name, type='BOOLEAN')
    bool_mod.object = cutter_object
    bool_mod.operation = operation

    # Set context for applying modifier
    bpy.ops.object.select_all(action='DESELECT')
    main_object.select_set(True)
    bpy.context.view_layer.objects.active = main_object

    try:
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    except Exception as e:
        print(f"Error applying modifier {bool_mod.name} to {main_object.name}: {e}")
        # Optionally, remove the modifier if it failed to apply but was added
        # main_object.modifiers.remove(bool_mod)
        raise # Re-raise the exception to halt script or allow further handling

    bpy.data.objects.remove(cutter_object, do_unlink=True) # Clean up the cutter object

# --- Object Creation Functions (using calculated dimensions) ---

def create_base_shroud(name, length, width, height):
    """Creates the main rectangular solid for the shroud."""
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        enter_editmode=False,
        align='WORLD',
        location=(0, 0, height / 2.0) # Origin at center of height, so base is at Z=0
    )
    base_obj = bpy.context.active_object
    base_obj.name = name
    base_obj.dimensions = (length, width, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return base_obj

def create_pin_hole_cutter(is_jumper, location_xy, name):
    """Creates a cutter object (cube) for a pin hole."""
    pin_hole_loc_x, pin_hole_loc_y = location_xy

    if is_jumper:
        depth = total_part_height # Jumper cutout: Square, goes all the way through
        width = jumper_cutout_square_width
        loc_z = total_part_height / 2.0 # Centered in the total part height
    else:
        depth = internal_pin_depth # Standard pin hole: blind hole
        width = standard_pin_hole_square_width
        loc_z = total_part_height - (internal_pin_depth / 2.0) # Cutter's center Z

    bpy.ops.mesh.primitive_cube_add(size=1, location=(pin_hole_loc_x, pin_hole_loc_y, loc_z))
    cutter = bpy.context.active_object
    cutter.name = name
    cutter.dimensions = (width, width, depth)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return cutter

# --- Main Script Execution ---

# 1. Setup Scene
clear_scene()
shroud_obj = None # Initialize shroud_obj in case of early exit

# 2. Create Base Shroud Body
shroud_obj = create_base_shroud(
    name=f"{board_config['name']}_Shroud",
    length=outer_shroud_length,
    width=outer_shroud_width,
    height=total_part_height
)

# 3. Create and Apply Pin Holes / Cutouts
# Pin locations are relative to the center of the pin block area (0,0 for X,Y)
start_x_offset = -pin_block_row_length / 2.0 # X-coordinate of the first pin in a row
# Y-coordinates for the centerlines of the two pin rows
# Row 0 will be at -Y, Row 1 at +Y (or vice-versa depending on pin_map convention)
row_y_offsets = [-board_config["row_spacing"] / 2.0, board_config["row_spacing"] / 2.0]

# Convert list of jumper pin names to a list of (row_index, pin_index_in_row) tuples
jumper_pin_coordinates = []
for pin_name_to_find in pins_for_jumper_access:
    if pin_name_to_find in board_config["pin_map"]:
        jumper_pin_coordinates.append(board_config["pin_map"][pin_name_to_find])
    else:
        print(f"Warning: Jumper pin name '{pin_name_to_find}' not found in pin_map. Skipping.")

# Iterate through each potential pin position
for r_idx in range(2):  # Corresponds to row_y_offsets[0] and row_y_offsets[1]
    current_row_y = row_y_offsets[r_idx]
    for p_idx in range(board_config["pins_per_row"]):  # Pin index in the current row (0 to N-1)
        current_pin_x = start_x_offset + (p_idx * board_config["pin_pitch"])
        pin_center_xy = (current_pin_x, current_row_y)

        # Check if the current pin (identified by its r_idx, p_idx) is a jumper pin
        is_jumper_pin = (r_idx, p_idx) in jumper_pin_coordinates
        
        cutter_object_name = f"Cutter_R{r_idx}_P{p_idx}_{'Jumper' if is_jumper_pin else 'Standard'}"
        pin_cutter_obj = create_pin_hole_cutter(is_jumper_pin, pin_center_xy, cutter_object_name)
        
        if shroud_obj: # Ensure shroud_obj was successfully created
            apply_boolean(shroud_obj, pin_cutter_obj)

            # If enabled, create and apply a chamfer/enlargement at the hole opening
            if enable_pin_hole_opening_chamfer and pin_hole_chamfer_additional_width_per_side > 0.001 and pin_hole_chamfer_depth > 0.001:
                chamfer_cutter_name = f"Chamfer_R{r_idx}_P{p_idx}"
                
                base_hole_width = jumper_cutout_square_width if is_jumper_pin else standard_pin_hole_square_width
                chamfer_cutter_width = base_hole_width + (2 * pin_hole_chamfer_additional_width_per_side)
                
                # Chamfer is at the top opening (Z=total_part_height), extending downwards by pin_hole_chamfer_depth.
                # Chamfer cutter Z range: [total_part_height - pin_hole_chamfer_depth, total_part_height]
                # Cutter's center Z:
                chamfer_loc_z = total_part_height - (pin_hole_chamfer_depth / 2.0)

                bpy.ops.mesh.primitive_cube_add(
                    size=1,
                    location=(pin_center_xy[0], pin_center_xy[1], chamfer_loc_z),
                    enter_editmode=False,
                    align='WORLD'
                )
                chamfer_obj = bpy.context.active_object
                chamfer_obj.name = chamfer_cutter_name
                chamfer_obj.dimensions = (chamfer_cutter_width, chamfer_cutter_width, pin_hole_chamfer_depth)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                apply_boolean(shroud_obj, chamfer_obj)
        else:
            # This case should ideally not be reached if create_base_shroud is robust
            print("Error: Base shroud object does not exist. Cannot apply boolean operations.")
            bpy.data.objects.remove(pin_cutter_obj, do_unlink=True) # Clean up the cutter
            break # Exit p_idx loop
    if not shroud_obj:
        break # Exit r_idx loop

# --- Optional: Remove material between pin rows ---
if shroud_obj and remove_middle_material:
    print("Attempting to remove middle material...")

    # Calculate the total reduction needed to accommodate jumper hole width and desired separation on both sides/ends.
    # This applies to both length and width calculations for the cutter.
    jumper_related_reduction = jumper_cutout_square_width + (2 * middle_channel_jumper_separation)

    # Calculate dimensions for the middle cutter
    # Base length respects end jumper pins with separation. Offset adjusts this.
    base_middle_cut_length = pin_block_row_length - jumper_related_reduction
    middle_cut_length = base_middle_cut_length + middle_material_cutout_length_offset
    # Width ensures separation from jumper holes on the sides.
    middle_cut_width = board_config["row_spacing"] - jumper_related_reduction
    # Height: Cut all the way through the part.
    middle_cut_height = total_part_height

    if middle_cut_width > 0.001: # Ensure there's actually material to remove (width is positive)
        print(f"Creating middle material cutter: L={middle_cut_length:.2f}, W={middle_cut_width:.2f}, H={middle_cut_height:.2f}")
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            enter_editmode=False,
            align='WORLD',
            location=(0, 0, total_part_height / 2.0), # Centered in X, Y, and Z of the shroud body
        )
        middle_cutter_obj = bpy.context.active_object
        middle_cutter_obj.name = "MiddleMaterialCutter"
        middle_cutter_obj.dimensions = (middle_cut_length, middle_cut_width, middle_cut_height)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        apply_boolean(shroud_obj, middle_cutter_obj) # Default operation is 'DIFFERENCE'
        print("Middle material removed.")
    else:
        print(f"Skipping middle material removal: calculated width ({middle_cut_width:.2f}mm) or length ({middle_cut_length:.2f}mm) is too small or negative. Check row_spacing, pin_block_row_length, jumper_cutout_square_width, and middle_channel_jumper_separation.")

# --- Model Finalization ---
# The model is built directly in its print orientation:
# - Solid base (formerly 'top_surface_thickness' part) is at Z=0.
# - Pin hole openings are on the top face at Z=total_part_height, facing +Z.
if shroud_obj: # Proceed only if shroud_obj was successfully created and processed
    print(f"Model '{shroud_obj.name}' generated in print orientation.")
    # --- Final Information ---
    print(f"--- {board_config['name']} Shroud Generation Complete ---")
    print(f"Overall Dimensions (LxWxH): {outer_shroud_length:.2f} x {outer_shroud_width:.2f} x {total_part_height:.2f} mm")
    print(f"Internal Pin Depth for Standard Pins: {internal_pin_depth:.2f} mm")
    print(f"Base Thickness (solid part on print bed): {top_surface_thickness:.2f} mm")
    print(f"Standard Pin Hole Square Width: {standard_pin_hole_square_width:.2f} mm")
    print(f"Jumper Cutout Square Width: {jumper_cutout_square_width:.2f} mm")
    if enable_pin_hole_opening_chamfer and pin_hole_chamfer_additional_width_per_side > 0 and pin_hole_chamfer_depth > 0:
        print(f"Pin Hole Opening Chamfer: Enabled (Enlargement per side: {pin_hole_chamfer_additional_width_per_side:.2f} mm, Depth: {pin_hole_chamfer_depth:.2f} mm)")

    print(f"Wall Thickness: {wall_thickness:.2f} mm")
    if jumper_pin_coordinates:
        print(f"Jumper access cutouts created for pins (Row Index, Pin Index in Row): {jumper_pin_coordinates}")
    else:
        print("No jumper access pins were successfully mapped or specified in `pins_for_jumper_access`.")
else:
    print("Shroud generation failed or was incomplete because the base shroud object was not created.")
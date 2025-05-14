## Setting up and Running a Script in Blender

This guide explains how to run a Python script within Blender's Text Editor.

1.  **Open Blender:** Launch the Blender application.

2.  **Switch to the Scripting Workspace:**
    *   At the top of the Blender window, you'll see different workspace tabs (e.g., Layout, Modeling, Sculpting).
    *   Click on the **Scripting** tab. This workspace is specifically designed for writing and running Python scripts.

    *Alternatively, you can manually change an editor window to the Text Editor:*
    *   Hover your mouse over the top-left corner of an editor window until the cursor changes to a crosshair.
    *   Click and drag to split the window, or right-click on the border between windows and select "Split Area".
    *   In the new window, click the editor type icon (usually a cube or sphere) in the top-left corner.
    *   Select **Text Editor** from the list.

3.  **Load or Paste Your Script:**
    *   In the Text Editor window:
        *   To load the `nodemcu_shroud.py` script:
            *   Click the **Open** button (it looks like a folder icon).
            *   Navigate to and select the `nodemcu_shroud.py` file (it should be in the same directory as this README).
        *   Alternatively, if you want to create a new script or paste code from elsewhere:
            *   Click the **+ New** button to create a new text block.
            *   You can then paste your Python script code into this editor area.

4.  **Run the Script:**
    *   Ensure the `nodemcu_shroud.py` script (or your desired script) is loaded and visible in the Text Editor.
    *   Click the **Run Script** button. This button looks like a play icon (a triangle pointing right) and is located in the header of the Text Editor window.
    *   The script will then execute. For `nodemcu_shroud.py`, this will generate a 3D model based on its internal configuration.

5.  **Check the Output (Optional):**
    *   Any output from `print()` statements in your script will appear in the **System Console**.
    *   To view the System Console, go to the top menu bar: `Window > Toggle System Console`.

6.  **Save Your Script (Optional but Recommended):**
    *   If you created a new text block or modified the script, you can save it by clicking the **Text** menu in the Text Editor header and selecting **Save** or **Save As**. This saves the script as a `.py` file.
    *   Saving the `.blend` file will also save the text block containing the script within that specific Blender file.

That's it! Your script should now execute within Blender.
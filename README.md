# SR-P-Lite-Plus

This modification allows you to use your SR-P Lite pedals outside Moza ecosystem.

For now it only supports single sensor, so main usecase might be to add standalone loadcell or to use SR-P Lite clutch with SR-P pedals.

# Required parts:
- Waveshare RP2040 Zero
- RJ11 6P4C connector (look for version with wires, not hole through pins)
- Double sided adhesive (optional)

# Wire layout:
- Green: GND
- Yellow: 3.3V
- Red: GPIO26
- Black: Remove (useless)

# 3D Printed parts
https://makerworld.com/pl/models/2160450-sr-p-lite-plus#profileId-2342378

# Assembly tutorial
https://youtube.com/shorts/x3Vuukb6zZ0

# Flashing instructions:
1. Press BOOT button on RP2040 and connect it to PC via USB-C (if this is first flash, it should turn on in bootloader mode without pressing button)
2. Wait for folder to appear
3. Grab UF2 file and put it into folder
4. Controller now should flash itself
5. Check if it is visible in joy.cpl or on https://hardwaretester.com/gamepad
In joy.cpl (and unfortunetly games, I haven't managed to change it's windows name yet) it should be visible as "RP2040 Zero", on Hardwaretester as "SR-P Lite+"
### Note:
You can flash it via Arduino with .ino file, but it won't have changed name in HID

# Calibration instructions
1. Run SR-P Lite+ app
2. Port should connect by itself, if not, selecct correct port and press "Connect"
3. Press "Set Min"
4. Press fully pedal and press "Set Max"
5. Press "Save", calibration shoud be saved and you shouldn't need to use software again :)
   
If something is not working, press Reset
If you reset settings by accident, press Load and everything should be fine :)

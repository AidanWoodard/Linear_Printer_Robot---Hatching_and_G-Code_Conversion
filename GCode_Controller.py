"""
#############################################################
SUMMARY: This file controls the printer directly through a new
serial connection. It is responsible for printing a group of
sticky notes by connecting to printer, orienting the pen, and
send command by command of g-code to the lulzbot.
#############################################################
"""

import serial, time
from Univ_Settings import *

def establish_printer_connection(port, baudr):
    """Create a connection with the printer"""
    try:
        ser = serial.Serial(port, baudr, timeout=1)     # timeout for establish connection
        time.sleep(2)
        print(f"Connected to printer on port {port}")
        # clear buffer messages from printer
        while ser.in_waiting:
            ser.readline()
        return ser
    except serial.SerialException as e:
        print(f"Encountered error from printer: {e}")
        return None

def send_gcode_command(ser, cmd):
    """Send a single g-code command to the printer"""
    cmd_bytes = (cmd + '\n').encode('utf-8')
    ser.write(cmd_bytes)

    response = ""
    start_time = time.time()
    # wait for 'ok' or 'resend' or a timeout
    while 'ok' not in response and 'resend' not in response and (time.time() - start_time < 10):    # 10 sec timeout
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            response += line

    if 'ok' not in response:
        print(f"Warning: Did not get 'ok' for {cmd} - {response}")
        if 'resend' in response:
            print("Printer requested resend.... ( ._.)")
        return False    # cmd failed, etc.
    return True         # cmd successful

def prepare_print(ser):
    """Prepare to do all unit group prints (start g-code)"""
    # orient the pen
    send_gcode_command(ser, "G90")                                                                              # change to absolute positioning
    send_gcode_command(ser, "G28")                                                                              # home axis
    send_gcode_command(ser, "G21")                                                                              # make sure g-code is in mm
    send_gcode_command(ser, f"G0 X{x_print_start_offset} Y{y_print_start_offset} Z{z_print_start_offset}")      # move away from starting marker
    send_gcode_command(ser, f"G92 X0 Y0")                                                                       # reset origin to current pos
    send_gcode_command(ser, "G0 Y130")
    send_gcode_command(ser, f"G1 Z{z_lift_level} F{print_speed}")                                               # descend slightly

def print_unit_group(ser, gcode):
    """Control printer and print out onto 2x2 sticky notes the lines in 'gcode' on the bed"""
    # draw all the lines
    for cmd in gcode:
        send_gcode_command(ser, cmd)

    send_gcode_command(ser, f"G0 X0 Y{2 * pixels_per_unit_y}")

    return None

def convert_to_gcode(raw_line_set):
    """Convert a set of lines (for 4 units) to g-code commands"""
    gcode_command_set = []

    for line in raw_line_set:
        flipped_xa = (2 * pixels_per_unit_x) - line[0]
        flipped_xb = (2 * pixels_per_unit_x) - line[2]

        gcode_command_set.append(f"G0 X{flipped_xa} Y{line[1]} F{travel_speed}")
        gcode_command_set.append(f"G0 Z{z_draw_level} F{travel_speed}")
        gcode_command_set.append(f"G1 X{flipped_xb} Y{line[3]} F{print_speed}")
        gcode_command_set.append(f"G0 Z{z_lift_level} F{travel_speed}")

    return gcode_command_set



"""
#############################################################
SUMMARY: This file controls the printer directly. It prints
each set of 2x2 units from the 'G-Code Converter' and waits
for user input before beginning each print (so that new notes
can be added onto the bed for printing).
#############################################################
"""
import sys
import math
import pygame

from Image_Generator import calculate_brightness_arrays
from Hatch_Algorithm import HatchingSet
from Unit_Reorderer import *
from GCode_Controller import *

class LinearPrinter:
    """Main program class - runs all other files"""

    def __init__(self):
        """Start pygame window"""
        self.new_brightness_array = calculate_brightness_arrays()
        self.new_hatching_array = HatchingSet(self.new_brightness_array)
        self.new_total_lines_set = self.new_hatching_array.create_hatching_set()

        # for line-rendering readability
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.x_offset = 0
        self.y_offset = 0
        self.u_idx = 0      # unit index
        self.y_unit_group_displacement = units_high * (pixels_per_unit_y + pixels_of_deadspace)     # space btwn each unit group

        self.drawn_preview = False

    def create_hatching_preview(self, screen, lines_set):
        """Display entire image in hatching style in the pygame window"""
        # preview hatching pattern
        for y in range(units_high):
            self.y_offset = y * (pixels_per_unit_y + pixels_of_deadspace)
            for x in range(units_wide):
                self.x_offset = x * (pixels_per_unit_x + pixels_of_deadspace)
                for line in lines_set[self.u_idx]:
                    # local to global coords
                    self.x1 = line[0] + self.x_offset
                    self.y1 = line[1] + self.y_offset
                    self.x2 = line[2] + self.x_offset
                    self.y2 = line[3] + self.y_offset

                    # render
                    pygame.draw.line(screen,
                                     preview_line_color,
                                     (self.x1, self.y1),
                                     (self.x2, self.y2))
                self.u_idx += 1

    def create_printing_layout_preview(self, screen, lines_set):
        """Display the order of printing with the image reordered into groups of 2x2 units"""
        # preview unlaid units using reorder script (2x2 layout)
        for unit_group in lines_set:
            self.y_unit_group_displacement += 2 * (pixels_per_unit_y + pixels_of_deadspace)
            for unit in unit_group:
                for line in unit:
                    # render
                    pygame.draw.line(screen,
                                     preview_line_color,
                                     (line[0], line[1] + self.y_unit_group_displacement),
                                     (line[2], line[3] + self.y_unit_group_displacement))



##########################################################
####################  MAIN CODE  #########################
##########################################################



if __name__ == '__main__':
    lp = LinearPrinter()
    total_lines_set = lp.new_total_lines_set

    # open a new pygame iteration
    pygame.init()
    screen = pygame.display.set_mode(preview_image_dim)
    pygame.display.set_caption(preview_image_cap)
    screen.fill((255, 255, 255))

    displayed_preview = False
    begun_printing = False
    redo_this_print = False
    start_button_counter_set = 5000
    start_button_counter = 5000

    # main loop (how exciting)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if start_button_counter <= 0:
                begun_printing = True
            else:
                start_button_counter -= 1
        else:
            start_button_counter = start_button_counter_set

        # preview before printing
        if not displayed_preview:
            lp.create_hatching_preview(screen, total_lines_set)
            reordered_total_lines_set = reorder_units_groups_of_four(total_lines_set)
            #lp.create_printing_layout_preview(screen, reordered_total_lines_set)
            displayed_preview = True

        # if input() == "begin":        # for debugging
        #     begun_printing = True

        # display most recent frame
        pygame.display.flip()

        # printing logic and printer control
        if begun_printing:
            raw_reordered_total_lines = get_raw_converted_total_lines(reordered_total_lines_set)

            # main printing code to control printer
            printer = establish_printer_connection(printer_port, baud_rate)
            if not printer:
                exit()

            # orient the pen
            prepare_print(printer)

            new_input = ""
            while new_input not in ["yes", "no", "y", "n"]:
                new_input = input("Continue with a standard print? (not a single note, yes/no):  ")

            if new_input == "yes" or new_input == "y":
                # begin sending g-code commands to the printer
                for i, new_print in enumerate(raw_reordered_total_lines):
                    new_input = input("Press enter to continue... (type 'skip' to skip or a number to print just one note)").lower()
                    if new_input == "skip":
                        continue

                    # get g-code commands for this group of units
                    new_gcode_cmds = convert_to_gcode(new_print)
                    response = "redo-print"

                    while response == "redo-print":
                        # print
                        print_unit_group(printer, new_gcode_cmds)

                        # each iteration of this loop is a full print, which can take 20 minutes-ish,
                        # so handle user input directly through terminal
                        while input('---- Has the printer finished? (type "yes" to continue) ---- ').lower() != "yes":
                            pass

                        response = ""
                        if i == len(raw_reordered_total_lines) - 1:
                            while response not in ["finish", "redo-print"]:
                                response = input(
                                    '---- What would you like to do next? ("finish", "redo-print") ---- ').lower()
                        else:
                            while response not in ["continue", "redo-print", "abort"]:
                                response = input(
                                    '---- What would you like to do next? ("continue", "redo-print", "abort") ---- ').lower()
                        if response == 'abort':
                            exit()
                        if response == 'finish':
                            print('\n'*5)
                            print("*DING* Your print is ready. Yay!")
            else:
                finished = False
                while not finished:
                    # print just one specific note
                    unit_num = -1
                    while unit_num < 0:
                        new_input = input("Which number unit would you like to print?  ")
                        try:
                            unit_num = int(new_input)
                            if unit_num > units_high * units_wide:
                                # handle error
                                unit_num = -1
                                print(f"That number is out of range. The range is 1 to {units_high * units_wide}")
                            else:
                                # find the index of the unit
                                unit_num -= 1
                                print_num = math.floor(unit_num / 4)
                                unit_idx = unit_num - print_num * 4
                                new_gcode_cmds = convert_to_gcode(reordered_total_lines_set[print_num][unit_idx])
                                print_unit_group(printer, new_gcode_cmds)

                        except ValueError:
                            unit_num = -1
                            print("Incorrect input. Expected a unit number to print (ex. '31' for the 31st note of a print, top left to bottom right)")
                    if input("Would you like to print another note? (yes/no): ").lower() == "no":
                        finished = True
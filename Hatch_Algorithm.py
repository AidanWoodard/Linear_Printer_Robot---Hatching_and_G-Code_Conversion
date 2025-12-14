"""
#############################################################
SUMMARY: This algorithm converts an image into a set of points
in a list.This is the hatching pattern that the Sharpie will draw.
The density of each pattern is directly associated with the
brightness of each pixel area. The list is passed onto the
'Unit Reorderer' algorithm which will prepare the lines for
printing.
#############################################################
"""

from Univ_Settings import *


################### LINE WRITING LOGIC FUNCS
# these funcs check if a pixel should be dark depending on how many above are
# covered. for some shades, there must be 1 dark pixel per 4 pixels (checked
# vertically.) EX: 'check_1by2' means draw pixel if above space is empty (1 pixel
# per 2 pixels)

def check_1by4(drawn_points, pos, unit_brightness_array):
    """
    LIGHT VALUE IS 5
    """
    x = pos[0]
    y = pos[1]
    can_draw = (
        [x, y-1] not in drawn_points and
         [x, y-2] not in drawn_points and
          [x, y-3] not in drawn_points
    )

    if can_draw:
        drawn_points.append([x, y])
    return can_draw

def check_1by2(drawn_points, pos, unit_brightness_array):
    """
    LIGHT VALUE IS 4
    """
    x = pos[0]
    y = pos[1]
    can_draw = ([x, y-1] not in drawn_points or unit_brightness_array[x, y-1] != 4)
    if can_draw:
        drawn_points.append([x, y])
    return can_draw

def check_2by3(drawn_points, pos, unit_brightness_array):
    """
    LIGHT VALUE IS 3
    """
    x = pos[0]
    y = pos[1]
    num_above = 0

    # check the above 2 lines (must be 1 or less lines in the above 2 spaces)
    if [x, y-1] in drawn_points and unit_brightness_array[x, y-1] == 3:
        num_above += 1
    if [x, y-2] in drawn_points and unit_brightness_array[x, y-2] == 3:
        num_above += 1

    can_draw = (num_above <= 1)
    if can_draw:
        drawn_points.append([x, y])
    return can_draw

def check_3by4(drawn_points, pos, unit_brightness_array):
    """
    LIGHT VALUE IS 2
    """
    x = pos[0]
    y = pos[1]
    num_above = 0

    for i in range(1, 4):
        if [x, y-i] in drawn_points and unit_brightness_array[x, y-i] == 2:
            num_above += 1

    can_draw = (num_above <= 2)
    if can_draw:
        drawn_points.append([x, y])
    return can_draw

################### MAIN CLASS

class HatchingSet:
    """Represents a list of all lines to draw (created in 'main.py' file)"""

    def __init__(self, brightness_arrays):
        # number of units wide and high the image will be (from settings.py)
        self.WIDTH = units_wide
        self.HEIGHT = units_wide

        # list of all unit brightness values (list of arrays)
        self.brightness_arrays = brightness_arrays

        # this will hold all the points of lines divided by unit in a hellish
        # series of lists of lists of lists: [[[x1, y1, x2, y2], ...], ...].
        # in other words, at the smallest scale is a set of 2 points representing a line in the format
        # [x1, y1, x2, y2]. At the next level, it's a list of lines. At the highest, it's a list of units.
        self.total_lines = []

    def create_hatching_set(self):
        """Main func"""
        # loop through all units
        for i, unit in enumerate(self.brightness_arrays):
            new_unit = NewUnit(self.brightness_arrays[i])
            new_unit.hatch_note()
            self.total_lines.append(new_unit.linesToPrint)

        return self.total_lines

##################### UNIT CLASS

class NewUnit:
    """All of the lines for one sticky note (a 'unit')"""

    def __init__(self, unit_brightness_array):
        # array of pixels
        self.raw_brightness_array = unit_brightness_array
        self.brightness_array = self.map_brightness_values(self.raw_brightness_array)

        # start of a new line when adding to 'linesToPrint'
        self.newx = 0
        self.newy = 0
        self.drawing_new_line = False

        # list of all points in a line. Used for logic to draw or skip a line.
        # is in the order of [[x1, y1], [x2, y2], ...], so that at any point,
        # the point can be looked up as 'if [xn, yn] in covered_points: ...'
        self.covered_points = []

        # this holds a series of 4 item lists, each being the coords of
        # a line to turn into g-code. It will hold all of this unit's lines
        # Ex: [[x1, y1, x2, y2], ... [xn, yn, xn+1, yn+1]]
        self.linesToPrint = []

    ################## FUNCS

    def hatch_note(self):
        """Use hatching algorithm to turn image into a set of lines and return that list"""
        for y in range(pixels_per_unit_y):
            for x in range(pixels_per_unit_x):
                light_val = self.brightness_array[y][x]
                curr_pos = [x, y]
                match light_val:
                    # darkest
                    case 1:
                        # always draw a line
                        self.covered_points.append(curr_pos)
                        self.end_or_start_line(True, curr_pos)
                    # if not darkest val, decide if draw line
                    case 2:
                        self.end_or_start_line(check_3by4(self.covered_points, curr_pos, self.brightness_array), curr_pos)
                    case 3:
                        self.end_or_start_line(check_2by3(self.covered_points, curr_pos, self.brightness_array), curr_pos)
                    case 4:
                        self.end_or_start_line(check_1by2(self.covered_points, curr_pos, self.brightness_array), curr_pos)
                    case 5:
                        self.end_or_start_line(check_1by4(self.covered_points, curr_pos, self.brightness_array), curr_pos)
                    case 6:
                        self.end_or_start_line(False, curr_pos), curr_pos

    def end_or_start_line(self, clear_to_draw, pos):
        if clear_to_draw:
            if not self.drawing_new_line:
                self.start_line(pos)
            # edge case (last pixel of unit - could be 1 pixel length line)
            if pos[0] == pixels_per_unit_x - 1:
                self.end_line(pos)
        # end a line also if at end of note
        elif self.drawing_new_line:
            self.end_line(pos)

    def start_line(self, pos):
        """Start drawing a new line by setting x/yStart"""
        self.newx = pos[0]
        self.newy = pos[1]
        self.drawing_new_line = True

    def end_line(self, pos):
        """End a line"""
        self.linesToPrint.append([self.newx, self.newy, pos[0], pos[1]])
        self.drawing_new_line = False

    def map_brightness_values(self, brightness_array):
        # 6 brightest (white), 1 darkest
        new_brightness_array = brightness_array

        # convert whole array at once
        for y in range(pixels_per_unit_y):
            for x in range(pixels_per_unit_x):
                light_val = brightness_array[y][x]
                # if pixel should be white
                if light_val >= white_cap:
                    new_brightness_array[y][x] = 6
                else:
                    # map remaining values onto a light value 1-5
                    remaining_range = white_cap / 5
                    for i in range(1, 6):
                        if light_val <= (i * remaining_range):
                            new_brightness_array[y][x] = i
                            break

        return new_brightness_array